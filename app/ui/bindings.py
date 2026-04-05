"""UI bindings and tab-driven refresh behavior."""

from __future__ import annotations

import threading

import dearpygui.dearpygui as dpg

from config import ENGINES
from helpers import port_open
from monitoring import refresh_models

_last_tab = None


def on_tab_change(sender, app_data) -> None:
    global _last_tab
    label = dpg.get_item_label(app_data) or ""
    if "MODELS" in label and _last_tab != "MODELS":
        if port_open(ENGINES["ollama_port"]):
            threading.Thread(target=refresh_models, daemon=True).start()
    _last_tab = label.strip()
