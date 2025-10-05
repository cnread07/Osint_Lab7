# collectors/reddit_collector.py
import os
from dotenv import load_dotenv
load_dotenv()
import praw

REDDIT_ID = os.getenv("REDDIT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

# Trim accidental whitespace from environment values
for varname in ("REDDIT_ID", "REDDIT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"):
    val = locals().get(varname)
    if isinstance(val, str):
        locals()[varname] = val.strip()


def _make_reddit_client():
    """Return a configured PRAW Reddit instance or raise the underlying exception.

    Tries app-only auth with client_id/client_secret first. If that fails and
    REDDIT_USERNAME/REDDIT_PASSWORD are provided, will fall back to script
    authentication (username/password)."""
    if REDDIT_ID and REDDIT_SECRET:
        # App-only (client credentials)
        return praw.Reddit(client_id=REDDIT_ID, client_secret=REDDIT_SECRET, user_agent="osint_lab_script")

    # If app credentials aren't present, try script auth (requires username/password and client id/secret)
    if REDDIT_ID and REDDIT_SECRET and REDDIT_USERNAME and REDDIT_PASSWORD:
        return praw.Reddit(client_id=REDDIT_ID, client_secret=REDDIT_SECRET,
                           username=REDDIT_USERNAME, password=REDDIT_PASSWORD,
                           user_agent="osint_lab_script")

    raise RuntimeError("Missing Reddit credentials")


def fetch_reddit(subreddit="technology", limit=100):
    try:
        reddit = _make_reddit_client()
    except Exception as e:
        print("Reddit credentials missing or misconfigured; skipping Reddit fetch.", type(e).__name__, e)
        return []

    try:
        results = []
        for post in reddit.subreddit(subreddit).hot(limit=limit):
            try:
                text = (post.title or "") + " " + (post.selftext or "")
                results.append({
                    "platform": "reddit",
                    "user": str(post.author),
                    "timestamp": str(post.created_utc),
                    "text": text,
                    "url": f"https://reddit.com{post.permalink}"
                })
            except Exception:
                # skip problematic post
                continue
        return results
    except Exception as e:
        # Improve guidance for common auth error (401)
        en = type(e).__name__
        msg = str(e)
        if "401" in msg or "401" in en or "Unauthorized" in msg:
            print("Reddit fetch failed with 401 Unauthorized. Double-check that your REDDIT_ID and REDDIT_SECRET are correct, that the app type is 'script' or supports script/app-only auth, and that there are no trailing spaces in .env.")
        else:
            print(f"Reddit fetch failed: {en}: {msg}")
        return []
