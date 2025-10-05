# collectors/linkedin_collector.py
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def fetch_linkedin(keyword="cybersecurity", limit=10) -> List[Dict]:
    """Fetch LinkedIn people/posts using linkedin-api.
    
    Requires LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env
    Note: Use a test account as this method may violate LinkedIn ToS.
    
    Returns a list of dicts with keys: platform, user, timestamp, text, url.
    """
    try:
        from linkedin_api import Linkedin
        
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        
        if not (email and password):
            print("LinkedIn credentials missing. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
            print("Note: LinkedIn may block automated access. Use a test account.")
            return []
        
        api = Linkedin(email.strip(), password.strip())
        results = []
        
        # Search for people related to keyword
        people = api.search_people(keywords=keyword, limit=limit)
        for p in people:
            results.append({
                "platform": "linkedin",
                "user": p.get("public_id", ""),
                "timestamp": "N/A",
                "text": p.get("headline", ""),
                "url": f"https://linkedin.com/in/{p.get('public_id', '')}"
            })
        
        return results
        
    except ImportError:
        print("linkedin-api not installed. Install with: pip install linkedin-api")
        return []
    except Exception as e:
        print(f"LinkedIn collector failed: {type(e).__name__}: {e}")
        return []