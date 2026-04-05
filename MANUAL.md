# USER MANUAL

This manual documents the **current behavior** of Sniper AI Console.
It is intentionally practical and focused on how the application behaves today.

For architecture and future direction, see:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [ROADMAP.md](ROADMAP.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)

---

## What the console does

Sniper AI Console is a local desktop control panel for a hybrid AI stack.
It is designed to manage:

- **Ollama** running locally on Windows
- **Open-WebUI** running locally on Windows
- **OpenClaw** running inside **WSL2 Ubuntu**

It also provides:

- system telemetry
- model management
- VRAM visibility
- process inspection
- operational logging

---

## Main UI Areas

The application is organized into:

- a **sidebar** for service control and quick stats
- main tabs for **Graphs**, **Models**, and **Processes**
- a persistent **System Log** visible across tabs
- top menu items for engine operations, portal actions, and help

---

## Sidebar

The sidebar contains:

- application branding / logo
- uptime display
- service status indicators
- quick CPU / RAM / GPU percentages
- memory usage summary
- control buttons

### Service status rows

Each managed service has:

- a coloured status light
- a text status (`ONLINE` / `OFFLINE`)
- a version label
- a `START` or `STOP` toggle button

### Service meanings

#### Ollama
- launched as a Windows-native process
- used for local model serving

#### WebUI
- launched as a Windows-native process
- used as the browser-facing UI for the local model stack

#### OpenClaw
- controlled via WSL2 commands
- treated as a gateway service managed from the console

---

## Service Control

### START / STOP toggles

Each service has its own dedicated toggle.

- if the service is offline, the button shows `START`
- if the service is online, the button shows `STOP`

The status light and state label are updated automatically.

### Start All

Available from the **Engines** menu.
This starts:

1. Ollama
2. Open-WebUI
3. OpenClaw

The system then monitors the stack for handshake completion and readiness.

### Restart All

Performs a controlled force shutdown, waits briefly, and relaunches the managed services.
Use this when:

- service state feels inconsistent
- a restart is faster than debugging a half-broken state
- configuration or models changed and you want a clean restart

### Force Shutdown

Performs a full shutdown sequence:

1. stop Ollama process tree
2. stop Open-WebUI process tree
3. run orphan cleanup for lingering WebUI-related workers
4. stop OpenClaw gateway inside WSL

This is the strongest stop action available from the app.

### Exit

Available from the **Engines** menu.
It performs a force shutdown and then closes the application.

---

## Telemetry / Graphs Tab

The **Graphs** tab shows real-time telemetry for:

- GPU usage
- CPU usage
- RAM usage

### Refresh behavior

The UI update loop refreshes telemetry roughly once per second.

### Hide / restore graphs

Each graph has an `X` button.
Use it to hide a graph temporarily.
Use `RESTORE ALL GRAPHS` to bring hidden graphs back.

### GPU note

The current implementation uses the existing working GPU telemetry path already present in the project.
This path is considered valuable and should be preserved during refactor unless there is a stronger replacement.

---

## Models Tab

The **Models** tab manages local Ollama models.

### Features available today

- refresh model list
- view installed models
- see model size, quantization, and family
- pull a model from the Ollama library
- delete a model with confirmation
- inspect the active model loaded in VRAM
- load a selected model into VRAM
- unload the active model from VRAM

### Model list refresh

The console automatically refreshes the model list when switching into the Models tab.
You can also refresh manually.

### Pulling a model

Enter a model name in the `Pull` field and click `PULL`.
Examples might include names such as:

- `llama3:8b`
- `mistral`
- `qwen2.5`

The log will show progress and completion state.

### Deleting a model

Click `DELETE` in the model table.
A confirmation dialog appears before the action is executed.

### VRAM / active model behavior

The top section of the Models tab displays:

- active model name
- estimated VRAM usage reported by Ollama

You can:

- `LOAD` a selected model into VRAM
- `UNLOAD` the currently active model

The current implementation uses Ollama API behavior based on `keep_alive` to load or unload a model.

---

## Processes Tab

The **Processes** tab shows the top processes by CPU usage.

### Current behavior

- refreshes periodically based on config
- highlights AI-related process names in cyan
- displays:
  - process name
  - CPU %
  - RAM usage in MB

