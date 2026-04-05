# ARCHITECTURE

This document describes:

1. the **current architecture**
2. the **main design problems** in the current implementation
3. the **target architecture** for the refactor
4. the **refactor principles** that should guide future changes

The goal is not to rewrite blindly.
The goal is to move the project from a useful personal operations console to a cleaner and more extensible system.

---

## 1. Current Architecture

The current project is a Python desktop application built with DearPyGui.
Its code is already split into multiple modules, but responsibility boundaries are still fairly loose.

### Current modules

#### `main.py`
Responsibilities:
- application entry point
- DearPyGui setup
- viewport creation
- central update loop
- periodic UI refresh and service state checks

#### `config.py`
Responsibilities:
- read `config.json`
- generate default config if missing
- merge user config with defaults
- expose configuration values as module-level constants

#### `state.py`
Responsibilities:
- global mutable state storage
- tracked process handles
- telemetry history buffers
- process snapshot storage
- simple UI queue for thread-safe updates

#### `logger.py`
Responsibilities:
- visual log rendering in DearPyGui
- rotating file logging

#### `helpers.py`
Responsibilities:
- utility functions
- port checks
- process termination helpers
- uptime formatting
- GPU telemetry retrieval
- optional dependency detection

#### `engines.py`
Responsibilities:
- start / stop / restart operations for:
  - Ollama
  - Open-WebUI
  - OpenClaw
- WSL command execution for OpenClaw control

#### `monitoring.py`
Responsibilities:
- Ollama API integration
- model list refresh
- model pull/delete operations
- active model and VRAM inspection
- process table collection and rendering support

#### `ui.py`
Responsibilities:
- full DearPyGui UI construction
- theming
- menus
- tabs
- popup windows
- system tray integration
- binding UI actions directly to operational functions

#### `updater.py`
Responsibilities:
- detect installed Open-WebUI version
- inspect latest available version
- run upgrade flow
- restart Open-WebUI after update

---

## 2. Current Runtime Shape

The current application behaves roughly like this:

1. load config
2. build UI
3. start a background update loop
4. periodically:
   - sample CPU / RAM / GPU telemetry
   - check service ports
   - detect service transitions
   - update status lights and labels
   - trigger browser launch if needed
   - refresh process table periodically
5. let UI callbacks directly call operational functions

This runtime model is practical and straightforward.
It is also where some of the future pain comes from.

---

## 3. What works well today

The following parts are already valuable and should be preserved:

### A. Working desktop UX
The current DearPyGui app is fast, native, and operationally useful.
There is no strong reason to replace the UI framework right now.

### B. Working GPU telemetry path
The existing Intel ARC / GPU telemetry implementation is already integrated and operational.
This should be preserved unless a clearly superior and equally reliable approach is introduced.

### C. Useful real service control
The app already controls real services and not toy abstractions.
That operational reality matters.

### D. UI queue approach
The current queue-based mechanism for updating DearPyGui from background threads is simple and valid for this scale.
It may evolve, but it is not the core problem.

### E. Modular starting point
The code is not trapped in one file.
That makes controlled refactor realistic.

---

## 4. Current Design Problems

The code works, but several architectural issues will hurt as the project grows.

## 4.1 Platform coupling is spread across the codebase
Windows- and WSL-specific behavior exists in multiple places:

- `taskkill`
- `subprocess.CREATE_NO_WINDOW`
- `start msedge`
- PowerShell GPU counters
- `wsl -e bash -lc ...`

This means the project is not only configured for a specific platform.
It is **implemented through platform-specific assumptions in multiple layers**.

### Why this matters
- makes portability harder
- makes testing harder
- makes service logic and platform logic hard to separate

---

## 4.2 State is global and mutable
`state.py` currently contains cross-module mutable runtime state.
That works while the project is small, but has predictable costs:

- unclear ownership of mutations
- harder debugging
- harder testing
- increased risk of subtle state bugs as features grow

This is currently acceptable as a tactical implementation.
It is not a good long-term architecture.

---

## 4.3 UI and operational logic are too tightly linked
The UI layer currently knows too much about:

- service control behavior
- browser launching
- process orchestration
- tab-triggered data refresh logic

The result is that the UI is not just rendering state.
It is participating in operational decisions.

---

## 4.4 The main update loop does too much
The central update loop handles too many responsibilities at once:

- telemetry sampling
- status detection
- health transitions
- version fetching
- browser auto-launch
- process refresh scheduling
- status light updates

This makes the loop harder to reason about and harder to evolve safely.

---

## 4.5 Services are not modeled uniformly
Ollama, Open-WebUI, and OpenClaw are each handled with hand-written logic.
That is understandable early on, but it limits extensibility.

Without a real service abstraction, adding more services will increase duplication and inconsistency.

---

## 4.6 Error handling is too silent in some critical paths
Some operational code swallows exceptions or hides details.
That reduces observability exactly where an operations console needs it most.

A control console must fail visibly and diagnostically, not quietly.

---

## 4.7 Configuration is flexible but lightly validated
The current config loader supports merging defaults with user overrides, which is good.
But it does not provide strong validation, typing, or explicit failure modes.

As more settings are introduced, that will become fragile.

---

## 4.8 No test boundary yet
There is currently no clear testing boundary around:

