#!/usr/bin/env python3
"""
抓取国外新闻 RSS，生成「最新国外新闻速览」区块。

说明：
- 仅写入标题和原文链接，避免动态内容喧宾夺主。
- 只有新闻链接列表发生变化时才更新 daily-news.md，减少纯时间戳提交。
- 默认读取 scripts/daily_check_config.json，可通过环境变量
  AIRPORT_ACCESS_DAILY_CHECK_CONFIG 指定其他配置文件。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable, List, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


ROOT_DIR = Path(__file__).resolve().parents[1]
NEWS_PATH = ROOT_DIR / "daily-news.md"

MARKER_START = "<!-- daily-check start -->"
MARKER_END = "<!-- daily-check end -->"

DEFAULT_LIMIT = 10
MAX_ITEMS_PER_SOURCE = 8
REQUEST_TIMEOUT = 15
LINK_PATTERN = re.compile(r"^\d+\.\s+\[[^\]]+\]\(([^)]+)\)", re.MULTILINE)


@dataclass
class FeedConfig:
    name: str
    url: str


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    published_at: datetime


def load_config() -> tuple[List[FeedConfig], int]:
    env_path = os.environ.get("AIRPORT_ACCESS_DAILY_CHECK_CONFIG")
    path = Path(env_path) if env_path else ROOT_DIR / "scripts" / "daily_check_config.json"

    if not path.exists():
        raise SystemExit(f"配置文件未找到：{path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    limit = int(data.get("limit", DEFAULT_LIMIT))
    sources_data = data.get("sources") or []
    sources: List[FeedConfig] = []
    for item in sources_data:
        name = str(item.get("name", "")).strip()
        url = str(item.get("url", "")).strip()
        if name and url:
            sources.append(FeedConfig(name=name, url=url))

    if not sources:
        raise SystemExit("配置文件中未找到有效的新闻源（sources 数组为空）")

    return sources, max(1, limit)


def fetch_feed(feed: FeedConfig) -> List[NewsItem]:
    headers = {
        "User-Agent": "Airport-Access-News-Digest/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
    }
    request = Request(feed.url, headers=headers, method="GET")

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            payload = response.read()
    except HTTPError as exc:
        raise RuntimeError(f"{feed.name} HTTP 错误：{exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"{feed.name} 网络错误：{exc.reason}") from exc
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"{feed.name} 请求失败：{exc}") from exc

    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise RuntimeError(f"{feed.name} XML 解析失败：{exc}") from exc

    items = parse_items(root, feed.name)
    if not items:
        raise RuntimeError(f"{feed.name} 未返回可用新闻")
    return items[:MAX_ITEMS_PER_SOURCE]


def parse_items(root: ET.Element, source_name: str) -> List[NewsItem]:
    items: List[NewsItem] = []

    channel_items = root.findall("./channel/item")
    if channel_items:
        for item in channel_items:
            news = parse_rss_item(item, source_name)
            if news:
                items.append(news)
        return items

    atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("./atom:entry", atom_ns):
        news = parse_atom_entry(entry, source_name, atom_ns)
        if news:
            items.append(news)
    return items


def parse_rss_item(item: ET.Element, source_name: str) -> NewsItem | None:
    title = clean_text(item.findtext("title"))
    link = clean_text(item.findtext("link"))
    pub_text = clean_text(item.findtext("pubDate")) or clean_text(item.findtext("published"))

    if not title or not link:
        return None

    return NewsItem(
        title=title,
        link=link,
        source=source_name,
        published_at=parse_datetime(pub_text),
    )


def parse_atom_entry(
    entry: ET.Element,
    source_name: str,
    namespaces: dict[str, str],
) -> NewsItem | None:
    title = clean_text(entry.findtext("atom:title", default="", namespaces=namespaces))
    updated = clean_text(entry.findtext("atom:updated", default="", namespaces=namespaces))
    published = clean_text(entry.findtext("atom:published", default="", namespaces=namespaces))

    link = ""
    for link_node in entry.findall("atom:link", namespaces):
        href = (link_node.attrib.get("href") or "").strip()
        rel = (link_node.attrib.get("rel") or "alternate").strip()
        if href and rel in {"alternate", ""}:
            link = href
            break

    if not title or not link:
        return None

    return NewsItem(
        title=title,
        link=link,
        source=source_name,
        published_at=parse_datetime(published or updated),
    )


def parse_datetime(value: str) -> datetime:
    if not value:
        return datetime.min

    try:
        dt = parsedate_to_datetime(value)
        return dt.astimezone().replace(tzinfo=None)
    except Exception:  # noqa: BLE001
        pass

    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is not None:
                return dt.astimezone().replace(tzinfo=None)
            return dt
        except ValueError:
            continue
    return datetime.min


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split()).strip()


def deduplicate(items: Sequence[NewsItem]) -> List[NewsItem]:
    deduped: List[NewsItem] = []
    seen: set[str] = set()
    for item in items:
        key = item.link.strip().lower() or item.title.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def select_latest(items: Iterable[NewsItem], limit: int) -> List[NewsItem]:
    deduped = deduplicate(list(items))
    deduped.sort(key=lambda item: item.published_at, reverse=True)
    return deduped[:limit]


def format_datetime_cn(dt: datetime) -> str:
    return f"{dt.year}年{dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"


def build_digest(items: Sequence[NewsItem], sources: Sequence[FeedConfig]) -> str:
    now = datetime.now()
    lines = [
        "更新时间：" + format_datetime_cn(now),
        "",
    ]

    for idx, item in enumerate(items, start=1):
        title = item.title.replace("[", "［").replace("]", "］")
        lines.append(f"{idx}. [{title}]({item.link})")

    return "\n".join(lines)


def extract_marker_block(content: str) -> str:
    start_index = content.find(MARKER_START)
    end_index = content.find(MARKER_END)
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise RuntimeError("文档中未找到新闻区块标记")
    return content[start_index + len(MARKER_START) : end_index].strip()


def extract_digest_links(block: str) -> List[str]:
    return [match.group(1).strip() for match in LINK_PATTERN.finditer(block)]


def replace_marker_block(content: str, new_block: str) -> str:
    start_index = content.find(MARKER_START)
    end_index = content.find(MARKER_END)
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise RuntimeError("文档中未找到新闻区块标记")

    end_index += len(MARKER_END)
    replacement = f"{MARKER_START}\n{new_block}\n{MARKER_END}"
    return content[:start_index] + replacement + content[end_index:]


def update_doc(path: Path, digest: str, selected_items: Sequence[NewsItem]) -> bool:
    content = path.read_text(encoding="utf-8")
    old_block = extract_marker_block(content)
    old_links = extract_digest_links(old_block)
    new_links = [item.link for item in selected_items]

    if old_links == new_links:
        print(f"[news-digest] 新闻列表未变化，跳过 {path.name} 更新")
        return False

    updated = replace_marker_block(content, digest)
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    sources, limit = load_config()
    all_items: List[NewsItem] = []
    errors: List[str] = []

    for source in sources:
        try:
            all_items.extend(fetch_feed(source))
        except RuntimeError as exc:
            errors.append(str(exc))

    if not all_items:
        details = "；".join(errors) if errors else "未知错误"
        raise SystemExit(f"新闻抓取失败：{details}")

    selected_items = select_latest(all_items, limit)
    digest = build_digest(selected_items, sources)
    changed = update_doc(NEWS_PATH, digest, selected_items)

    if changed:
        print(f"[news-digest] {NEWS_PATH.name} 新闻区块已更新")

    if errors:
        print("[news-digest] 部分新闻源抓取失败：")
        for message in errors:
            print(f"- {message}")


if __name__ == "__main__":
    main()
