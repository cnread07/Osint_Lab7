# snscrape_collector.py
from twitter_collector import fetch_twitter
from reddit_collector import fetch_reddit

def fetch_snscrape(keyword, limit=10):
    results = []
    try:
        results.extend(fetch_twitter(keyword, limit=limit//2 or 1))
    except Exception:
        pass
    try:
        results.extend(fetch_reddit(keyword, limit=limit//2 or 1))
    except Exception:
        pass
    return results
