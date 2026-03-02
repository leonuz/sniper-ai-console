"""
Sniper AI Console - Main Entry Point
Enhanced cyberpunk control panel for Ollama + Open-WebUI + OpenClaw local AI stack.
"""

import os
import threading
import time

import dearpygui.dearpygui as dpg
import psutil

import state
from config import APP_NAME, APP_VERSION, ICON_FILE, PORTAL_URL, UI, ENGINES
from logger import log
from helpers import (
    port_open, uptime_str, get_gpu_val, is_proc_alive,
    GREEN, RED, GREEN_RGB, RED_RGB,
)
from monitoring import (
    fetch_ollama_version, fetch_webui_version,
    collect_procs, update_proc_table,
)
from engines import fetch_openclaw_version
from updater import check_for_updates_async
from ui import build_gui


# ─────────────────────────────────────────────
#  MAIN UPDATE LOOP
# ─────────────────────────────────────────────
def update_loop() -> None:
    time.sleep(2.8)

    # Transition from splash to main window
    def _show_main():
        if dpg.does_item_exist("splash_win"):
            dpg.hide_item("splash_win")
        if dpg.does_item_exist("PrimaryWindow"):
            dpg.show_item("PrimaryWindow")
    state.queue(_show_main)

    proc_tick = 0
    ol_port = ENGINES["ollama_port"]
    wb_port = ENGINES["webui_port"]
    oc_port = ENGINES["openclaw_port"]
    proc_interval = UI["proc_refresh_interval"]
    browser_cmd = ENGINES["browser_command"]

    while dpg.is_dearpygui_running():
        try:
            # ── Telemetry ─────────────────────
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            gpu = get_gpu_val()

            def _graphs(c=cpu, r=ram, g=gpu):
                for key, val in zip(("cpu", "ram", "gpu"), (c, r, g)):
                    state.history[key].append(val)
                    state.history[key].pop(0)
                    if dpg.does_item_exist(f"{key}_series"):
                        dpg.set_value(f"{key}_series",
                                      [state.x_axis, state.history[key]])
                    if dpg.does_item_exist(f"{key}_pct"):
                        dpg.configure_item(f"{key}_pct",
                                           default_value=f"{val:5.1f}%")
            state.queue(_graphs)

            # ── Sidebar stats ─────────────────
            vm = psutil.virtual_memory()
            ug = vm.used / (1024 ** 3)
            tg = vm.total / (1024 ** 3)
            up = uptime_str()

            def _sidebar(u=up, ra=f"{ug:.1f}/{tg:.1f} GB"):
                if dpg.does_item_exist("uptime_val"):
                    dpg.configure_item("uptime_val", default_value=u)
                if dpg.does_item_exist("ram_abs"):
                    dpg.configure_item("ram_abs", default_value=ra)
            state.queue(_sidebar)

            # ── Service status ────────────────
            ol_on = port_open(ol_port)
            wb_on = port_open(wb_port)

            # Health check: process died but port might still show open briefly
            if not is_proc_alive(state.ollama_proc) and state.ol_logged:
                ol_on = False
            if not is_proc_alive(state.webui_proc) and state.wb_logged:
                wb_on = False

            if ol_on and not state.ol_logged:
                log("Ollama service online.", "SUCCESS")
                state.ol_logged = True
                ov = fetch_ollama_version()
                def _set_ol_ver(v=ov):
                    if dpg.does_item_exist("ol_ver"):
                        dpg.configure_item("ol_ver", default_value=v)
                state.queue(_set_ol_ver)

            if wb_on and not state.wb_logged:
                log("Open-WebUI service online.", "SUCCESS")
                state.wb_logged = True
                wv = fetch_webui_version()
                def _set_wb_ver(v=wv):
                    if dpg.does_item_exist("wb_ver"):
                        dpg.configure_item("wb_ver", default_value=v)
                state.queue(_set_wb_ver)
                # Auto-check for updates once per session
                if not state.update_checked:
                    state.update_checked = True
                    check_for_updates_async()

            if not ol_on and state.ol_logged:
                # Service went down — health check detected crash
                if state.ollama_proc is not None and not is_proc_alive(state.ollama_proc):
                    log("Ollama process crashed or was killed externally.", "ERROR")
                    state.ollama_proc = None
                state.ol_logged = False

            if not wb_on and state.wb_logged:
                if state.webui_proc is not None and not is_proc_alive(state.webui_proc):
                    log("Open-WebUI process crashed or was killed externally.", "ERROR")
                    state.webui_proc = None
                state.wb_logged = False

            # ── OpenClaw status ───────────────
            oc_on = port_open(oc_port)

            if oc_on and not state.oc_logged:
                log("OpenClaw gateway online.", "SUCCESS")
                state.oc_logged = True
                def _fetch_oc_ver():
                    ocv = fetch_openclaw_version()
                    def _set(v=ocv):
                        if dpg.does_item_exist("oc_ver"):
                            dpg.configure_item("oc_ver", default_value=v)
                    state.queue(_set)
                threading.Thread(target=_fetch_oc_ver, daemon=True).start()

            if not oc_on and state.oc_logged:
                log("OpenClaw gateway went offline.", "WARN")
                state.oc_logged = False

            # ── Status lights + toggle buttons ─
            def _lights(oo=ol_on, wo=wb_on, co=oc_on):
                if dpg.does_item_exist("ol_light"):
                    dpg.configure_item("ol_light", fill=GREEN_RGB if oo else RED_RGB)
                if dpg.does_item_exist("wb_light"):
                    dpg.configure_item("wb_light", fill=GREEN_RGB if wo else RED_RGB)
                if dpg.does_item_exist("oc_light"):
                    dpg.configure_item("oc_light", fill=GREEN_RGB if co else RED_RGB)
                if dpg.does_item_exist("ol_status"):
                    dpg.configure_item("ol_status",
                        default_value="ONLINE" if oo else "OFFLINE",
                        color=GREEN if oo else RED)
                if dpg.does_item_exist("wb_status"):
                    dpg.configure_item("wb_status",
                        default_value="ONLINE" if wo else "OFFLINE",
                        color=GREEN if wo else RED)
                if dpg.does_item_exist("oc_status"):
                    dpg.configure_item("oc_status",
                        default_value="ONLINE" if co else "OFFLINE",
                        color=GREEN if co else RED)
                # Toggle buttons
                if dpg.does_item_exist("ol_toggle"):
                    dpg.configure_item("ol_toggle",
                        label="STOP" if oo else "START")
                    dpg.bind_item_theme("ol_toggle",
                        "theme_btn_on" if oo else "theme_btn_off")
                if dpg.does_item_exist("wb_toggle"):
                    dpg.configure_item("wb_toggle",
                        label="STOP" if wo else "START")
                    dpg.bind_item_theme("wb_toggle",
                        "theme_btn_on" if wo else "theme_btn_off")
                if dpg.does_item_exist("oc_toggle"):
                    dpg.configure_item("oc_toggle",
                        label="STOP" if co else "START")
                    dpg.bind_item_theme("oc_toggle",
                        "theme_btn_on" if co else "theme_btn_off")
                # Version labels: reset to -- when offline
                if not oo and dpg.does_item_exist("ol_ver"):
                    dpg.configure_item("ol_ver", default_value="--")
                if not wo and dpg.does_item_exist("wb_ver"):
                    dpg.configure_item("wb_ver", default_value="--")
                if not co and dpg.does_item_exist("oc_ver"):
                    dpg.configure_item("oc_ver", default_value="--")
            state.queue(_lights)

            # ── Auto browser launch ───────────
            if ol_on and wb_on and not state.browser_launched:
                log("Full handshake confirmed. Launching browser ...", "SUCCESS")
                os.system(f"{browser_cmd} {PORTAL_URL}")
                state.browser_launched = True
            elif not (ol_on and wb_on):
                state.browser_launched = False

            # ── Process table ─────────────────
            proc_tick += 1
            if proc_tick >= proc_interval:
                proc_tick = 0
                collect_procs()
                state.queue(update_proc_table)

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
