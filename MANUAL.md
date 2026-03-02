# USER MANUAL

## SERVICE TOGGLES

Each service (Ollama, WebUI) has its own **START / STOP** button in the sidebar.

- **Green button (STOP)** - service is running. Click to shut it down individually.
- **Red button (START)** - service is offline. Click to launch it.

The status light, label (ONLINE/OFFLINE), and version number update automatically.

## RESTART

Performs a Force Shutdown of both engines, waits briefly, then relaunches both.
Useful after model changes, config updates, or when something feels stuck.

## FORCE SHUTDOWN

Stops Ollama and Open-WebUI in 3 steps:

1. Kill Ollama by tracked PID + full process tree.
2. Kill Open-WebUI by tracked PID + full process tree.
3. psutil sweep to remove any orphaned worker processes.

The console itself stays open.

## MINIMIZE TO TRAY

Hides the console window to the system tray.
Right-click the tray icon to restore or exit completely.

## GRAPHS TAB

Real-time telemetry graphs for GPU, CPU, and RAM.
Click **[X]** on any graph to hide it; use **RESTORE ALL GRAPHS** to bring them back.

## MODELS TAB

Lists all locally installed Ollama models with size, quantization, and family.
The list **auto-refreshes** when you switch to this tab.

- **Pull** a new model by entering a name from the Ollama library and clicking PULL.
- **Delete** a model by clicking its DELETE button.
- **Refresh** manually with the REFRESH button.

## PROCESSES TAB

Top running processes by CPU usage, refreshed automatically.
Ollama and Open-WebUI processes are highlighted in cyan.

## SYSTEM LOG

Visible at the bottom of every tab. Shows timestamped events colour-coded by level:

- **DEBUG** (cyan) - internal details
- **INFO** (grey) - general status
- **WARN** (yellow) - warnings
- **SUCCESS** (green) - confirmations
- **ERROR** (red) - failures
- **MODEL** (purple) - model operations

Logs are also written to `sniper_ai.log` (configurable in `config.json`).

## HELP MENU

Manual, Changelog, and Who Am I are accessible from the Help menu in the top menu bar.

## UPDATES

Open-WebUI updates are managed from the **Help** menu:

- **Check for Updates** - compares your installed version against the latest on PyPI. The result is shown in the System Log.
- **Update Open-WebUI** - stops WebUI, runs `pip install --upgrade open-webui`, then restarts WebUI automatically. Only available after a check confirms an update exists.

The console also checks for updates **automatically** the first time WebUI comes online each session.

## CONFIGURATION

Edit `config.json` to change paths, URLs, UI dimensions, and logging options
without modifying any code. The file is auto-generated with defaults if missing.
