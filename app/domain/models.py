"""Domain dataclasses for Sniper AI Console."""

from dataclasses import dataclass, field
from typing import List, Optional

from .enums import ServiceKind, ServiceName, ServiceStatus


@dataclass(slots=True)
class ServiceInfo:
    name: ServiceName
    display_name: str
    kind: ServiceKind
    port: Optional[int] = None
    version: str = "--"
    status: ServiceStatus = ServiceStatus.UNKNOWN


@dataclass(slots=True)
class TelemetrySnapshot:
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    gpu_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    uptime: str = "--:--:--"


@dataclass(slots=True)
class ProcessInfo:
    name: str
    cpu_percent: float
    ram_mb: float
    highlighted: bool = False


@dataclass(slots=True)
class ModelInfo:
    name: str
    size_gb: float = 0.0
    quantization: str = "?"
    family: str = "?"


@dataclass(slots=True)
class ActiveModelInfo:
    name: str = ""
    vram_gb: float = 0.0


@dataclass(slots=True)
class AppStateSnapshot:
    services: List[ServiceInfo] = field(default_factory=list)
    telemetry: TelemetrySnapshot = field(default_factory=TelemetrySnapshot)
    processes: List[ProcessInfo] = field(default_factory=list)
    models: List[ModelInfo] = field(default_factory=list)
    active_model: ActiveModelInfo = field(default_factory=ActiveModelInfo)
