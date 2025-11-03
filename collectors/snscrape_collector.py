# snscrape_collector.py

from twitter_collector import fetch_twitter
from reddit_collector import fetch_reddit
from sentiment import add_sentiment
from database import save_to_db

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
    # Add sentiment and store in DB
    results = add_sentiment(results)
    save_to_db(results)
    return results
