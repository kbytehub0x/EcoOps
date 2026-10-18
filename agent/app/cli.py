"""Standalone, zero-dependency CLI runner for GitLab CI jobs.

This entry point imports ONLY standard library modules and pure internal
diff/fallback logic. It never touches web servers, network libraries, or external frameworks.
"""

import argparse
import sys
from .diff_parser import resolve_tests_for_changes, generate_child_pipeline_yaml


def main():
    parser = argparse.ArgumentParser(
        description="EcoOps CLI Test Selector & Child Pipeline Generator"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="List of changed file paths in commit or MR",
    )
    parser.add_argument(
        "--output-yaml",
        default="generated-config.yml",
        help="Path where the generated child pipeline YAML will be written",
    )
    args = parser.parse_args()

    resolution = resolve_tests_for_changes(args.files)
    yaml_content = generate_child_pipeline_yaml(
        resolution["selected_tests"], resolution["fallback_triggered"]
    )

    with open(args.output_yaml, "w") as f:
        f.write(yaml_content)

    print(f"EcoOps CLI: Generated child pipeline at {args.output_yaml}")
    print(f"EcoOps CLI: Mode={'Fallback (Full Suite)' if resolution['fallback_triggered'] else 'Pruned'}")
    print(f"EcoOps CLI: Reason={resolution['reason']}")
    print(f"EcoOps CLI: Selected {len(resolution['selected_tests'])} test files.")


if __name__ == "__main__":
    main()
