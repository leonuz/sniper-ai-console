"""Ollama managed service adapter."""

from __future__ import annotations

import os
import time

import state
from config import ENGINES, OLLAMA_PATH
from helpers import is_proc_alive, port_open
from logger import log
from monitoring import fetch_ollama_version
from app.adapters.platform.windows import spawn_process
from app.domain.contracts import ServiceHealth
from app.domain.enums import ServiceName, ServiceStatus


class OllamaService:
    name = ServiceName.OLLAMA
    display_name = "Ollama"

    def start(self) -> None:
        if state.ollama_proc is not None and is_proc_alive(state.ollama_proc):
            log("Ollama is already running.", "WARN")
            return
        if state.engine_start_time == 0:
            state.engine_start_time = time.time()
        host = ENGINES["ollama_host"]
        log(f"Launching Ollama (listening on {host}) ...", "INFO")
        ol_env = os.environ.copy()
        ol_env["OLLAMA_HOST"] = host
        state.ollama_proc = spawn_process([OLLAMA_PATH, "serve"], env=ol_env)
        log(f"  Ollama PID: {state.ollama_proc.pid}", "DEBUG")

    def stop(self) -> None:
        from helpers import kill_proc
        if state.ollama_proc is None:
            log("Ollama is not running.", "WARN")
            return
        log("Stopping Ollama ...", "INFO")
        kill_proc(state.ollama_proc, "Ollama")
        state.ollama_proc = None
        state.ol_logged = False

    def is_online(self) -> bool:
        online = port_open(ENGINES["ollama_port"])
        if not is_proc_alive(state.ollama_proc) and state.ol_logged:
            online = False
        return online

    def fetch_version(self) -> str:
        return fetch_ollama_version()

    def health(self) -> ServiceHealth:
        online = self.is_online()
        return ServiceHealth(
            name=self.name,
            status=ServiceStatus.ONLINE if online else ServiceStatus.OFFLINE,
            version=self.fetch_version() if online else "--",
            port_open=online,
        )
