import sys
import os
import json
import urllib.request
import urllib.parse
import re
import html
from agent_reach.config import Config

def search_tiktok(query, limit=6):
    config = Config()
    cookies_str = config.get("tiktok_cookies", "")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if cookies_str:
        headers["Cookie"] = cookies_str

    items = []
    
    # 1. Primary: Scrape TikTok Tag / Explore Search
    tag = query.replace("#", "").replace(" ", "").lower()
    tag_url = f"https://www.tiktok.com/tag/{urllib.parse.quote(tag)}"
    
    try:
        req = urllib.request.Request(tag_url, headers=headers)
        html_raw = urllib.request.urlopen(req, timeout=8).read().decode("utf-8")
        
        # Look for universal rehydration data
        script_m = re.search(r"<script id=\"__UNIVERSAL_DATA_FOR_REHYDRATION__\"[^>]*>(\{.+?\})</script>", html_raw)
        if script_m:
            data = json.loads(script_m.group(1))
            scope = data.get("__DEFAULT_SCOPE__", {})
            raw_items = scope.get("webapp.challenge-detail", {}).get("itemList", []) or scope.get("webapp.video-detail", {}).get("itemList", [])
            for v in raw_items:
                vid = v.get("id")
                desc = v.get("desc", f"TikTok #{tag} videosu")
                author_obj = v.get("author", {})
                author = author_obj.get("nickname") or author_obj.get("uniqueId") or "TikTok Creator"
                handle = f"@{author_obj.get('uniqueId', 'tiktok')}"
                stats = v.get("stats", {})
                likes = stats.get("diggCount", 0)
                comments = stats.get("commentCount", 0)
                
                video_obj = v.get("video", {})
                cover_url = video_obj.get("cover") or video_obj.get("dynamicCover") or ""
                play_url = video_obj.get("playAddr") or ""
                
                items.append({
                    "id": f"tt_{vid}",
                    "platform": "tiktok",
                    "platformLabel": "TikTok",
                    "author": author,
                    "handle": handle,
                    "url": f"https://www.tiktok.com/@{author_obj.get('uniqueId')}/video/{vid}",
                    "mediaUrl": cover_url,
                    "videoUrl": play_url,
                    "date": "TikTok",
                    "verified": author_obj.get("verified", False),
                    "initial": author[0].upper() if author else "T",
                    "hue": 180,
                    "text": desc,
                    "metrics": [
                        {"label": "beğeni", "value": f"{likes:,}" if likes else "0"},
                        {"label": "yorum", "value": f"{comments:,}" if comments else "0"}
                    ],
                    "media": bool(cover_url or play_url),
                    "mediaBadge": "video",
                    "isVideo": True
                })
                if len(items) >= limit:
                    break
    except Exception as e:
        sys.stderr.write(f"TikTok Tag arama uyarısı: {e}\n")

    # 2. Fallback: Search Tag URLs & Video URLs from TikTok HTML search
    if not items:
        try:
            search_url = f"https://www.tiktok.com/search?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(search_url, headers=headers)
            html_search = urllib.request.urlopen(req, timeout=8).read().decode("utf-8")
            
            video_matches = list(dict.fromkeys(re.findall(r'href=\"(/@[a-zA-Z0-9_\.]+/video/(\d+))\"', html_search)))
            for vpath, vid in video_matches[:limit]:
                user_match = re.search(r'/@([a-zA-Z0-9_\.]+)/video', vpath)
                username = user_match.group(1) if user_match else "tiktok_user"
                full_url = f"https://www.tiktok.com{vpath}"
                
                items.append({
                    "id": f"tt_{vid}",
                    "platform": "tiktok",
                    "platformLabel": "TikTok",
                    "author": username,
                    "handle": f"@{username}",
                    "url": full_url,
                    "mediaUrl": "",
                    "videoUrl": "",
                    "date": "TikTok",
                    "verified": False,
                    "initial": username[0].upper(),
                    "hue": 180,
                    "text": f"TikTok platformunda {query} üzerine yayınlanan popüler kısa video (#{vid}).",
                    "metrics": [
                        {"label": "kaynak", "value": "yerel motor"},
                        {"label": "maliyet", "value": "0 token"}
                    ],
                    "media": False,
                    "mediaBadge": "video",
                    "isVideo": True
                })
        except Exception as e:
            sys.stderr.write(f"TikTok Arama uyarısı: {e}\n")

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d printer"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_tiktok(q, lim)
    print(json.dumps(results, ensure_ascii=False))
