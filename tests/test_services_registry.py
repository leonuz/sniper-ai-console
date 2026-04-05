import unittest

from app.domain.enums import ServiceName


class ServicesRegistryTests(unittest.TestCase):
    def test_registry_module_exports_expected_names(self):
        with open("app/application/services_registry.py", "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("ServiceName.OLLAMA", content)
        self.assertIn("ServiceName.OPEN_WEBUI", content)
        self.assertIn("ServiceName.OPENCLAW", content)
        self.assertIn("def get_service", content)

    def test_service_name_enum_still_matches_registry_expectations(self):
        self.assertEqual(ServiceName.OLLAMA.value, "ollama")
        self.assertEqual(ServiceName.OPEN_WEBUI.value, "open-webui")
        self.assertEqual(ServiceName.OPENCLAW.value, "openclaw")


if __name__ == "__main__":
    unittest.main()
