# reddit_collector.py

import os
import praw
from datetime import datetime

def fetch_reddit(keyword, limit=10):
    results = []
    try:
        # Load credentials from environment variables
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'osint-lab7-script')
        if not client_id or not client_secret:
            raise Exception('Missing Reddit API credentials in .env')

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        for submission in reddit.subreddit('all').search(keyword, sort='new', limit=limit):
            text = (submission.title or '')
            if getattr(submission, 'selftext', None):
                text += "\n\n" + submission.selftext
            timestamp = ''
            try:
                timestamp = datetime.utcfromtimestamp(submission.created_utc).strftime("%Y-%m-%dT%H:%M:%S")
            except:
                timestamp = ''
            results.append({
                'platform': 'reddit',
                'user': str(submission.author) if submission.author else '[deleted]',
                'text': text,
                'timestamp': timestamp,
                'url': submission.url
            })
    except Exception as e:
        print("reddit_collector error:", e)
    return results
