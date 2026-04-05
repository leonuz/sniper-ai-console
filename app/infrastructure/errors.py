"""Shared error helpers for safer runtime diagnostics."""

from __future__ import annotations

import traceback

from app.infrastructure.logging_runtime import log


def log_exception(context: str, exc: Exception) -> None:
    """Log an exception with traceback for easier diagnosis."""
    log(f"{context}: {exc}", "ERROR")
    tb = traceback.format_exc().strip()
    if tb:
        for line in tb.splitlines()[-8:]:
            log(line, "DEBUG")
