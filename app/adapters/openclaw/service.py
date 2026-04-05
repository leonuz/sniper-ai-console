"""OpenClaw managed service adapter."""

from __future__ import annotations

import state
from config import ENGINES, OPENCLAW_PATH
from helpers import port_open
from logger import log
from app.adapters.platform.wsl import run_wsl_bash
from app.domain.contracts import ServiceHealth
from app.domain.enums import ServiceName, ServiceStatus


class OpenClawService:
    name = ServiceName.OPENCLAW
    display_name = "OpenClaw"

    def _exec(self, cmd: str):
        return run_wsl_bash(cmd, timeout=30)

    def start(self) -> None:
        if port_open(ENGINES["openclaw_port"]):
            log("OpenClaw is already running.", "WARN")
            return
        log("Launching OpenClaw gateway (WSL) ...", "INFO")
        try:
            result = self._exec(f"{OPENCLAW_PATH} gateway start")
            output = (result.stdout + result.stderr).strip()
            if result.returncode == 0:
                log("OpenClaw gateway start command sent.", "SUCCESS")
            else:
                log(f"OpenClaw start issue: {output[:200]}", "WARN")
        except Exception as exc:
            log(f"OpenClaw start error: {exc}", "ERROR")

    def stop(self) -> None:
        if not port_open(ENGINES["openclaw_port"]):
            log("OpenClaw is not running.", "WARN")
            return
        log("Stopping OpenClaw gateway (WSL) ...", "INFO")
        try:
            result = self._exec(f"{OPENCLAW_PATH} gateway stop")
            output = (result.stdout + result.stderr).strip()
            if result.returncode == 0:
                log("OpenClaw gateway stopped.", "SUCCESS")
            else:
                log(f"OpenClaw stop issue: {output[:200]}", "WARN")
            state.oc_logged = False
        except Exception as exc:
            log(f"OpenClaw stop error: {exc}", "ERROR")

    def is_online(self) -> bool:
        return port_open(ENGINES["openclaw_port"])

    def fetch_version(self) -> str:
        try:
            result = self._exec(f"{OPENCLAW_PATH} --version 2>/dev/null || echo unknown")
            ver = result.stdout.strip()
            if ver and ver != "unknown":
                parts = ver.split()
                for part in parts:
                    if any(c.isdigit() for c in part) and "." in part:
                        return part
                return ver[:30]
            return "unknown"
        except Exception:
            return "offline"

    def health(self) -> ServiceHealth:
        online = self.is_online()
        return ServiceHealth(
            name=self.name,
            status=ServiceStatus.ONLINE if online else ServiceStatus.OFFLINE,
            version=self.fetch_version() if online else "--",
            port_open=online,
        )
