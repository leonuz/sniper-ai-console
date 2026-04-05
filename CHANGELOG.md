# CHANGELOG

All notable changes to this project will be documented in this file.

The format is intentionally simple and human-readable.

---

## Unreleased

### Documentation
- rewrote the project README to reflect the real scope, current architecture, and intended direction
- expanded the manual to better document current behavior and operational assumptions
- added architecture documentation covering current design, pain points, and target structure
- added a roadmap for the planned refactor
- added a development guide for future work on the codebase

### Project direction
- formalized the refactor direction toward a cleaner separation between domain logic, service control, platform adapters, application orchestration, and UI rendering
- documented that the working Intel ARC telemetry path and current library choices should be preserved unless a stronger replacement is justified
- documented the intent to refactor incrementally rather than perform a blind rewrite

---

## v1.3
- **OpenClaw integration** - start/stop/monitor OpenClaw gateway running on WSL2 Ubuntu
- **OpenClaw dashboard** - open OpenClaw web UI from Portal menu or sidebar button
- **VRAM model manager** - view active model, load/unload models from GPU memory, switch between models
- **Delete confirmation** - modal dialog before deleting a model ("Are you sure?")
- **Open-WebUI updater** - check for updates and install via Help menu; auto-checks on startup
- **Exit button** - added to Engines menu for clean app shutdown
- **Splash logo** - enlarged and centered on the splash screen
- **Scrollbar removed** - eliminated unnecessary scrollbar from all tabs
- **Portal menu split** - separate entries for Open WebUI Portal and OpenClaw Dashboard
- shutdown expanded to 4 steps (includes OpenClaw via WSL)
- Start All / Restart All now include OpenClaw
- OpenClaw path configurable in `config.json` (WSL full path)
- fixed numbered list rendering in help windows (supports 4+ items)
- added `###` heading support in help window markdown renderer
- version bump to `v1.3`

## v1.2
- **Project restructured** into modular architecture (`config`, `engines`, `monitoring`, `ui`, `logger`)
- **Externalised configuration** to `config.json` so paths, URLs, and UI settings can be changed without touching code
- **Externalised documentation** to standalone `CHANGELOG.md` and `MANUAL.md`
- **File logging** with rotation via `sniper_ai.log`
- **Individual service toggles** with colour feedback
- **Health check** to detect zombie or crashed processes
- **Auto-refresh models** when entering the Models tab
- renamed main telemetry tab from `DASHBOARD` to `GRAPHS`
- made the system log visible across all tabs
- improved model pull validation and non-existent model handling
- removed redundant `START ENGINES` button from the sidebar

## v1.1d
- moved system log outside tabs so it remains visible from all views
- added START / STOP toggle per service with dynamic theming
- standardised tab content heights
- improved model pull validation for 404 responses

## v1.1c
- model manager: pull from library, delete, auto-refresh
- process monitor: top 25 processes by CPU, AI stack highlighted in cyan

## v1.1b
- dark cyberpunk theme with teal/cyan accent palette
- real-time GPU, CPU, RAM telemetry graphs

## v1.1a
- initial release with Ollama + Open-WebUI process management
- sidebar with service status lights and quick stats
- system tray support (minimize / restore / exit)
