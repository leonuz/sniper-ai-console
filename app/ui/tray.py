"""System tray integration helpers."""

from __future__ import annotations

import threading

import dearpygui.dearpygui as dpg

from config import APP_NAME, ICON_FILE
from engines import nuclear_shutdown
from helpers import HAS_TRAY


def _tray_thread() -> None:
    if not HAS_TRAY:
        return
    from PIL import Image
    import pystray
    from pystray import MenuItem as item

    try:
        img = Image.open(ICON_FILE)
    except Exception:
        img = Image.new("RGB", (64, 64), (0, 200, 200))

    def on_show(icon, _):
        icon.stop()
        dpg.maximize_viewport()

    def on_exit(icon, _):
        icon.stop()
        nuclear_shutdown()
        dpg.stop_dearpygui()

    menu = pystray.Menu(item("Show Console", on_show), item("Exit", on_exit))
    pystray.Icon("SniperAI", img, APP_NAME, menu).run()


def minimize_to_tray() -> None:
    dpg.minimize_viewport()
    threading.Thread(target=_tray_thread, daemon=True).start()
