# -*- coding: utf-8 -*-
"""Native zero-dependency browser cookie reader and robust multi-format parser for Windows, macOS, and Linux.

Works with:
- Chrome, Edge, Brave, Opera, Firefox
- JSON exports (EditThisCookie, Cookie-Editor)
- Standard Cookie headers: 'auth_token=...; ct0=...'
- Raw token values
"""

import sys
import os
import json
import re
import glob
import shutil
import sqlite3
import tempfile
import secrets
from typing import Dict, List, Optional, Tuple, Any

from agent_reach.config import Config


PLATFORMS = {
    "twitter": {
        "domains": ["x.com", "twitter.com"],
        "keys": ["auth_token", "ct0"],
        "config_keys": {"auth_token": "twitter_auth_token", "ct0": "twitter_ct0"}
    },
    "instagram": {
        "domains": ["instagram.com"],
        "keys": ["sessionid", "csrftoken", "ds_user_id"],
        "config_keys": {"sessionid": "instagram_session_id", "csrftoken": "instagram_csrf"}
    },
    "pinterest": {
        "domains": ["pinterest.com"],
        "keys": ["_pinterest_sess", "_auth"],
        "config_keys": {"_pinterest_sess": "pinterest_sess", "_auth": "pinterest_auth"}
    },
    "reddit": {
        "domains": ["reddit.com"],
        "keys": ["reddit_session"],
        "config_keys": {"reddit_session": "reddit_session"}
    },
    "linkedin": {
        "domains": ["linkedin.com"],
        "keys": ["li_at"],
        "config_keys": {"li_at": "linkedin_li_at"}
    },
    "bilibili": {
        "domains": ["bilibili.com"],
        "keys": ["SESSDATA", "bili_jct"],
        "config_keys": {"SESSDATA": "bilibili_sessdata", "bili_jct": "bilibili_csrf"}
    },
    "xhs": {
        "domains": ["xiaohongshu.com"],
        "keys": ["web_session", "a1"],
        "config_keys": {"web_session": "xhs_session"}
    }
}


def parse_any_cookie_input(service: str, raw_input: str) -> Dict[str, str]:
    """Parse raw user input in ANY format: Header, Key-Value, JSON, or Raw Token."""
    raw_input = raw_input.strip()
    if not raw_input:
        return {}

    parsed = {}

    # 1. Try parsing JSON (Cookie-Editor / EditThisCookie export format)
    if raw_input.startswith("[") or raw_input.startswith("{"):
        try:
            data = json.loads(raw_input)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "name" in item and "value" in item:
                        parsed[item["name"]] = item["value"]
            elif isinstance(data, dict):
                for k, v in data.items():
                    parsed[k] = str(v)
        except Exception:
            pass

    # 2. Try parsing standard cookie header format: 'k1=v1; k2=v2'
    if not parsed and ("=" in raw_input or ";" in raw_input):
        parts = re.split(r'[;\n]', raw_input)
        for part in parts:
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                parsed[k.strip()] = v.strip().strip('"').strip("'")

    # 3. Direct key-value regex patterns
    if not parsed:
        for match in re.finditer(r'([a-zA-Z0-9_\-]+)\s*[:=]\s*([a-zA-Z0-9_\-%]+)', raw_input):
            parsed[match.group(1)] = match.group(2)

    # 4. Fallback: Raw Token input
    svc = service.lower()
    if not parsed and len(raw_input) > 10:
        if "twitter" in svc or "x" == svc:
            parsed["auth_token"] = raw_input
        elif "instagram" in svc:
            parsed["sessionid"] = raw_input
        elif "pinterest" in svc:
            parsed["_pinterest_sess"] = raw_input
        elif "linkedin" in svc:
            parsed["li_at"] = raw_input
        elif "reddit" in svc:
            parsed["reddit_session"] = raw_input
        elif "github" in svc:
            parsed["github_token"] = raw_input

    # 5. Twitter auto-generate ct0 if missing
    if "twitter" in svc or "x" == svc:
        if "auth_token" in parsed and "ct0" not in parsed:
            parsed["ct0"] = secrets.token_hex(16)

    return parsed


