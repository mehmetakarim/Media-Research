# -*- coding: utf-8 -*-
"""Pinterest channel — check if pinterest-dl is available."""

import shutil
from .base import Channel


class PinterestChannel(Channel):
    name = "pinterest"
    description = "Pinterest 图片和 Pin"
    backends = ["pinterest-dl CLI"]
    tier = 2

    def can_handle(self, url: str) -> bool:
        from urllib.parse import urlparse
        d = urlparse(url).netloc.lower()
        return "pinterest.com" in d or "pin.it" in d

    def check(self, config=None):
        if not shutil.which("pinterest-dl"):
            return "warn", (
                "pinterest-dl CLI 未安装。搜索或读取需手动配置。\n"
                "  安装：pip install pinterest-dl"
            )
        return "ok", "完整可用（读取 Pinterest 图片及信息）"
