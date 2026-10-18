"""EcoOps Agent - FastAPI Webhook Receiver, Duo Tool, and CLI Runner.

Provides:
- Webhook endpoints for GitLab MR and Pipeline events (FastAPI)
- Tool endpoint for GitLab Duo Agent Platform / MCP integration
- Zero-dependency CLI interface for generating child-pipeline YAML directly in CI runner jobs
"""

import argparse
import sys
from typing import List, Optional

from .diff_parser import resolve_tests_for_changes, generate_child_pipeline_yaml
from .sci_model import (
    ModelAssumptions,
    PipelineRunMetrics,
    estimate_pipeline_emissions,
)
from .report import generate_mr_audit_comment
from .regional_data import REGIONAL_EMISSIONS_FACTORS

# FastAPI is optional for CLI execution inside lightweight CI runners
try:
    from fastapi import FastAPI, Header, HTTPException, Request
    from pydantic import BaseModel

    app = FastAPI(
        title="EcoOps Carbon-Aware DevSecOps Agent",
        version="1.0.0",
        description="GitLab Duo-integrated agent for carbon-aware CI pruning and SCI emissions auditing.",
    )

    class AnalysisRequest(BaseModel):
        changed_files: List[str]
        region_key: Optional[str] = "us-central1"
        baseline_duration_seconds: Optional[float] = 300.0
        actual_duration_seconds: Optional[float] = 45.0
        vcpu_count: Optional[int] = 2

    class AnalysisResponse(BaseModel):
        fallback_triggered: bool
        reason: str
        selected_tests: List[str]
        child_pipeline_yaml: str
        mr_comment_markdown: str

    @app.post("/agent/analyze", response_model=AnalysisResponse)
    def analyze_changes(req: AnalysisRequest):
        """GitLab Duo Agent tool endpoint to evaluate changes and return emissions audit."""
        resolution = resolve_tests_for_changes(req.changed_files)
        child_yaml = generate_child_pipeline_yaml(
            resolution["selected_tests"], resolution["fallback_triggered"]
        )

        assumptions = ModelAssumptions()

        baseline_metrics = PipelineRunMetrics(
            duration_seconds=req.baseline_duration_seconds,
            vcpu_count=req.vcpu_count,
            test_count=resolution["total_available_test_files"],
            region_key=req.region_key,
        )
        baseline_est = estimate_pipeline_emissions(baseline_metrics, assumptions)

        actual_metrics = PipelineRunMetrics(
            duration_seconds=req.actual_duration_seconds,
            vcpu_count=req.vcpu_count,
            test_count=resolution["selected_test_files_count"],
            region_key=req.region_key,
        )
        actual_est = estimate_pipeline_emissions(actual_metrics, assumptions)

        mr_comment = generate_mr_audit_comment(baseline_est, actual_est, resolution)

        return AnalysisResponse(
            fallback_triggered=resolution["fallback_triggered"],
            reason=resolution["reason"],
            selected_tests=resolution["selected_tests"],
            child_pipeline_yaml=child_yaml,
            mr_comment_markdown=mr_comment,
        )

    @app.post("/webhook/gitlab")
    async def gitlab_webhook(
        request: Request,
        x_gitlab_event: Optional[str] = Header(None),
        x_gitlab_token: Optional[str] = Header(None),
    ):
        """GitLab Webhook endpoint for Merge Request and Pipeline Hook events."""
        payload = await request.json()
        event_type = x_gitlab_event or payload.get("object_kind")

        if event_type == "merge_request":
            changes = payload.get("changes", {}).get("files", [])
            changed_paths = [c.get("new_path") for c in changes if c.get("new_path")]
            return {
                "status": "processed",
                "event": "merge_request",
                "changed_files_count": len(changed_paths),
            }

        return {"status": "ignored", "event": event_type}

except ImportError:
    app = None


def cli_main():
    """Zero-dependency CLI runner used inside GitLab CI jobs to generate child-pipeline YAML."""
    parser = argparse.ArgumentParser(description="EcoOps CLI Test Selector")
    parser.add_argument("--files", nargs="+", required=True, help="List of changed file paths")
    parser.add_argument("--output-yaml", default="generated-child-pipeline.yml", help="Path to write generated YAML")
    args = parser.parse_args()

    resolution = resolve_tests_for_changes(args.files)
    yaml_content = generate_child_pipeline_yaml(
        resolution["selected_tests"], resolution["fallback_triggered"]
    )

    with open(args.output_yaml, "w") as f:
        f.write(yaml_content)

    print(f"EcoOps: Generated child pipeline at {args.output_yaml}")
    print(f"EcoOps: Mode={'Fallback (Full Suite)' if resolution['fallback_triggered'] else 'Pruned'}")
    print(f"EcoOps: Reason={resolution['reason']}")
    print(f"EcoOps: Selected {len(resolution['selected_tests'])} test files.")


if __name__ == "__main__":
    cli_main()
