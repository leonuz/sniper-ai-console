"""
ui.py — GUI construction for Sniper AI Console.
Theme, splash, primary window, tabs, and top-level composition.
"""

import os
import threading

import dearpygui.dearpygui as dpg

import state
from config import (
    APP_NAME, APP_VERSION, CFG,
    LOGO_FILE, PORTAL_URL, OPENCLAW_DASHBOARD, UI,
)
from helpers import (
    CYAN, GREEN, YELLOW, RED, DIM, WHITE,
    CYAN_RGB, GREEN_RGB, RED_RGB,
)
from engines import (
    start_all, nuclear_shutdown, restart_all,
    toggle_ollama, toggle_webui, toggle_openclaw,
)
from monitoring import (
    refresh_models, pull_model_callback,
    load_model_callback, unload_model_callback,
)
from updater import check_for_updates_async, apply_update_async
from app.adapters.platform.browser import open_url
from app.ui.bindings import on_tab_change
from app.ui.tray import minimize_to_tray
from app.ui.windows import show_help_window, show_changelog_window, show_whoami_window


# ─────────────────────────────────────────────
#  TOP-LEVEL THEME
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
def _apply_theme() -> None:
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,       ( 8, 10, 18))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,        (12, 15, 25))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,        (18, 24, 40))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (28, 38, 62))
            dpg.add_theme_color(dpg.mvThemeCol_Button,         ( 0, 75, 88))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  ( 0,155,170))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,   ( 0,215,230))
            dpg.add_theme_color(dpg.mvThemeCol_Header,         ( 0, 65, 78))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered,  ( 0,125,140))
            dpg.add_theme_color(dpg.mvThemeCol_Tab,            ( 0, 50, 65))
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered,     ( 0,155,175))
            dpg.add_theme_color(dpg.mvThemeCol_TabActive,      ( 0,195,215))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,        ( 5,  7, 15))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,  ( 0, 45, 65))
            dpg.add_theme_color(dpg.mvThemeCol_Border,         ( 0,140,155, 80))
            dpg.add_theme_color(dpg.mvThemeCol_Text,           (200,200,200))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg,    ( 8, 10, 18))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab,  ( 0, 95,115))
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg,        (10, 14, 24))
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,  3)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,  10, 10)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,     8,  5)
    dpg.bind_theme(t)

    # Toggle button themes
    with dpg.theme(tag="theme_btn_on"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,        ( 0, 110,  40))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  ( 0, 160,  60))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,   ( 0, 200,  80))
    with dpg.theme(tag="theme_btn_off"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,        (110,  20,  20))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,  (160,  30,  30))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,   (200,  40,  40))


