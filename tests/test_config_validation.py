import unittest

from app.infrastructure.config_runtime import RuntimeConfig, RuntimePaths, RuntimePorts
from app.infrastructure.config_validation import validate_runtime_config


class ConfigValidationTests(unittest.TestCase):
    def test_valid_runtime_config_passes(self):
        cfg = RuntimeConfig(
            app_name="Sniper AI Console",
            app_version="v1.0",
            paths=RuntimePaths(
                ollama="C:/ollama/ollama.exe",
                webui="C:/webui/open-webui.exe",
                openclaw="/home/user/.npm-global/bin/openclaw",
            ),
            ports=RuntimePorts(ollama=11434, webui=8080, openclaw=18789),
            portal_url="https://example.local",
            openclaw_dashboard="http://127.0.0.1:18789",
            browser_command="start msedge",
        )

        result = validate_runtime_config(cfg)
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])

    def test_invalid_ports_fail_validation(self):
        cfg = RuntimeConfig(
            app_name="Sniper AI Console",
            app_version="v1.0",
            paths=RuntimePaths(ollama="a", webui="b", openclaw="c"),
            ports=RuntimePorts(ollama=-1, webui=0, openclaw=70000),
            portal_url="",
            openclaw_dashboard="",
            browser_command="",
        )

        result = validate_runtime_config(cfg)
        self.assertFalse(result.ok)
        self.assertGreaterEqual(len(result.errors), 3)

    def test_missing_paths_fail_validation(self):
        cfg = RuntimeConfig(
            app_name="Sniper AI Console",
            app_version="v1.0",
            paths=RuntimePaths(ollama="", webui="", openclaw=""),
            ports=RuntimePorts(ollama=11434, webui=8080, openclaw=18789),
            portal_url="https://example.local",
            openclaw_dashboard="http://127.0.0.1:18789",
            browser_command="start msedge",
        )

        result = validate_runtime_config(cfg)
        self.assertFalse(result.ok)
        self.assertIn("paths.ollama is empty", result.errors)
        self.assertIn("paths.webui is empty", result.errors)
        self.assertIn("paths.openclaw is empty", result.errors)


if __name__ == "__main__":
    unittest.main()
