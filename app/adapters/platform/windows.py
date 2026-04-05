"""Windows platform process helpers."""

from __future__ import annotations

import os
import subprocess


def create_no_window_flag() -> int:
    """Return the Windows no-window creation flag when available."""
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def taskkill_process_tree(pid: int) -> subprocess.CompletedProcess:
    """Kill a process tree using taskkill."""
    return subprocess.run(
        f"taskkill /F /T /PID {pid}",
        shell=True,
        capture_output=True,
        text=True,
    )


def spawn_process(command: list[str], env: dict | None = None) -> subprocess.Popen:
    """Spawn a Windows process with the preferred flags for this project."""
    return subprocess.Popen(
        command,
        creationflags=create_no_window_flag(),
        env=env,
    )


def kill_pid(pid: int) -> bool:
    """Kill a PID directly through psutil/os fallback if needed."""
    try:
        os.kill(pid, 9)
        return True
    except Exception:
        return False
