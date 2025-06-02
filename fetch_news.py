import feedparser
from datetime import datetime
import zoneinfo  # Python 3.9+

def run_fetch_news(output_file="latest-news.md"):
    sources = {
        "🌍 BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
        "📰 Google News": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    }

    now = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y年%m月%d日 %H:%M:%S（北京时间）")

    md_lines = [
        "# 🧠 新闻自动更新",
        "",
        f"🕒 更新时间：**{now}**",
        "",
        "---"
    ]

    for name, url in sources.items():
        md_lines.append(f"\n## {name}")
        md_lines.append("")
        md_lines.append("| 🌐 标题 | 🔗 原文链接 |")
        md_lines.append("|--------|-------------|")

        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title = entry.title.replace("|", "｜").replace("\n", " ").strip()
            link = entry.link

            # 过滤掉 Google News 中的中文条目
            if "Google" in name and any(u'\u4e00' <= ch <= u'\u9fff' for ch in title):
                continue

            md_lines.append(f"| {title} | [阅读全文]({link}) |")

    md_lines.append("\n---")
    md_lines.append("> 本页面内容来自公开的 BBC 和 Google 新闻 RSS 源，每 10 分钟自动更新。")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

def run_fetch_news_docs(output_file="./docs/latest-news.md"):
    sources = {
        "🌍 BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
        "📰 Google News": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    }

    now = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y年%m月%d日 %H:%M:%S（北京时间）")

    md_lines = [
        "# 🧠 新闻自动更新",
        "",
        f"🕒 更新时间：**{now}**",
        "",
        "---"
    ]

    for name, url in sources.items():
        md_lines.append(f"\n## {name}")
        md_lines.append("")
        md_lines.append("| 🌐 标题 | 🔗 原文链接 |")
        md_lines.append("|--------|-------------|")

        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title = entry.title.replace("|", "｜").replace("\n", " ").strip()
            link = entry.link

            # 过滤掉 Google News 中的中文条目
            if "Google" in name and any(u'\u4e00' <= ch <= u'\u9fff' for ch in title):
                continue

            md_lines.append(f"| {title} | [阅读全文]({link}) |")

    md_lines.append("\n---")
    md_lines.append("> 本页面内容来自公开的 BBC 和 Google 新闻 RSS 源，每 10 分钟自动更新。")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

if __name__ == "__main__":
    run_fetch_news()
    run_fetch_news_docs()
