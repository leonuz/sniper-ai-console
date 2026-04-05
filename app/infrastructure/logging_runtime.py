"""Forward-compatible logging bridge for the new package structure.

Phase 1 keeps the existing logger implementation as the source of truth.
This module gives future code a stable import path while the old runtime
continues to work unchanged.
"""

from logger import log

__all__ = ["log"]
