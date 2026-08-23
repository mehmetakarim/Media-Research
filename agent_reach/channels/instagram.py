# -*- coding: utf-8 -*-
"""Instagram channel — check if instaloader or session is configured."""

import os
import shutil
from .base import Channel


class InstagramChannel(Channel):
    name = "instagram"
    description = "Instagram 帖子和主页"
    backends = ["instaloader CLI"]
    tier = 2

    def can_handle(self, url: str) -> bool:
        from urllib.parse import urlparse
        d = urlparse(url).netloc.lower()
        return "instagram.com" in d

    def check(self, config=None):
        if not shutil.which("instaloader"):
            return "warn", (
                "instaloader 未安装。\n"
                "  安装：pip install instaloader"
            )
            
        session_exists = False
        if config:
            session_file = config.get("instagram_session_file")
            if session_file and os.path.exists(session_file):
                session_exists = True
            elif config.get("instagram_cookies"):
                session_exists = True
                
        # Check standard instaloader session dir ~/.config/instaloader/
        instaloader_dir = os.path.expanduser("~/.config/instaloader")
        if os.path.exists(instaloader_dir) and any(os.path.isfile(os.path.join(instaloader_dir, f)) for f in os.listdir(instaloader_dir)):
            session_exists = True

        if not session_exists:
            return "warn", "Instagram çerezleri veya oturumu yapılandırılmamış (Giriş yapılması önerilir)."

        return "ok", "Tam kullanılabilir (Instagram çerezleri/oturumu aktif)"
