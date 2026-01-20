"""
Reddit Post Fetcher
===================
Fetches top posts from specified subreddits using Reddit's public JSON API.
Includes retry logic and proper error handling.
"""

import time
import requests


def fetch_posts(subreddit_name="AI_Agents", limit=5, time_period="week", max_retries=3):
    """
    Fetches posts from a subreddit and returns a list of clean dictionaries.
    
    Args:
        subreddit_name: Name of the subreddit to fetch from
        limit: Number of posts to fetch
        time_period: Time period for top posts (hour, day, week, month, year, all)
        max_retries: Number of retry attempts for failed requests
    
    Returns:
        List of dictionaries with 'title', 'score', 'url', 'reddit_link', and 'text'
    """
    url = f"https://www.reddit.com/r/{subreddit_name}/top.json?t={time_period}&limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Retry loop with exponential backoff
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                print(f"    ⏳ Rate limited. Waiting {wait_time}s before retry {attempt}/{max_retries}...")
                time.sleep(wait_time)
                continue
            
            # Handle other non-success codes
            if response.status_code != 200:
                print(f"    ❌ Failed to fetch r/{subreddit_name}. Status: {response.status_code}")
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                return []

            # Parse JSON response
            data = response.json()
            raw_posts = data.get('data', {}).get('children', [])
            
            # Clean and structure the data
            clean_posts = []
            for post in raw_posts:
                post_data = post.get('data', {})
                
                clean_item = {
                    "title": post_data.get('title', 'Untitled'),
                    "score": post_data.get('score', 0),
                    "url": post_data.get('url', ''),
                    "reddit_link": f"https://www.reddit.com{post_data.get('permalink', '')}",
                    "text": (post_data.get('selftext', '') or '')[:800]  # Truncate long text
                }
                clean_posts.append(clean_item)
            
            print(f"    ✅ Got {len(clean_posts)} posts from r/{subreddit_name}")
            return clean_posts

        except requests.exceptions.Timeout:
            print(f"    ⏱️ Timeout fetching r/{subreddit_name}. Attempt {attempt}/{max_retries}")
            if attempt < max_retries:
                time.sleep(2)
                continue
            return []
            
        except requests.exceptions.ConnectionError:
            print(f"    🔌 Connection error for r/{subreddit_name}. Attempt {attempt}/{max_retries}")
            if attempt < max_retries:
                time.sleep(2)
                continue
            return []
            
        except Exception as e:
            print(f"    💥 Unexpected error fetching r/{subreddit_name}: {e}")
            return []
    
    return []