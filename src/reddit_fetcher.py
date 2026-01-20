"""
Reddit Post Fetcher
===================
Fetches top posts from specified subreddits using Reddit's RSS feeds.
This works better from cloud servers than the JSON API.
"""

import time
import requests
import re
from html import unescape


def fetch_posts(subreddit_name="AI_Agents", limit=5, time_period="week", max_retries=3):
    """
    Fetches posts from a subreddit using RSS feeds.
    
    Args:
        subreddit_name: Name of the subreddit to fetch from
        limit: Number of posts to fetch
        time_period: Time period for top posts (week, month, year, all)
        max_retries: Number of retry attempts for failed requests
    
    Returns:
        List of dictionaries with 'title', 'score', 'url', 'reddit_link', and 'text'
    """
    # RSS feed URL for top posts
    url = f"https://www.reddit.com/r/{subreddit_name}/top/.rss?t={time_period}&limit={limit}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*"
    }

    # Retry loop with exponential backoff
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"    ⏳ Rate limited. Waiting {wait_time}s before retry {attempt}/{max_retries}...")
                time.sleep(wait_time)
                continue
            
            if response.status_code == 403:
                # Try alternative: old.reddit.com
                alt_url = f"https://old.reddit.com/r/{subreddit_name}/top/.rss?t={time_period}&limit={limit}"
                response = requests.get(alt_url, headers=headers, timeout=15)
                
                if response.status_code != 200:
                    print(f"    ❌ Blocked by Reddit (403). Trying JSON fallback...")
                    return _fetch_json_fallback(subreddit_name, limit, time_period)
            
            if response.status_code != 200:
                print(f"    ❌ Failed to fetch r/{subreddit_name}. Status: {response.status_code}")
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                return []

            # Parse RSS/XML response
            clean_posts = _parse_rss(response.text, limit)
            
            if clean_posts:
                print(f"    ✅ Got {len(clean_posts)} posts from r/{subreddit_name}")
                return clean_posts
            else:
                # Fallback to JSON if RSS parsing failed
                return _fetch_json_fallback(subreddit_name, limit, time_period)

        except requests.exceptions.Timeout:
            print(f"    ⏱️ Timeout fetching r/{subreddit_name}. Attempt {attempt}/{max_retries}")
            if attempt < max_retries:
                time.sleep(2)
                continue
            return []
            
        except Exception as e:
            print(f"    💥 Error fetching r/{subreddit_name}: {e}")
            return []
    
    return []


def _parse_rss(xml_content, limit):
    """Parse RSS feed and extract posts."""
    import re
    
    posts = []
    
    # Find all entry blocks
    entries = re.findall(r'<entry>(.*?)</entry>', xml_content, re.DOTALL)
    
    for entry in entries[:limit]:
        try:
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            title = unescape(title_match.group(1)) if title_match else "Untitled"
            
            # Extract link (reddit permalink)
            link_match = re.search(r'<link href="([^"]+)"', entry)
            reddit_link = link_match.group(1) if link_match else ""
            
            # Extract content/description for text posts
            content_match = re.search(r'<content[^>]*>(.*?)</content>', entry, re.DOTALL)
            content = ""
            external_url = reddit_link  # Default to reddit link
            
            if content_match:
                content_html = unescape(content_match.group(1))
                # Try to extract external link from content
                ext_link_match = re.search(r'<a href="([^"]+)">\[link\]</a>', content_html)
                if ext_link_match:
                    potential_url = ext_link_match.group(1)
                    if not potential_url.startswith("https://www.reddit.com"):
                        external_url = potential_url
                
                # Extract text (strip HTML)
                content = re.sub(r'<[^>]+>', '', content_html)[:800]
            
            posts.append({
                "title": title,
                "score": 0,  # RSS doesn't include score
                "url": external_url,
                "reddit_link": reddit_link,
                "text": content.strip()
            })
            
        except Exception as e:
            continue
    
    return posts


def _fetch_json_fallback(subreddit_name, limit, time_period):
    """Fallback to JSON API if RSS fails."""
    url = f"https://www.reddit.com/r/{subreddit_name}/top.json?t={time_period}&limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"    ❌ JSON fallback also failed. Status: {response.status_code}")
            return []
        
        data = response.json()
        raw_posts = data.get('data', {}).get('children', [])
        
        clean_posts = []
        for post in raw_posts[:limit]:
            post_data = post.get('data', {})
            clean_posts.append({
                "title": post_data.get('title', 'Untitled'),
                "score": post_data.get('score', 0),
                "url": post_data.get('url', ''),
                "reddit_link": f"https://www.reddit.com{post_data.get('permalink', '')}",
                "text": (post_data.get('selftext', '') or '')[:800]
            })
        
        print(f"    ✅ Got {len(clean_posts)} posts via JSON fallback")
        return clean_posts
        
    except Exception as e:
        print(f"    💥 JSON fallback error: {e}")
        return []