import sys
import os
import json
import urllib.request
import urllib.parse
import re
from agent_reach.config import Config
from agent_reach.tools.translate_util import translate_to_turkish_fast

def extract_pin_metadata(pin_id, cookies_str=""):
    """Fetch accurate pin details (title, description, pinner, direct mp4 video URL, high-res image) directly from the pin page."""
    url = f"https://www.pinterest.com/pin/{pin_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if cookies_str:
        headers["Cookie"] = cookies_str

    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=6).read().decode("utf-8")
        
        # Direct MP4 video extraction from pin HTML
        mp4_matches = re.findall(r'https://v1\.pinimg\.com/videos/iht/expMp4/[a-f0-9/]+_720w\.mp4', html)
        if not mp4_matches:
            mp4_matches = re.findall(r'https://v1\.pinimg\.com/videos/[^\"]+?\.mp4', html)
        direct_video_url = mp4_matches[0] if mp4_matches else ""
        
        scripts = re.findall(r"<script[^>]*type=\"application/json\"[^>]*>(\{.+?\})</script>", html)
        for s in scripts:
            if "PinResource" in s:
                data = json.loads(s)
                pin_data = data.get("resource_response", {}).get("data", {})
                if pin_data and isinstance(pin_data, dict):
                    title = (pin_data.get("grid_title") or pin_data.get("title") or "").strip()
                    desc = (pin_data.get("description") or "").strip()
                    pinner = pin_data.get("pinner", {})
                    author = pinner.get("full_name") or pinner.get("username") or "Pinterest Kullanıcısı"
                    handle = f"@{pinner.get('username') or 'pinterest'}"
                    
                    is_video = bool(
                        direct_video_url or
                        pin_data.get("is_video") or 
                        pin_data.get("videos") or 
                        pin_data.get("story_pin_data") or 
                        pin_data.get("video_cover_images")
                    )
                    
                    # High res image
                    images = pin_data.get("images", {})
                    img_url = (
                        images.get("orig", {}).get("url") or 
                        images.get("736x", {}).get("url") or 
                        images.get("474x", {}).get("url") or 
                        images.get("236x", {}).get("url") or ""
                    )
                    
                    repins = pin_data.get("repin_count", 0)
                    comments = pin_data.get("comment_count", 0)
                    
                    raw_text = f"{title}\n\n{desc}".strip() if (title and desc and title != desc) else (title or desc or f"Pinterest Pin #{pin_id}")
                    full_text = translate_to_turkish_fast(raw_text)
                    
                    return {
                        "id": f"pin_{pin_id}",
                        "platform": "pinterest",
                        "platformLabel": "Pinterest",
                        "author": author,
                        "handle": handle,
                        "url": url,
                        "mediaUrl": img_url,
                        "videoUrl": direct_video_url,
                        "date": "Pinterest",
                        "verified": pinner.get("is_verified_merchant", False),
                        "initial": author[0].upper() if author else "P",
                        "hue": 0,
                        "text": full_text,
                        "metrics": [
                            {"label": "kaydetme", "value": f"{repins:,}" if repins else "0"},
                            {"label": "yorum", "value": f"{comments:,}" if comments else "0"}
                        ],
                        "media": bool(img_url or direct_video_url),
                        "mediaBadge": "video" if is_video else "pin görseli",
                        "isVideo": is_video
                    }
    except Exception:
        pass
        
    return None


def search_pinterest(query, limit=6):
    config = Config()
    cookies_str = config.get("pinterest_cookies", "")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if cookies_str:
        headers["Cookie"] = cookies_str

    url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(query)}"
    
    items = []
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        
        # Extract authentic Pin IDs from search page
        pin_ids = list(dict.fromkeys(re.findall(r'/pin/(\d+)/', html)))
        
        for pid in pin_ids[:limit]:
            meta = extract_pin_metadata(pid, cookies_str)
            if meta:
                items.append(meta)
    except Exception as e:
        sys.stderr.write(f"Pinterest arama hatası: {e}\n")

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d printer"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_pinterest(q, lim)
    print(json.dumps(results, ensure_ascii=False))
