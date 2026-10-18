"""Unit tests for diff parser and dynamic child-pipeline generation."""

import unittest
from agent.app.diff_parser import resolve_tests_for_changes, generate_child_pipeline_yaml, FULL_TEST_SUITE


class TestDiffParser(unittest.TestCase):

    def test_resolve_auth_service_only(self):
        changed = ["demo-app/services/auth/auth_service.py"]
        res = resolve_tests_for_changes(changed)
        self.assertFalse(res["fallback_triggered"])
        self.assertEqual(res["selected_tests"], ["demo-app/tests/test_auth.py"])
        self.assertEqual(res["selected_test_files_count"], 1)

    def test_resolve_billing_service_only(self):
        changed = ["demo-app/services/billing/billing_service.py"]
        res = resolve_tests_for_changes(changed)
        self.assertFalse(res["fallback_triggered"])
        self.assertEqual(res["selected_tests"], ["demo-app/tests/test_billing.py"])
        self.assertEqual(res["selected_test_files_count"], 1)

    def test_resolve_multiple_services_pruned(self):
        changed = [
            "demo-app/services/auth/auth_service.py",
            "demo-app/services/billing/billing_service.py",
        ]
        res = resolve_tests_for_changes(changed)
        self.assertFalse(res["fallback_triggered"])
        self.assertEqual(
            set(res["selected_tests"]),
            {"demo-app/tests/test_auth.py", "demo-app/tests/test_billing.py"}
        )
        self.assertEqual(res["selected_test_files_count"], 2)

    def test_resolve_core_triggers_full_suite(self):
        changed = ["demo-app/core/base.py"]
        res = resolve_tests_for_changes(changed)
        self.assertTrue(res["fallback_triggered"])
        self.assertEqual(res["selected_tests"], FULL_TEST_SUITE)
        self.assertEqual(res["selected_test_files_count"], len(FULL_TEST_SUITE))

    def test_child_pipeline_yaml_generation_pruned(self):
        selected = ["demo-app/tests/test_auth.py"]
        yaml_text = generate_child_pipeline_yaml(selected, fallback_triggered=False)
        self.assertIn("Carbon-Optimized Pruned Test Suite", yaml_text)
        self.assertIn("pytest demo-app/tests/test_auth.py -v", yaml_text)

    def test_child_pipeline_yaml_generation_fallback(self):
        yaml_text = generate_child_pipeline_yaml(FULL_TEST_SUITE, fallback_triggered=True)
        self.assertIn("Safety Fallback (Full Test Suite Executed)", yaml_text)
        self.assertIn("pytest demo-app/tests/test_auth.py demo-app/tests/test_billing.py demo-app/tests/test_core.py -v", yaml_text)


if __name__ == "__main__":
    unittest.main()