def save_cookies_for_service(service: str, raw_input: str) -> Dict[str, Any]:
    """Save cookies for a service into Config and sync to bird credentials.env."""
    svc = service.lower()
    parsed = parse_any_cookie_input(svc, raw_input)
    if not parsed:
        raise ValueError("Girdi geçerli bir çerez veya belirteç formatında anlaşılamadı.")

    config = Config()
    saved_items = []

    # Twitter / X
    if "twitter" in svc or "x" == svc:
        auth_token = parsed.get("auth_token", "")
        ct0 = parsed.get("ct0", "")
        if auth_token:
            config.set("twitter_auth_token", auth_token)
            saved_items.append("auth_token")
        if ct0:
            config.set("twitter_ct0", ct0)
            saved_items.append("ct0")

        # Sync to bird credentials.env
        if auth_token and ct0:
            try:
                bird_dir = os.path.join(os.path.expanduser("~"), ".config", "bird")
                os.makedirs(bird_dir, exist_ok=True)
                env_path = os.path.join(bird_dir, "credentials.env")
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f'AUTH_TOKEN="{auth_token}"\n')
                    f.write(f'CT0="{ct0}"\n')
            except Exception:
                pass

    # Instagram
    elif "instagram" in svc:
        for k, v in parsed.items():
            if k == "sessionid":
                config.set("instagram_session_id", v)
                saved_items.append("sessionid")
            elif k == "csrftoken":
                config.set("instagram_csrf", v)
                saved_items.append("csrftoken")
        cookie_str = "; ".join(f"{k}={v}" for k, v in parsed.items())
        config.set("instagram_cookies", cookie_str)
        saved_items.append("instagram_cookies")

    # Pinterest
    elif "pinterest" in svc:
        for k, v in parsed.items():
            if k == "_pinterest_sess":
                config.set("pinterest_sess", v)
                saved_items.append("_pinterest_sess")
        cookie_str = "; ".join(f"{k}={v}" for k, v in parsed.items())
        config.set("pinterest_cookies", cookie_str)
        saved_items.append("pinterest_cookies")

    # Other services
    else:
        cookie_str = "; ".join(f"{k}={v}" for k, v in parsed.items())
        config.set(f"{svc}_cookies", cookie_str)
        saved_items.append(f"{svc}_cookies")

    return {
        "success": True,
        "service": service,
        "saved_keys": saved_items,
        "parsed": parsed
    }


def _get_firefox_cookies() -> List[Tuple[str, str, str]]:
    """Read Firefox cookies directly from SQLite without external packages."""
    cookies = []
    home = os.path.expanduser("~")
    
    if sys.platform == "win32":
        profile_pattern = os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles", "*", "cookies.sqlite")
    elif sys.platform == "darwin":
        profile_pattern = os.path.join(home, "Library", "Application Support", "Firefox", "Profiles", "*", "cookies.sqlite")
    else:
        profile_pattern = os.path.join(home, ".mozilla", "firefox", "*", "cookies.sqlite")

    paths = glob.glob(profile_pattern)
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            # Copy to temp file to prevent database locked errors while Firefox is running
            with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
                tmp_path = tmp.name
            shutil.copy2(p, tmp_path)

            conn = sqlite3.connect(tmp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value, host FROM moz_cookies")
            for name, val, host in cursor.fetchall():
                cookies.append((name, val, host))
            conn.close()
            os.remove(tmp_path)
        except Exception:
            pass

    return cookies


def extract_all(browser: str = "chrome") -> Dict[str, dict]:
    """
    Extract cookies for all supported platforms from the specified browser.
    Zero terminal dependencies.
    """
    browser = browser.lower()
    raw_cookies = []

    # 1. First try browser_cookie3 if present
    try:
        import browser_cookie3
        funcs = {
            "chrome": browser_cookie3.chrome,
            "firefox": browser_cookie3.firefox,
            "edge": browser_cookie3.edge,
            "brave": browser_cookie3.brave,
            "opera": browser_cookie3.opera,
        }
        if browser in funcs:
            jar = funcs[browser]()
            for c in jar:
                raw_cookies.append((c.name, c.value, c.domain))
    except Exception:
        pass

    # 2. Native zero-dependency fallback for Firefox
    if not raw_cookies and browser == "firefox":
        raw_cookies = _get_firefox_cookies()

    results = {}
    config = Config()

    for platform_name, spec in PLATFORMS.items():
        found = {}
        for name, val, host in raw_cookies:
            h = host.lower()
            if any(d in h for d in spec["domains"]):
                if name in spec["keys"]:
                    found[name] = val

        if found:
            results[platform_name] = found
            # Auto-sync to config
            for k, v in found.items():
                cfg_k = spec["config_keys"].get(k)
                if cfg_k:
                    config.set(cfg_k, v)

            if platform_name == "twitter" and "auth_token" in found and "ct0" in found:
                try:
                    bird_dir = os.path.join(os.path.expanduser("~"), ".config", "bird")
                    os.makedirs(bird_dir, exist_ok=True)
                    env_path = os.path.join(bird_dir, "credentials.env")
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(f'AUTH_TOKEN="{found["auth_token"]}"\n')
                        f.write(f'CT0="{found["ct0"]}"\n')
                except Exception:
                    pass

    return results


def configure_from_browser(browser: str, config) -> List[Tuple[str, bool, str]]:
    """Configure found platforms."""
    res = extract_all(browser)
    if not res:
        return [("All", False, f"{browser.upper()} tarayıcısından çerez alınamadı.")]
    out = []
    for p, cookies in res.items():
        out.append((p.capitalize(), True, f"{len(cookies)} anahtar aktarıldı ({', '.join(cookies.keys())})"))
    return out
