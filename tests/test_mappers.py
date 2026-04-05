import unittest

from app.application.mappers import (
    active_model_info,
    model_info_from_ollama,
    process_info,
    telemetry_snapshot,
)


class MapperTests(unittest.TestCase):
    def test_telemetry_snapshot_maps_fields(self):
        snapshot = telemetry_snapshot(
            cpu_percent=10.5,
            ram_percent=44.2,
            gpu_percent=12.1,
            ram_used_gb=12.3,
            ram_total_gb=32.0,
            uptime="01:02:03",
        )
        self.assertEqual(snapshot.cpu_percent, 10.5)
        self.assertEqual(snapshot.uptime, "01:02:03")

    def test_process_info_highlights_known_ai_processes(self):
        proc = process_info("ollama.exe", 20.0, 300.0)
        self.assertTrue(proc.highlighted)

        proc2 = process_info("explorer.exe", 2.0, 150.0)
        self.assertFalse(proc2.highlighted)

    def test_model_info_from_ollama_maps_values(self):
        model = {
            "name": "llama3:8b",
            "size": 8 * (1024 ** 3),
            "details": {
                "quantization_level": "Q4_K_M",
                "family": "llama",
            },
        }
        mapped = model_info_from_ollama(model)
        self.assertEqual(mapped.name, "llama3:8b")
        self.assertEqual(mapped.quantization, "Q4_K_M")
        self.assertEqual(mapped.family, "llama")
        self.assertAlmostEqual(mapped.size_gb, 8.0, places=2)

    def test_active_model_info_defaults(self):
        active = active_model_info()
        self.assertEqual(active.name, "")
        self.assertEqual(active.vram_gb, 0.0)


if __name__ == "__main__":
    unittest.main()
