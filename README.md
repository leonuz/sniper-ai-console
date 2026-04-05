# Sniper AI Console

<p align="center">
  <img src="logo.png" alt="Sniper AI Console" width="300">
</p>

**Sniper AI Console** is a native desktop operations console for managing a local AI stack built around **Ollama**, **Open-WebUI**, and **OpenClaw**.

The project is currently implemented as a **Python + DearPyGui** desktop application focused on a real hybrid environment:

- **Windows** for native desktop UX, local process control, and GPU telemetry
- **WSL2 Ubuntu** for OpenClaw gateway control
- **Ollama** for local model serving
- **Open-WebUI** for browser-based interaction with the model stack

This repository already works as a practical personal operations console.
The next stage is to turn it into a cleaner, more extensible architecture without breaking the parts that already work well.

---

## Current Status

Sniper AI Console is in an **early but functional** stage.

Today it already provides:

- individual **START / STOP** service control for Ollama, Open-WebUI, and OpenClaw
- real-time **CPU / RAM / GPU telemetry**
- **Ollama model management** (list, pull, delete)
- **VRAM management** (inspect active model, load, unload, switch)
- **process monitoring** with AI-related process highlighting
- **Open-WebUI update checks and upgrades**
- **OpenClaw gateway control via WSL2**
- rotating **file logging** for diagnostics
- **system tray** support

The project is intentionally opinionated around a real working environment rather than a generic cross-platform package.
That is useful for speed, but it also means the current implementation is tightly coupled to one platform and one deployment shape.

---

## Why this project exists

The goal is not just to launch a few tools.
The real goal is to provide a **single local control surface** for an AI workstation or AI-enabled laptop:

- start and stop critical services fast
- know what is online or broken right now
- inspect resource pressure quickly
- manage models without dropping into multiple terminals
- bridge Windows-native tools and Linux/WSL workflows
- reduce friction in daily operation

---

## Technology Stack

### Runtime
- **Python 3.10+**

### UI
- **DearPyGui**

### Monitoring / utilities
- **psutil**
- **requests**
- **pystray**
- **pillow**

### Managed services
- **Ollama**
- **Open-WebUI**
- **OpenClaw**

### Platform assumptions
- **Windows 10/11**
- **WSL2 Ubuntu** for OpenClaw integration

---

## Current Architecture

The current codebase is modular, but still relatively small and tightly integrated.

### Main modules

- `main.py`
  - entry point
  - viewport creation
  - application update loop

- `config.py`
  - loads `config.json`
  - provides merged defaults

- `state.py`
  - shared mutable application state
  - simple cross-thread UI queue

- `logger.py`
  - visual app log
  - rotating file log

- `helpers.py`
  - utility functions
  - process control helpers
  - GPU telemetry helpers

- `engines.py`
  - start/stop/toggle logic for Ollama, Open-WebUI, OpenClaw

- `monitoring.py`
  - telemetry collection
  - process table
  - Ollama model operations
  - active model / VRAM operations

- `ui.py`
  - DearPyGui layout, themes, menus, dialogs

- `updater.py`
  - Open-WebUI version check and upgrade flow

### Architectural reality

The current project is best described as:

**a functional desktop operations console with a modular code layout, but with significant coupling between UI, process control, platform details, and service-specific logic**.

That is acceptable for the current project size.
It is not the right long-term shape if the console is going to keep growing.

For the forward-looking design, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Current Strengths

- already useful in real day-to-day operation
- modular enough to refactor without a total rewrite
- clear focus on practical local AI stack management
- UI is fast and native
- working Intel ARC telemetry path is already integrated
- OpenClaw WSL integration is already functional
- model operations and VRAM control are real, not mocked

---

## Current Weaknesses

- strong platform coupling to one Windows + WSL workflow
- global mutable state
- hardcoded service assumptions in several layers
- one central update loop doing too much
- some error handling is too silent
- no test suite yet
- no formal packaging / installer / CI pipeline yet

---

## Direction of the Refactor

The intended direction is **not** to replace what already works.
It is to reorganize the project so the working parts become easier to maintain, test, and extend.

Key principles for the next stage:

1. **Keep the working Intel ARC and current library integrations intact** unless there is a clear reason to change them.
2. **Separate domain logic from platform-specific code**.
3. **Treat services as first-class objects** instead of scattered special cases.
4. **Make the UI thinner** and push operational logic downward.
5. **Introduce a controlled application state model**.
6. **Improve observability and error handling** before adding too many new features.

See:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [ROADMAP.md](ROADMAP.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)

---

## Installation

### Requirements

- Windows 10/11
- Python 3.10+
- Ollama installed locally
- Open-WebUI installed in a Python virtual environment
- OpenClaw available inside WSL2 Ubuntu

### Python dependencies

```bash
pip install dearpygui psutil requests pillow pystray
```

> `requests`, `pillow`, and `pystray` are optional in some flows, but recommended for full functionality.

### Clone the repository

```bash
git clone https://github.com/leonuz/sniper-ai-console.git
cd sniper-ai-console
```

### Configure paths

Edit `config.json` to match your environment.
A typical shape is:

```json
{
  "paths": {
    "ollama": "C:\\path\\to\\ollama.exe",
    "webui": "C:\\path\\to\\open-webui\\venv\\Scripts\\open-webui.exe",
    "openclaw": "/home/youruser/.npm-global/bin/openclaw"
  }
}
```

### Run

```bash
python main.py
```

Or run:

```bash
start.bat
```

---

## Configuration

All runtime settings live in `config.json`.

### Main sections

| Section | Purpose |
|---|---|
| `app` | app metadata |
| `paths` | executable paths |
| `urls` | local and dashboard URLs |
| `files` | icon and logo filenames |
| `ui` | viewport sizes and refresh intervals |
| `engines` | ports, browser command, delays |
| `logging` | file log settings |
| `gpu` | GPU label and telemetry method |

The current config loader supports default generation and deep merging with user-provided values.
Future refactor work will strengthen validation and typing around configuration.

---

## Documentation Map

- [MANUAL.md](MANUAL.md) — current usage guide
- [CHANGELOG.md](CHANGELOG.md) — version history
- [ARCHITECTURE.md](ARCHITECTURE.md) — current architecture, design issues, target architecture
- [ROADMAP.md](ROADMAP.md) — refactor roadmap and phases
- [DEVELOPMENT.md](DEVELOPMENT.md) — development notes and project structure

---

## Project Structure

```text
sniper-ai-console/
├── main.py
├── config.py
├── state.py
├── logger.py
├── helpers.py
├── engines.py
├── monitoring.py
├── updater.py
├── ui.py
├── config.json
├── README.md
├── MANUAL.md
├── CHANGELOG.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── DEVELOPMENT.md
├── start.bat
├── icon.ico
├── logo.png
└── screenshots/
```

---

## Refactor Philosophy

This project should evolve through **controlled restructuring**, not a blind rewrite.

That means:

- document first
- preserve working behavior
- improve module boundaries
- add architecture before adding abstraction for its own sake
- make each refactor phase small enough to validate safely

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Author

**Leonuz**

GitHub: <https://github.com/leonuz>
