# ROADMAP

This roadmap documents the intended refactor path for Sniper AI Console.

The project already works.
The goal is not to discard that work.
The goal is to move it into a cleaner and more durable architecture.

---

## Guiding idea

Refactor for **clarity, maintainability, and extensibility** while preserving the parts that already provide real value.

Especially important:

- keep the current Intel ARC / GPU telemetry path working
- keep current Windows + WSL operational behavior working
- avoid a big-bang rewrite
- improve structure before chasing too many new features

---

## Phase 0 — Documentation and planning

### Goal
Create an explicit baseline before moving code.

### Deliverables
- refreshed `README.md`
- improved `MANUAL.md`
- updated `CHANGELOG.md`
- new `ARCHITECTURE.md`
- new `ROADMAP.md`
- new `DEVELOPMENT.md`

### Why this matters
This makes the refactor intentional.
Without this phase, future changes drift and lose context.

### Status
- completed

---

## Phase 1 — Create the new structure without breaking behavior

### Goal
Introduce a new project structure alongside the current code.

### Main work
- create `app/` package structure
- introduce domain models and enums
- introduce infrastructure modules for config and logging boundaries
- leave current runtime behavior intact while scaffolding the target layout

### Deliverables
- initial `app/` tree
- typed domain models for services, telemetry, processes, and models
- basic application state model introduced without full migration yet

### Success criteria
- project still runs
- no behavior regressions
- future code has a proper place to live

### Phase 1 progress
- added `app/` package scaffold
- added initial domain enums and dataclasses
- added a lightweight application store scaffold
- added forward-compatible infrastructure wrappers for config and logging
- kept the legacy runtime active so behavior remains unchanged while the new structure is introduced

---

## Phase 2 — Separate platform-specific behavior into adapters

### Goal
Move Windows- and WSL-specific behavior out of mixed utility modules.

### Main work
- isolate Windows process management
- isolate browser launching
- isolate PowerShell GPU reading
- isolate WSL command execution

### Deliverables
- platform adapters under a dedicated package
- reduced platform logic in generic modules

### Phase 2 progress
- added platform adapters for Windows process spawning, WSL command execution, browser launch, and GPU telemetry
- connected the existing runtime to those adapters without changing the external behavior of the app
- preserved the current Intel ARC / PowerShell GPU telemetry path by moving it behind an adapter boundary

### Success criteria
- UI no longer directly depends on shell/platform commands
- service control logic becomes easier to reason about

---

## Phase 3 — Introduce service abstractions

### Goal
Represent Ollama, Open-WebUI, and OpenClaw through a common service-oriented model.

### Main work
- define service interfaces / contracts
- implement concrete service controllers
- unify status / version / start / stop behavior patterns

### Deliverables
- `OllamaService`
- `OpenWebUIService`
- `OpenClawService`
- shared service status model

### Phase 3 progress
- introduced explicit managed service adapters for Ollama, Open-WebUI, and OpenClaw
- added a shared domain contract for managed services and service health
- rewired `engines.py` to delegate service start/stop/version behavior through the new service registry
- kept the current UX and external runtime behavior intact while reducing engine-specific logic in the legacy entry points

### Success criteria
- services can be rendered and managed more uniformly
- less engine-specific branching scattered across the app

---

## Phase 4 — Replace global mutable runtime state with a controlled store

### Goal
Move away from loosely shared globals.

### Main work
- define application state object
- define update paths / actions / events
- migrate runtime flags and snapshots gradually

### Deliverables
- centralized store
- explicit state transitions
- clearer ownership of runtime values

### Phase 4 progress
- added explicit state-sync helpers to project the legacy runtime into the new `AppStore`
- added mapping helpers for telemetry, process, model, and active-model snapshots
- connected the update loop and monitoring paths so key runtime data now updates the new store in parallel with the legacy state module
- kept `state.py` as the active compatibility layer while beginning the migration toward explicit state updates

### Success criteria
- state changes are easier to trace
- UI rendering depends on structured state instead of scattered globals

---

## Phase 5 — Break up the monolithic update loop

### Goal
Separate periodic responsibilities into focused components.

### Main work
- split telemetry polling
- split service health polling
- split process polling
- isolate startup / handshake coordination

### Deliverables
- dedicated poller/coordinator modules
- slimmer main loop or orchestrator layer

### Success criteria
- timing behavior is clearer
- easier to test and debug periodic logic

---

## Phase 6 — Thin the UI layer

### Goal
Reduce operational logic inside DearPyGui construction and callbacks.

### Main work
- push business logic out of `ui.py`
- make the UI render state and dispatch actions
- group UI components by responsibility

### Deliverables
- cleaner UI module boundaries
- reduced direct coupling between UI and service code

### Success criteria
- the UI mostly presents state rather than orchestrating service logic

---

## Phase 7 — Improve configuration and diagnostics

### Goal
Make the app safer and easier to operate under failure.

### Main work
- strengthen config validation
- reduce silent exception handling
- improve structured logging and failure visibility
- surface degraded states more clearly

### Deliverables
- better config boundary
- better startup diagnostics
- better runtime observability

### Success criteria
- failures are actionable
- broken config or environment issues are easier to diagnose

---

## Phase 8 — Add tests around the core

### Goal
Protect the refactor and enable safer iteration.

### Main work
- add tests for config behavior
- add tests for version parsing
- add tests for service status logic
- add tests for model parsing and transformations
- add tests for store or state transitions

### Deliverables
- initial automated test suite

### Success criteria
- future refactors have guardrails
- logic changes become lower-risk

---

## Phase 9 — Packaging and polish

### Goal
Prepare the project for cleaner installation and long-term maintainability.

### Main work
- define dependency management more clearly
- add packaging metadata
- evaluate installer or build packaging strategy
- consider CI for lint/test validation

### Deliverables
- cleaner developer setup
- cleaner future release flow

### Success criteria
- easier to install, validate, and maintain

---

## What should not change early

The following should be treated as stable unless there is a very strong reason otherwise:

- the working GPU / Intel ARC telemetry path
- the current DearPyGui UI framework
- the use of current practical dependencies if they are already solving the job
- WSL-based OpenClaw control model

The architecture is the problem to solve first, not the fact that these components currently work.

---

## What success looks like

A successful refactor will produce a project that is still recognizably the same console, but with:

- cleaner boundaries
- lower coupling
- safer state handling
- clearer error behavior
- easier extension to additional services and capabilities

That is the right direction.
