"""GPU telemetry adapter for the current Windows/PowerShell implementation."""

from __future__ import annotations

import re
import subprocess

from .windows import create_no_window_flag


def read_gpu_percent() -> float:
    """Read GPU utilization via the existing PowerShell performance counter path."""
    try:
        ps_cmd = (
            r"Get-Counter '\GPU Engine(*)\Utilization Percentage'"
            r" -SampleInterval 1 -MaxSamples 1"
            r" | Select-Object -ExpandProperty CounterSamples"
            r" | Select-Object -ExpandProperty CookedValue"
        )
        cmd = ["powershell", "-Command", ps_cmd]
        output = subprocess.check_output(
            cmd,
            creationflags=create_no_window_flag(),
        ).decode()
        values = re.findall(r"(\d+\.?\d*)", output)
        return min(100.0, max(float(v) for v in values)) if values else 0.0
    except Exception:
        return 0.0
