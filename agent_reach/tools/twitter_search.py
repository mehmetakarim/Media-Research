import sys
import os
import json
import subprocess
import urllib.request
import urllib.parse
import re
import html
import concurrent.futures

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from agent_reach.tools.translate_util import translate_to_turkish_fast

def resolve_single_tweet_media(tweet_id):
    """Fetch accurate images/videos for a tweet via lightweight open resolver."""
    if not tweet_id:
        return tweet_id, "", ""
    try:
        api_url = f"https://api.fxtwitter.com/status/{tweet_id}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        resp = urllib.request.urlopen(req, timeout=4)
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
        try:
            api_url = f"https://api.vxtwitter.com/Twitter/status/{tweet_id}"
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            resp = urllib.request.urlopen(req, timeout=4)
            data = json.loads(resp.read().decode("utf-8"))
            media_urls = data.get("mediaURLs", [])
            vid_url = data.get("video_url", "")
            img_url = media_urls[0] if media_urls else ""
            return tweet_id, img_url, vid_url
        except Exception:
            return tweet_id, "", ""

def search_twitter_open(query, limit=6):
    """Zero-auth open web fallback for Twitter/X search (Windows & macOS)."""
    items = []
    target = f"site:x.com OR site:twitter.com {query}"
    rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(target)}&hl=tr&gl=TR&ceid=TR:tr"
    try:
        req = urllib.request.Request(rss_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=6)
        xml_data = resp.read().decode("utf-8")
        raw_items = re.findall(r"<item>(.+?)</item>", xml_data, re.DOTALL)
        
        for i, it in enumerate(raw_items):
            t_match = re.search(r"<title>(.+?)</title>", it)
            l_match = re.search(r"<link>(.+?)</link>", it)
            d_match = re.search(r"<pubDate>(.+?)</pubDate>", it)
            
            raw_title = html.unescape(t_match.group(1)).strip() if t_match else f"{query} paylaşımı"
            link = l_match.group(1).strip() if l_match else "https://x.com"
            pub_date = d_match.group(1)[:16].strip() if d_match else "Canlı Akış"
            
            clean_title = raw_title
            author = "X Kullanıcısı"
            handle = "@twitter"
            if " - " in raw_title:
                parts = raw_title.rsplit(" - ", 1)
                clean_title = parts[0].strip()
                author = parts[1].strip()
                handle = "@" + author.lower().replace(" ", "").replace("onx:", "").replace("ontwitter:", "").strip()

            tweet_id = ""
            id_m = re.search(r'/status/(\d+)', link)
            if id_m:
                tweet_id = id_m.group(1)

            items.append({
                "id": f"x_{tweet_id or abs(hash(clean_title))}_{i}",
                "tweet_id": tweet_id,
                "platform": "x",
                "platformLabel": "Twitter/X",
                "author": author,
                "handle": handle,
                "url": link,
                "mediaUrl": "",
                "videoUrl": "",
                "date": pub_date,
                "verified": True if ("resmi" in clean_title.lower() or "haber" in clean_title.lower() or "fenerbahce" in author.lower()) else False,
                "initial": author[0].upper() if author else "X",
                "hue": 210,
                "text": clean_title,
                "metrics": [
                    {"label": "kaynak", "value": "Açık Ağ"},
                    {"label": "maliyet", "value": "0 token"}
                ],
                "media": False,
                "mediaBadge": None,
                "isVideo": False
            })
            if len(items) >= limit:
                break
    except Exception as e:
        sys.stderr.write(f"Açık Twitter arama uyarısı: {e}\n")
        
    return items

def search_twitter(query, limit=6):
    items = []
    
    # 1. Read bird credentials if they exist
    home = os.path.expanduser("~")
    creds_path = os.path.join(home, ".config", "bird", "credentials.env")
    auth_token = os.environ.get("AUTH_TOKEN", "")
    ct0 = os.environ.get("CT0", "")
    
    if os.path.exists(creds_path):
        try:
            with open(creds_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        k = k.replace("export ", "").strip()
                        v = v.strip().strip('"').strip("'")
                        if k == "AUTH_TOKEN" and not auth_token:
                            auth_token = v
                        elif k == "CT0" and not ct0:
                            ct0 = v
        except Exception:
            pass

    # 2. Try bird search directly (without bash -c)
    if auth_token and ct0:
        try:
            bird_args = ["bird", "--auth-token", auth_token, "--ct0", ct0, "search", query, "-n", str(limit)]
            creationflags = 0x08000000 if sys.platform == "win32" else 0
            res = subprocess.run(bird_args, capture_output=True, text=True, timeout=12, creationflags=creationflags)
            raw_output = res.stdout or ""
            
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

            if parsed_entries:
                # Parallel resolution of all tweet media in under 1 second
                media_map = {}
                if tweet_ids_to_resolve:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                        res_list = executor.map(resolve_single_tweet_media, tweet_ids_to_resolve)
                        for tid, img, vid in res_list:
                            media_map[tid] = (img, vid)

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
            sys.stderr.write(f"Bird arama uyarısı: {e}\n")

    # 3. If bird returned nothing or credentials missing, use open fallback
    if not items:
        items = search_twitter_open(query, limit)

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d yazıcı"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_twitter(q, lim)
    print(json.dumps(results, ensure_ascii=False))
