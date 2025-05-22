import feedparser
from datetime import datetime

rss_url = "https://feeds.bbci.co.uk/news/rss.xml"
feed = feedparser.parse(rss_url)

md_lines = []
md_lines.append("# 🌐 最新 BBC 国际新闻（自动更新）\n")
md_lines.append(f"更新时间：{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}（UTC）\n")
md_lines.append("| 标题 | 链接 |\n|------|------|")

for entry in feed.entries[:5]:
    title = entry.title
    link = entry.link
    md_lines.append(f"| {title} | [阅读原文]({link}) |")

md_lines.append("\n> 本列表每 20 分钟自动更新一次，由 GitHub Actions 驱动。来源：BBC News RSS。")

with open("latest-news.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
