import feedparser
from datetime import datetime
import zoneinfo  # Python 3.9+

def run_fetch_news(output_file="latest-news.md"):
    sources = {
        "🌐 BBC 新闻": "https://feeds.bbci.co.uk/news/rss.xml",
        "🔍 Google 新闻": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    }

    now = datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y年%m月%d日 %H:%M:%S（北京时间）")

    md_lines = [
        "# 📰 新闻自动更新",
        "",
        f"**🕒 更新时间：{now}**  ",
        "",
        "---"
    ]

    for name, url in sources.items():
        md_lines.append(f"\n### {name}")
        md_lines.append("")
        md_lines.append("| 标题 | 原文链接 |")
        md_lines.append("| ---- | -------- |")
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title = entry.title.replace("|", "｜").replace("\n", " ").strip()
            link = entry.link
            md_lines.append(f"| {title} | [阅读全文]({link}) |")

    md_lines.append("\n> 本页面内容来自 BBC 和 Google News RSS 源，自动每 10 分钟更新一次。")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

if __name__ == "__main__":
    run_fetch_news()