# ─────────────────────────────────────────────
#  UI composition below uses extracted tray/windows/bindings modules
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
#  GUI BUILD
# ─────────────────────────────────────────────
def build_gui() -> None:
    _apply_theme()

    gpu_label    = CFG["gpu"]["label"]
    sw           = UI["sidebar_width"]
    gh           = UI["graph_height"]
    gw           = UI["graph_width"]
    tab_h        = UI["tab_content_height"]
    log_h        = UI["log_height"]
    vw           = UI["viewport_width"]
    vh           = UI["viewport_height"]

    # Logo
    logo_loaded = False
    sidebar_logo_w, sidebar_logo_h = 180, 60
    splash_logo_w = 400
    if os.path.exists(LOGO_FILE):
        try:
            w, h, _, data = dpg.load_image(LOGO_FILE)
            with dpg.texture_registry(show=False):
                dpg.add_static_texture(w, h, data, tag="logo_tex")
            sidebar_logo_h = max(1, int(h * (180 / w)))
            splash_logo_h  = max(1, int(h * (splash_logo_w / w)))
            logo_loaded = True
        except Exception:
            pass

    # ── Splash ────────────────────────────────
    with dpg.window(tag="splash_win", no_title_bar=True,
                    no_move=True, no_resize=True,
                    width=vw, height=vh):
        dpg.add_spacer(height=150)
        if logo_loaded:
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=(vw - splash_logo_w) // 2)
                dpg.add_image("logo_tex", width=splash_logo_w, height=splash_logo_h)
            dpg.add_spacer(height=30)
        else:
            dpg.add_spacer(height=120)
        title_spaced = "     " + "  ".join(APP_NAME.upper().replace(" ", "   "))
        dpg.add_text(title_spaced, color=CYAN)
        dpg.add_spacer(height=8)
        dpg.add_text(f"     {APP_VERSION}  -  Enhanced Edition", color=(0, 180, 180, 255))
        dpg.add_spacer(height=16)
        dpg.add_text("     Initialising system ...", color=DIM)

    # ── Primary Window ────────────────────────
    with dpg.window(label=f"{APP_NAME.upper()}  {APP_VERSION}",
                    tag="PrimaryWindow", show=False,
                    menubar=True):

        with dpg.menu_bar():
            with dpg.menu(label="Engines"):
                dpg.add_menu_item(label="Start All",    callback=start_all)
                dpg.add_menu_item(label="Restart All",
                    callback=lambda: threading.Thread(target=restart_all, daemon=True).start())
                dpg.add_menu_item(label="Shutdown All", callback=nuclear_shutdown)
                dpg.add_separator()
                dpg.add_menu_item(label="Toggle Ollama",  callback=lambda: toggle_ollama())
                dpg.add_menu_item(label="Toggle WebUI",     callback=lambda: toggle_webui())
                dpg.add_menu_item(label="Toggle OpenClaw", callback=lambda: toggle_openclaw())
                dpg.add_separator()
                dpg.add_menu_item(label="Exit", callback=lambda: (nuclear_shutdown(), dpg.stop_dearpygui()))
            with dpg.menu(label="View"):
                dpg.add_menu_item(label="Minimize to Tray", callback=minimize_to_tray)
                dpg.add_menu_item(label="Clear Logs",
                    callback=lambda: [dpg.delete_item(c)
                        for c in (dpg.get_item_children("log_win", 1) or [])])
                dpg.add_menu_item(label="Restore All Graphs",
                    callback=lambda: [dpg.show_item(t)
                        for t in ("grp_gpu", "grp_cpu", "grp_ram")
                        if dpg.does_item_exist(t)])
            with dpg.menu(label="Models"):
                dpg.add_menu_item(label="Refresh List",
                    callback=lambda: threading.Thread(target=refresh_models, daemon=True).start())
            with dpg.menu(label="Portal"):
                dpg.add_menu_item(label="Open WebUI Portal",
                    callback=lambda: open_url(
                        CFG['engines']['browser_command'], PORTAL_URL))
                dpg.add_menu_item(label="Open OpenClaw Dashboard",
                    callback=lambda: open_url(
                        CFG['engines']['browser_command'], OPENCLAW_DASHBOARD))
            with dpg.menu(label="Help"):
                dpg.add_menu_item(label="Manual",    callback=show_help_window)
                dpg.add_menu_item(label="Changelog", callback=show_changelog_window)
                dpg.add_menu_item(label="Who Am I",  callback=show_whoami_window)
                dpg.add_separator()
                dpg.add_menu_item(label="Check for Updates",
                    callback=lambda: check_for_updates_async())
                dpg.add_menu_item(label="Update Open-WebUI",
                    callback=lambda: apply_update_async())

        with dpg.group(horizontal=True):

            # ── Sidebar ───────────────────────
            with dpg.child_window(width=sw, border=True):
                if logo_loaded:
                    dpg.add_image("logo_tex", width=sidebar_logo_w, height=sidebar_logo_h)
                    dpg.add_spacer(height=6)
                else:
                    dpg.add_text(APP_NAME.upper(), color=CYAN)
                dpg.add_separator()
                dpg.add_spacer(height=4)

                with dpg.group(horizontal=True):
                    dpg.add_text("UPTIME:", color=DIM)
                    dpg.add_text("--:--:--", tag="uptime_val", color=CYAN)

                dpg.add_spacer(height=10)
                dpg.add_text("SERVICE STATUS", color=DIM)
                dpg.add_spacer(height=4)

                # Ollama toggle row
                with dpg.group(horizontal=True):
                    with dpg.drawlist(width=14, height=14):
                        dpg.draw_circle((7, 7), 5, fill=RED_RGB, tag="ol_light")
                    dpg.add_text(" Ollama ", color=WHITE)
                    dpg.add_text("OFFLINE", tag="ol_status", color=RED)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="START", tag="ol_toggle", width=90, height=22,
                                   callback=lambda: toggle_ollama())
                    dpg.add_spacer(width=4)
                    dpg.add_text("--", tag="ol_ver", color=CYAN)
                dpg.add_spacer(height=4)

                # WebUI toggle row
                with dpg.group(horizontal=True):
                    with dpg.drawlist(width=14, height=14):
                        dpg.draw_circle((7, 7), 5, fill=RED_RGB, tag="wb_light")
                    dpg.add_text(" WebUI  ", color=WHITE)
                    dpg.add_text("OFFLINE", tag="wb_status", color=RED)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="START", tag="wb_toggle", width=90, height=22,
                                   callback=lambda: toggle_webui())
                    dpg.add_spacer(width=4)
                    dpg.add_text("--", tag="wb_ver", color=CYAN)
                dpg.add_spacer(height=4)

                # OpenClaw toggle row
                with dpg.group(horizontal=True):
                    with dpg.drawlist(width=14, height=14):
                        dpg.draw_circle((7, 7), 5, fill=RED_RGB, tag="oc_light")
                    dpg.add_text(" OpenClaw", color=WHITE)
                    dpg.add_text("OFFLINE", tag="oc_status", color=RED)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="START", tag="oc_toggle", width=90, height=22,
                                   callback=lambda: toggle_openclaw())
                    dpg.add_spacer(width=4)
                    dpg.add_text("--", tag="oc_ver", color=CYAN)
                dpg.add_spacer(height=2)

                dpg.add_spacer(height=10)
                dpg.add_text("QUICK STATS", color=DIM)
                dpg.add_spacer(height=4)

                for label, pct_tag in (("CPU", "cpu_pct"), ("RAM", "ram_pct"), ("GPU", "gpu_pct")):
                    with dpg.group(horizontal=True):
                        dpg.add_text(f"{label}:", color=DIM)
                        dpg.add_text("  0.0%", tag=pct_tag, color=CYAN)

                with dpg.group(horizontal=True):
                    dpg.add_text("MEM:", color=DIM)
                    dpg.add_text("", tag="ram_abs", color=DIM)

                dpg.add_spacer(height=12)
                dpg.add_text("CONTROLS", color=DIM)
                dpg.add_spacer(height=4)

                dpg.add_button(label="RESTART", width=-1, height=28,
                    callback=lambda: threading.Thread(target=restart_all, daemon=True).start())
                dpg.add_spacer(height=3)
                dpg.add_button(label="FORCE SHUTDOWN", width=-1, height=28,
                               callback=nuclear_shutdown)
                dpg.add_spacer(height=10)
                dpg.add_button(label="MINIMIZE TO TRAY", width=-1, height=28,
                               callback=minimize_to_tray)
                dpg.add_spacer(height=3)
                dpg.add_button(label="OPEN PORTAL", width=-1, height=28,
                    callback=lambda: open_url(
                        CFG['engines']['browser_command'], PORTAL_URL))
                dpg.add_spacer(height=3)
                dpg.add_button(label="OPEN CLAW", width=-1, height=28,
                    callback=lambda: open_url(
                        CFG['engines']['browser_command'], OPENCLAW_DASHBOARD))

            # ── Main content ──────────────────
            with dpg.group():
                with dpg.tab_bar(callback=on_tab_change):

                    # Graphs tab
                    with dpg.tab(label="  GRAPHS  "):
                        with dpg.child_window(border=False, height=tab_h, width=-1, no_scrollbar=True):
                            dpg.add_spacer(height=8)
                            dpg.add_text("SYSTEM TELEMETRY", color=CYAN)
                            dpg.add_separator()
                            dpg.add_spacer(height=8)
                            with dpg.group(horizontal=True):
                                for g_label, g_tag, key in [
                                    (gpu_label,  "grp_gpu", "gpu"),
                                    ("CPU %",    "grp_cpu", "cpu"),
                                    ("RAM %",    "grp_ram", "ram"),
                                ]:
                                    with dpg.group(tag=g_tag):
                                        with dpg.group(horizontal=True):
                                            dpg.add_text(g_label, color=CYAN)
                                            dpg.add_button(label="X", small=True,
                                                user_data=g_tag,
                                                callback=lambda s, a, u: dpg.hide_item(u))
                                        with dpg.plot(height=gh, width=gw, no_menus=True):
                                            dpg.add_plot_axis(dpg.mvXAxis, no_tick_labels=True)
                                            with dpg.plot_axis(dpg.mvYAxis, tag=f"{key}_y"):
                                                dpg.set_axis_limits(f"{key}_y", 0, 100)
                                                dpg.add_line_series(
                                                    state.x_axis, state.history[key],
                                                    tag=f"{key}_series")

                            dpg.add_spacer(height=4)
                            dpg.add_button(label="RESTORE ALL GRAPHS",
                                callback=lambda: [dpg.show_item(t)
                                    for t in ("grp_gpu", "grp_cpu", "grp_ram")
                                    if dpg.does_item_exist(t)])

                    # Models tab
                    with dpg.tab(label="  MODELS  "):
                        with dpg.child_window(border=False, height=tab_h, width=-1, no_scrollbar=True):
                            dpg.add_spacer(height=8)
                            dpg.add_text("OLLAMA MODEL MANAGER", color=CYAN)
                            dpg.add_separator()
                            dpg.add_spacer(height=6)

                            # Active model display
                            with dpg.group(horizontal=True):
                                dpg.add_text("Active:", color=DIM)
                                dpg.add_text("(none loaded)", tag="active_model_name",
                                             color=DIM)
                                dpg.add_text("", tag="active_model_vram", color=CYAN)
                                dpg.add_spacer(width=10)
                                dpg.add_button(label="UNLOAD",
                                               callback=unload_model_callback)

                            dpg.add_spacer(height=4)

                            # Model selector + load
                            with dpg.group(horizontal=True):
                                dpg.add_text("Switch:", color=DIM)
                                dpg.add_combo(tag="model_combo", items=[],
                                              width=320)
                                dpg.add_button(label="LOAD",
                                               callback=load_model_callback)
                                dpg.add_spacer(width=20)
                                dpg.add_text("Pull:", color=DIM)
                                dpg.add_input_text(tag="pull_input",
                                                   hint="e.g. llama3:8b", width=200)
                                dpg.add_button(label="PULL",
                                               callback=pull_model_callback)
                                dpg.add_spacer(width=6)
                                dpg.add_button(label="REFRESH",
                                    callback=lambda: threading.Thread(
                                        target=refresh_models, daemon=True).start())

                            dpg.add_spacer(height=6)

                            with dpg.child_window(border=True, height=-1, width=-1):
                                with dpg.table(tag="model_table", header_row=True,
                                               borders_innerH=True, borders_outerH=True,
                                               borders_outerV=True, row_background=True,
                                               resizable=True):
                                    dpg.add_table_column(label="Model Name")
                                    dpg.add_table_column(label="Size",
                                        width_fixed=True, init_width_or_weight=95)
                                    dpg.add_table_column(label="Quant",
                                        width_fixed=True, init_width_or_weight=72)
                                    dpg.add_table_column(label="Family",
                                        width_fixed=True, init_width_or_weight=95)
                                    dpg.add_table_column(label="Action",
                                        width_fixed=True, init_width_or_weight=78)

                    # Processes tab
                    with dpg.tab(label="  PROCESSES  "):
                        with dpg.child_window(border=False, height=tab_h, width=-1, no_scrollbar=True):
                            dpg.add_spacer(height=8)
                            dpg.add_text(
                                f"TOP PROCESSES  (auto-refresh every "
                                f"{UI['proc_refresh_interval']} s)", color=CYAN)
                            dpg.add_text("AI stack processes highlighted in cyan.",
                                         color=DIM)
                            dpg.add_separator()
                            dpg.add_spacer(height=6)

                            with dpg.child_window(border=True, height=-1, width=-1):
                                with dpg.table(tag="proc_table", header_row=True,
                                               borders_innerH=True, borders_outerH=True,
                                               borders_outerV=True, row_background=True,
                                               resizable=True):
                                    dpg.add_table_column(label="Process")
                                    dpg.add_table_column(label="CPU %",
                                        width_fixed=True, init_width_or_weight=80)
                                    dpg.add_table_column(label="RAM",
                                        width_fixed=True, init_width_or_weight=105)

                # ── System Log (visible on all tabs) ──
                dpg.add_spacer(height=6)
                dpg.add_separator()
                dpg.add_spacer(height=4)

                with dpg.group(horizontal=True):
                    dpg.add_text("SYSTEM LOG", color=CYAN)
                    dpg.add_spacer(width=20)
                    dpg.add_button(label="CLEAR",
                        callback=lambda: [dpg.delete_item(c)
                            for c in (dpg.get_item_children("log_win", 1) or [])])

                with dpg.child_window(tag="log_win", border=True,
                                      height=log_h, width=-1):
                    pass
