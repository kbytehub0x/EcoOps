"""MR Comment and Audit Report Generator.

Formats the auditable comparison table, assumptions disclosure,
and human-in-the-loop action triggers for GitLab Merge Requests.
"""

from typing import Dict, Any
from .sci_model import OperationalEmissionsEstimate


def generate_mr_audit_comment(
    baseline_estimate: OperationalEmissionsEstimate,
    actual_estimate: OperationalEmissionsEstimate,
    test_resolution: Dict[str, Any],
) -> str:
    """Generate Markdown audit report for posting to a GitLab MR discussion note."""
    
    # Calculate deltas
    duration_delta = baseline_estimate.duration_seconds - actual_estimate.duration_seconds
    duration_pct = (duration_delta / baseline_estimate.duration_seconds * 100) if baseline_estimate.duration_seconds > 0 else 0

    energy_delta = baseline_estimate.energy_kwh - actual_estimate.energy_kwh
    energy_pct = (energy_delta / baseline_estimate.energy_kwh * 100) if baseline_estimate.energy_kwh > 0 else 0

    emissions_delta = baseline_estimate.emissions_gco2e - actual_estimate.emissions_gco2e
    emissions_pct = (emissions_delta / baseline_estimate.emissions_gco2e * 100) if baseline_estimate.emissions_gco2e > 0 else 0

    fallback_badge = (
        "⚠️ **SAFETY FALLBACK ACTIVE** (Full Suite Run)"
        if test_resolution.get("fallback_triggered")
        else "🌱 **CARBON-OPTIMIZED** (Pruned Suite Run)"
    )

    reason = test_resolution.get("reason", "Standard execution.")
    selected_tests = test_resolution.get("selected_tests", [])
    tests_summary = f"{len(selected_tests)} test files selected: `{', '.join(selected_tests)}`"

    comment = f"""## 🌱 EcoOps Carbon & Compute Audit

**Execution Mode:** {fallback_badge}  
**Selection Reason:** {reason}  
**Test Scope:** {tests_summary}

---

### Comparison Summary: Operational Emissions per Pipeline Run (R = 1)

| Metric | Standard Baseline (Full Suite) | EcoOps Execution | Delta / Savings |
| :--- | :--- | :--- | :--- |
| **Runner Duration** | {baseline_estimate.duration_seconds:.1f}s | {actual_estimate.duration_seconds:.1f}s | **-{duration_delta:.1f}s (-{duration_pct:.1f}%)** |
| **Est. IT Energy ($E$)** | {baseline_estimate.energy_kwh:.6f} kWh | {actual_estimate.energy_kwh:.6f} kWh | **-{energy_delta:.6f} kWh (-{energy_pct:.1f}%)** |
| **Est. Operational Emissions** | **{baseline_estimate.emissions_gco2e:.3f} gCO₂e** | **{actual_estimate.emissions_gco2e:.3f} gCO₂e** | **-{emissions_delta:.3f} gCO₂e (-{emissions_pct:.1f}%)** |
| **Region & Grid Factor** | `{baseline_estimate.region_key}` ({baseline_estimate.grid_factor_gco2e_kwh} g/kWh) | `{actual_estimate.region_key}` ({actual_estimate.grid_factor_gco2e_kwh} g/kWh) | Identical Grid Boundary |

---

### Methodology Disclosures & Boundary (ISO/IEC 21031 SCI Aligned)
* **Functional Unit ($R$):** 1 completed pipeline run for this Merge Request.
* **Scope:** Operational emissions only ($E \\times I$). Embodied hardware emissions ($M$) are excluded from this headline comparison.
* **Power Proxy:** Modeled at {actual_estimate.assumptions.vcpu_power_proxy_watts} W per vCPU (IT equipment estimate at runner load).
* **Facility PUE:** {actual_estimate.assumptions.pue} applied to IT electricity for Google Cloud data center overhead.
* **Regional Data Source:** {actual_estimate.data_source_citation} (annual average regional emissions factor, not live marginal intensity feed).

---

### Autonomy Controls (Human-on-the-Loop)
* To force-run the full 100% test suite, reply with `/ecoops full-suite` or trigger the manual pipeline job in the GitLab Pipeline UI.
"""
    return comment
