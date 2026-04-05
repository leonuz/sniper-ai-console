"""Open-WebUI managed service adapter."""

from __future__ import annotations

import time

import state
from config import ENGINES, WEBUI_PATH
from helpers import is_proc_alive, kill_orphans, port_open
from logger import log
from monitoring import fetch_webui_version
from app.adapters.platform.windows import spawn_process
from app.domain.contracts import ServiceHealth
from app.domain.enums import ServiceName, ServiceStatus


class OpenWebUIService:
    name = ServiceName.OPEN_WEBUI
    display_name = "Open-WebUI"

    def start(self) -> None:
        if state.webui_proc is not None and is_proc_alive(state.webui_proc):
            log("Open-WebUI is already running.", "WARN")
            return
        if state.engine_start_time == 0:
            state.engine_start_time = time.time()
        log("Launching Open-WebUI ...", "INFO")
        state.webui_proc = spawn_process([WEBUI_PATH, "serve"])
        log(f"  Open-WebUI PID: {state.webui_proc.pid}", "DEBUG")

    def stop(self) -> None:
        from helpers import kill_proc
        if state.webui_proc is None:
            log("Open-WebUI is not running.", "WARN")
            return
        log("Stopping Open-WebUI ...", "INFO")
        kill_proc(state.webui_proc, "Open-WebUI")
        state.webui_proc = None
        state.wb_logged = False
        time.sleep(ENGINES["orphan_kill_delay"])
        kill_orphans()

    def is_online(self) -> bool:
        online = port_open(ENGINES["webui_port"])
        if not is_proc_alive(state.webui_proc) and state.wb_logged:
            online = False
        return online

    def fetch_version(self) -> str:
        return fetch_webui_version()

    def health(self) -> ServiceHealth:
        online = self.is_online()
        return ServiceHealth(
            name=self.name,
            status=ServiceStatus.ONLINE if online else ServiceStatus.OFFLINE,
            version=self.fetch_version() if online else "--",
            port_open=online,
        )
