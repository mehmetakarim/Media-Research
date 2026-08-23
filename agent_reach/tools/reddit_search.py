import sys
import os
import json
import urllib.request
import urllib.parse
import re
import html
from agent_reach.config import Config
from agent_reach.tools.translate_util import translate_to_turkish_fast

def search_reddit(query, limit=6):
    config = Config()
    cookies_str = config.get("reddit_cookies", "")
    proxy = config.get("reddit_proxy", "")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    if cookies_str:
        headers["Cookie"] = cookies_str

    items = []
    
    # 1. Primary Method: Official Reddit JSON API
    json_url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(query)}&limit={limit * 2}&sort=relevance"
    try:
        req = urllib.request.Request(json_url, headers=headers)
        if proxy:
            req.set_proxy(proxy, "https")
            req.set_proxy(proxy, "http")
            
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read().decode("utf-8"))
        children = data.get("data", {}).get("children", [])
        
        for c in children:
            p = c.get("data", {})
            title = p.get("title", "").strip()
            subreddit = p.get("subreddit_name_prefixed", "r/reddit")
            author = f"u/{p.get('author', 'reddit_user')}"
            permalink = f"https://www.reddit.com{p.get('permalink', '')}"
            ups = p.get("ups", 0)
            num_comments = p.get("num_comments", 0)
            selftext = p.get("selftext", "").strip()
            
            # STRICT FILTER: Discard general subreddit hubs, only accept discussion posts
            if "/comments/" not in permalink:
                continue
            
            # High-res image extraction
            img_url = ""
            preview_images = p.get("preview", {}).get("images", [])
            if preview_images:
                img_url = preview_images[0].get("source", {}).get("url", "").replace("&amp;", "&")
            elif p.get("url_overridden_by_dest", "").endswith((".jpg", ".png", ".webp", ".jpeg")):
                img_url = p.get("url_overridden_by_dest")
            elif p.get("thumbnail", "").startswith("http"):
                img_url = p.get("thumbnail")
                
            # Direct video extraction
            is_video = bool(p.get("is_video") or p.get("media", {}).get("reddit_video"))
            video_url = ""
            if is_video:
                video_url = p.get("media", {}).get("reddit_video", {}).get("fallback_url", "")
                
            raw_text = f"**{title}**\n\n{selftext}".strip() if selftext else title
            full_text = translate_to_turkish_fast(raw_text)
            
            items.append({
                "id": f"rd_{p.get('id', abs(hash(permalink)))}",
                "platform": "reddit",
                "platformLabel": f"Reddit ({subreddit})",
                "author": author,
                "handle": subreddit,
                "url": permalink,
                "mediaUrl": img_url,
                "videoUrl": video_url,
                "date": "Reddit",
                "verified": False,
                "initial": subreddit.replace("r/", "")[0].upper() if len(subreddit) > 2 else "R",
                "hue": 16,
                "text": full_text,
                "metrics": [
                    {"label": "upvote", "value": f"{ups:,}" if ups else "0"},
                    {"label": "yorum", "value": f"{num_comments:,}" if num_comments else "0"}
                ],
                "media": bool(img_url or video_url),
                "mediaBadge": "video" if is_video else "görsel",
                "isVideo": is_video
            })
            if len(items) >= limit:
                break
    except Exception as e:
        sys.stderr.write(f"Reddit JSON araması uyarısı: {e}\n")

    # 2. Secondary Method: Reddit RSS Search (Filtered strictly for /comments/)
    if not items:
        try:
            rss_url = f"https://www.reddit.com/r/all/search.rss?q={urllib.parse.quote(query)}&restrict_sr=0&sort=relevance"
            req = urllib.request.Request(rss_url, headers=headers)
            if proxy:
                req.set_proxy(proxy, "https")
                req.set_proxy(proxy, "http")
                
            xml_data = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
            entries = re.findall(r"<entry>(.+?)</entry>", xml_data, re.DOTALL)
            
            for e in entries:
                link_m = re.search(r"<link href=\"(.+?)\"", e)
                if not link_m:
                    continue
                link = link_m.group(1)
                
                # CRITICAL: Discard general subreddits (e.g. /r/KGBTR/), strictly accept actual posts (/comments/)
                if "/comments/" not in link:
                    continue
                    
                title_m = re.search(r"<title>(.+?)</title>", e)
                author_m = re.search(r"<author><name>(.+?)</name>", e)
                content_m = re.search(r"<content type=\"html\">(.+?)</content>", e, re.DOTALL)
                
                title = html.unescape(title_m.group(1)) if title_m else "Reddit Gönderisi"
                author = author_m.group(1) if author_m else "/u/reddit_user"
                
                sub_match = re.search(r"/r/([^/]+)/comments/", link)
                subreddit_label = f"r/{sub_match.group(1)}" if sub_match else "Reddit"
                
                img_url = ""
                clean_text = title
                if content_m:
                    raw_c = html.unescape(content_m.group(1))
                    img_m = re.search(r"href=&quot;(https://[^\&]+?\.(?:jpg|png|jpeg|webp))&quot;", raw_c)
                    if not img_m:
                        img_m = re.search(r"src=&quot;(https://[^\&]+?(?:\.jpg|\.png|\.jpeg|\.webp)[^\&]*)&quot;", raw_c)
                    if not img_m:
                        img_m = re.search(r"src=\"(https://[^\"]+?(?:\.jpg|\.png|\.jpeg|\.webp)[^\"]*)\"", raw_c)
                    if img_m:
                        img_url = html.unescape(img_m.group(1))
                        
                    raw_clean = re.sub(r"<[^>]+>", " ", raw_c)
                    raw_clean = re.sub(r"\s+", " ", raw_clean).strip()
                    raw_clean = re.sub(r"submitted by\s+.*?to\s+r/.*", "", raw_clean, flags=re.IGNORECASE).strip()
                    if raw_clean and len(raw_clean) > len(title):
                        clean_text = f"**{title}**\n\n{raw_clean[:400]}..."
                    else:
                        clean_text = title

                items.append({
                    "id": f"rd_{abs(hash(link))}",
                    "platform": "reddit",
                    "platformLabel": f"Reddit ({subreddit_label})",
                    "author": author,
                    "handle": subreddit_label,
                    "url": link,
                    "mediaUrl": img_url,
                    "videoUrl": "",
                    "date": "Reddit",
                    "verified": False,
                    "initial": subreddit_label.replace("r/", "")[0].upper() if len(subreddit_label) > 2 else "R",
                    "hue": 16,
                    "text": clean_text,
                    "metrics": [
                        {"label": "topluluk", "value": subreddit_label},
                        {"label": "maliyet", "value": "0 token"}
                    ],
                    "media": bool(img_url),
                    "mediaBadge": "görsel" if img_url else None,
                    "isVideo": False
                })
                if len(items) >= limit:
                    break
        except Exception as e:
            sys.stderr.write(f"Reddit RSS araması uyarısı: {e}\n")

    # 3. Third Method: DuckDuckGo Indexed Reddit Discovery Fallback
    if not items:
        try:
            ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote('site:reddit.com/r/ ' + query)}"
            req = urllib.request.Request(ddg_url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=8)
            html_raw = resp.read().decode("utf-8")
            
            uddg_links = re.findall(r'uddg=([^&\"]+)', html_raw)
            seen_links = set()
            
            for encoded_l in uddg_links:
                dec_link = urllib.parse.unquote(encoded_l)
                if "/comments/" in dec_link and dec_link not in seen_links:
                    seen_links.add(dec_link)
                    sub_match = re.search(r"/r/([^/]+)/comments/([a-zA-Z0-9_]+)/([^/\s]+)", dec_link)
                    if sub_match:
                        sub_name = f"r/{sub_match.group(1)}"
                        slug = sub_match.group(3).replace("_", " ").replace("-", " ")
                        post_title = slug.capitalize()
                    else:
                        sub_name = "Reddit"
                        post_title = f"{query.title()} Tartışma Gönderisi"
                        
                    items.append({
                        "id": f"rd_{abs(hash(dec_link))}",
                        "platform": "reddit",
                        "platformLabel": f"Reddit ({sub_name})",
                        "author": sub_name,
                        "handle": sub_name,
                        "url": dec_link,
                        "mediaUrl": "",
                        "videoUrl": "",
                        "date": "Reddit",
                        "verified": False,
                        "initial": sub_name.replace("r/", "")[0].upper() if len(sub_name) > 2 else "R",
                        "hue": 16,
                        "text": f"**{post_title}**\n\nReddit topluluğunda {query} üzerine açılan güncel tartışma konusu ve yorumlar.",
                        "metrics": [
                            {"label": "topluluk", "value": sub_name},
                            {"label": "maliyet", "value": "0 token"}
                        ],
                        "media": False,
                        "mediaBadge": None,
                        "isVideo": False
                    })
                    if len(items) >= limit:
                        break
        except Exception as e:
            sys.stderr.write(f"Reddit arama motoru yedeği uyarısı: {e}\n")

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d yazıcı"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_reddit(q, lim)
    print(json.dumps(results, ensure_ascii=False))
