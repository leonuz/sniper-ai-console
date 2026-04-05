"""Service definitions and factory helpers for Sniper AI Console."""

from .enums import ServiceKind, ServiceName, ServiceStatus
from .models import ServiceInfo


def default_services() -> list[ServiceInfo]:
    """Return the default managed services for the application."""
    return [
        ServiceInfo(
            name=ServiceName.OLLAMA,
            display_name="Ollama",
            kind=ServiceKind.PROCESS,
            port=11434,
            status=ServiceStatus.UNKNOWN,
        ),
        ServiceInfo(
            name=ServiceName.OPEN_WEBUI,
            display_name="Open-WebUI",
            kind=ServiceKind.PROCESS,
            port=8080,
            status=ServiceStatus.UNKNOWN,
        ),
        ServiceInfo(
            name=ServiceName.OPENCLAW,
            display_name="OpenClaw",
            kind=ServiceKind.WSL_GATEWAY,
            port=18789,
            status=ServiceStatus.UNKNOWN,
        ),
    ]
