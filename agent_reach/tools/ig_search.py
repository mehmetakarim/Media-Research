import sys
import os
import json
import urllib.request
import urllib.parse
from agent_reach.config import Config

def search_instagram(query, limit=6):
    config = Config()
    cookies_str = config.get("instagram_cookies", "")
    
    # Format tag
    tag = query.replace("#", "").replace(" ", "").lower()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    if cookies_str:
        headers["Cookie"] = cookies_str
        for part in cookies_str.split(";"):
            part = part.strip()
            if part.startswith("csrftoken="):
                headers["X-CSRFToken"] = part.split("=", 1)[1]
            elif part.startswith("ds_user_id="):
                headers["X-IG-App-ID"] = "936619743392459"

    api_url = f"https://www.instagram.com/api/v1/tags/web_info/?tag_name={urllib.parse.quote(tag)}"
    items = []
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        
        sections = data.get("data", {}).get("top", {}).get("sections", []) + data.get("data", {}).get("recent", {}).get("sections", [])
        for sec in sections:
            medias = sec.get("layout_content", {}).get("medias", [])
            for m in medias:
                media_info = m.get("media", {})
                code = media_info.get("code")
                if not code:
                    continue
                user = media_info.get("user", {})
                username = user.get("username", "instagram_user")
                full_name = user.get("full_name") or username
                caption = media_info.get("caption", {}).get("text", "")
                
                # Image
                image_versions = media_info.get("image_versions2", {}).get("candidates", [])
                image_url = image_versions[0].get("url") if image_versions else ""
                
                # Direct Video URL extraction
                video_versions = media_info.get("video_versions", [])
                video_url = video_versions[0].get("url") if video_versions else ""
                is_video = bool(video_url or media_info.get("media_type") == 2)
                
                like_count = media_info.get("like_count", 0)
                comment_count = media_info.get("comment_count", 0)
                
                items.append({
                    "id": f"ig_{code}",
                    "platform": "instagram",
                    "platformLabel": "Instagram",
                    "author": full_name,
                    "handle": f"@{username}",
                    "url": f"https://www.instagram.com/p/{code}/",
                    "mediaUrl": image_url,
                    "videoUrl": video_url,
                    "date": "Instagram",
                    "verified": user.get("is_verified", False),
                    "initial": full_name[0].upper() if full_name else "I",
                    "hue": 330,
                    "text": caption or f"Instagram #{tag} gönderisi",
                    "metrics": [
                        {"label": "beğeni", "value": f"{like_count:,}" if like_count else "0"},
                        {"label": "yorum", "value": f"{comment_count:,}" if comment_count else "0"}
                    ],
                    "media": bool(image_url or video_url),
                    "mediaBadge": "video" if is_video else "görsel",
                    "isVideo": is_video
                })
                if len(items) >= limit:
                    break
            if len(items) >= limit:
                break
    except Exception as e:
        sys.stderr.write(f"Instagram doğrudan API uyarısı: {e}\n")

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3dyazici"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_instagram(q, lim)
    print(json.dumps(results, ensure_ascii=False))
