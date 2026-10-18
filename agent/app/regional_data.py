"""Regional carbon emissions data and source attributions.

DISCLOSURE & METHODOLOGY NOTE:
The figures below represent published annual average regional grid emissions factors
(or carbon-free energy percentages) from Google Cloud Environmental & Sustainability
Reporting datasets. They are NOT live marginal grid intensity feeds.
All reports must disclose the dataset version and publication year.
"""

from typing import Dict, Any, Optional

# Published Google Cloud Regional Environmental Factors (2024-2025 Dataset)
# Source: Google Cloud Region Carbon Information (https://cloud.google.com/sustainability/region-carbon)
GCP_REGIONAL_DATASET_METADATA = {
    "source_name": "Google Cloud Regional Carbon Information",
    "publication_year": "2025",
    "dataset_type": "Annual Average Grid Carbon Intensity & CFE%",
    "live_marginal_feed": False,
    "caveat": "Values are published regional annual averages, not real-time marginal grid dispatch data.",
}

REGIONAL_EMISSIONS_FACTORS: Dict[str, Dict[str, Any]] = {
    "us-central1": {
        "region_name": "Iowa, North America",
        "grid_carbon_factor_gco2e_kwh": 432.0,
        "hourly_cfe_percentage": 64.0,
        "eligible_for_batch": True,
        "notes": "Annual average grid emissions factor; includes significant wind mix."
    },
    "europe-west9": {
        "region_name": "Paris, Europe",
        "grid_carbon_factor_gco2e_kwh": 16.0,
        "hourly_cfe_percentage": 93.0,
        "eligible_for_batch": True,
        "notes": "Low-carbon nuclear and hydro grid mix."
    },
    "europe-north1": {
        "region_name": "Finland, Europe",
        "grid_carbon_factor_gco2e_kwh": 45.0,
        "hourly_cfe_percentage": 97.0,
        "eligible_for_batch": True,
        "notes": "High hydro, biomass, and nuclear energy share."
    },
    "us-east4": {
        "region_name": "Northern Virginia, North America",
        "grid_carbon_factor_gco2e_kwh": 379.0,
        "hourly_cfe_percentage": 49.0,
        "eligible_for_batch": True,
        "notes": "PJM regional transmission grid average."
    }
}


def get_regional_factor(region_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve regional emissions data with source attribution.
    
    Returns None if the region is not recognized.
    """
    data = REGIONAL_EMISSIONS_FACTORS.get(region_key)
    if not data:
        return None
    return {
        "region_key": region_key,
        **data,
        "metadata": GCP_REGIONAL_DATASET_METADATA
    }
