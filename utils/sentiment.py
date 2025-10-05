from textblob import TextBlob
from typing import Iterable, Dict


def add_sentiment(records: Iterable[Dict]) -> list:
	out = []
	for r in records:
		try:
			text = r.get("text") if isinstance(r, dict) else ""
			polarity = TextBlob(text).sentiment.polarity if text else 0.0
		except Exception:
			polarity = 0.0
		r["sentiment"] = polarity
		out.append(r)
	return out
