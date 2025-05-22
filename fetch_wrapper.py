import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "news-fetch-core"))

from news_core import run_fetch_news

if __name__ == "__main__":
    run_fetch_news("latest-news.md")
