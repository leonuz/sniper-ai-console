"""
state.py — Shared mutable state for Sniper AI Console.
All cross-module state lives here to avoid circular imports.

Phase 1 note:
This module remains the active runtime state container for compatibility,
while the new `app.application.store` scaffolding is introduced in parallel.
"""

import subprocess
import threading
from config import UI
from app.application.store import store as app_store

# ─────────────────────────────────────────────
#  SERVICE STATE
# ─────────────────────────────────────────────
browser_launched   = False
ol_logged          = False
wb_logged          = False
oc_logged          = False
engine_start_time  = 0.0
pull_in_progress   = False
update_checked     = False

# Tracked process handles
ollama_proc: subprocess.Popen = None
webui_proc:  subprocess.Popen = None

# ─────────────────────────────────────────────
#  TELEMETRY HISTORY
# ─────────────────────────────────────────────
MAX_DATA = UI["max_data_points"]
history  = {k: [0.0] * MAX_DATA for k in ("cpu", "ram", "gpu")}
x_axis   = list(range(MAX_DATA))

# ─────────────────────────────────────────────
#  PROCESS SNAPSHOT
# ─────────────────────────────────────────────
proc_snapshot: list = []
proc_lock = threading.Lock()

# ─────────────────────────────────────────────
#  MODEL LIST
# ─────────────────────────────────────────────
model_list: list = []

# ─────────────────────────────────────────────
#  CROSS-THREAD UI QUEUE
# ─────────────────────────────────────────────
_ui_queue: list = []
_ui_lock  = threading.Lock()


def queue(fn) -> None:
    """Enqueue a callable to be executed on the main/UI thread."""
    with _ui_lock:
        _ui_queue.append(fn)


def flush_ui_queue() -> None:
    """Execute all queued UI callables. Call from the main thread."""
    with _ui_lock:
        items = list(_ui_queue)
        _ui_queue.clear()
    for fn in items:
        try:
            fn()
        except Exception:
            pass
