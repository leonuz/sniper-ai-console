"""
updater.py - Update checker and installer for Open-WebUI.
Compares installed version against PyPI and runs pip upgrade.
"""

import subprocess
import threading
import re

import state
from config import WEBUI_PIP, ENGINES
from logger import log
from helpers import port_open

# ─────────────────────────────────────────────
#  STATE
# ─────────────────────────────────────────────
_update_in_progress = False
_latest_version: str = ""
_installed_version: str = ""
update_available: bool = False


# ─────────────────────────────────────────────
#  VERSION HELPERS
# ─────────────────────────────────────────────
def _get_installed_version() -> str:
    """Get installed open-webui version via pip show."""
    try:
        result = subprocess.run(
            [WEBUI_PIP, "show", "open-webui"],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    except Exception as exc:
        log(f"Could not get installed WebUI version: {exc}", "ERROR")
    return ""


def _get_latest_version() -> str:
    """Get latest open-webui version available on PyPI via pip index."""
    try:
        result = subprocess.run(
            [WEBUI_PIP, "index", "versions", "open-webui"],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        # Output format: "open-webui (X.Y.Z)"  or  "Available versions: X.Y.Z, ..."
        output = result.stdout + result.stderr
        # Try parsing "open-webui (X.Y.Z)" format
        match = re.search(r"open-webui\s*\(([^)]+)\)", output)
        if match:
            return match.group(1).strip()
        # Try parsing "LATEST:" or first version in available list
        match = re.search(r"Available versions?:\s*([^\s,]+)", output)
        if match:
            return match.group(1).strip()
    except Exception as exc:
        log(f"Could not fetch latest WebUI version: {exc}", "ERROR")
    return ""


# ─────────────────────────────────────────────
#  CHECK FOR UPDATES
# ─────────────────────────────────────────────
def check_for_updates() -> None:
    """Compare installed vs latest version. Logs result."""
    global _installed_version, _latest_version, update_available

    log("Checking for Open-WebUI updates ...", "INFO")

    _installed_version = _get_installed_version()
    if not _installed_version:
        log("Could not determine installed version.", "ERROR")
        return

    _latest_version = _get_latest_version()
    if not _latest_version:
        log("Could not determine latest version from PyPI.", "ERROR")
        return

    log(f"  Installed: {_installed_version}  |  Latest: {_latest_version}", "INFO")

    if _installed_version == _latest_version:
        update_available = False
        log("Open-WebUI is up to date.", "SUCCESS")
    else:
        update_available = True
        log(f"Update available: {_installed_version} -> {_latest_version}", "WARN")
        log("Use Help > Update Open-WebUI to install.", "WARN")


def check_for_updates_async() -> None:
    """Run update check in background thread."""
    threading.Thread(target=check_for_updates, daemon=True).start()


# ─────────────────────────────────────────────
#  APPLY UPDATE
# ─────────────────────────────────────────────
def apply_update() -> None:
    """Stop WebUI, run pip upgrade, restart WebUI."""
    global _update_in_progress, update_available

    if _update_in_progress:
        log("Update already in progress.", "WARN")
        return

    if not update_available:
        log("No update available. Run 'Check for Updates' first.", "WARN")
        return

    _update_in_progress = True
    log("== OPEN-WEBUI UPDATE =======================", "WARN")

    try:
        # Step 1: Stop WebUI if running
        wb_port = ENGINES["webui_port"]
        if port_open(wb_port):
            log("Step 1/3 - Stopping Open-WebUI ...", "INFO")
            from engines import stop_webui
            stop_webui()
        else:
            log("Step 1/3 - Open-WebUI already stopped.", "INFO")

        # Step 2: Run pip upgrade
        log("Step 2/3 - Installing update (this may take a minute) ...", "INFO")
        result = subprocess.run(
            [WEBUI_PIP, "install", "--upgrade", "open-webui"],
            capture_output=True, text=True, timeout=600,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        if result.returncode == 0:
            # Extract new version from pip output
            new_ver = _get_installed_version()
            log(f"  Update installed successfully: {new_ver}", "SUCCESS")
            update_available = False
        else:
            err = result.stderr.strip()[-300:] if result.stderr else "unknown error"
            log(f"  pip upgrade failed: {err}", "ERROR")
            return

        # Step 3: Restart WebUI
        log("Step 3/3 - Restarting Open-WebUI ...", "INFO")
        from engines import start_webui
        start_webui()

        log("== Update complete. =======================", "SUCCESS")

    except Exception as exc:
        log(f"Update error: {exc}", "ERROR")
    finally:
        _update_in_progress = False


def apply_update_async() -> None:
    """Run update in background thread."""
    threading.Thread(target=apply_update, daemon=True).start()
