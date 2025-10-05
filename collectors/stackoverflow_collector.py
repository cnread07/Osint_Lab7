# collectors/stackoverflow_collector.py
import requests
from typing import List, Dict
import time
from datetime import datetime

def fetch_stackoverflow(query="osint", limit=5) -> List[Dict]:
    """Fetch Stack Overflow questions using their free API.
    
    No API key required, but has rate limits (300 requests/day per IP).
    API Docs: https://api.stackexchange.com/docs
    
    Returns a list of dicts with keys: platform, user, timestamp, text, url.
    """
    try:
        url = "https://api.stackexchange.com/2.3/search"
        params = {
            'order': 'desc',
            'sort': 'activity',
            'intitle': query,
            'site': 'stackoverflow',
            'pagesize': limit,
            'filter': 'default'  # Include more fields
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            # Convert Unix timestamp to readable format
            timestamp = datetime.fromtimestamp(
                item.get('creation_date', 0)
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            results.append({
                "platform": "stackoverflow",
                "user": item.get('owner', {}).get('display_name', 'anonymous'),
                "timestamp": timestamp,
                "text": item.get('title', ''),
                "url": item.get('link', '')
            })
        
        # Check rate limit info
        quota_remaining = data.get('quota_remaining', 'unknown')
        if quota_remaining != 'unknown' and quota_remaining < 50:
            print(f"⚠️ Stack Overflow API quota low: {quota_remaining} requests remaining")
        
        return results
        
    except Exception as e:
        print(f"Stack Overflow collector failed: {type(e).__name__}: {e}")
        return []