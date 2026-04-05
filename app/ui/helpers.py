"""UI helper functions reused across DearPyGui components."""

from __future__ import annotations

import os

from config import BASE_DIR


def read_markdown_file(filename: str) -> str:
    path = os.path.join(BASE_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return f"(Could not load {filename})"
