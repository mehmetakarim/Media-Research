# -*- coding: utf-8 -*-
"""Auto-extract cookies from local browsers for all supported platforms.

Supports: Chrome, Firefox, Edge, Brave, Opera
Extracts: Twitter, XiaoHongShu, Bilibili cookies in one shot.

Usage:
    agent-reach configure --from-browser chrome
"""

import sys
import os
import subprocess
from typing import Dict, List, Optional, Tuple


# Platform cookie specs: (platform_name, domain_pattern, needed_cookies)
PLATFORM_SPECS = [
    {
        "name": "Twitter/X",
        "domains": [".x.com", ".twitter.com"],
        "cookies": ["auth_token", "ct0"],
        "config_key": "twitter",
    },
    {
        "name": "XiaoHongShu",
        "domains": [".xiaohongshu.com"],
        "cookies": None,  # None = grab all cookies as header string
        "config_key": "xhs",
    },
    {
        "name": "Bilibili",
        "domains": [".bilibili.com"],
        "cookies": ["SESSDATA", "bili_jct"],
        "config_key": "bilibili",
    },
    {
        "name": "Instagram",
        "domains": [".instagram.com"],
        "cookies": ["sessionid", "csrftoken", "ds_user_id"],
        "config_key": "instagram",
    },
    {
        "name": "Pinterest",
        "domains": [".pinterest.com"],
        "cookies": ["_pinterest_sess", "_auth"],
        "config_key": "pinterest",
    }
]


def extract_all(browser: str = "chrome") -> Dict[str, dict]:
    """
    Extract cookies for all supported platforms from the specified browser.
    
    Returns:
        {
            "twitter": {"auth_token": "xxx", "ct0": "yyy"},
            "xhs": {"cookie_string": "a=1; b=2; ..."},
            "bilibili": {"SESSDATA": "xxx", "bili_jct": "yyy"},
        }
    """
    try:
        import browser_cookie3
    except ImportError:
        # Otomatik olarak pip ile browser-cookie3 kurmayı dene
        try:
            creationflags = 0x08000000 if sys.platform == "win32" else 0
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "browser-cookie3", "--quiet"],
                capture_output=True,
                timeout=45,
                creationflags=creationflags
            )
            import browser_cookie3
        except Exception:
            raise RuntimeError(
                "Otomatik çerez çekebilmek için 'browser-cookie3' modülü gereklidir. "
                "Lütfen komut satırında 'pip install browser-cookie3' çalıştırın veya çerezlerinizi manuel yapıştırın."
            )

    # Get browser cookie jar
    browser_funcs = {
        "chrome": browser_cookie3.chrome,
        "firefox": browser_cookie3.firefox,
        "edge": browser_cookie3.edge,
        "brave": browser_cookie3.brave,
        "opera": browser_cookie3.opera,
    }

    browser = browser.lower()
    if browser not in browser_funcs:
        raise ValueError(
            f"Desteklenmeyen tarayıcı: {browser}. "
            f"Desteklenenler: {', '.join(browser_funcs.keys())}"
        )

    try:
        cookie_jar = browser_funcs[browser]()
    except Exception as e:
        raise RuntimeError(
            f"{browser.upper()} tarayıcı çerezleri okunamadı: {e}. "
            f"Lütfen tarayıcının tamamen kapalı olduğundan ve yetkilerinizin tam olduğundan emin olun."
        )

    results = {}

    for spec in PLATFORM_SPECS:
        platform_cookies = {}
        all_cookies_for_domain = []

        for cookie in cookie_jar:
            domain_match = any(
                cookie.domain.endswith(d) or cookie.domain == d.lstrip(".")
                for d in spec["domains"]
            )
            if not domain_match:
                continue

            all_cookies_for_domain.append(cookie)

            if spec["cookies"] is not None:
                if cookie.name in spec["cookies"]:
                    platform_cookies[cookie.name] = cookie.value

        if spec["cookies"] is None:
            if all_cookies_for_domain:
                cookie_str = "; ".join(
                    f"{c.name}={c.value}" for c in all_cookies_for_domain
                )
                results[spec["config_key"]] = {"cookie_string": cookie_str}
        else:
            if platform_cookies:
                results[spec["config_key"]] = platform_cookies

    return results


