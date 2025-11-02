# cleaner.py
import re

def clean_text(text):
    if not text:
        return ''
    # remove urls, mentions, extra whitespace
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
