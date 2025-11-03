# mastodon_collector.py

import requests
from datetime import datetime
from sentiment import add_sentiment
from database import save_to_db

# This function attempts to use the Mastodon instance search via mastodon.social or returns stub
KNOWN_INSTANCES = [
    "https://mastodon.social",
    "https://mstdn.social"
]

def fetch_mastodon(keyword, limit=10):
    results = []
    try:
        # Try Mastodon instance public timeline search (if instance supports it)
        for inst in KNOWN_INSTANCES:
            try:
                search_url = f"{inst}/api/v2/search"
                params = {'q': keyword, 'limit': limit, 'resolve': True}
                r = requests.get(search_url, params=params, timeout=8)
                if r.status_code == 200:
                    data = r.json()
                    for status in data.get('statuses', [])[:limit]:
                        results.append({
                            'platform': 'mastodon',
                            'user': status.get('account', {}).get('acct', ''),
                            'text': status.get('content', ''),
                            'timestamp': status.get('created_at', ''),
                            'url': status.get('url')
                        })
                    if results:
                        break
            except Exception:
                continue
        # fallback: if not found, return empty list
    except Exception as e:
        print("mastodon_collector error:", e)
    # Add sentiment and store in DB
    results = add_sentiment(results)
    save_to_db(results)
    return results
