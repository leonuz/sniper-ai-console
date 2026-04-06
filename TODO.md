# TODO

## Next priorities

### 1. Packaging and dependency management
- add `requirements.txt` or `pyproject.toml`
- document a cleaner install path for Windows 11
- make dependency expectations explicit and reproducible

### 2. CI / validation automation
- add a basic CI workflow to run unit tests automatically
- optionally add lightweight linting or formatting validation

### 3. Continue migrating away from legacy runtime state
- reduce direct dependence on `state.py`
- move more runtime behavior toward the new application store
- reduce remaining legacy coupling between old and new modules

### 4. Continue thinning large modules
- split more of `ui.py` into larger reusable components if justified
- keep shrinking legacy operational hot spots where that improves clarity

### 5. Service and diagnostics polish
- improve service health reporting beyond current online/offline checks
- make more degraded states visible in the UI when useful
- tighten runtime diagnostics based on real-world test feedback

### 6. Packaging / release ergonomics
- evaluate Windows-friendly packaging options
- consider installer or packaged desktop distribution when the project stabilizes further

---

## Completed recently
- full architecture refactor phases 1-8 completed
- documentation rewritten and expanded
- smoke-test documentation added
- GitHub repo updated through post-phase-8 refactor commits
- real smoke test validated successfully on the target machine and OS:
  - Windows 11
  - Lenovo ThinkPad X1 Carbon Gen 13
  - Intel ARC 140V GPU
  - 32 GB RAM
- validated behaviors:
  - GUI startup
  - telemetry updates
  - GPU activity visibility during Open-WebUI query
  - service stop/start cycles
  - correct ONLINE/OFFLINE transitions
  - no traceback during validated smoke test
  - no lingering processes after tested stop/start flows
