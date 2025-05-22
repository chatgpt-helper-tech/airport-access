import feedparser
from datetime import datetime

sources = {
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "Google News": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
}

md_lines = []
md_lines.append("# 📰 最新国际新闻（BBC + Google News）自动更新\n")
md_lines.append(f"更新时间：{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

for source_name, rss_url in sources.items():
    feed = feedparser.parse(rss_url)
    md_lines.append(f"\n## 🌍 {source_name} 最新 10 条")
    md_lines.append("| 标题 | 链接 |\n|------|------|")
    for entry in feed.entries[:10]:
        md_lines.append(f"| {entry.title} | [阅读原文]({entry.link}) |")

md_lines.append("\n> 每 20 分钟自动更新一次，由 GitHub Actions 驱动。来源：BBC News & Google News RSS。")

with open("latest-news.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
