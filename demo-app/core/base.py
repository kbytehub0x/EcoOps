"""Shared Core Utilities for Demo Application.

Modifying any file in this module triggers the EcoOps safety fallback,
forcing GitLab to run 100% of all tests across all services.
"""

from typing import Dict, Any


class CoreDatabaseClient:
    def __init__(self, dsn: str = "sqlite:///:memory:"):
        self.dsn = dsn
        self.connected = True

    def query(self, sql: str) -> Dict[str, Any]:
        return {"status": "success", "sql": sql, "rows": []}


class BaseService:
    def __init__(self, name: str):
        self.name = name
        self.db = CoreDatabaseClient()
