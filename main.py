"""
Sniper AI Console - Main Entry Point
Enhanced cyberpunk control panel for Ollama + Open-WebUI + OpenClaw local AI stack.
"""

import threading
import time

import dearpygui.dearpygui as dpg

import state
from config import APP_NAME, APP_VERSION, ICON_FILE, PORTAL_URL, UI, ENGINES
from logger import log
from updater import check_for_updates_async
from ui import build_gui
from app.adapters.platform.browser import open_url
from app.application.coordinator import RuntimeCoordinator


# ─────────────────────────────────────────────
#  MAIN UPDATE LOOP
# ─────────────────────────────────────────────
def update_loop() -> None:
    time.sleep(2.8)

    def _show_main():
        if dpg.does_item_exist("splash_win"):
            dpg.hide_item("splash_win")
        if dpg.does_item_exist("PrimaryWindow"):
            dpg.show_item("PrimaryWindow")

    state.queue(_show_main)

    proc_tick = 0
    proc_interval = UI["proc_refresh_interval"]
    browser_cmd = ENGINES["browser_command"]
    coordinator = RuntimeCoordinator()

    while dpg.is_dearpygui_running():
        try:
            coordinator.poll_telemetry()
            status = coordinator.poll_services()

            if status["webui"] and not state.update_checked:
                state.update_checked = True
                check_for_updates_async()

            if status["ollama"] and status["webui"] and not state.browser_launched:
                log("Full handshake confirmed. Launching browser ...", "SUCCESS")
                open_url(browser_cmd, PORTAL_URL)
                state.browser_launched = True
            elif not (status["ollama"] and status["webui"]):
                state.browser_launched = False

            proc_tick += 1
            if proc_tick >= proc_interval:
                proc_tick = 0
                coordinator.poll_processes()

        except Exception:
            pass

        state.flush_ui_queue()
        time.sleep(1)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    dpg.create_context()
    build_gui()

    dpg.create_viewport(
        title=f"{APP_NAME}  {APP_VERSION}",
        width=UI["viewport_width"],
        height=UI["viewport_height"],
        min_width=UI["min_width"],
        min_height=UI["min_height"],
    )
    try:
        dpg.set_viewport_small_icon(ICON_FILE)
        dpg.set_viewport_large_icon(ICON_FILE)
    except Exception:
        pass

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("PrimaryWindow", True)

    threading.Thread(target=update_loop, daemon=True).start()

    log(f"{APP_NAME} {APP_VERSION} ready.", "SUCCESS")

    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
