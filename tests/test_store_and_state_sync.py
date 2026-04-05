import unittest

from app.application.state_sync import (
    mark_all_services_unknown,
    update_active_model,
    update_models,
    update_processes,
    update_service_status,
    update_telemetry,
)
from app.application.store import store
from app.domain.enums import ServiceName, ServiceStatus
from app.domain.models import ActiveModelInfo, ModelInfo, ProcessInfo, TelemetrySnapshot


class StoreAndStateSyncTests(unittest.TestCase):
    def setUp(self):
        mark_all_services_unknown()
        update_models([])
        update_processes([])
        update_active_model(ActiveModelInfo())
        update_telemetry(TelemetrySnapshot())

    def test_update_service_status_changes_target_service(self):
        update_service_status(ServiceName.OLLAMA, status=ServiceStatus.ONLINE, version="1.0")
        snapshot = store.get_snapshot()
        ollama = next(s for s in snapshot.services if s.name == ServiceName.OLLAMA)
        self.assertEqual(ollama.status, ServiceStatus.ONLINE)
        self.assertEqual(ollama.version, "1.0")

    def test_update_telemetry_replaces_snapshot(self):
        update_telemetry(TelemetrySnapshot(cpu_percent=55.0, uptime="00:10:00"))
        snapshot = store.get_snapshot()
        self.assertEqual(snapshot.telemetry.cpu_percent, 55.0)
        self.assertEqual(snapshot.telemetry.uptime, "00:10:00")

    def test_update_collections_replace_store_values(self):
        update_models([ModelInfo(name="llama3:8b", size_gb=8.0)])
        update_processes([ProcessInfo(name="ollama.exe", cpu_percent=40.0, ram_mb=512.0)])
        update_active_model(ActiveModelInfo(name="llama3:8b", vram_gb=7.8))

        snapshot = store.get_snapshot()
        self.assertEqual(len(snapshot.models), 1)
        self.assertEqual(snapshot.models[0].name, "llama3:8b")
        self.assertEqual(len(snapshot.processes), 1)
        self.assertEqual(snapshot.active_model.name, "llama3:8b")


if __name__ == "__main__":
    unittest.main()
