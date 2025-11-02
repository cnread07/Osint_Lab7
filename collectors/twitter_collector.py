# twitter_collector.py
from datetime import datetime
import snscrape.modules.twitter as sntwitter

def fetch_twitter(keyword, limit=10):
    results = []
    try:
        scraper = sntwitter.TwitterSearchScraper(keyword)
        for i, tweet in enumerate(scraper.get_items()):
            if i >= limit:
                break
            results.append({
                'platform': 'twitter',
                'user': getattr(tweet.user, 'username', '') or getattr(tweet.user, 'displayname', ''),
                'text': tweet.content,
                'timestamp': tweet.date.strftime("%Y-%m-%dT%H:%M:%S"),
                'url': f"https://twitter.com/{tweet.user.username}/status/{tweet.id}"
            })
    except Exception as e:
        print("twitter_collector error:", e)
    return results
