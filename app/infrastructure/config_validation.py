"""Basic runtime config validation for the migration period."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.infrastructure.config_runtime import RuntimeConfig


@dataclass(slots=True)
class ValidationResult:
    ok: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def validate_runtime_config(cfg: RuntimeConfig) -> ValidationResult:
    result = ValidationResult()

    if not cfg.app_name:
        result.ok = False
        result.errors.append("app_name is empty")

    if not cfg.app_version:
        result.warnings.append("app_version is empty")

    if not cfg.paths.ollama:
        result.ok = False
        result.errors.append("paths.ollama is empty")
    if not cfg.paths.webui:
        result.ok = False
        result.errors.append("paths.webui is empty")
    if not cfg.paths.openclaw:
        result.ok = False
        result.errors.append("paths.openclaw is empty")

    for label, port in {
        "ollama": cfg.ports.ollama,
        "webui": cfg.ports.webui,
        "openclaw": cfg.ports.openclaw,
    }.items():
        if not isinstance(port, int) or port <= 0 or port > 65535:
            result.ok = False
            result.errors.append(f"invalid port for {label}: {port}")

    if not cfg.browser_command:
        result.warnings.append("browser_command is empty")

    if not cfg.portal_url:
        result.warnings.append("portal_url is empty")

    return result
