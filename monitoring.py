"""
monitoring.py — System telemetry and model management for Sniper AI Console.
"""

import json
import threading

import dearpygui.dearpygui as dpg
import psutil

import state
from config import OLLAMA_API, UI
from logger import log
from helpers import (
    HAS_REQUESTS, CYAN, YELLOW, WHITE, DIM, GREEN, RED,
    heat_colour,
)
from app.application.mappers import active_model_info, model_info_from_ollama, process_info
from app.application.state_sync import update_active_model, update_models, update_processes

if HAS_REQUESTS:
    import requests

# ─────────────────────────────────────────────
#  KNOWN AI PROCESSES
# ─────────────────────────────────────────────
AI_PROCS = {"ollama.exe", "python.exe", "open-webui.exe"}


# ─────────────────────────────────────────────
#  OLLAMA API
# ─────────────────────────────────────────────
def api_get(path: str):
    """GET request to the Ollama API, returns parsed JSON or None."""
    if not HAS_REQUESTS:
        log("'requests' package not installed.", "ERROR")
        return None
    try:
        r = requests.get(f"{OLLAMA_API}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.ConnectionError:
        # Service is offline — not an error, just unavailable
        return None
    except Exception as exc:
        log(f"Ollama API error: {exc}", "ERROR")
        return None


def fetch_ollama_version() -> str:
    try:
        data = api_get("/api/version")
        return data.get("version", "unknown") if data else "offline"
    except Exception:
        return "offline"


def fetch_webui_version() -> str:
    if not HAS_REQUESTS:
        return "n/a"
    try:
        r = requests.get("http://127.0.0.1:8080/api/version", timeout=3)
        r.raise_for_status()
        data = r.json()
        return data.get("version", data.get("app_version", "unknown"))
    except Exception:
        return "offline"


# ─────────────────────────────────────────────
#  MODEL MANAGEMENT
# ─────────────────────────────────────────────
def refresh_models() -> None:
    """Fetch model list from Ollama and update the UI table."""
    from helpers import port_open
    from config import ENGINES
    if not port_open(ENGINES["ollama_port"]):
        log("Ollama is offline. Cannot refresh models.", "WARN")
        return
    data = api_get("/api/tags")
    if data is None:
        return
    state.model_list = data.get("models", [])
    update_models([model_info_from_ollama(m) for m in state.model_list])
    log(f"Model list refreshed -- {len(state.model_list)} model(s).", "MODEL")
    state.queue(rebuild_model_table)
    refresh_active_model()


def rebuild_model_table() -> None:
    """Rebuild the Models tab table and model selector from state.model_list."""
    if not dpg.does_item_exist("model_table"):
        return
    for c in (dpg.get_item_children("model_table", slot=1) or []):
        dpg.delete_item(c)
    names = []
    for m in state.model_list:
        name  = m.get("name", "unknown")
        size  = m.get("size", 0) / (1024 ** 3)
        quant = m.get("details", {}).get("quantization_level", "?")
        fam   = m.get("details", {}).get("family", "?")
        names.append(name)
        with dpg.table_row(parent="model_table"):
            dpg.add_text(name,             color=CYAN)
            dpg.add_text(f"{size:.2f} GB", color=WHITE)
            dpg.add_text(quant,            color=YELLOW)
            dpg.add_text(fam,              color=DIM)
            dpg.add_button(label="DELETE", small=True,
                           user_data=name, callback=_delete_model_cb)
    # Update model selector combo
    if dpg.does_item_exist("model_combo"):
        dpg.configure_item("model_combo", items=names)
        if names and not dpg.get_value("model_combo"):
            dpg.set_value("model_combo", names[0])


def _delete_model_cb(sender, app_data, user_data: str) -> None:
    """Show confirmation dialog before deleting a model."""
    name = user_data
    dialog_tag = "delete_confirm_dlg"

    # Remove existing dialog if any
    if dpg.does_item_exist(dialog_tag):
        dpg.delete_item(dialog_tag)

    def _confirm():
        dpg.delete_item(dialog_tag)
        log(f"Deleting '{name}' ...", "WARN")
        def _do():
            try:
                r = requests.delete(f"{OLLAMA_API}/api/delete",
                                    json={"name": name}, timeout=15)
                if r.status_code == 200:
                    log(f"'{name}' deleted.", "SUCCESS")
                else:
                    log(f"Delete failed ({r.status_code}).", "ERROR")
            except Exception as exc:
                log(f"Delete error: {exc}", "ERROR")
            refresh_models()
        threading.Thread(target=_do, daemon=True).start()

    def _cancel():
        dpg.delete_item(dialog_tag)
        log(f"Delete '{name}' cancelled.", "INFO")

    with dpg.window(label="Confirm Delete", tag=dialog_tag,
                    modal=True, no_resize=True, no_move=False,
                    width=420, height=130):
        dpg.add_spacer(height=8)
        dpg.add_text(f"  Are you sure you want to delete '{name}'?",
                     color=(255, 210, 0, 255))
        dpg.add_text("  This action cannot be undone.",
                     color=(180, 180, 180, 255))
        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=120)
            dpg.add_button(label="  YES, DELETE  ", callback=lambda: _confirm())
            dpg.add_spacer(width=20)
            dpg.add_button(label="  CANCEL  ", callback=lambda: _cancel())


