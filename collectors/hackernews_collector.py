# collectors/hackernews_collector.py
import requests
from typing import List, Dict
import time

def fetch_hackernews(query="osint", limit=5) -> List[Dict]:
    """Fetch HackerNews stories using their free API.
    
    No API key required, completely free to use.
    API Docs: https://github.com/HackerNews/API
    
    Returns a list of dicts with keys: platform, user, timestamp, text, url.
    """
    try:
        # Search using Algolia HN Search API (free, no key needed)
        search_url = "http://hn.algolia.com/api/v1/search"
        params = {
            'query': query,
            'tags': 'story',
            'hitsPerPage': limit
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('hits', []):
            # Get the actual story URL
            story_url = f"https://news.ycombinator.com/item?id={item.get('objectID', '')}"
            
            results.append({
                "platform": "hackernews",
                "user": item.get('author', 'anonymous'),
                "timestamp": item.get('created_at', ''),
                "text": item.get('title', ''),
                "url": story_url
            })
        
        return results
        
    except Exception as e:
        print(f"HackerNews collector failed: {type(e).__name__}: {e}")
        return []