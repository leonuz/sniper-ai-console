# DEVELOPMENT

This document is for maintainers and future contributors working on Sniper AI Console.

It explains how the project is structured today, how to run it, and how to approach the upcoming refactor without making the code worse.

---

## Development goals

When working on this project, optimize for:

- preserving currently working behavior
- reducing coupling
- making module boundaries clearer
- improving diagnosability
- avoiding unnecessary rewrites

Do not refactor just to make the tree look fancier.
Every structural change should solve a real maintenance problem.

---

## Current repository layout

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

### Current module responsibilities

- `main.py` — app startup and update loop
- `config.py` — config loader and defaults
- `state.py` — runtime shared state
- `logger.py` — visual and file logging
- `helpers.py` — low-level helpers and utility functions
- `engines.py` — engine start/stop logic
- `monitoring.py` — telemetry and model operations
- `updater.py` — Open-WebUI update flow
- `ui.py` — DearPyGui rendering and user interactions

---

## Running the project

### Requirements
- Windows 10/11
- Python 3.10+
- Ollama installed locally
- Open-WebUI installed locally in a Python environment
- WSL2 Ubuntu available for OpenClaw

### Install dependencies

```bash
pip install dearpygui psutil requests pillow pystray
```

### Run

```bash
python main.py
```

Or use:

```bash
start.bat
```

---

## Configuration notes

The app reads `config.json` from the repository root.
If the file is missing, defaults are generated automatically.

Current important config areas:
- executable paths
- local URLs
- UI sizes
- engine ports
- browser command
- logging parameters
- GPU metadata

### Development caution
Do not casually hardcode new paths, URLs, or executable assumptions in multiple files.
If a value belongs to environment configuration, it should go through the config boundary.

---

## Current technical constraints

This project currently assumes:

- Windows-native process control for Ollama and Open-WebUI
- WSL-mediated control for OpenClaw
- the current GPU telemetry path remains valid
- DearPyGui is the active presentation layer

These constraints are real and should be acknowledged rather than hidden.
The refactor should reduce coupling to them, not pretend they do not exist.

---

## Refactor guidance

### 1. Preserve behavior before improving elegance
If a subsystem is already working reliably, do not replace it just because a cleaner abstraction seems possible.

Example:
- keep the working Intel ARC GPU integration unless a better replacement is proven

### 2. Split responsibilities, not files for vanity
The goal is not more files.
The goal is better boundaries.

### 3. Prefer adapters for environment-specific behavior
Platform-specific code should migrate toward dedicated adapters.
That includes:
- PowerShell GPU calls
- WSL command execution
- browser launching
- Windows process termination and spawn flags

### 4. UI should become thinner over time
DearPyGui code should mostly:
- render state
- dispatch actions
- show dialogs and logs

It should not keep absorbing operational logic.

### 5. Avoid introducing complex frameworks too early
The current project does not need enterprise architecture theater.
It needs better separation and more discipline.

### 6. Reduce silent failures
Do not swallow important exceptions without logging.
If something can fail operationally, it should be diagnosable.

---

## Suggested near-term directory evolution

A likely future structure is:

```text
sniper-ai-console/
├── app/
│   ├── domain/
│   ├── application/
│   ├── adapters/
│   ├── ui/
│   └── infrastructure/
├── tests/
├── main.py
└── config.json
```

This should be introduced gradually.
Do not move everything at once unless there is a compelling reason.

---

## Testing strategy

The project now has an initial automated `unittest` suite for core logic.
It should continue to grow during the refactor.

### Good first test targets
- config merge behavior
- version parsing logic
- service state / health logic
- model parsing from Ollama API responses
- store/state transitions once introduced

### Current test coverage
- config validation
- mapper functions
- default service definitions
- store/state sync behavior
- lightweight registry expectations

### What not to test first
- full DearPyGui rendering
- visual styling details
- platform process behavior through brittle end-to-end hacks

Start by testing the logic that is easiest to isolate and most valuable to protect.

---

## Logging and observability

The project already has:
- visual log output
- rotating file log output

That is good.
What needs improvement is consistency of error reporting.

Future development should favor:
- visible operational failures
- clear error messages
- fewer silent exception paths
- easier diagnosis when environment assumptions are wrong

---

## Documentation discipline

When changing the project in meaningful ways, update the relevant docs as part of the same work.

At minimum, consider whether changes require updates to:
- `README.md`
- `MANUAL.md`
- `CHANGELOG.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `DEVELOPMENT.md`

This project should not drift into undocumented architecture.

---

## Commit style guidance

There is no strict required convention yet, but commits should be:
- specific
- readable
- scoped to one meaningful change when practical

Good examples:
- `Document current architecture and refactor roadmap`
- `Add platform adapter scaffolding for Windows and WSL`
- `Move service status models into domain layer`
- `Introduce centralized app state store`

Bad examples:
- `fix stuff`
- `updates`
- `misc changes`

---

## If you are touching the refactor next

Recommended order:

1. scaffold new package layout
2. introduce domain models and enums
3. isolate platform adapters
4. introduce service abstractions
5. move state toward a controlled store
6. split polling responsibilities
7. thin the UI layer
8. add tests

That order will produce less chaos than rewriting from the outside inward.

---

## Bottom line

Sniper AI Console already works as a real local operations console.
The right next move is disciplined restructuring, not dramatic reinvention.

One important consequence of that approach: once the refactor reached Phase 8, the application became a candidate for real smoke testing on the target Windows 11 workstation instead of waiting for a final rewrite milestone.
