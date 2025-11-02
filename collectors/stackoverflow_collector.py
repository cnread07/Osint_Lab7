# stackoverflow_collector.py
import requests

def fetch_stackoverflow(keyword, limit=10):
    results = []
    try:
        url = "https://api.stackexchange.com/2.3/search/advanced"
        params = {
            'order': 'desc',
            'sort': 'relevance',
            'site': 'stackoverflow',
            'q': keyword,
            'pagesize': limit
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            for item in r.json().get('items', [])[:limit]:
                results.append({
                    'platform': 'stackoverflow',
                    'user': item.get('owner', {}).get('display_name', ''),
                    'text': item.get('title'),
                    'timestamp': '',
                    'url': item.get('link')
                })
        else:
            print("StackOverflow API error:", r.status_code)
    except Exception as e:
        print("stackoverflow_collector error:", e)
    return results
