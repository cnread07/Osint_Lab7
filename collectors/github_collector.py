# collectors/github_collector.py
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def fetch_github(query="leak", limit=10) -> List[Dict]:
    """Fetch GitHub repositories using PyGithub.
    
    Requires GITHUB_TOKEN in .env (optional but recommended for higher rate limits)
    Create a personal access token at https://github.com/settings/tokens
    
    Returns a list of dicts with keys: platform, user, timestamp, text, url.
    """
    try:
        from github import Github
        
        token = os.getenv("GITHUB_TOKEN")
        
        if token:
            g = Github(token.strip())
        else:
            g = Github()  # Unauthenticated (lower rate limits)
            print("GitHub token not provided. Rate limits may be lower.")
        
        repos = g.search_repositories(query=query)
        results = []
        
        for i, repo in enumerate(repos):
            if i >= limit:
                break
            
            results.append({
                "platform": "github",
                "user": repo.owner.login,
                "timestamp": str(repo.created_at),
                "text": repo.description or "",
                "url": repo.html_url
            })
        
        return results
        
    except ImportError:
        print("PyGithub not installed. Install with: pip install PyGithub")
        return []
    except Exception as e:
        print(f"GitHub collector failed: {type(e).__name__}: {e}")
        return []