- configuration behavior
- service control logic
- version parsing
- health detection
- model parsing
- state transitions

That makes future refactor work riskier than it needs to be.

---

## 5. Target Architecture

The target architecture should keep the current project practical, but create clearer separation between concerns.

The intended structure is a layered desktop application with a thin UI and explicit adapters.

---

## 5.1 Architectural layers

### A. Domain layer
Purpose:
- pure application concepts
- no DearPyGui
- no subprocess calls
- no platform-specific shell behavior

Examples:
- `ServiceName`
- `ServiceStatus`
- `TelemetrySnapshot`
- `ModelInfo`
- `ActiveModel`
- `ProcessInfo`
- `UpdateState`

This layer defines the vocabulary of the application.

---

### B. Application layer
Purpose:
- orchestration and use cases
- state transitions
- coordination between services and UI

Examples:
- start service
- stop service
- restart all
- refresh telemetry
- refresh model list
- load model
- unload model
- check updates

This layer is the behavioral core of the app.

---

### C. Adapter layer
Purpose:
- talk to the real world
- isolate external dependencies and platform specifics

Subcategories:

#### Platform adapters
- Windows process spawning
- Windows process kill
- browser launch
- PowerShell GPU telemetry
- WSL command execution

#### Service adapters
- Ollama HTTP client
- Open-WebUI service controller
- OpenClaw WSL controller

This is where environment-specific behavior should live.

---

### D. UI layer
Purpose:
- render current state
- dispatch user actions
- display logs and dialogs

The UI should not own business logic.
It should mostly bind buttons and menus to application-layer actions.

---

## 5.2 Recommended structural shape

A realistic target tree could look like this:

```text
sniper-ai-console/
├── app/
│   ├── domain/
│   │   ├── enums.py
│   │   ├── models.py
│   │   └── services.py
│   ├── application/
│   │   ├── store.py
│   │   ├── actions.py
│   │   ├── events.py
│   │   └── usecases/
│   │       ├── services.py
│   │       ├── telemetry.py
│   │       ├── models.py
│   │       └── updates.py
│   ├── adapters/
│   │   ├── platform/
│   │   │   ├── windows.py
│   │   │   ├── wsl.py
│   │   │   ├── browser.py
│   │   │   └── gpu.py
│   │   ├── ollama/
│   │   │   └── client.py
│   │   ├── openwebui/
│   │   │   └── service.py
│   │   └── openclaw/
│   │       └── service.py
│   ├── ui/
│   │   ├── app.py
│   │   ├── views.py
│   │   ├── components/
│   │   └── bindings.py
│   └── infrastructure/
│       ├── config.py
│       ├── logging.py
│       └── paths.py
├── tests/
├── main.py
└── config.json
```

This is a direction, not a strict mandate.
The important part is the separation of concerns.

---

## 5.3 Service abstraction goal

Each managed service should eventually behave like a first-class service object.

A service should conceptually expose behavior like:

- `start()`
- `stop()`
- `restart()`
- `status()`
- `version()`
- `health()`

Concrete implementations may differ internally, but the rest of the application should not care whether a service is:

- a Windows process
- a WSL-managed service
- an HTTP-only service
- a hybrid controlled service

That abstraction is one of the biggest improvements this project needs.

---

## 5.4 State model goal

The project should move away from free-form global mutable state toward a controlled application state model.

That does **not** require heavy framework machinery.
It can be a lightweight store with explicit state updates.

Desired properties:
- centralized runtime state
- explicit mutation paths
- easier UI rendering
- easier testing
- easier debugging

---

## 5.5 Polling model goal

The current monolithic update loop should eventually be split into focused pollers or coordinators.

Examples:
- telemetry poller
- service health poller
- process poller
- startup coordinator

This keeps timing logic explicit and reduces accidental coupling.

---

## 6. Refactor Principles

The refactor should follow these rules:

Phase 2 has started by introducing dedicated platform adapters for Windows process spawning, WSL command execution, browser launch, and GPU telemetry while keeping the legacy runtime behavior intact. Phase 3 continues that work by introducing explicit managed service adapters for Ollama, Open-WebUI, and OpenClaw. Phase 5 then begins breaking the legacy monolithic update loop into focused pollers coordinated by a runtime coordinator. Phase 6 starts thinning the UI layer by moving secondary windows, tray behavior, and tab bindings into dedicated UI modules.

### 1. Preserve working behavior first
Do not break:
- Intel ARC / GPU telemetry path
- working DearPyGui experience
- current Ollama / WebUI / OpenClaw operations

### 2. Refactor in layers, not as a rewrite event
Move one concern at a time.
Do not attempt a giant all-or-nothing migration.

### 3. Improve boundaries before adding major features
The architecture needs room to breathe before the app grows much more.

### 4. Avoid abstraction for its own sake
Every new abstraction should remove real coupling or duplication.

### 5. Make failures more visible, not less
Operational software should be diagnosable under failure.

### 6. Add tests around the core as boundaries become clearer
Testing should protect the refactor, not trail far behind it.

---

## 7. Near-Term Target

The short-term goal is not to become a platform.
The short-term goal is to become a **cleaner local operations console** with:

- better service boundaries
- better platform separation
- safer state handling
- better diagnostics
- clearer documentation

That is the correct next step.
