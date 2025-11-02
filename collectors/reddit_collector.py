# reddit_collector.py
import snscrape.modules.reddit as snreddit
from datetime import datetime

def fetch_reddit(keyword, limit=10):
    results = []
    try:
        scraper = snreddit.RedditSearchScraper(keyword)
        for i, post in enumerate(scraper.get_items()):
            if i >= limit:
                break
            # post has attributes: title, selftext, url, author, created
            text = (post.title or '') + ("\n\n" + (post.selftext or '') if getattr(post, 'selftext', None) else '')
            timestamp = ''
            try:
                timestamp = post.created.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                timestamp = ''
            results.append({
                'platform': 'reddit',
                'user': getattr(post, 'author', '[deleted]'),
                'text': text,
                'timestamp': timestamp,
                'url': getattr(post, 'url', '')
            })
    except Exception as e:
        print("reddit_collector error:", e)
    return results
