# -*- coding: utf-8 -*-
"""Instagram channel — check if instaloader is available."""

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
                "instaloader 未安装。搜索或读取需手动配置。\n"
                "  安装：pip install instaloader"
            )
        return "ok", "完整可用（读取 Instagram 帖子、主页等）"
