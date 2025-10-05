# collectors/mastodon_collector.py
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def fetch_mastodon(hashtag="osint", limit=10) -> List[Dict]:
    """Fetch Mastodon posts using Mastodon.py.
    
    Requires MASTODON_ACCESS_TOKEN and MASTODON_API_BASE_URL in .env
    Register an app at your Mastodon instance to get credentials.
    
    Returns a list of dicts with keys: platform, user, timestamp, text, url.
    """
    try:
        from mastodon import Mastodon
        
        access_token = os.getenv("MASTODON_ACCESS_TOKEN")
        api_base_url = os.getenv("MASTODON_API_BASE_URL", "https://mastodon.social")
        
        if not access_token:
            print("Mastodon access token missing. Set MASTODON_ACCESS_TOKEN in .env")
            print("To get token: Create app at your Mastodon instance > Copy access token")
            return []
        
        mastodon = Mastodon(
            access_token=access_token.strip(),
            api_base_url=api_base_url.strip()
        )
        
        results = []
        
        # Try hashtag timeline first, fall back to public timeline if hashtag fails
        try:
            posts = mastodon.timeline_hashtag(hashtag, limit=limit)
            if not posts:  # If no posts found for hashtag, try public timeline
                posts = mastodon.timeline_public(limit=limit)
        except Exception as hashtag_error:
            print(f"Hashtag search failed, using public timeline: {hashtag_error}")
            posts = mastodon.timeline_public(limit=limit)
        
        for p in posts:
            # Remove HTML tags from content
            import re
            clean_text = re.sub('<[^<]+?>', '', p["content"])
            
            results.append({
                "platform": "mastodon",
                "user": p["account"]["username"],
                "timestamp": str(p["created_at"]),
                "text": clean_text,
                "url": p["url"]
            })
        
        return results
        
    except ImportError:
        print("Mastodon.py not installed. Install with: pip install Mastodon.py")
        return []
    except Exception as e:
        print(f"Mastodon collector failed: {type(e).__name__}: {e}")
        return []