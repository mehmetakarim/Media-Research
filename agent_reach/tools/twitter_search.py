import sys
import os
import json
import subprocess
import urllib.request
import re
import concurrent.futures
from agent_reach.config import Config
from agent_reach.tools.translate_util import translate_to_turkish_fast

def resolve_single_tweet_media(tweet_id):
    """Fetch accurate images/videos for a tweet via lightweight open resolver."""
    if not tweet_id:
        return tweet_id, "", ""
    try:
        api_url = f"https://api.fxtwitter.com/status/{tweet_id}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) agent-reach"})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode("utf-8"))
        tweet = data.get("tweet", {})
        media = tweet.get("media", {})
        
        photos = media.get("photos", [])
        videos = media.get("videos", [])
        
        img_url = photos[0].get("url") if photos else ""
        video_url = videos[0].get("url") if videos else ""
        if videos and not img_url:
            img_url = videos[0].get("thumbnail_url", "")
            
        return tweet_id, img_url, video_url
    except Exception:
        # Fallback to vxtwitter resolver
        try:
            api_url = f"https://api.vxtwitter.com/Twitter/status/{tweet_id}"
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) agent-reach"})
            resp = urllib.request.urlopen(req, timeout=5)
            data = json.loads(resp.read().decode("utf-8"))
            media_urls = data.get("mediaURLs", [])
            vid_url = data.get("video_url", "")
            img_url = media_urls[0] if media_urls else ""
            return tweet_id, img_url, vid_url
        except Exception:
            return tweet_id, "", ""

def search_twitter(query, limit=6):
    items = []
    
    # Run bird search with saved credentials
    cmd = f'source ~/.config/bird/credentials.env 2>/dev/null; export AUTH_TOKEN CT0; bird --auth-token "$AUTH_TOKEN" --ct0 "$CT0" search "{query}" -n {limit}'
    try:
        res = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=4)
        raw_output = res.stdout
        
        chunks = raw_output.split('──────────────────────────────────────────────────')
        parsed_entries = []
        tweet_ids_to_resolve = []
        
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if not chunk:
                continue
                
            lines = chunk.split('\n')
            author = 'Kullanıcı'
            handle = '@kullanici'
            text_lines = []
            date = 'Twitter'
            url = ''
            media_url = ''
            tweet_id = ''

            header_match = re.search(r'@([a-zA-Z0-9_]+)\s*\(([^)]+)\):?', lines[0])
            if header_match:
                handle = '@' + header_match.group(1)
                author = header_match.group(2)
                for j in range(1, len(lines)):
                    line = lines[j].strip()
                    if line.startswith('🔗'):
                        url = line.replace('🔗', '').strip()
                        id_m = re.search(r'/status/(\d+)', url)
                        if id_m:
                            tweet_id = id_m.group(1)
                    elif line.startswith('🖼️'):
                        media_url = line.replace('🖼️', '').strip()
                    elif line.startswith('📅'):
                        date = line.replace('📅', '').strip().replace('+0000', '').strip()
                    elif line:
                        text_lines.append(line)
            else:
                text_lines.append(chunk)

            raw_text = ' '.join(text_lines).strip() or chunk
            full_text = translate_to_turkish_fast(raw_text)
            
            entry = {
                "id": f"x_{tweet_id or i}",
                "tweet_id": tweet_id,
                "platform": "x",
                "platformLabel": "Twitter/X",
                "author": author,
                "handle": handle,
                "url": url,
                "mediaUrl": media_url,
                "videoUrl": "",
                "date": date,
                "verified": True if ("official" in handle.lower() or "tubitak" in handle.lower() or "dhaspor" in handle.lower()) else False,
                "initial": author[0].upper() if author else "X",
                "hue": 210,
                "text": full_text,
                "metrics": [
                    {"label": "kaynak", "value": "yerel bird"},
                    {"label": "maliyet", "value": "0 token"}
                ],
                "media": bool(media_url),
                "mediaBadge": "görsel" if media_url else None,
                "isVideo": False
            }
            parsed_entries.append(entry)
            if tweet_id:
                tweet_ids_to_resolve.append(tweet_id)
            if len(parsed_entries) >= limit:
                break

        # Parallel resolution of all tweet media in under 1 second
        media_map = {}
        if tweet_ids_to_resolve:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                res_list = executor.map(resolve_single_tweet_media, tweet_ids_to_resolve)
                for tid, img, vid in res_list:
                    media_map[tid] = (img, vid)

        # Apply resolved media to items
        for entry in parsed_entries:
            tid = entry.get("tweet_id")
            if tid in media_map:
                img, vid = media_map[tid]
                if img:
                    entry["mediaUrl"] = img
                    entry["media"] = True
                if vid:
                    entry["videoUrl"] = vid
                    entry["isVideo"] = True
                    entry["media"] = True
                    entry["mediaBadge"] = "video"
                    if not entry["mediaUrl"]:
                        entry["mediaUrl"] = vid
                elif img:
                    entry["mediaBadge"] = "görsel"
            
            entry.pop("tweet_id", None)
            items.append(entry)

    except Exception as e:
        sys.stderr.write(f"Twitter arama hatası: {e}\n")

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d yazıcı"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_twitter(q, lim)
    print(json.dumps(results, ensure_ascii=False))
    sys.stdout.flush()
    os._exit(0)
