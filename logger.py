"""
logger.py — Logging for Sniper AI Console.
Dual output: DearPyGui visual log + rotating file log.
"""

import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler

import dearpygui.dearpygui as dpg

from config import BASE_DIR, LOGGING

# ─────────────────────────────────────────────
#  PALETTE (log-level colours)
# ─────────────────────────────────────────────
WHITE = (210, 210, 210, 255)

LEVEL_COLOUR = {
    "DEBUG":   (0,   200, 255, 255),
    "INFO":    (180, 180, 180, 255),
    "WARN":    (255, 210,   0, 255),
    "SUCCESS": (0,   220,  90, 255),
    "ERROR":   (255,  60,  60, 255),
    "MODEL":   (180,  80, 255, 255),
}

# ─────────────────────────────────────────────
#  FILE LOGGER  (rotating)
# ─────────────────────────────────────────────
_file_logger = None
_log_lock = threading.Lock()

if LOGGING["log_to_file"]:
    _log_path = os.path.join(BASE_DIR, LOGGING["log_file"])
    _file_logger = logging.getLogger("sniper_ai")
    _file_logger.setLevel(logging.DEBUG)

    _handler = RotatingFileHandler(
        _log_path,
        maxBytes=LOGGING["max_file_size_mb"] * 1024 * 1024,
        backupCount=LOGGING["backup_count"],
        encoding="utf-8",
    )
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-7s] %(message)s",
                                            datefmt="%Y-%m-%d %H:%M:%S"))
    _file_logger.addHandler(_handler)

    # Map custom levels to standard logging levels
    _LEVEL_MAP = {
        "DEBUG":   logging.DEBUG,
        "INFO":    logging.INFO,
        "WARN":    logging.WARNING,
        "SUCCESS": logging.INFO,
        "ERROR":   logging.ERROR,
        "MODEL":   logging.INFO,
    }


# ─────────────────────────────────────────────
#  PUBLIC LOG FUNCTION
# ─────────────────────────────────────────────
def log(msg: str, level: str = "INFO") -> None:
    """
    Log a message to both the visual DearPyGui log and the rotating file log.
    Thread-safe — can be called from any thread.
    """
    t      = time.strftime("%H:%M:%S")
    colour = LEVEL_COLOUR.get(level, WHITE)
    text   = f"[{t}] [{level:<7}] {msg}"

    # File log
    if _file_logger is not None:
        py_level = _LEVEL_MAP.get(level, logging.INFO)
        _file_logger.log(py_level, f"[{level:<7}] {msg}")

    # Visual log (queued for main thread)
    from state import queue
    def _do():
        if dpg.does_item_exist("log_win"):
            with _log_lock:
                dpg.add_text(text, parent="log_win", color=colour)
                dpg.set_y_scroll("log_win", dpg.get_y_scroll_max("log_win"))
    queue(_do)
