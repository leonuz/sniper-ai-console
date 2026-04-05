import unittest

from app.domain.enums import ServiceKind, ServiceName, ServiceStatus
from app.domain.services import default_services


class DomainServicesTests(unittest.TestCase):
    def test_default_services_contains_expected_entries(self):
        services = default_services()
        self.assertEqual(len(services), 3)
        names = {service.name for service in services}
        self.assertEqual(
            names,
            {ServiceName.OLLAMA, ServiceName.OPEN_WEBUI, ServiceName.OPENCLAW},
        )

    def test_default_services_have_expected_ports(self):
        services = {service.name: service for service in default_services()}
        self.assertEqual(services[ServiceName.OLLAMA].port, 11434)
        self.assertEqual(services[ServiceName.OPEN_WEBUI].port, 8080)
        self.assertEqual(services[ServiceName.OPENCLAW].port, 18789)
        self.assertEqual(services[ServiceName.OPENCLAW].kind, ServiceKind.WSL_GATEWAY)
        self.assertEqual(services[ServiceName.OLLAMA].status, ServiceStatus.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
