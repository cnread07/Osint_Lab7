# main.py - Multi-Platform OSINT Pipeline
import os
from collectors.snscrape_collector import fetch_twitter_scrape
from collectors.twitter_collector import fetch_twitter_v2
from collectors.reddit_collector import fetch_reddit
from collectors.linkedin_collector import fetch_linkedin
from collectors.mastodon_collector import fetch_mastodon
from collectors.github_collector import fetch_github
from collectors.stackoverflow_collector import fetch_stackoverflow
from collectors.hackernews_collector import fetch_hackernews

from utils.cleaner import clean_text, is_english
from utils.sentiment import add_sentiment
from utils.database import save_to_db, init_db
from utils.visualizer import plot_sentiment_by_platform, plot_top_words

def run_pipeline():
    """Multi-Platform OSINT pipeline orchestrator."""
    print("🚀 Starting Multi-Platform OSINT Pipeline...")
    
    init_db()
    data = []

    # 1) snscrape (Twitter scraping) - disabled by default
    use_snscrape = os.getenv("USE_SNSCRAPE", "false").lower() == "true"
    if use_snscrape:
        try:
            print("🐦 Collecting from Twitter (snscrape)...")
            data.extend(fetch_twitter_scrape("AI OR cybersecurity OR osint", limit=10))
        except Exception as e:
            print(f"snscrape collector failed: {e}")

    # 2) Twitter API v2 (official API)
    try:
        print("🐦 Collecting from Twitter API v2...")
        data.extend(fetch_twitter_v2("AI", max_results=10))
    except Exception as e:
        print(f"twitter v2 collector failed: {e}")

    # 3) Reddit
    try:
        print("🔴 Collecting from Reddit...")
        data.extend(fetch_reddit("cybersecurity", limit=10))
    except Exception as e:
        print(f"reddit collector failed: {e}")

    # 4) LinkedIn (requires authentication)
    try:
        print("💼 Collecting from LinkedIn...")
        data.extend(fetch_linkedin("cybersecurity", 5))
    except Exception as e:
        print(f"linkedin collector failed: {e}")

    # 5) Mastodon (requires token)
    try:
        print("🦣 Collecting from Mastodon...")
        data.extend(fetch_mastodon("cybersecurity", 10))
    except Exception as e:
        print(f"mastodon collector failed: {e}")

    # 6) GitHub (public repos)
    try:
        print("🐙 Collecting from GitHub...")
        data.extend(fetch_github("osint", 5))
    except Exception as e:
        print(f"github collector failed: {e}")

    # 7) Stack Overflow (free API)
    try:
        print("📚 Collecting from Stack Overflow...")
        data.extend(fetch_stackoverflow("osint", 5))
    except Exception as e:
        print(f"stackoverflow collector failed: {e}")

    # 8) HackerNews (free API)
    try:
        print("🗞 Collecting from HackerNews...")
        data.extend(fetch_hackernews("osint", 5))
    except Exception as e:
        print(f"hackernews collector failed: {e}")

    print(f"📊 Raw data collected: {len(data)} records")

    # Clean, filter, deduplicate
    print("🧹 Cleaning and filtering data...")
    cleaned = []
    seen_texts = set()
    for r in data:
        text = clean_text(r.get("text") or "")
        if not text or len(text) < 10:
            continue
        if not is_english(text):
            continue
        if text in seen_texts:
            continue
        seen_texts.add(text)
        
        cleaned_record = {
            "platform": r.get("platform"),
            "user": r.get("user", "unknown"),
            "timestamp": r.get("timestamp", ""),
            "text": text,
            "url": r.get("url", "")
        }
        cleaned.append(cleaned_record)

    print(f"✅ Cleaned records: {len(cleaned)}")

    # Add sentiment analysis
    print("😊 Adding sentiment analysis...")
    for record in cleaned:
        record["sentiment"] = add_sentiment(record["text"])

    # Save to database
    print("💾 Saving to database...")
    saved_count = save_to_db(cleaned)

    print(f"💾 Saved {saved_count} records to database")

    # Generate visualizations
    print("📈 Generating visualizations...")
    try:
        plot_sentiment_by_platform()
        plot_top_words()
        print("📊 Charts saved to screenshots/ directory")
    except Exception as e:
        print(f"Visualization failed: {e}")

    print("✅ Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()
