import sys
import os
import json
import urllib.request
import urllib.parse
import re
from agent_reach.config import Config
from agent_reach.tools.translate_util import translate_to_turkish_fast

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def search_github(query, limit=6):
    config = Config()
    token = config.get("github_token", "")
    
    headers = {
        "User-Agent": "agent-reach-desktop-app",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Check if token is a browser cookie string or real Personal Access Token (ghp_...)
    if token:
        if token.startswith("ghp_") or token.startswith("github_pat_"):
            headers["Authorization"] = f"token {token}"
        elif "__Host-user_session_same_site" in token or "user_session=" in token:
            headers["Cookie"] = token

    api_url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page={limit}"
    
    items = []
    try:
        req = urllib.request.Request(api_url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        repos = data.get("items", [])
        
        for r in repos:
            full_name = r.get("full_name", "")
            owner = r.get("owner", {})
            owner_login = owner.get("login", "github_user")
            avatar_url = owner.get("avatar_url", "")
            html_url = r.get("html_url", "")
            raw_desc = r.get("description") or f"GitHub açık kaynak deposu: {full_name}"
            description = translate_to_turkish_fast(raw_desc)
            stars = r.get("stargazers_count", 0)
            forks = r.get("forks_count", 0)
            language = r.get("language") or "Code"
            
            full_text = f"**{full_name}** ({language})\n\n{description}"
            
            items.append({
                "id": f"gh_{r.get('id', hash(html_url))}",
                "platform": "github",
                "platformLabel": f"GitHub ({language})",
                "author": full_name,
                "handle": f"@{owner_login}",
                "url": html_url,
                "mediaUrl": avatar_url,
                "videoUrl": "",
                "date": "GitHub",
                "verified": True,
                "initial": owner_login[0].upper() if owner_login else "G",
                "hue": 220,
                "text": full_text,
                "metrics": [
                    {"label": "yıldız ⭐", "value": f"{stars:,}" if stars else "0"},
                    {"label": "çatal 🍴", "value": f"{forks:,}" if forks else "0"}
                ],
                "media": bool(avatar_url),
                "mediaBadge": "profil",
                "isVideo": False
            })
    except urllib.error.HTTPError as e:
        # If rate-limited or unauthenticated on API, fallback without authorization header
        try:
            req_public = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 agent-reach"})
            resp_pub = urllib.request.urlopen(req_public, timeout=8)
            data_pub = json.loads(resp_pub.read().decode("utf-8"))
            for r in data_pub.get("items", [])[:limit]:
                full_name = r.get("full_name", "")
                owner = r.get("owner", {})
                owner_login = owner.get("login", "github_user")
                avatar_url = owner.get("avatar_url", "")
                html_url = r.get("html_url", "")
                description = r.get("description") or f"GitHub açık kaynak deposu: {full_name}"
                stars = r.get("stargazers_count", 0)
                forks = r.get("forks_count", 0)
                language = r.get("language") or "Code"
                
                items.append({
                    "id": f"gh_{r.get('id', hash(html_url))}",
                    "platform": "github",
                    "platformLabel": f"GitHub ({language})",
                    "author": full_name,
                    "handle": f"@{owner_login}",
                    "url": html_url,
                    "mediaUrl": avatar_url,
                    "videoUrl": "",
                    "date": "GitHub",
                    "verified": True,
                    "initial": owner_login[0].upper() if owner_login else "G",
                    "hue": 220,
                    "text": f"**{full_name}** ({language})\n\n{description}",
                    "metrics": [
                        {"label": "yıldız ⭐", "value": f"{stars:,}" if stars else "0"},
                        {"label": "çatal 🍴", "value": f"{forks:,}" if forks else "0"}
                    ],
                    "media": bool(avatar_url),
                    "mediaBadge": "profil",
                    "isVideo": False
                })
        except Exception as fallback_err:
            sys.stderr.write(f"GitHub genel arama hatası: {fallback_err}\n")
    except Exception as e:
        sys.stderr.write(f"GitHub arama hatası: {e}\n")

    return items

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "3d printer"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    results = search_github(q, lim)
    print(json.dumps(results, ensure_ascii=False))
