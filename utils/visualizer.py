# utils/visualizer.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import os

OUTDIR = "screenshots"
os.makedirs(OUTDIR, exist_ok=True)

def plot_sentiment_by_platform(db_path="data/osint.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT platform, text FROM osint_data", conn)
    conn.close()
    from textblob import TextBlob
    df['sentiment'] = df['text'].fillna('').apply(lambda x: TextBlob(x).sentiment.polarity)
    agg = df.groupby('platform')['sentiment'].mean().sort_values()
    ax = agg.plot(kind='bar', title='Average Sentiment by Platform', figsize=(8,4))
    ax.set_ylabel('Average sentiment')
    plt.tight_layout()
    out = os.path.join(OUTDIR, "sentiment_by_platform.png")
    plt.savefig(out)
    plt.close()
    print("Saved", out)

def plot_top_words(db_path="data/osint.db", top_n=20):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT text FROM osint_data", conn)
    conn.close()
    all_text = " ".join(df['text'].dropna().values).lower()
    words = [w for w in all_text.split() if len(w) > 3]
    c = Counter(words)
    common = c.most_common(top_n)
    if not common:
        print("No words to plot")
        return
    words, counts = zip(*common)
    plt.figure(figsize=(10,5))
    plt.bar(words, counts)
    plt.xticks(rotation=45, ha='right')
    plt.title("Top words")
    plt.tight_layout()
    out = os.path.join(OUTDIR, "top_words.png")
    plt.savefig(out)
    plt.close()
    print("Saved", out)
