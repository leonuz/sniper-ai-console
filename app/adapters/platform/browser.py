"""Browser launch adapter."""

from __future__ import annotations

import os


def open_url(browser_command: str, url: str) -> int:
    """Launch a URL using the configured browser command."""
    return os.system(f"{browser_command} {url}")
