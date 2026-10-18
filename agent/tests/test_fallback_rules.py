"""Unit tests for fail-safe fallback rules."""

import unittest
from agent.app.fallback_rules import should_fallback_to_full_suite


class TestFallbackRules(unittest.TestCase):

    def test_empty_diff_triggers_fallback(self):
        fallback, reason = should_fallback_to_full_suite([])
        self.assertTrue(fallback)
        self.assertIn("No changed files", reason)

    def test_isolated_auth_change_does_not_trigger_fallback(self):
        files = ["demo-app/services/auth/auth_service.py"]
        fallback, reason = should_fallback_to_full_suite(files)
        self.assertFalse(fallback)
        self.assertIn("safely mapped", reason)

    def test_isolated_billing_change_does_not_trigger_fallback(self):
        files = ["demo-app/services/billing/billing_service.py"]
        fallback, reason = should_fallback_to_full_suite(files)
        self.assertFalse(fallback)
        self.assertIn("safely mapped", reason)

    def test_core_change_triggers_fallback(self):
        files = [
            "demo-app/services/auth/auth_service.py",
            "demo-app/core/base.py",
        ]
        fallback, reason = should_fallback_to_full_suite(files)
        self.assertTrue(fallback)
        self.assertIn("Critical shared file", reason)
        self.assertIn("demo-app/core/base.py", reason)

    def test_gitlab_ci_change_triggers_fallback(self):
        files = [".gitlab-ci.yml"]
        fallback, reason = should_fallback_to_full_suite(files)
        self.assertTrue(fallback)
        self.assertIn("Critical shared file", reason)

    def test_requirements_txt_change_triggers_fallback(self):
        files = ["requirements.txt"]
        fallback, reason = should_fallback_to_full_suite(files)
        self.assertTrue(fallback)
        self.assertIn("Critical shared file", reason)

    def test_unknown_file_triggers_fallback(self):
        files = ["random_script.py"]
        fallback, reason = should_fallback_to_full_suite(files)
        self.assertTrue(fallback)
        self.assertIn("Unmapped or unknown file", reason)


if __name__ == "__main__":
    unittest.main()