### Why this exists

This view is meant for quick operational inspection, not full process forensics.
It helps answer:

- what is consuming resources right now?
- are the AI stack processes active?
- is something obviously stuck or runaway?

---

## System Log

The **System Log** is visible below the main tabs and stays accessible across all views.

### Log levels

- `DEBUG` — internal diagnostics
- `INFO` — normal operational messages
- `WARN` — non-fatal issues or caution states
- `SUCCESS` — successful actions
- `ERROR` — failures
- `MODEL` — model-specific operations

### File logging

If enabled in `config.json`, log messages are also written to a rotating log file.
By default that file is:

- `sniper_ai.log`

This is useful for post-mortem debugging when the visual log is no longer visible.

---

## Portal Menu

The **Portal** menu contains browser shortcuts.

### Open WebUI Portal
Opens the configured WebUI portal URL.

### Open OpenClaw Dashboard
Opens the configured OpenClaw dashboard URL.

The exact command used to launch the browser is controlled by configuration.

---

## Help Menu

The **Help** menu provides:

- `Manual`
- `Changelog`
- `Who Am I`
- `Check for Updates`
- `Update Open-WebUI`

### Manual
Shows the current user manual.

### Changelog
Shows release notes and version history.

### Who Am I
Displays project and author metadata.

### Check for Updates
Checks whether a newer Open-WebUI version is available.

### Update Open-WebUI
Runs the update flow for Open-WebUI.
This is currently an operational helper inside the console, not a full project auto-updater.

---

## Open-WebUI Update Flow

The current update workflow is:

1. determine installed Open-WebUI version
2. determine latest available version from package index output
3. stop Open-WebUI if needed
4. run `pip install --upgrade open-webui`
5. restart Open-WebUI

This works as a practical local maintenance feature, but it is not yet a generalized update subsystem.

---

## System Tray

If the optional tray dependencies are installed, the app supports minimizing to the system tray.

### Tray actions
- show / restore the console
- exit the application

### Required packages
- `pystray`
- `pillow`

---

## Configuration

All settings are controlled through `config.json`.

### Important keys

#### `paths`
Executable paths for:
- Ollama
- Open-WebUI
- OpenClaw in WSL

#### `urls`
Configured URLs for:
- portal
- Ollama API
- WebUI local API
- model library
- OpenClaw dashboard

#### `ui`
Controls:
- viewport size
- graph sizes
- refresh intervals
- process table limits

#### `engines`
Controls:
- ports
- browser command
- restart timing
- cleanup timing

#### `logging`
Controls:
- whether file logging is enabled
- log filename
- max log size
- rotation count

#### `gpu`
Controls:
- display label
- telemetry method metadata

---

## Operational Assumptions

The current application assumes a specific environment shape:

- Windows-native local executables for Ollama and Open-WebUI
- WSL2 available for OpenClaw control
- browser launch command compatible with the configured Windows shell behavior
- local ports matching the current service assumptions

This is important: **the current project is environment-aware, not fully abstracted yet**.
That is one of the main reasons a refactor is planned.

---

## Known limitations

Current limitations include:

- strong coupling to one Windows + WSL workflow
- global mutable state in the runtime
- some silent exception handling that should be improved
- no automated test suite yet
- no formal packaging strategy yet
- no generalized plugin or service framework yet

These are documented more fully in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Troubleshooting

### A service says online/offline unexpectedly
Possible causes:
- tracked process died
- port check is stale or misleading
- service was started or killed outside the console

### OpenClaw does not start
Check:
- WSL2 is installed and working
- the configured OpenClaw path inside WSL is correct
- the gateway port matches the actual OpenClaw configuration

### GPU graph shows zero
Possible causes:
- the current telemetry method failed
- performance counters are unavailable
- no meaningful GPU engine activity is present

### Model actions fail
Check:
- Ollama is online
- the configured API URL is correct
- the model name exists in Ollama library when pulling

### WebUI update check fails
Possible causes:
- `pip` path is wrong
- environment is missing
- package index lookup changed format
- network access failed

---

## Practical Scope

Sniper AI Console should currently be understood as:

**a useful local operations console for a real AI workstation, not yet a generalized operations platform**.

That is fine.
The next step is to improve the architecture without losing the working behavior.
