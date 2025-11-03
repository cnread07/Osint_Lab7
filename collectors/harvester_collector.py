# harvester_collector.py

import subprocess
import json
import os
from datetime import datetime
from sentiment import add_sentiment
from database import save_to_db

def fetch_theharvester(keyword, limit=10):
    """
    If theHarvester CLI is installed, tries to run it and parse JSON output.
    Returns only real results; no mock/fallback data.
    """
    results = []
    try:
        # try to call theHarvester CLI (if installed)
        cmd = ["theHarvester", "-d", keyword, "-b", "bing", "-l", str(limit), "-f", "harvester_output.json"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if os.path.exists("harvester_output.json"):
            with open("harvester_output.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            # theHarvester JSON structure depends on version; we look for 'emails' and 'hosts'
            for email in data.get('emails', []):
                results.append({
                    'platform': 'harvester',
                    'user': email.split("@")[0] if "@" in email else email,
                    'text': f"Email: {email}",
                    'timestamp': datetime.utcnow().isoformat(),
                    'url': ''
                })
            for host in data.get('hosts', []):
                results.append({
                    'platform': 'harvester',
                    'user': 'host',
                    'text': f"Host: {host}",
                    'timestamp': datetime.utcnow().isoformat(),
                    'url': ''
                })
            try:
                os.remove("harvester_output.json")
            except:
                pass
    except Exception as e:
        print("harvester_collector error:", e)
    # Only real results, no fallback
    results = add_sentiment(results)
    save_to_db(results)
    return results[:limit]
