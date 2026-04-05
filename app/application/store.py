"""Lightweight application state store for the next architecture stage."""

from __future__ import annotations

from copy import deepcopy
from threading import Lock

from app.domain.models import AppStateSnapshot
from app.domain.services import default_services


class AppStore:
    """Thread-safe holder for application state snapshots."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._state = AppStateSnapshot(services=default_services())

    def get_snapshot(self) -> AppStateSnapshot:
        with self._lock:
            return deepcopy(self._state)

    def replace(self, new_state: AppStateSnapshot) -> None:
        with self._lock:
            self._state = new_state


store = AppStore()
