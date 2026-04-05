"""WSL command adapter."""

from __future__ import annotations

import subprocess

from .windows import create_no_window_flag


def run_wsl_bash(command: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a bash command inside WSL and capture the result."""
    return subprocess.run(
        ["wsl", "-e", "bash", "-lc", command],
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=create_no_window_flag(),
    )
