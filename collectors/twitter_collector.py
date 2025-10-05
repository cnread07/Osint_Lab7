# collectors/twitter_collector.py
import os, time
from dotenv import load_dotenv
import tweepy

load_dotenv()
BEARER = os.getenv("TWITTER_BEARER")

def fetch_twitter_v2(query="osint", max_results=200):
    """Fetch recent tweets (10-100) using Twitter API v2 (bearer token)."""
    if not BEARER:
        print("TWITTER_BEARER not set; skipping v2 fetch")
        return []
    if max_results < 10:
        max_results = 10
    if max_results > 100:
        max_results = 100

    client = tweepy.Client(bearer_token=BEARER)
    # Single attempt: if rate-limited, don't block the pipeline — return empty and log.
    try:
        resp = client.search_recent_tweets(query=query, tweet_fields=["created_at","lang","author_id"], max_results=max_results)
    except tweepy.TooManyRequests:
        print("Twitter API rate-limited (429). Skipping twitter v2 fetch this run.")
        return []
    except Exception as e:
        print("Twitter API error:", e)
        return []

    results = []
    if resp and resp.data:
        for t in resp.data:
            results.append({
                "platform": "twitter",
                "user": str(t.author_id),
                "timestamp": str(t.created_at),
                "text": t.text,
                "url": f"https://twitter.com/i/web/status/{t.id}"
            })
    return results
