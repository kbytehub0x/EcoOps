"""Unit tests for Billing Service."""

import unittest
from demo-app.services.billing.billing_service import BillingService


class TestBilling(unittest.TestCase):
    def setUp(self):
        self.billing = BillingService()

    def test_get_balance(self):
        self.assertEqual(self.billing.get_balance("alice"), 150.0)

    def test_charge_success(self):
        self.assertTrue(self.billing.charge("alice", 50.0))
        self.assertEqual(self.billing.get_balance("alice"), 100.0)

    def test_charge_insufficient_funds(self):
        self.assertFalse(self.billing.charge("bob", 100.0))
        self.assertEqual(self.billing.get_balance("bob"), 45.0)


if __name__ == "__main__":
    unittest.main()
