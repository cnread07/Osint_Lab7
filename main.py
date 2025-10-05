# main.py
import os
from collectors.snscrape_collector import fetch_twitter_scrape
from collectors.twitter_collector import fetch_twitter_v2
from collectors.reddit_collector import fetch_reddit

from utils.cleaner import clean_text, is_english
from utils.sentiment import add_sentiment
from utils.database import save_to_db, init_db
from utils.visualizer import plot_sentiment_by_platform, plot_top_words

def run_pipeline():
    init_db()
    data = []

    # 1) Bulk collect Twitter via snscrape (fast) - disabled by default because Twitter
    # may block unauthenticated scraping endpoints. Enable by setting USE_SNSCRAPE=true
    use_snscrape = os.getenv("USE_SNSCRAPE", "false").lower() == "true"
    if use_snscrape:
        try:
            data.extend(fetch_twitter_scrape("AI OR cybersecurity OR osint", limit=150))
        except Exception as e:
            print(f"snscrape collector failed: {e}")
    else:
        print("Skipping snscrape (USE_SNSCRAPE not set). Enable with USE_SNSCRAPE=true in .env to try scraping.")

    # 2) Add some authenticated v2 tweets if tokens exist
    try:
        data.extend(fetch_twitter_v2("AI", max_results=10))
    except Exception as e:
        print(f"twitter v2 collector failed: {e}")

    # 3) Reddit posts from multiple subreddits
    try:
        data.extend(fetch_reddit("technology", limit=50))
        data.extend(fetch_reddit("cybersecurity", limit=30))
        data.extend(fetch_reddit("privacy", limit=20))
    except Exception as e:
        print(f"reddit collector failed: {e}")

    # 4) (Instagram removed) optional collectors can be added here

    # Clean, filter, deduplicate basic
    cleaned = []
    seen_texts = set()
    for r in data:
        text = clean_text(r.get("text") or "")
        if not text:
            continue
        if not is_english(text):
            continue
        if text in seen_texts:
            continue
        seen_texts.add(text)
        cleaned.append({
            "platform": r.get("platform"),
            "user": r.get("user"),
            "timestamp": r.get("timestamp"),
            "text": text,
            "url": r.get("url")
        })

    # add sentiment
    cleaned = add_sentiment(cleaned)

    # save to DB
    save_to_db(cleaned)
    print(f"Saved {len(cleaned)} records to DB")

    # visualizations
    plot_sentiment_by_platform()
    plot_top_words()

if __name__ == "__main__":
    run_pipeline()
