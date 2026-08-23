import sys
import urllib.request
import urllib.parse
import json
import re
from agent_reach.tools.translate_util import translate_to_turkish_fast

def search_youtube(query, limit=6):
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        
        matches = re.findall(r"ytInitialData = (\{.+?\});</script>", html)
        if not matches:
            matches = re.findall(r"var ytInitialData = (\{.+?\});</script>", html)
            
        if not matches:
            return []
            
        data = json.loads(matches[0])
        items = []
        
        contents = (
            data.get("contents", {})
            .get("twoColumnSearchResultsRenderer", {})
            .get("primaryContents", {})
            .get("sectionListRenderer", {})
            .get("contents", [])
        )
        
        for c in contents:
            item_section = c.get("itemSectionRenderer", {}).get("contents", [])
            for it in item_section:
                vr = it.get("videoRenderer")
                if vr:
                    vid = vr.get("videoId")
                    raw_title = vr.get("title", {}).get("runs", [{}])[0].get("text", "")
                    title = translate_to_turkish_fast(raw_title)
                    author = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "YouTube Kanalı")
                    views = vr.get("viewCountText", {}).get("simpleText", "Yeni")
                    time_txt = vr.get("lengthText", {}).get("simpleText", "Video")
                    thumb = vr.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url", "")
                    
                    items.append({
                        "id": f"yt_{vid}",
                        "platform": "youtube",
                        "platformLabel": "YouTube",
                        "author": author,
                        "handle": f"@{author}".replace(" ", ""),
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "mediaUrl": thumb,
                        "date": "YouTube",
                        "verified": True,
                        "initial": author[0].upper() if author else "Y",
                        "hue": 8,
                        "text": title,
                        "badge": "Video · Canlı",
                        "metrics": [
                            {"label": "izlenme", "value": views},
                            {"label": "süre", "value": time_txt}
                        ],
                        "media": True,
                        "mediaBadge": time_txt,
                        "isVideo": True
                    })
                    if len(items) >= limit:
                        break
            if len(items) >= limit:
                break
                
        return items
    except Exception as e:
        sys.stderr.write(f"YouTube arama hatası: {e}\n")
        return []

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d printer"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_youtube(q, lim)
    print(json.dumps(results, ensure_ascii=False))
