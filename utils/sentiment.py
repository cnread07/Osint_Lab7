from textblob import TextBlob
from typing import Union


def add_sentiment(text: Union[str, dict]) -> float:
    """Add sentiment analysis to text or record.
    
    Args:
        text: Either a string of text or a dict record
        
    Returns:
        float: Sentiment polarity score (-1.0 to 1.0)
    """
    try:
        if isinstance(text, dict):
            text_content = text.get("text", "")
        else:
            text_content = str(text)
            
        if not text_content:
            return 0.0
            
        polarity = TextBlob(text_content).sentiment.polarity
        return polarity
    except Exception:
        return 0.0
