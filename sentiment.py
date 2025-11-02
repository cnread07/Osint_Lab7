# sentiment.py
from textblob import TextBlob

def add_sentiment(records):
    for r in records:
        try:
            txt = r.get('text', '') or ''
            polarity = TextBlob(txt).sentiment.polarity
            r['sentiment'] = round(float(polarity), 3)
        except Exception:
            r['sentiment'] = 0.0
    return records
