import feedparser
from datetime import datetime

def run_fetch_news(output_file):
    sources = {
        "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
        "Google News": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    }

    md_lines = [f"# 📰 新闻自动更新\n更新时间: {datetime.utcnow()} UTC\n"]
    for name, url in sources.items():
        feed = feedparser.parse(url)
        md_lines.append(f"\n## {name}\n| 标题 | 链接 |\n|------|------|")
        for entry in feed.entries[:10]:
            md_lines.append(f"| {entry.title} | [阅读原文]({entry.link}) |")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

if __name__ == "__main__":
    run_fetch_news("latest-news.md")