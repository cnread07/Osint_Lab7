# collectors/snscrape_collector.py
import json
import shutil
import subprocess
from typing import List, Dict


def _fetch_with_package(query: str, limit: int) -> List[Dict]:
    # Import inside function to avoid import-time failures on some Python versions
    import snscrape.modules.twitter as sntwitter

    results = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit:
            break
        results.append({
            "platform": "twitter",
            "user": tweet.user.username,
            "timestamp": str(tweet.date),
            "text": tweet.content,
            "url": tweet.url
        })
    return results


def _fetch_with_cli(query: str, limit: int) -> List[Dict]:
    """Fallback that calls the `snscrape` CLI and parses JSON lines."""
    if not shutil.which("snscrape"):
        raise RuntimeError("snscrape Python package import failed and CLI 'snscrape' not found")

    cmd = [
        "snscrape",
        "--jsonl",
        "-n", str(limit),
        "twitter-search",
        query,
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    if proc.returncode != 0:
        # Provide the stderr for debugging but don't crash the caller
        raise RuntimeError(f"snscrape CLI failed: {err.strip()}")

    results = []
    for line in out.splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            results.append({
                "platform": "twitter",
                "user": obj.get("user", {}).get("username") if isinstance(obj.get("user"), dict) else obj.get("user"),
                "timestamp": obj.get("date"),
                "text": obj.get("content") or obj.get("rawContent") or "",
                "url": obj.get("url")
            })
        except Exception:
            continue
    return results


def fetch_twitter_scrape(query: str = "osint", limit: int = 200) -> List[Dict]:
    """Fetch tweets using snscrape. Tries Python package first, then CLI fallback.

    Returns a list of dicts with keys: platform, user, timestamp, text, url.
    """
    try:
        return _fetch_with_package(query, limit)
    except AttributeError as ae:
        # Known incompatibility: older snscrape uses importer.find_module which
        # is removed in newer importlib/FileFinder implementations. Fail gracefully.
        print("snscrape package import failed due to legacy importer API; skipping snscrape (", ae, ")")
        return []
    except Exception as e_pkg:
        # Try CLI fallback
        try:
            return _fetch_with_cli(query, limit)
        except Exception as e_cli:
            # Raise a combined error for debugging
            raise RuntimeError(f"snscrape fetch failed (package error: {e_pkg}; cli error: {e_cli})")

