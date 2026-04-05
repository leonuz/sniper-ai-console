"""
engines.py - Start / stop / toggle logic for Ollama, Open-WebUI, and OpenClaw.
"""

import subprocess
import threading
import time

import state
from config import OPENCLAW_PATH, ENGINES
from logger import log
from app.adapters.platform.wsl import run_wsl_bash
from app.application.services_registry import get_service
from app.application.state_sync import mark_all_services_unknown, update_service_status
from app.domain.enums import ServiceName, ServiceStatus


# ─────────────────────────────────────────────
#  INDIVIDUAL SERVICE CONTROL
# ─────────────────────────────────────────────
def start_ollama() -> None:
    """Launch Ollama serve process."""
    get_service(ServiceName.OLLAMA).start()


def stop_ollama() -> None:
    """Stop Ollama process tree."""
    get_service(ServiceName.OLLAMA).stop()


def start_webui() -> None:
    """Launch Open-WebUI serve process."""
    get_service(ServiceName.OPEN_WEBUI).start()


def stop_webui() -> None:
    """Stop Open-WebUI process tree + orphan sweep."""
    get_service(ServiceName.OPEN_WEBUI).stop()


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
#  OPENCLAW (WSL) SERVICE CONTROL
# ─────────────────────────────────────────────
def _wsl_exec(cmd: str) -> subprocess.CompletedProcess:
    """Execute a command inside WSL and return the result."""
    return run_wsl_bash(cmd, timeout=30)


def start_openclaw() -> None:
    """Start OpenClaw gateway via WSL systemd."""
    get_service(ServiceName.OPENCLAW).start()


def stop_openclaw() -> None:
    """Stop OpenClaw gateway via WSL systemd."""
    get_service(ServiceName.OPENCLAW).stop()


def toggle_openclaw() -> None:
    """Toggle OpenClaw on/off based on current port status."""
    if port_open(ENGINES["openclaw_port"]):
        threading.Thread(target=stop_openclaw, daemon=True).start()
    else:
        threading.Thread(target=start_openclaw, daemon=True).start()


def fetch_openclaw_version() -> str:
    """Get OpenClaw version from WSL."""
    return get_service(ServiceName.OPENCLAW).fetch_version()


# ─────────────────────────────────────────────
#  BULK OPERATIONS
# ─────────────────────────────────────────────
def start_all() -> None:
    """Launch all engines."""
    state.ol_logged = state.wb_logged = state.oc_logged = False
    state.browser_launched = False
    state.engine_start_time = time.time()
    mark_all_services_unknown()
    log("Sniper AI Engines initialising ...", "DEBUG")
    try:
        start_ollama()
        start_webui()
        start_openclaw()
        log("Monitoring handshake ...", "WARN")
    except Exception as exc:
        log(f"Startup failed: {exc}", "ERROR")


def nuclear_shutdown() -> None:
    """Force-stop all engines with full cleanup."""
    log("== FORCE SHUTDOWN ==========================", "WARN")

    log("Step 1/4 - Stopping Ollama ...", "INFO")
    kill_proc(state.ollama_proc, "Ollama")
    state.ollama_proc = None

    log("Step 2/4 - Stopping Open-WebUI ...", "INFO")
    kill_proc(state.webui_proc, "Open-WebUI")
    state.webui_proc = None

    log("Step 3/4 - Orphan process sweep ...", "INFO")
    time.sleep(ENGINES["orphan_kill_delay"])
    kill_orphans()

    log("Step 4/4 - Stopping OpenClaw (WSL) ...", "INFO")
    try:
        _wsl_exec(f"{OPENCLAW_PATH} gateway stop")
        log("  OpenClaw gateway stopped.", "SUCCESS")
    except Exception:
        log("  OpenClaw stop skipped (WSL unavailable).", "WARN")

    state.browser_launched = state.ol_logged = state.wb_logged = False
    state.oc_logged = False
    state.engine_start_time = 0.0
    update_service_status(ServiceName.OLLAMA, status=ServiceStatus.OFFLINE, version="--")
    update_service_status(ServiceName.OPEN_WEBUI, status=ServiceStatus.OFFLINE, version="--")
    update_service_status(ServiceName.OPENCLAW, status=ServiceStatus.OFFLINE, version="--")
    log("== Shutdown complete. Console still running. ==", "SUCCESS")


def restart_all() -> None:
    """Shutdown then relaunch all engines."""
    nuclear_shutdown()
    time.sleep(ENGINES["restart_delay"])
    start_all()
