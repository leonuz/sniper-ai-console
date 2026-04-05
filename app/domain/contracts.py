"""Domain service contracts for managed engines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .enums import ServiceName, ServiceStatus


@dataclass(slots=True)
class ServiceHealth:
    name: ServiceName
    status: ServiceStatus
    version: str = "--"
    port_open: bool = False


class ManagedService(Protocol):
    name: ServiceName
    display_name: str

    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...

    def is_online(self) -> bool:
        ...

    def fetch_version(self) -> str:
        ...

    def health(self) -> ServiceHealth:
        ...
