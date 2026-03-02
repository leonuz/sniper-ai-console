# CHANGELOG

## v1.2
- **Project restructured** into modular architecture (config, engines, monitoring, ui, logger, updater)
- **Externalised configuration** to `config.json` - edit paths, URLs, UI settings without touching code
- **Externalised documentation** - `CHANGELOG.md` and `MANUAL.md` are now standalone files
- **File logging** with rotation - writes to `sniper_ai.log` (configurable size + backup count)
- **Individual service toggles** - START/STOP buttons per service (Ollama, WebUI) with colour feedback
- **Health check** - detects zombie/crashed processes and updates status automatically
- **Auto-refresh models** - model list refreshes automatically when switching to the Models tab
- **Open-WebUI updater** - check for updates and install via Help menu; auto-checks on startup
- **Tab renamed** DASHBOARD -> GRAPHS with "SYSTEM TELEMETRY" title
- **System Log** now visible across all tabs (standardised tab content height)
- **Pull validation** - detects non-existent models and reports errors correctly
- Removed redundant START ENGINES button from sidebar

## v1.1d
- Shutdown now tracks PIDs at launch time
- Kill uses `taskkill /F /T /PID` - kills full process tree reliably
- psutil orphan sweep as step 3 catches any surviving WebUI workers
- Shutdown log split into 3 labelled steps for full traceability

## v1.1c
- Force Shutdown kills only Ollama/WebUI, not the console
- Logo displayed on splash screen
- Service version numbers shown in sidebar
- Help moved to top menu bar (Manual / Changelog / Who Am I)
- Version control formalised starting at v1.1c

## v1.1b (internal)
- GPU graph reverted to original PowerShell counter method
- Crash fixes: font registry, draw_circle alpha, set_value on text
- Cross-thread UI queue for stable background updates

## v1.1a (internal)
- Full cyberpunk dark theme via bind_theme
- Model Manager tab: pull, list, delete Ollama models
- Processes tab with AI stack highlighting
- Restart button, uptime counter, service version labels
- Menu bar with keyboard-accessible actions
- requests / pystray made optional (graceful degradation)

## v1.0 (original)
- Initial release: start/shutdown engines, GPU/CPU/RAM graphs
- System log, service status lights, minimize-to-tray
