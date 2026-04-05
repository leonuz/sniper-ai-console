"""Runtime coordinator used to reduce the legacy monolithic update loop."""

from __future__ import annotations

from helpers import is_proc_alive, port_open
from config import ENGINES
from app.application.pollers.processes import ProcessPoller
from app.application.pollers.services import ServicePoller
from app.application.pollers.telemetry import TelemetryPoller


class RuntimeCoordinator:
    def __init__(self) -> None:
        self.telemetry = TelemetryPoller()
        self.services = ServicePoller()
        self.processes = ProcessPoller()

    def poll_telemetry(self) -> None:
        payload = self.telemetry.collect()
        self.telemetry.queue_ui_updates(payload)

    def poll_services(self) -> dict:
        ol_on = port_open(ENGINES["ollama_port"])
        wb_on = port_open(ENGINES["webui_port"])
        oc_on = port_open(ENGINES["openclaw_port"])
        status = self.services.collect_status(ol_on=ol_on, wb_on=wb_on, oc_on=oc_on)
        self.services.handle_transitions(status)
        self.services.queue_status_ui(status)
        return status

    def poll_processes(self) -> None:
        self.processes.collect()
        self.processes.queue_ui_updates()
