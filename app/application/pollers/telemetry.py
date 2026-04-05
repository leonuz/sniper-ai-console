"""Telemetry poller for system metrics and sidebar stats."""

from __future__ import annotations

import psutil

import state
from helpers import get_gpu_val, uptime_str
from app.application.mappers import telemetry_snapshot
from app.application.state_sync import update_telemetry


class TelemetryPoller:
    def collect(self) -> dict:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        gpu = get_gpu_val()
        vm = psutil.virtual_memory()
        ram_used_gb = vm.used / (1024 ** 3)
        ram_total_gb = vm.total / (1024 ** 3)
        uptime = uptime_str()

        update_telemetry(
            telemetry_snapshot(
                cpu_percent=cpu,
                ram_percent=ram,
                gpu_percent=gpu,
                ram_used_gb=ram_used_gb,
                ram_total_gb=ram_total_gb,
                uptime=uptime,
            )
        )

        return {
            "cpu": cpu,
            "ram": ram,
            "gpu": gpu,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "uptime": uptime,
        }

    def queue_ui_updates(self, payload: dict) -> None:
        cpu = payload["cpu"]
        ram = payload["ram"]
        gpu = payload["gpu"]
        uptime = payload["uptime"]
        ram_abs = f"{payload['ram_used_gb']:.1f}/{payload['ram_total_gb']:.1f} GB"

        def _graphs(c=cpu, r=ram, g=gpu):
            for key, val in zip(("cpu", "ram", "gpu"), (c, r, g)):
                state.history[key].append(val)
                state.history[key].pop(0)
                if dpg.does_item_exist(f"{key}_series"):
                    dpg.set_value(f"{key}_series", [state.x_axis, state.history[key]])
                if dpg.does_item_exist(f"{key}_pct"):
                    dpg.configure_item(f"{key}_pct", default_value=f"{val:5.1f}%")

        def _sidebar(u=uptime, ra=ram_abs):
            if dpg.does_item_exist("uptime_val"):
                dpg.configure_item("uptime_val", default_value=u)
            if dpg.does_item_exist("ram_abs"):
                dpg.configure_item("ram_abs", default_value=ra)

        import dearpygui.dearpygui as dpg

        state.queue(_graphs)
        state.queue(_sidebar)
