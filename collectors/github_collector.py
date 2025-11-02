# github_collector.py
import os
import requests
from datetime import datetime

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # optional: set in .env to increase rate limit

def fetch_github(keyword, limit=10):
    results = []
    try:
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        q = requests.utils.quote(keyword)
        url = f'https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={limit}'
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for repo in data.get('items', [])[:limit]:
                results.append({
                    'platform': 'github',
                    'user': repo.get('owner', {}).get('login', ''),
                    'text': repo.get('description') or repo.get('name'),
                    'timestamp': repo.get('created_at') or '',
                    'url': repo.get('html_url')
                })
        else:
            print("GitHub API returned:", resp.status_code, resp.text)
    except Exception as e:
        print("github_collector error:", e)
    return results
