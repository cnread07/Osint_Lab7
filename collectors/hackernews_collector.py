# hackernews_collector.py
import requests
from datetime import datetime

def fetch_hackernews(keyword, limit=10):
    results = []
    try:
        url = f'https://hn.algolia.com/api/v1/search?query={requests.utils.quote(keyword)}&hitsPerPage={limit}'
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for hit in r.json().get('hits', [])[:limit]:
                user = hit.get('author') or ''
                title = hit.get('title') or hit.get('story_text') or ''
                created = hit.get('created_at') or ''
                link = hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                results.append({
                    'platform': 'hackernews',
                    'user': user,
                    'text': title,
                    'timestamp': created,
                    'url': link
                })
        else:
            print("HN API error:", r.status_code)
    except Exception as e:
        print("hackernews_collector error:", e)
    return results
