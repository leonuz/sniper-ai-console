"""Secondary UI windows and markdown popups."""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from config import APP_NAME, APP_VERSION, CFG
from helpers import CYAN, YELLOW, WHITE, DIM
from app.adapters.platform.browser import open_url
from app.ui.helpers import read_markdown_file


def render_md_window(tag: str, title: str, filename: str,
                     width: int = 700, height: int = 580) -> None:
    if dpg.does_item_exist(tag):
        dpg.show_item(tag)
        dpg.focus_item(tag)
        return

    content = read_markdown_file(filename)

    with dpg.window(label=title, tag=tag, width=width, height=height,
                    on_close=lambda: dpg.hide_item(tag)):
        with dpg.child_window(border=False, height=-1, width=-1):
            for line in content.split("\n"):
                stripped = line.rstrip()
                if stripped.startswith("# "):
                    dpg.add_text(stripped[2:], color=CYAN)
                    dpg.add_separator()
                    dpg.add_spacer(height=6)
                elif stripped.startswith("## "):
                    dpg.add_spacer(height=6)
                    dpg.add_text(f"  {stripped[3:]}", color=YELLOW)
                    dpg.add_spacer(height=2)
                elif stripped.startswith("### "):
                    dpg.add_spacer(height=4)
                    dpg.add_text(f"    {stripped[4:]}", color=CYAN)
                    dpg.add_spacer(height=2)
                elif stripped.startswith("- **"):
                    dpg.add_text(f"    {stripped[2:]}", color=WHITE)
                elif stripped.startswith("- "):
                    dpg.add_text(f"    {stripped}", color=WHITE)
                elif stripped and stripped[0].isdigit() and ". " in stripped[:4]:
                    dpg.add_text(f"    {stripped}", color=WHITE)
                elif stripped == "":
                    dpg.add_spacer(height=4)
                else:
                    dpg.add_text(f"  {stripped}", color=WHITE)


def show_help_window() -> None:
    render_md_window("win_manual", "Help - User Manual", "MANUAL.md")


def show_changelog_window() -> None:
    render_md_window("win_changelog", "Help - Changelog", "CHANGELOG.md",
                     width=660, height=520)


def show_whoami_window() -> None:
    tag = "win_whoami"
    if dpg.does_item_exist(tag):
        dpg.show_item(tag)
        dpg.focus_item(tag)
        return

    app = CFG["app"]
    with dpg.window(label="Help - Who Am I", tag=tag,
                    width=520, height=300, on_close=lambda: dpg.hide_item(tag)):
        dpg.add_spacer(height=10)
        dpg.add_text("  ABOUT THE AUTHOR", color=CYAN)
        dpg.add_separator()
        dpg.add_spacer(height=10)
        dpg.add_text(f"  {APP_NAME} was built by {app['author']}.", color=WHITE)
        dpg.add_spacer(height=10)
        dpg.add_text("  GitHub / Portfolio:", color=DIM)
        dpg.add_spacer(height=4)
        dpg.add_text(f"  {app['portfolio_url']}", color=CYAN)
        dpg.add_spacer(height=8)
        dpg.add_button(
            label="  Open in Browser  ",
            callback=lambda: open_url("start msedge", app["portfolio_url"]),
        )
        dpg.add_spacer(height=16)
        dpg.add_separator()
        dpg.add_spacer(height=8)
        dpg.add_text(f"  App Version :  {APP_VERSION}", color=DIM)
        dpg.add_text(f"  License     :  {app['license']}", color=DIM)
        dpg.add_text("  Stack       :  DearPyGui + Ollama + Open-WebUI + OpenClaw", color=DIM)
