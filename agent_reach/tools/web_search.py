import sys
import os
import json
import urllib.request
import urllib.parse
import re
import html

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def search_web(query, limit=6):
    """Zero-cookie, zero-token global web and news article search engine."""
    items = []
    
    # 1. Primary: Google News / Web RSS Search (Global & Turkish multi-source)
    rss_urls = [
        f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=tr&gl=TR&ceid=TR:tr",
        f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    ]
    
    seen_titles = set()
    for rss_url in rss_urls:
        try:
            req = urllib.request.Request(rss_url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            resp = urllib.request.urlopen(req, timeout=8)
            xml_data = resp.read().decode("utf-8")
            raw_items = re.findall(r"<item>(.+?)</item>", xml_data, re.DOTALL)
            
            for it in raw_items:
                t_match = re.search(r"<title>(.+?)</title>", it)
                l_match = re.search(r"<link>(.+?)</link>", it)
                source_match = re.search(r"<source[^>]*>(.+?)</source>", it)
                date_match = re.search(r"<pubDate>(.+?)</pubDate>", it)
                
                raw_title = html.unescape(t_match.group(1)).strip() if t_match else f"{query} Makalesi"
                link = l_match.group(1).strip() if l_match else ""
                source_name = html.unescape(source_match.group(1)).strip() if source_match else "Web Yayını"
                pub_date = date_match.group(1)[:16].strip() if date_match else "Bugün"
                
                # Split source name if inside title
                clean_title = raw_title
                if " - " in raw_title:
                    parts = raw_title.rsplit(" - ", 1)
                    clean_title = parts[0].strip()
                    if not source_name or source_name == "Web Yayını":
                        source_name = parts[1].strip()
                        
                if clean_title in seen_titles:
                    continue
                seen_titles.add(clean_title)
                
                items.append({
                    "id": f"web_{abs(hash(clean_title))}",
                    "platform": "web",
                    "platformLabel": f"Web ({source_name})",
                    "author": source_name,
                    "handle": f"@{source_name.lower().replace(' ', '')}",
                    "url": link,
                    "mediaUrl": "",
                    "videoUrl": "",
                    "date": pub_date,
                    "verified": True,
                    "initial": source_name[0].upper() if source_name else "W",
                    "hue": 200,
                    "text": f"**{clean_title}**\n\n{source_name} tarafından yayınlanan güncel teknoloji, ürün ve sektör haberi.",
                    "metrics": [
                        {"label": "kaynak", "value": source_name},
                        {"label": "maliyet", "value": "0 token"}
                    ],
                    "media": False,
                    "mediaBadge": None,
                    "isVideo": False
                })
                if len(items) >= limit:
                    break
        except Exception as e:
            sys.stderr.write(f"Web RSS uyarısı: {e}\n")
            
        if len(items) >= limit:
            break

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d yazıcı"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_web(q, lim)
    print(json.dumps(results, ensure_ascii=False))
