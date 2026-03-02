# CHANGELOG

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
- Shutdown expanded to 4 steps (includes OpenClaw via WSL)
- Start All / Restart All now include OpenClaw
- OpenClaw path configurable in config.json (WSL full path)
- Fixed numbered list rendering in help windows (supports 4+ items)
- Added ### heading support in help window markdown renderer
- Version bump to v1.3

## v1.2
- **Project restructured** into modular architecture (config, engines, monitoring, ui, logger)
- **Externalised configuration** to `config.json` - edit paths, URLs, UI settings without touching code
- **Externalised documentation** - `CHANGELOG.md` and `MANUAL.md` are now standalone files
- **File logging** with rotation - writes to `sniper_ai.log` (configurable size + backup count)
- **Individual service toggles** - START/STOP buttons per service with colour feedback
- **Health check** - detects zombie/crashed processes and updates status automatically
- **Auto-refresh models** - model list refreshes automatically when switching to the Models tab
- **Tab renamed** DASHBOARD -> GRAPHS with "SYSTEM TELEMETRY" title
- **System Log** now visible across all tabs (standardised tab content height)
- **Pull validation** - detects non-existent models and reports errors correctly
- Removed redundant START ENGINES button from sidebar

## v1.1d
- System log moved outside tabs (visible from all views)
- Added START/STOP toggle per service with dynamic theming
- Standardised tab content heights
- Model pull now validates 404 responses

## v1.1c
- Model manager: pull from library, delete, auto-refresh
- Process monitor: top 25 by CPU, AI stack highlighted in cyan

## v1.1b
- Dark cyberpunk theme with teal/cyan accent palette
- Real-time GPU, CPU, RAM telemetry graphs

## v1.1a
- Initial release with Ollama + Open-WebUI process management
- Sidebar with service status lights and quick stats
- System tray support (minimize/restore/exit)
