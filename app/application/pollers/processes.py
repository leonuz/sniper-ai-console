"""Process poller wrapper for the legacy process table logic."""

from __future__ import annotations

import state
from monitoring import collect_procs, update_proc_table


class ProcessPoller:
    def collect(self) -> None:
        collect_procs()

    def queue_ui_updates(self) -> None:
        state.queue(update_proc_table)
