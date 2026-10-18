"""SCI-Aligned Operational Emissions Estimation Model.

METHODOLOGY & SYSTEM BOUNDARY:
- Metric: Estimated Operational Emissions per Pipeline Run (R = 1 pipeline run).
- Boundary: Cloud CI Runner IT electricity consumption scaled by Data Center PUE.
- Standard Alignment: Aligned with the operational emissions component (E * I)
  of the Software Carbon Intensity (SCI) Specification (ISO/IEC 21031).
- Hardware Power: Disclosed as a model assumption/proxy (default: 15W per vCPU).
  Not an official standard constant.
- Embodied Emissions (M): Excluded from the primary score to avoid unverified
  hardware amortization claims; labeled explicitly as operational emissions only.
"""

from dataclasses import dataclass
from typing import Dict, Any
from .regional_data import get_regional_factor


@dataclass
class ModelAssumptions:
    """Configurable model assumptions for the energy estimation."""
    vcpu_power_proxy_watts: float = 15.0  # Estimated IT equipment power draw per vCPU at typical CI runner load
    pue: float = 1.10                    # Power Usage Effectiveness for Google Cloud Data Centers (Facility / IT)
    pue_applied_to_it_energy: bool = True # PUE applied because power proxy represents IT equipment energy only


@dataclass
class PipelineRunMetrics:
    """Observed runtime metrics for a pipeline execution."""
    duration_seconds: float
    vcpu_count: int
    test_count: int
    region_key: str = "us-central1"


@dataclass
class OperationalEmissionsEstimate:
    """Calculated operational emissions and energy estimate with full disclosure."""
    functional_unit: str  # e.g. "1 pipeline run"
    duration_seconds: float
    vcpu_count: int
    energy_kwh: float
    emissions_gco2e: float
    region_key: str
    grid_factor_gco2e_kwh: float
    assumptions: ModelAssumptions
    data_source_citation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "functional_unit": self.functional_unit,
            "duration_seconds": round(self.duration_seconds, 2),
            "vcpu_count": self.vcpu_count,
            "energy_kwh": round(self.energy_kwh, 6),
            "emissions_gco2e": round(self.emissions_gco2e, 3),
            "region_key": self.region_key,
            "grid_factor_gco2e_kwh": self.grid_factor_gco2e_kwh,
            "power_proxy_watts_per_vcpu": self.assumptions.vcpu_power_proxy_watts,
            "pue": self.assumptions.pue,
            "data_source_citation": self.data_source_citation,
        }


def estimate_pipeline_emissions(
    metrics: PipelineRunMetrics,
    assumptions: ModelAssumptions = ModelAssumptions(),
) -> OperationalEmissionsEstimate:
    """Calculate the operational emissions estimate for a single pipeline run.
    
    Formula:
        Duration_hours = duration_seconds / 3600
        IT_Power_kW = (vcpu_count * vcpu_power_proxy_watts) / 1000
        Facility_Energy_kWh (E) = Duration_hours * IT_Power_kW * PUE
        Emissions_gCO2e = Energy_kWh * Grid_Factor_gCO2e_kWh
    """
    region_info = get_regional_factor(metrics.region_key)
    if not region_info:
        raise ValueError(f"Unknown region key: {metrics.region_key}")

    grid_factor = region_info["grid_carbon_factor_gco2e_kwh"]
    data_source = (
        f"{region_info['metadata']['source_name']} "
        f"({region_info['metadata']['publication_year']})"
    )

    duration_hours = metrics.duration_seconds / 3600.0
    it_power_kw = (metrics.vcpu_count * assumptions.vcpu_power_proxy_watts) / 1000.0

    if assumptions.pue_applied_to_it_energy:
        energy_kwh = duration_hours * it_power_kw * assumptions.pue
    else:
        energy_kwh = duration_hours * it_power_kw

    emissions_gco2e = energy_kwh * grid_factor

    return OperationalEmissionsEstimate(
        functional_unit="1 pipeline run",
        duration_seconds=metrics.duration_seconds,
        vcpu_count=metrics.vcpu_count,
        energy_kwh=energy_kwh,
        emissions_gco2e=emissions_gco2e,
        region_key=metrics.region_key,
        grid_factor_gco2e_kwh=grid_factor,
        assumptions=assumptions,
        data_source_citation=data_source,
    )
