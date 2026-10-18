"""Unit tests for SCI operational emissions estimation model."""

import unittest
from agent.app.sci_model import (
    ModelAssumptions,
    PipelineRunMetrics,
    estimate_pipeline_emissions,
)
from agent.app.report import generate_mr_audit_comment


class TestSciModel(unittest.TestCase):

    def test_estimate_pipeline_emissions_us_central1(self):
        # 2 vCPUs running for 300s (5 minutes) in us-central1 (432 gCO2e/kWh)
        # IT Power = 2 * 15W = 30W = 0.030 kW
        # Hours = 300 / 3600 = 0.08333 hrs
        # Energy = 0.08333 * 0.030 * 1.1 (PUE) = 0.00275 kWh
        # Emissions = 0.00275 * 432 = 1.188 gCO2e
        metrics = PipelineRunMetrics(
            duration_seconds=300.0,
            vcpu_count=2,
            test_count=100,
            region_key="us-central1",
        )
        assumptions = ModelAssumptions(
            vcpu_power_proxy_watts=15.0,
            pue=1.10,
            pue_applied_to_it_energy=True,
        )
        est = estimate_pipeline_emissions(metrics, assumptions)

        self.assertEqual(est.functional_unit, "1 pipeline run")
        self.assertEqual(est.grid_factor_gco2e_kwh, 432.0)
        self.assertAlmostEqual(est.energy_kwh, 0.00275, delta=1e-4)
        self.assertAlmostEqual(est.emissions_gco2e, 1.188, delta=1e-2)

    def test_estimate_pipeline_emissions_europe_west9(self):
        # Low carbon grid: 16 gCO2e/kWh
        metrics = PipelineRunMetrics(
            duration_seconds=300.0,
            vcpu_count=2,
            test_count=100,
            region_key="europe-west9",
        )
        est = estimate_pipeline_emissions(metrics)
        self.assertEqual(est.grid_factor_gco2e_kwh, 16.0)
        # Emissions should be much lower (16 / 432 ~= 3.7% of us-central1)
        self.assertLess(est.emissions_gco2e, 0.05)

    def test_mr_report_generation_disclosures(self):
        baseline_metrics = PipelineRunMetrics(duration_seconds=300.0, vcpu_count=2, test_count=100)
        actual_metrics = PipelineRunMetrics(duration_seconds=45.0, vcpu_count=2, test_count=10)

        base_est = estimate_pipeline_emissions(baseline_metrics)
        act_est = estimate_pipeline_emissions(actual_metrics)

        res = {
            "fallback_triggered": False,
            "reason": "All files safely mapped to auth service.",
            "selected_tests": ["demo-app/tests/test_auth.py"],
        }

        report_md = generate_mr_audit_comment(base_est, act_est, res)

        # Verify key disclosures are present in the output
        self.assertIn("EcoOps Carbon & Compute Audit", report_md)
        self.assertIn("CARBON-OPTIMIZED", report_md)
        self.assertIn("Operational Emissions per Pipeline Run (R = 1)", report_md)
        self.assertIn("ISO/IEC 21031 SCI Aligned", report_md)
        self.assertIn("15.0 W per vCPU", report_md)
        self.assertIn("PUE", report_md)
        self.assertIn("Google Cloud Regional Carbon Information", report_md)


if __name__ == "__main__":
    unittest.main()
