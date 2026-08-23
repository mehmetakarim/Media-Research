import sys
import os
import json
import urllib.request
import urllib.parse
import re
import html
from agent_reach.config import Config

def extract_linkedin_activity_metadata(activity_id, cookies_str=""):
    """Fetch accurate post title, image, and author from LinkedIn embed update page."""
    url = f"https://www.linkedin.com/embed/feed/update/urn:li:activity:{activity_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    if cookies_str:
        headers["Cookie"] = cookies_str

    try:
        req = urllib.request.Request(url, headers=headers)
        html_raw = urllib.request.urlopen(req, timeout=5).read().decode("utf-8")
        
        # Title & Author
        title_m = re.search(r"<title>(.+?)</title>", html_raw)
        title = html.unescape(title_m.group(1)).strip() if title_m else f"LinkedIn Gönderisi #{activity_id}"
        
        # Discard invalid/empty embeds
        if not title or "LinkedIn" == title:
            return None

        # Author extraction from title or content
        author = "LinkedIn Üyesi"
        if "|" in title:
            parts = title.split("|")
            author = parts[-1].strip()
            title = parts[0].strip()
        elif "–" in title:
            parts = title.split("–")
            author = parts[-1].strip()
            title = parts[0].strip()
            
        # Image extraction
        img_m = re.search(r'https://media\.licdn\.com/dms/image/[^\"]+', html_raw)
        img_url = html.unescape(img_m.group(0)) if img_m else ""
        
        return {
            "id": f"li_{activity_id}",
            "platform": "linkedin",
            "platformLabel": "LinkedIn",
            "author": author,
            "handle": "@linkedin",
            "url": f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}/",
            "mediaUrl": img_url,
            "videoUrl": "",
            "date": "LinkedIn",
            "verified": True,
            "initial": author[0].upper() if author else "L",
            "hue": 210,
            "text": f"**{title}**\n\nLinkedIn iş ve teknoloji ağında paylaşılan güncel sektörel analiz ve içerik.",
            "metrics": [
                {"label": "kaynak", "value": "yerel çerez"},
                {"label": "maliyet", "value": "0 token"}
            ],
            "media": bool(img_url),
            "mediaBadge": "görsel" if img_url else None,
            "isVideo": False
        }
    except Exception:
        return None

def search_linkedin(query, limit=10):
    config = Config()
    cookies_str = config.get("linkedin_cookies", "")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if cookies_str:
        headers["Cookie"] = cookies_str

    # Query multiple facets (Date Posted, Relevance, General Content) to fetch 10+ posts
    search_urls = [
        f"https://www.linkedin.com/search/results/content/?keywords={urllib.parse.quote(query)}&origin=GLOBAL_SEARCH_HEADER",
        f"https://www.linkedin.com/search/results/content/?keywords={urllib.parse.quote(query)}&sortBy=%22date_posted%22",
        f"https://www.linkedin.com/search/results/content/?keywords={urllib.parse.quote(query)}&sortBy=%22relevance%22",
        f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(query)}"
    ]
    
    activity_ids = []
    seen = set()
    
    for url in search_urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            html_raw = urllib.request.urlopen(req, timeout=8).read().decode("utf-8")
            acts = re.findall(r"urn:li:activity:(\d+)", html_raw)
            for a in acts:
                if len(a) >= 15 and a not in seen:
                    seen.add(a)
                    activity_ids.append(a)
            if len(activity_ids) >= limit:
                break
        except Exception:
            pass

    items = []
    for aid in activity_ids[:limit]:
        meta = extract_linkedin_activity_metadata(aid, cookies_str)
        if meta:
            items.append(meta)

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d printer"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    results = search_linkedin(q, lim)
    print(json.dumps(results, ensure_ascii=False))
