# USER MANUAL

## SERVICE TOGGLES

Each service (Ollama, WebUI, OpenClaw) has its own **START / STOP** button in the sidebar.

- **Green button (STOP)** - service is running. Click to shut it down individually.
- **Red button (START)** - service is offline. Click to launch it.

The status light, label (ONLINE/OFFLINE), and version number update automatically every second.

Ollama and Open-WebUI run as native Windows processes. OpenClaw runs on WSL2 Ubuntu and is controlled via `wsl` commands. The OpenClaw binary path is configurable in `config.json`.

## RESTART

Performs a Force Shutdown of all engines, waits briefly, then relaunches all.
Useful after model changes, config updates, or when something feels stuck.

## FORCE SHUTDOWN

Stops all services in 4 steps:

1. Kill Ollama by tracked PID + full process tree.
2. Kill Open-WebUI by tracked PID + full process tree.
3. psutil sweep to remove any orphaned worker processes.
4. Stop OpenClaw gateway via WSL.

## EXIT

Found in the **Engines** menu. Performs a Force Shutdown then closes the console application.

## GRAPHS TAB

Real-time telemetry graphs for GPU, CPU, and RAM.
Click **[X]** on any graph to hide it; use **RESTORE ALL GRAPHS** to bring them back.

## MODELS TAB

Lists all locally installed Ollama models with size, quantization, and family.
The list **auto-refreshes** when you switch to this tab.

### Active Model (VRAM)

The top of the Models tab shows which model is currently loaded in GPU memory (VRAM) and how much VRAM it uses.

- **UNLOAD** - removes the active model from VRAM, freeing GPU memory.
- **Switch dropdown** - select any installed model from the dropdown.
- **LOAD** - loads the selected model into VRAM. The previously loaded model is replaced.

### Model Library

- **Pull** a new model by entering a name from the Ollama library and clicking PULL.
- **Delete** a model by clicking its DELETE button. A confirmation dialog will appear.
- **Refresh** manually with the REFRESH button.

## PROCESSES TAB

Shows the top 25 processes by CPU usage, refreshed every 5 seconds (configurable).
AI stack processes (ollama.exe, python.exe, open-webui.exe) are highlighted in cyan.

## SYSTEM LOG

Visible across all tabs. Shows timestamped messages with colour-coded levels:

- **DEBUG** (cyan) - internal diagnostics.
- **INFO** (grey) - routine status updates.
- **WARN** (yellow) - non-critical issues.
- **SUCCESS** (green) - operations that completed successfully.
- **ERROR** (red) - failures.
- **MODEL** (purple) - model-specific operations.

Use **CLEAR** to empty the log. All log messages are also written to `sniper_ai.log` (rotating file).

## PORTAL MENU

- **Open WebUI Portal** - opens the Open-WebUI web interface in the browser.
- **Open OpenClaw Dashboard** - opens the OpenClaw web dashboard in the browser.

## HELP MENU

- **Manual** - this document.
- **Changelog** - version history.
- **Who Am I** - author info and app version.
- **Check for Updates** - compares installed Open-WebUI version against the latest on PyPI.
- **Update Open-WebUI** - stops WebUI, runs pip upgrade, restarts WebUI automatically.

## UPDATES

Open-WebUI updates are managed from the **Help** menu:

- **Check for Updates** - compares your installed version against the latest on PyPI. The result is shown in the System Log.
- **Update Open-WebUI** - stops WebUI, runs `pip install --upgrade open-webui`, then restarts WebUI automatically. Only available after a check confirms an update exists.

The console also checks for updates **automatically** the first time WebUI comes online each session.

## CONFIGURATION

Edit `config.json` to change paths, URLs, UI dimensions, and logging options
without modifying any code. The file is auto-generated with defaults if missing.

Key settings:

- **paths.ollama** - full path to ollama.exe
- **paths.webui** - full path to open-webui.exe in venv
- **paths.openclaw** - full path to openclaw binary inside WSL (e.g. /home/user/.npm-global/bin/openclaw)
- **engines.openclaw_port** - OpenClaw gateway port (default: 18789)
- **urls.openclaw_dashboard** - OpenClaw dashboard URL
- **logging.log_to_file** - enable/disable file logging
- **logging.log_file** - log filename
- **logging.max_file_size_mb** - max size before rotation
- **ui.sidebar_width** - sidebar pixel width
- **ui.graph_height / graph_width** - telemetry graph dimensions
- **ui.proc_refresh_interval** - seconds between process table updates

## SYSTEM TRAY

Click **MINIMIZE TO TRAY** to hide the console window. Right-click the tray icon to **Show Console** or **Exit**. Requires the `pystray` and `pillow` packages.
