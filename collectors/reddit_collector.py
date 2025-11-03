# reddit_collector.py
import os
import praw
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
def analyze_sentiment(text):
    """Return sentiment category and polarity score."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # Range: -1.0 to 1.0
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"sentiment": sentiment, "polarity": round(polarity, 3)}

def fetch_reddit(keyword, limit=10, comments_per_post=5):
    results = []

    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

        print(f"[reddit_collector] Searching Reddit for '{keyword}' ...")

        for i, submission in enumerate(reddit.subreddit("all").search(keyword, sort="new", limit=limit)):
            post_data = {
                'platform': 'reddit',
                'type': 'post',
                'user': submission.author.name if submission.author else 'unknown',
                'text': submission.title,
                'timestamp': datetime.utcfromtimestamp(submission.created_utc).strftime("%Y-%m-%dT%H:%M:%S"),
                'url': f"https://reddit.com{submission.permalink}"
            }
            results.append(post_data)

            # ✅ Fetch top-level comments
            submission.comments.replace_more(limit=0)
            comment_count = 0
            for comment in submission.comments.list():
                if comment_count >= comments_per_post:
                    break
                comment_data = {
                    'platform': 'reddit',
                    'type': 'comment',
                    'user': comment.author.name if comment.author else 'unknown',
                    'text': comment.body[:500],  # trim long comments
                    'timestamp': datetime.utcfromtimestamp(comment.created_utc).strftime("%Y-%m-%dT%H:%M:%S"),
                    'url': f"https://reddit.com{comment.permalink}"
                }
                results.append(comment_data)
                comment_count += 1

            # Small delay between posts to avoid rate limit
            time.sleep(1)

        print(f"[reddit_collector] Collected {len(results)} total items ({limit} posts + comments)")

    except Exception as e:
        print(f"[reddit_collector] error: {type(e).__name__}: {e}")

    return results