# ─────────────────────────────────────────────
#  VRAM / ACTIVE MODEL MANAGEMENT
# ─────────────────────────────────────────────
def refresh_active_model() -> None:
    """Fetch running models from /api/ps and update the UI."""
    data = api_get("/api/ps")
    if data is None:
        update_active_model(active_model_info())
        state.queue(lambda: _update_active_display("", 0.0))
        return
    models = data.get("models", [])
    if models:
        m = models[0]
        name = m.get("name", "unknown")
        # Try multiple fields for VRAM size
        vram_bytes = (m.get("size_vram", 0)
                      or m.get("size", 0)
                      or m.get("vram", 0))
        vram_gb = vram_bytes / (1024 ** 3) if vram_bytes else 0.0
        log(f"Active model: {name} | VRAM: {vram_gb:.2f} GB", "DEBUG")
        update_active_model(active_model_info(name, vram_gb))
        state.queue(lambda n=name, v=vram_gb: _update_active_display(n, v))
    else:
        update_active_model(active_model_info())
        state.queue(lambda: _update_active_display("", 0.0))


def _update_active_display(name: str, vram_gb: float = 0.0) -> None:
    """Update active model labels on the UI thread."""
    if dpg.does_item_exist("active_model_name"):
        if name:
            dpg.configure_item("active_model_name",
                               default_value=name, color=GREEN)
        else:
            dpg.configure_item("active_model_name",
                               default_value="(none loaded)", color=DIM)
    if dpg.does_item_exist("active_model_vram"):
        if name:
            dpg.configure_item("active_model_vram",
                               default_value=f"  VRAM: {vram_gb:.2f} GB", color=CYAN)
        else:
            dpg.configure_item("active_model_vram",
                               default_value="", color=DIM)


def load_model_callback() -> None:
    """Load the selected model into VRAM."""
    if not dpg.does_item_exist("model_combo"):
        return
    name = dpg.get_value("model_combo")
    if not name:
        log("Select a model first.", "WARN")
        return
    log(f"Loading '{name}' into VRAM ...", "MODEL")

    def _do():
        try:
            r = requests.post(
                f"{OLLAMA_API}/api/generate",
                json={"model": name, "prompt": "", "keep_alive": -1},
                timeout=120,
            )
            if r.status_code == 200:
                log(f"'{name}' loaded into VRAM.", "SUCCESS")
            else:
                log(f"Load failed ({r.status_code}).", "ERROR")
        except Exception as exc:
            log(f"Load error: {exc}", "ERROR")
        refresh_active_model()

    threading.Thread(target=_do, daemon=True).start()


