"""Service health polling and UI synchronization."""

from __future__ import annotations

import threading

import dearpygui.dearpygui as dpg

import state
from logger import log
from monitoring import fetch_ollama_version, fetch_webui_version
from engines import fetch_openclaw_version
from helpers import GREEN, RED, GREEN_RGB, RED_RGB, is_proc_alive
from app.application.state_sync import update_service_status
from app.domain.enums import ServiceName, ServiceStatus


class ServicePoller:
    def collect_status(self, *, ol_on: bool, wb_on: bool, oc_on: bool) -> dict:
        return {
            "ollama": ol_on,
            "webui": wb_on,
            "openclaw": oc_on,
        }

    def handle_transitions(self, status: dict) -> None:
        ol_on = status["ollama"]
        wb_on = status["webui"]
        oc_on = status["openclaw"]

        if ol_on and not state.ol_logged:
            log("Ollama service online.", "SUCCESS")
            state.ol_logged = True
            ov = fetch_ollama_version()
            update_service_status(ServiceName.OLLAMA, status=ServiceStatus.ONLINE, version=ov)

            def _set_ol_ver(v=ov):
                if dpg.does_item_exist("ol_ver"):
                    dpg.configure_item("ol_ver", default_value=v)

            state.queue(_set_ol_ver)

        if wb_on and not state.wb_logged:
            log("Open-WebUI service online.", "SUCCESS")
            state.wb_logged = True
            wv = fetch_webui_version()
            update_service_status(ServiceName.OPEN_WEBUI, status=ServiceStatus.ONLINE, version=wv)

            def _set_wb_ver(v=wv):
                if dpg.does_item_exist("wb_ver"):
                    dpg.configure_item("wb_ver", default_value=v)

            state.queue(_set_wb_ver)

        if not ol_on and state.ol_logged:
            if state.ollama_proc is not None and not is_proc_alive(state.ollama_proc):
                log("Ollama process crashed or was killed externally.", "ERROR")
                state.ollama_proc = None
            state.ol_logged = False
            update_service_status(ServiceName.OLLAMA, status=ServiceStatus.OFFLINE, version="--")

        if not wb_on and state.wb_logged:
            if state.webui_proc is not None and not is_proc_alive(state.webui_proc):
                log("Open-WebUI process crashed or was killed externally.", "ERROR")
                state.webui_proc = None
            state.wb_logged = False
            update_service_status(ServiceName.OPEN_WEBUI, status=ServiceStatus.OFFLINE, version="--")

        if oc_on and not state.oc_logged:
            log("OpenClaw gateway online.", "SUCCESS")
            state.oc_logged = True

            def _fetch_oc_ver():
                ocv = fetch_openclaw_version()
                update_service_status(ServiceName.OPENCLAW, status=ServiceStatus.ONLINE, version=ocv)

                def _set(v=ocv):
                    if dpg.does_item_exist("oc_ver"):
                        dpg.configure_item("oc_ver", default_value=v)

                state.queue(_set)

            threading.Thread(target=_fetch_oc_ver, daemon=True).start()

        if not oc_on and state.oc_logged:
            log("OpenClaw gateway went offline.", "WARN")
            state.oc_logged = False
            update_service_status(ServiceName.OPENCLAW, status=ServiceStatus.OFFLINE, version="--")

    def queue_status_ui(self, status: dict) -> None:
        ol_on = status["ollama"]
        wb_on = status["webui"]
        oc_on = status["openclaw"]

        def _lights(oo=ol_on, wo=wb_on, co=oc_on):
            if dpg.does_item_exist("ol_light"):
                dpg.configure_item("ol_light", fill=GREEN_RGB if oo else RED_RGB)
            if dpg.does_item_exist("wb_light"):
                dpg.configure_item("wb_light", fill=GREEN_RGB if wo else RED_RGB)
            if dpg.does_item_exist("oc_light"):
                dpg.configure_item("oc_light", fill=GREEN_RGB if co else RED_RGB)
            if dpg.does_item_exist("ol_status"):
                dpg.configure_item("ol_status", default_value="ONLINE" if oo else "OFFLINE", color=GREEN if oo else RED)
            if dpg.does_item_exist("wb_status"):
                dpg.configure_item("wb_status", default_value="ONLINE" if wo else "OFFLINE", color=GREEN if wo else RED)
            if dpg.does_item_exist("oc_status"):
                dpg.configure_item("oc_status", default_value="ONLINE" if co else "OFFLINE", color=GREEN if co else RED)
            if dpg.does_item_exist("ol_toggle"):
                dpg.configure_item("ol_toggle", label="STOP" if oo else "START")
                dpg.bind_item_theme("ol_toggle", "theme_btn_on" if oo else "theme_btn_off")
            if dpg.does_item_exist("wb_toggle"):
                dpg.configure_item("wb_toggle", label="STOP" if wo else "START")
                dpg.bind_item_theme("wb_toggle", "theme_btn_on" if wo else "theme_btn_off")
            if dpg.does_item_exist("oc_toggle"):
                dpg.configure_item("oc_toggle", label="STOP" if co else "START")
                dpg.bind_item_theme("oc_toggle", "theme_btn_on" if co else "theme_btn_off")
            if not oo and dpg.does_item_exist("ol_ver"):
                dpg.configure_item("ol_ver", default_value="--")
            if not wo and dpg.does_item_exist("wb_ver"):
                dpg.configure_item("wb_ver", default_value="--")
            if not co and dpg.does_item_exist("oc_ver"):
                dpg.configure_item("oc_ver", default_value="--")

        state.queue(_lights)
