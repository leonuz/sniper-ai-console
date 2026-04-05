"""Startup diagnostics for the migration-period runtime."""

from __future__ import annotations

from app.infrastructure.config_runtime import load_runtime_config
from app.infrastructure.config_validation import validate_runtime_config
from app.infrastructure.logging_runtime import log


def run_startup_checks() -> None:
    cfg = load_runtime_config()
    result = validate_runtime_config(cfg)

    if result.errors:
        for item in result.errors:
            log(f"Config error: {item}", "ERROR")
    if result.warnings:
        for item in result.warnings:
            log(f"Config warning: {item}", "WARN")

    if result.ok:
        log("Runtime config validation passed.", "DEBUG")
    else:
        log("Runtime config validation found blocking issues.", "ERROR")
