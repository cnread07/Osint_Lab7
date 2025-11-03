# twitter_collector.py
from datetime import datetime
import snscrape.modules.twitter as sntwitter
import time

def fetch_twitter(keyword, limit=10):
    results = []
    try:
        scraper = sntwitter.TwitterSearchScraper(keyword)
        for i, tweet in enumerate(scraper.get_items()):
            if i >= limit:
                break

            user = getattr(tweet.user, 'username', None) or getattr(tweet.user, 'displayname', 'unknown')

            results.append({
                'platform': 'twitter',
                'user': user,
                'text': tweet.content,
                'timestamp': tweet.date.strftime("%Y-%m-%dT%H:%M:%S") if tweet.date else None,
                'url': f"https://x.com/{tweet.user.username}/status/{tweet.id}"
            })

        # Handle case where snscrape returns nothing
        if not results:
            print(f"[twitter_collector] No tweets found for keyword: '{keyword}'")

    except Exception as e:
        print(f"[twitter_collector] error: {type(e).__name__}: {e}")
        time.sleep(2)  # small delay in case of rate limit
    return results
