"""Registry for managed services during the refactor transition."""

from app.adapters.ollama.service import OllamaService
from app.adapters.openwebui.service import OpenWebUIService
from app.adapters.openclaw.service import OpenClawService
from app.domain.enums import ServiceName


SERVICES = {
    ServiceName.OLLAMA: OllamaService(),
    ServiceName.OPEN_WEBUI: OpenWebUIService(),
    ServiceName.OPENCLAW: OpenClawService(),
}


def get_service(name: ServiceName):
    return SERVICES[name]
