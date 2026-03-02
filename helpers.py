"""
helpers.py — Utility functions for Sniper AI Console.
Port checking, process killing, uptime, colour helpers, GPU reading.
"""

import os
import re
import socket
import subprocess
import time

import psutil

import state
from config import ENGINES
from logger import log

# ─────────────────────────────────────────────
#  OPTIONAL IMPORTS
# ─────────────────────────────────────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from PIL import Image
    import pystray
    from pystray import MenuItem as item
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ─────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────
CYAN   = (0,   255, 255, 255)
GREEN  = (0,   220,  90, 255)
YELLOW = (255, 215,   0, 255)
RED    = (255,  55,  55, 255)
DIM    = (110, 110, 110, 255)
WHITE  = (210, 210, 210, 255)
PURPLE = (200,  80, 255, 255)

CYAN_RGB  = (0,   255, 255)
GREEN_RGB = (0,   220,  90)
RED_RGB   = (255,  55,  55)

# ─────────────────────────────────────────────
#  NETWORK
# ─────────────────────────────────────────────
def port_open(port: int) -> bool:
    """Check if a TCP port is accepting connections on localhost."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    ok = s.connect_ex(("127.0.0.1", port)) == 0
    s.close()
    return ok


# ─────────────────────────────────────────────
#  PROCESS MANAGEMENT
# ─────────────────────────────────────────────
def kill_proc(proc: subprocess.Popen, label: str) -> None:
    """Kill a tracked Popen and its ENTIRE child process tree."""
    if proc is None:
        log(f"  {label}: no tracked PID, skipping.", "WARN")
        return
    try:
        pid = proc.pid
        # Check if process is still alive before attempting kill
        if proc.poll() is not None:
            log(f"  {label} (PID {pid}) already stopped.", "INFO")
            return
        log(f"  Killing {label} (PID {pid}) + process tree ...", "INFO")
        result = subprocess.run(
            f"taskkill /F /T /PID {pid}",
            shell=True, capture_output=True, text=True,
        )
        if result.returncode == 0:
            log(f"  {label} (PID {pid}) terminated.", "SUCCESS")
        else:
            msg = result.stderr.strip() or result.stdout.strip() or "already stopped"
            log(f"  {label} (PID {pid}) already stopped.", "INFO")
    except Exception as exc:
        log(f"  Error killing {label}: {exc}", "ERROR")


def kill_orphans() -> None:
    """Sweep for any remaining WebUI-related processes."""
    keywords = ("open-webui", "uvicorn", "open_webui")
    killed = []
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(p.info["cmdline"] or []).lower()
            if any(k in cmdline for k in keywords):
                if p.pid == os.getpid():
                    continue
                p.kill()
                killed.append(f"{p.info['name']}({p.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if killed:
        log(f"  Orphan sweep terminated: {', '.join(killed)}", "SUCCESS")
    else:
        log("  Orphan sweep: no residual WebUI workers found.", "INFO")


def is_proc_alive(proc: subprocess.Popen) -> bool:
    """Check if a tracked subprocess is still running."""
    if proc is None:
        return False
    return proc.poll() is None


# ─────────────────────────────────────────────
#  DISPLAY HELPERS
# ─────────────────────────────────────────────
def uptime_str() -> str:
    """Return formatted uptime string HH:MM:SS."""
    if state.engine_start_time == 0:
        return "--:--:--"
    secs   = int(time.time() - state.engine_start_time)
    h, rem = divmod(secs, 3600)
    m, s   = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def heat_colour(val: float):
    """Return a colour tuple based on a percentage value."""
    if val > 70: return RED
    if val > 40: return YELLOW
    return GREEN


# ─────────────────────────────────────────────
#  GPU READING
# ─────────────────────────────────────────────
def get_gpu_val() -> float:
    """Read GPU utilisation via PowerShell performance counter."""
    try:
        ps_cmd = (
            r"Get-Counter '\GPU Engine(*)\Utilization Percentage'"
            r" -SampleInterval 1 -MaxSamples 1"
            r" | Select-Object -ExpandProperty CounterSamples"
            r" | Select-Object -ExpandProperty CookedValue"
        )
        cmd = ["powershell", "-Command", ps_cmd]
        output = subprocess.check_output(cmd, creationflags=subprocess.CREATE_NO_WINDOW).decode()
        values = re.findall(r"(\d+\.?\d*)", output)
        return min(100.0, max(float(v) for v in values)) if values else 0.0
    except Exception:
        return 0.0