def _sync_xfetch_session(auth_token: str, ct0: str) -> None:
    """Sync Twitter credentials to ~/.config/xfetch/session.json (legacy xreach compat)."""
    import json
    import os

    try:
        xfetch_dir = os.path.join(os.path.expanduser("~"), ".config", "xfetch")
        os.makedirs(xfetch_dir, exist_ok=True)
        session_path = os.path.join(xfetch_dir, "session.json")
        session_data: dict = {}
        if os.path.exists(session_path):
            try:
                with open(session_path, "r", encoding="utf-8") as sf:
                    session_data = json.load(sf)
            except (json.JSONDecodeError, OSError):
                session_data = {}
        session_data["authToken"] = auth_token
        session_data["ct0"] = ct0
        with open(session_path, "w", encoding="utf-8") as sf:
            json.dump(session_data, sf, indent=2)
        os.chmod(session_path, 0o600)
    except Exception:
        pass


def _sync_bird_env(auth_token: str, ct0: str) -> None:
    """Write Twitter credentials to ~/.config/bird/credentials.env for bird CLI."""
    import os

    try:
        bird_dir = os.path.join(os.path.expanduser("~"), ".config", "bird")
        os.makedirs(bird_dir, exist_ok=True)
        env_path = os.path.join(bird_dir, "credentials.env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f'AUTH_TOKEN="{auth_token}"\n')
            f.write(f'CT0="{ct0}"\n')
        os.chmod(env_path, 0o600)
    except Exception:
        pass


_sync_bird_credentials = _sync_bird_env


def configure_from_browser(browser: str, config) -> List[Tuple[str, bool, str]]:
    """
    Extract cookies and configure all found platforms.
    
    Returns list of (platform_name, success, message) tuples.
    """
    results_list = []

    try:
        extracted = extract_all(browser)
    except Exception as e:
        return [("Browser", False, str(e))]

    if not extracted:
        return [("All platforms", False,
                 f"{browser} tarayıcısında platform oturum çerezi bulunamadı. "
                 f"Lütfen tarayıcınızda ilgili sitelere giriş yaptığınızdan emin olun.")]

    if "twitter" in extracted:
        tc = extracted["twitter"]
        if "auth_token" in tc and "ct0" in tc:
            config.set("twitter_auth_token", tc["auth_token"])
            config.set("twitter_ct0", tc["ct0"])
            _sync_bird_env(tc["auth_token"], tc["ct0"])
            _sync_xfetch_session(tc["auth_token"], tc["ct0"])
            results_list.append(("Twitter/X", True, "auth_token + ct0"))
        else:
            found = ", ".join(tc.keys())
            missing = [k for k in ["auth_token", "ct0"] if k not in tc]
            results_list.append(("Twitter/X", False,
                                 f"{found} bulundu fakat eksik: {', '.join(missing)}."))

    if "xhs" in extracted:
        cookie_str = extracted["xhs"].get("cookie_string", "")
        if cookie_str:
            config.set("xhs_cookie", cookie_str)
            n_cookies = len(cookie_str.split(";"))
            results_list.append(("XiaoHongShu", True, f"{n_cookies} çerez"))

    if "bilibili" in extracted:
        bc = extracted["bilibili"]
        if "SESSDATA" in bc:
            config.set("bilibili_sessdata", bc["SESSDATA"])
            if "bili_jct" in bc:
                config.set("bilibili_csrf", bc["bili_jct"])
            results_list.append(("Bilibili", True, "SESSDATA" +
                                 (" + bili_jct" if "bili_jct" in bc else "")))
        else:
            results_list.append(("Bilibili", False, "SESSDATA bulunamadı."))

    return results_list
