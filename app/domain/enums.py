"""Domain enums for Sniper AI Console."""

from enum import Enum


class ServiceName(str, Enum):
    OLLAMA = "ollama"
    OPEN_WEBUI = "open-webui"
    OPENCLAW = "openclaw"


class ServiceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ServiceKind(str, Enum):
    PROCESS = "process"
    WSL_GATEWAY = "wsl_gateway"
    HTTP = "http"
    HYBRID = "hybrid"


class UpdateChannel(str, Enum):
    STABLE = "stable"
    UNKNOWN = "unknown"