def unload_model_callback() -> None:
    """Unload the current model from VRAM."""
    # Get the active model name from the UI label
    if not dpg.does_item_exist("active_model_name"):
        return
    name = dpg.get_value("active_model_name")
    if not name or name == "(none loaded)":
        log("No model loaded in VRAM.", "WARN")
        return
    log(f"Unloading '{name}' from VRAM ...", "MODEL")

    def _do():
        try:
            r = requests.post(
                f"{OLLAMA_API}/api/generate",
                json={"model": name, "prompt": "", "keep_alive": 0},
                timeout=30,
            )
            if r.status_code == 200:
                log(f"'{name}' unloaded from VRAM.", "SUCCESS")
            else:
                log(f"Unload failed ({r.status_code}).", "ERROR")
        except Exception as exc:
            log(f"Unload error: {exc}", "ERROR")
        refresh_active_model()

    threading.Thread(target=_do, daemon=True).start()


def pull_model_callback() -> None:
    """Pull a model from the Ollama library (streamed with validation)."""
    if state.pull_in_progress:
        log("Pull already in progress.", "WARN")
        return
    name = dpg.get_value("pull_input").strip()
    if not name:
        log("Enter a model name first.", "WARN")
        return
    state.pull_in_progress = True
    log(f"Pulling '{name}' ...", "MODEL")

    def _do():
        try:
            resp = requests.post(
                f"{OLLAMA_API}/api/pull",
                json={"name": name, "stream": True},
                stream=True, timeout=600,
            )

            if resp.status_code != 200:
                try:
                    err_data = resp.json()
                    err_msg = err_data.get("error", resp.text[:200])
                except Exception:
                    err_msg = resp.text[:200] or f"HTTP {resp.status_code}"
                log(f"Pull failed: {err_msg}", "ERROR")
                return

            pull_ok  = False
            last_pct = -1

            for line in resp.iter_lines():
                if not line:
                    continue
                obj = json.loads(line)

                if "error" in obj:
                    log(f"Pull failed: {obj['error']}", "ERROR")
                    return

                total  = obj.get("total",     0)
                comp   = obj.get("completed", 0)
                status = obj.get("status",    "")

                if total > 0:
                    pct = int(comp / total * 100)
                    if pct != last_pct and pct % 10 == 0:
                        log(f"  Download {name} {pct}%", "MODEL")
                        last_pct = pct
                elif status:
                    log(f"  {status}", "DEBUG")

                if status == "success":
                    pull_ok = True

            if pull_ok:
                log(f"Pull complete: {name}", "SUCCESS")
            else:
                log(f"Pull ended without confirmation for '{name}'.", "WARN")

        except Exception as exc:
            log(f"Pull error: {exc}", "ERROR")
        finally:
            state.pull_in_progress = False
            refresh_models()

    threading.Thread(target=_do, daemon=True).start()


# ─────────────────────────────────────────────
#  PROCESS TABLE
# ─────────────────────────────────────────────
def collect_procs() -> None:
    """Snapshot top processes by CPU usage."""
    procs = []
    for p in psutil.process_iter(["name", "cpu_percent", "memory_info"]):
        try:
            procs.append((
                p.info["name"] or "?",
                p.info["cpu_percent"] or 0.0,
                (p.info["memory_info"].rss if p.info["memory_info"] else 0) / (1024 ** 2),
            ))
        except Exception:
            pass
    procs.sort(key=lambda x: x[1], reverse=True)
    with state.proc_lock:
        state.proc_snapshot.clear()
        state.proc_snapshot.extend(procs)
    update_processes([process_info(name, cpu, ram_mb) for name, cpu, ram_mb in procs[:UI["top_processes"]]])


def update_proc_table() -> None:
    """Redraw the process table in the UI."""
    if not dpg.does_item_exist("proc_table"):
        return
    for c in (dpg.get_item_children("proc_table", slot=1) or []):
        dpg.delete_item(c)
    with state.proc_lock:
        snapshot = list(state.proc_snapshot[:UI["top_processes"]])
    for name, cpu, ram_mb in snapshot:
        col = CYAN if name.lower() in AI_PROCS else WHITE
        with dpg.table_row(parent="proc_table"):
            dpg.add_text(name,               color=col)
            dpg.add_text(f"{cpu:.1f}%",      color=heat_colour(cpu))
            dpg.add_text(f"{ram_mb:.0f} MB", color=DIM)
