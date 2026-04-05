"""Helpers to synchronize the legacy runtime state into the new AppStore."""

from __future__ import annotations

from app.application.store import store
from app.domain.enums import ServiceName, ServiceStatus
from app.domain.models import ActiveModelInfo, ModelInfo, ProcessInfo, TelemetrySnapshot


def update_service_status(
    name: ServiceName,
    *,
    status: ServiceStatus,
    version: str | None = None,
) -> None:
    snapshot = store.get_snapshot()
    for service in snapshot.services:
        if service.name == name:
            service.status = status
            if version is not None:
                service.version = version
            break
    store.replace(snapshot)


def update_telemetry(snapshot_data: TelemetrySnapshot) -> None:
    snapshot = store.get_snapshot()
    snapshot.telemetry = snapshot_data
    store.replace(snapshot)


def update_processes(processes: list[ProcessInfo]) -> None:
    snapshot = store.get_snapshot()
    snapshot.processes = processes
    store.replace(snapshot)


def update_models(models: list[ModelInfo]) -> None:
    snapshot = store.get_snapshot()
    snapshot.models = models
    store.replace(snapshot)


def update_active_model(active_model: ActiveModelInfo) -> None:
    snapshot = store.get_snapshot()
    snapshot.active_model = active_model
    store.replace(snapshot)


def mark_all_services_unknown() -> None:
    snapshot = store.get_snapshot()
    for service in snapshot.services:
        service.status = ServiceStatus.UNKNOWN
        service.version = "--"
    store.replace(snapshot)
