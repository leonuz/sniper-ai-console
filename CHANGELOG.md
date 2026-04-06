# CHANGELOG

All notable changes to this project will be documented in this file.

The format is intentionally simple and human-readable.

---

## Unreleased

### Consolidation
- documented successful real-world smoke testing on the target workstation and operating environment
- added a project TODO file capturing the next priorities after the completed architecture refactor phases

## v1.4

### Refactor
- introduced a new `app/` package scaffold for the next architecture stage
- added domain enums, dataclasses, service contracts, and initial state/store scaffolding
- extracted platform adapters for Windows process behavior, WSL execution, browser launch, and GPU telemetry
- introduced explicit managed service adapters for Ollama, Open-WebUI, and OpenClaw
- added state synchronization from the legacy runtime into the new application store
- split the legacy monolithic runtime loop into focused pollers coordinated by a runtime coordinator
- thinned the UI layer by extracting tray logic, popup windows, helpers, and tab bindings
- improved runtime diagnostics and added migration-period config validation
- added an initial automated `unittest` suite for core logic

### Documentation
- rewrote and expanded README, manual, architecture guide, roadmap, and development notes
- documented that the post-refactor application should be smoke-tested on the target Windows 11 environment

### Validation
- validated the application successfully on the real target environment:
  - Windows 11
  - Lenovo ThinkPad X1 Carbon Gen 13
  - Intel ARC 140V GPU
  - 32 GB RAM
- confirmed successful GUI startup and splash transition
- confirmed live CPU / RAM / GPU telemetry
- confirmed Open-WebUI handled a real query while GPU activity appeared in the graphs
- confirmed service stop/start cycles worked correctly
- confirmed ONLINE/OFFLINE state transitions behaved correctly
- confirmed no traceback during the validated smoke test
- confirmed no lingering processes after tested service restart flows

### Fixes
- fixed a refactor regression where legacy engine helper imports were missing from `engines.py`, breaking service toggles until restored

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
