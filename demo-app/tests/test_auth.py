"""Unit tests for Auth Service."""

import unittest
from demo-app.services.auth.auth_service import AuthService


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.auth = AuthService()

    def test_authenticate_success(self):
        self.assertTrue(self.auth.authenticate("alice", "secret123"))

    def test_authenticate_failure(self):
        self.assertFalse(self.auth.authenticate("alice", "wrongpass"))

    def test_register_new_user(self):
        self.assertTrue(self.auth.register("charlie", "newpass"))
        self.assertTrue(self.auth.authenticate("charlie", "newpass"))


if __name__ == "__main__":
    unittest.main()
