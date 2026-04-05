"""Mapping helpers from legacy runtime structures into domain models."""

from __future__ import annotations

from app.domain.models import ActiveModelInfo, ModelInfo, ProcessInfo, TelemetrySnapshot


AI_PROCESS_NAMES = {"ollama.exe", "python.exe", "open-webui.exe"}


def telemetry_snapshot(
    *,
    cpu_percent: float,
    ram_percent: float,
    gpu_percent: float,
    ram_used_gb: float,
    ram_total_gb: float,
    uptime: str,
) -> TelemetrySnapshot:
    return TelemetrySnapshot(
        cpu_percent=cpu_percent,
        ram_percent=ram_percent,
        gpu_percent=gpu_percent,
        ram_used_gb=ram_used_gb,
        ram_total_gb=ram_total_gb,
        uptime=uptime,
    )


def process_info(name: str, cpu_percent: float, ram_mb: float) -> ProcessInfo:
    return ProcessInfo(
        name=name,
        cpu_percent=cpu_percent,
        ram_mb=ram_mb,
        highlighted=name.lower() in AI_PROCESS_NAMES,
    )


def model_info_from_ollama(model: dict) -> ModelInfo:
    return ModelInfo(
        name=model.get("name", "unknown"),
        size_gb=model.get("size", 0) / (1024 ** 3),
        quantization=model.get("details", {}).get("quantization_level", "?"),
        family=model.get("details", {}).get("family", "?"),
    )


def active_model_info(name: str = "", vram_gb: float = 0.0) -> ActiveModelInfo:
    return ActiveModelInfo(name=name, vram_gb=vram_gb)
