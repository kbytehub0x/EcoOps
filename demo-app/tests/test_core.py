"""Unit tests for Core Shared Utilities."""

import unittest
from demo-app.core.base import CoreDatabaseClient, BaseService


class TestCore(unittest.TestCase):
    def test_database_connection(self):
        client = CoreDatabaseClient()
        self.assertTrue(client.connected)

    def test_database_query(self):
        client = CoreDatabaseClient()
        res = client.query("SELECT 1")
        self.assertEqual(res["status"], "success")

    def test_base_service_init(self):
        service = BaseService("test_service")
        self.assertEqual(service.name, "test_service")
        self.assertTrue(service.db.connected)


if __name__ == "__main__":
    unittest.main()
