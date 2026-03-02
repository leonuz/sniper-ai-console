"""
config.py — Configuration loader for Sniper AI Console.
Reads config.json from the application directory.
Generates a default config.json if none exists.
"""

import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# ─────────────────────────────────────────────
#  DEFAULT CONFIG (used when config.json is missing)
# ─────────────────────────────────────────────
_DEFAULTS = {
    "app": {
        "name": "Sniper AI Console",
        "version": "v1.2",
        "author": "Leonuz",
        "license": "MIT",
        "portfolio_url": "https://leonuz.github.com",
    },
    "paths": {
        "ollama": r"C:\ollama-intel\ollama.exe",
        "webui": r"C:\ollama-intel\open-webui\venv\Scripts\open-webui.exe",
    },
    "urls": {
        "portal": "https://sniperx1.uzc",
        "ollama_api": "http://127.0.0.1:11434",
        "webui_local": "http://127.0.0.1:8080",
        "model_library": "https://ollama.com/library",
    },
    "files": {
        "icon": "icon.ico",
        "logo": "logo.png",
    },
    "ui": {
        "viewport_width": 1400,
        "viewport_height": 900,
        "min_width": 900,
        "min_height": 600,
        "sidebar_width": 215,
        "graph_height": 200,
        "graph_width": 375,
        "tab_content_height": 310,
        "log_height": 260,
        "max_data_points": 120,
        "proc_refresh_interval": 5,
        "top_processes": 25,
    },
    "engines": {
        "ollama_host": "0.0.0.0:11434",
        "ollama_port": 11434,
        "webui_port": 8080,
        "browser_command": "start msedge",
        "restart_delay": 1.5,
        "orphan_kill_delay": 0.5,
    },
    "logging": {
        "log_to_file": True,
        "log_file": "sniper_ai.log",
        "max_file_size_mb": 5,
        "backup_count": 3,
    },
    "gpu": {
        "label": "ARC 140V GPU %",
        "method": "powershell_counter",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, filling missing keys from base."""
    merged = base.copy()
    for key, val in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(val, dict):
            merged[key] = _deep_merge(merged[key], val)
        else:
            merged[key] = val
    return merged


def _generate_default_config() -> None:
    """Write default config.json to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(_DEFAULTS, f, indent=4, ensure_ascii=False)


def load() -> dict:
    """
    Load config.json and merge with defaults.
    Creates config.json with defaults if it doesn't exist.
    """
    if not os.path.exists(CONFIG_FILE):
        _generate_default_config()
        return _DEFAULTS.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_cfg = json.load(f)
        return _deep_merge(_DEFAULTS, user_cfg)
    except (json.JSONDecodeError, IOError) as exc:
        # Backup broken file and regenerate
        backup = CONFIG_FILE + ".bak"
        shutil.copy2(CONFIG_FILE, backup)
        _generate_default_config()
        return _DEFAULTS.copy()


# ─────────────────────────────────────────────
#  MODULE-LEVEL CONFIG (loaded once at import)
# ─────────────────────────────────────────────
CFG = load()

# Convenience accessors
APP_NAME    = CFG["app"]["name"]
APP_VERSION = CFG["app"]["version"]

OLLAMA_PATH = CFG["paths"]["ollama"]
WEBUI_PATH  = CFG["paths"]["webui"]
WEBUI_PIP   = os.path.join(os.path.dirname(WEBUI_PATH), "pip.exe")

PORTAL_URL  = CFG["urls"]["portal"]
OLLAMA_API  = CFG["urls"]["ollama_api"]
WEBUI_LOCAL = CFG["urls"]["webui_local"]

ICON_FILE   = os.path.join(BASE_DIR, CFG["files"]["icon"])
LOGO_FILE   = os.path.join(BASE_DIR, CFG["files"]["logo"])

# UI dimensions
UI = CFG["ui"]
ENGINES = CFG["engines"]
LOGGING = CFG["logging"]
GPU_CFG = CFG["gpu"]
