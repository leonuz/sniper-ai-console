"""Typed config accessors layered on top of the existing config module.

Phase 1 note:
This module does not replace the existing config.py yet.
It provides a forward-compatible boundary that later modules can depend on
without forcing a full runtime migration today.
"""

from dataclasses import dataclass

import config as legacy_config


@dataclass(slots=True)
class RuntimePaths:
    ollama: str
    webui: str
    openclaw: str


@dataclass(slots=True)
class RuntimePorts:
    ollama: int
    webui: int
    openclaw: int


@dataclass(slots=True)
class RuntimeConfig:
    app_name: str
    app_version: str
    paths: RuntimePaths
    ports: RuntimePorts
    portal_url: str
    openclaw_dashboard: str
    browser_command: str


def load_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        app_name=legacy_config.APP_NAME,
        app_version=legacy_config.APP_VERSION,
        paths=RuntimePaths(
            ollama=legacy_config.OLLAMA_PATH,
            webui=legacy_config.WEBUI_PATH,
            openclaw=legacy_config.OPENCLAW_PATH,
        ),
        ports=RuntimePorts(
            ollama=legacy_config.ENGINES["ollama_port"],
            webui=legacy_config.ENGINES["webui_port"],
            openclaw=legacy_config.ENGINES["openclaw_port"],
        ),
        portal_url=legacy_config.PORTAL_URL,
        openclaw_dashboard=legacy_config.OPENCLAW_DASHBOARD,
        browser_command=legacy_config.ENGINES["browser_command"],
    )
