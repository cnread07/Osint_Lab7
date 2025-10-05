def clean_text(text): 
 text = re.sub(r"http\S+", "", text) # remove URLs 
 text = re.sub(r"[^A-Za-z0-9\s]", "", text) # remove symbols  return text.strip()
import re
from langdetect import detect, DetectorFactory

# make language detection deterministic
DetectorFactory.seed = 0

def clean_text(text: str) -> str:
	"""Clean raw text: remove URLs, punctuation, control chars and extra whitespace.

	Returns empty string for None input.
	"""
	if not text:
		return ""

	# Remove URLs
	text = re.sub(r"http\S+", "", text)

	# Replace control chars with space
	text = re.sub(r"[\r\n\t]+", " ", text)

	# Remove most punctuation (keep letters, numbers, underscores and basic quotes)
	text = re.sub(r"[^\w\s\'\"]", "", text)

	# Collapse whitespace
	text = re.sub(r"\s+", " ", text).strip()

	return text


def is_english(text: str) -> bool:
	"""Return True if detected language is English. Safe on short/missing text."""
	if not text:
		return False
	try:
		return detect(text) == "en"
	except Exception:
		return False


def filter_english(records: list) -> list:
	"""Keep only records whose 'text' field is detected as English.

	Expects records to be dictionaries with a 'text' key.
	"""
	out = []
	for r in records:
		text = r.get("text") if isinstance(r, dict) else None
		if is_english(text):
			out.append(r)
	return out
