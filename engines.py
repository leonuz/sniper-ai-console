"""
engines.py — Start / stop / toggle logic for Ollama and Open-WebUI.
"""

import os
import subprocess
import threading
import time

import state
from config import OLLAMA_PATH, WEBUI_PATH, ENGINES
from logger import log
from helpers import kill_proc, kill_orphans, port_open, is_proc_alive


# ─────────────────────────────────────────────
#  INDIVIDUAL SERVICE CONTROL
# ─────────────────────────────────────────────
def start_ollama() -> None:
    """Launch Ollama serve process."""
    if state.ollama_proc is not None and is_proc_alive(state.ollama_proc):
        log("Ollama is already running.", "WARN")
        return
    if state.engine_start_time == 0:
        state.engine_start_time = time.time()
    host = ENGINES["ollama_host"]
    log(f"Launching Ollama (listening on {host}) ...", "INFO")
    ol_env = os.environ.copy()
    ol_env["OLLAMA_HOST"] = host
    state.ollama_proc = subprocess.Popen(
        [OLLAMA_PATH, "serve"],
        creationflags=subprocess.CREATE_NO_WINDOW,
        env=ol_env,
    )
    log(f"  Ollama PID: {state.ollama_proc.pid}", "DEBUG")


def stop_ollama() -> None:
    """Stop Ollama process tree."""
    if state.ollama_proc is None:
        log("Ollama is not running.", "WARN")
        return
    log("Stopping Ollama ...", "INFO")
    kill_proc(state.ollama_proc, "Ollama")
    state.ollama_proc = None
    state.ol_logged = False


def start_webui() -> None:
    """Launch Open-WebUI serve process."""
    if state.webui_proc is not None and is_proc_alive(state.webui_proc):
        log("Open-WebUI is already running.", "WARN")
        return
    if state.engine_start_time == 0:
        state.engine_start_time = time.time()
    log("Launching Open-WebUI ...", "INFO")
    state.webui_proc = subprocess.Popen(
        [WEBUI_PATH, "serve"],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    log(f"  Open-WebUI PID: {state.webui_proc.pid}", "DEBUG")


def stop_webui() -> None:
    """Stop Open-WebUI process tree + orphan sweep."""
    if state.webui_proc is None:
        log("Open-WebUI is not running.", "WARN")
        return
    log("Stopping Open-WebUI ...", "INFO")
    kill_proc(state.webui_proc, "Open-WebUI")
    state.webui_proc = None
    state.wb_logged = False
    time.sleep(ENGINES["orphan_kill_delay"])
    kill_orphans()


# ─────────────────────────────────────────────
#  TOGGLES (thread-safe wrappers)
# ─────────────────────────────────────────────
def toggle_ollama() -> None:
    """Toggle Ollama on/off based on current port status."""
    if port_open(ENGINES["ollama_port"]):
        threading.Thread(target=stop_ollama, daemon=True).start()
    else:
        threading.Thread(target=start_ollama, daemon=True).start()


def toggle_webui() -> None:
    """Toggle Open-WebUI on/off based on current port status."""
    if port_open(ENGINES["webui_port"]):
        threading.Thread(target=stop_webui, daemon=True).start()
    else:
        threading.Thread(target=start_webui, daemon=True).start()


# ─────────────────────────────────────────────
#  BULK OPERATIONS
# ─────────────────────────────────────────────
def start_all() -> None:
    """Launch both engines."""
    state.ol_logged = state.wb_logged = state.browser_launched = False
    state.engine_start_time = time.time()
    log("Sniper AI Engines initialising ...", "DEBUG")
    try:
        start_ollama()
        start_webui()
        log("Monitoring handshake ...", "WARN")
    except Exception as exc:
        log(f"Startup failed: {exc}", "ERROR")


def nuclear_shutdown() -> None:
    """Force-stop both engines with full cleanup."""
    log("== FORCE SHUTDOWN ==========================", "WARN")

    log("Step 1/3 - Stopping Ollama ...", "INFO")
    kill_proc(state.ollama_proc, "Ollama")
    state.ollama_proc = None

    log("Step 2/3 - Stopping Open-WebUI ...", "INFO")
    kill_proc(state.webui_proc, "Open-WebUI")
    state.webui_proc = None

    log("Step 3/3 - Orphan process sweep ...", "INFO")
    time.sleep(ENGINES["orphan_kill_delay"])
    kill_orphans()

    state.browser_launched = state.ol_logged = state.wb_logged = False
    state.engine_start_time = 0.0
    log("== Shutdown complete. Console still running. ==", "SUCCESS")


def restart_all() -> None:
    """Shutdown then relaunch both engines."""
    nuclear_shutdown()
    time.sleep(ENGINES["restart_delay"])
    start_all()
