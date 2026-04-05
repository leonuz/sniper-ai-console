"""
engines.py - Start / stop / toggle logic for Ollama, Open-WebUI, and OpenClaw.
"""

import os
import subprocess
import threading
import time

import state
from config import OLLAMA_PATH, WEBUI_PATH, OPENCLAW_PATH, ENGINES
from logger import log
from helpers import kill_proc, kill_orphans, port_open, is_proc_alive
from app.adapters.platform.windows import spawn_process
from app.adapters.platform.wsl import run_wsl_bash


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
    state.ollama_proc = spawn_process(
        [OLLAMA_PATH, "serve"],
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
    state.webui_proc = spawn_process(
        [WEBUI_PATH, "serve"],
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
#  OPENCLAW (WSL) SERVICE CONTROL
# ─────────────────────────────────────────────
def _wsl_exec(cmd: str) -> subprocess.CompletedProcess:
    """Execute a command inside WSL and return the result."""
    return run_wsl_bash(cmd, timeout=30)


def start_openclaw() -> None:
    """Start OpenClaw gateway via WSL systemd."""
    if port_open(ENGINES["openclaw_port"]):
        log("OpenClaw is already running.", "WARN")
        return
    log("Launching OpenClaw gateway (WSL) ...", "INFO")
    try:
        result = _wsl_exec(f"{OPENCLAW_PATH} gateway start")
        output = (result.stdout + result.stderr).strip()
        if result.returncode == 0:
            log("OpenClaw gateway start command sent.", "SUCCESS")
        else:
            log(f"OpenClaw start issue: {output[:200]}", "WARN")
    except Exception as exc:
        log(f"OpenClaw start error: {exc}", "ERROR")


def stop_openclaw() -> None:
    """Stop OpenClaw gateway via WSL systemd."""
    if not port_open(ENGINES["openclaw_port"]):
        log("OpenClaw is not running.", "WARN")
        return
    log("Stopping OpenClaw gateway (WSL) ...", "INFO")
    try:
        result = _wsl_exec(f"{OPENCLAW_PATH} gateway stop")
        output = (result.stdout + result.stderr).strip()
        if result.returncode == 0:
            log("OpenClaw gateway stopped.", "SUCCESS")
        else:
            log(f"OpenClaw stop issue: {output[:200]}", "WARN")
        state.oc_logged = False
    except Exception as exc:
        log(f"OpenClaw stop error: {exc}", "ERROR")


def toggle_openclaw() -> None:
    """Toggle OpenClaw on/off based on current port status."""
    if port_open(ENGINES["openclaw_port"]):
        threading.Thread(target=stop_openclaw, daemon=True).start()
    else:
        threading.Thread(target=start_openclaw, daemon=True).start()


def fetch_openclaw_version() -> str:
    """Get OpenClaw version from WSL."""
    try:
        result = _wsl_exec(f"{OPENCLAW_PATH} --version 2>/dev/null || echo unknown")
        ver = result.stdout.strip()
        # Parse version from output like "OpenClaw 2026.2.26 (bc50708)"
        if ver and ver != "unknown":
            parts = ver.split()
            for p in parts:
                if any(c.isdigit() for c in p) and "." in p:
                    return p
            return ver[:30]
        return "unknown"
    except Exception:
        return "offline"


# ─────────────────────────────────────────────
#  BULK OPERATIONS
# ─────────────────────────────────────────────
def start_all() -> None:
    """Launch all engines."""
    state.ol_logged = state.wb_logged = state.oc_logged = False
    state.browser_launched = False
    state.engine_start_time = time.time()
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
    log("== Shutdown complete. Console still running. ==", "SUCCESS")


def restart_all() -> None:
    """Shutdown then relaunch all engines."""
    nuclear_shutdown()
    time.sleep(ENGINES["restart_delay"])
    start_all()
