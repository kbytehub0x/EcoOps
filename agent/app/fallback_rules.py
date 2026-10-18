"""Fail-Safe Rules Engine for CI Test Pruning.

SAFETY PRINCIPLE:
If the diff touches shared/core files, build configurations, dependency files,
CI definitions, or any unmapped/uncertain files, the engine MUST fallback to running
the 100% full test suite.
"""

from typing import List, Tuple
import os

# Files and directory patterns that ALWAYS trigger a full-suite fallback
CRITICAL_FALLBACK_PATTERNS = [
    ".gitlab-ci.yml",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Dockerfile",
    "docker-compose.yml",
    "core/",
]

# Explicit file-to-test mapping rules
SERVICE_TEST_MAP = {
    "demo-app/services/auth/": "demo-app/tests/test_auth.py",
    "demo-app/services/billing/": "demo-app/tests/test_billing.py",
}


def should_fallback_to_full_suite(changed_files: List[str]) -> Tuple[bool, str]:
    """Inspect changed files and decide whether safety fallback to full suite is required.
    
    Returns:
        (fallback_triggered: bool, reason: str)
    """
    if not changed_files:
        return True, "No changed files detected or empty diff; falling back to full suite."

    for file_path in changed_files:
        norm_path = os.path.normpath(file_path).replace("\\", "/")

        # Rule 1: Critical configs or core libraries
        for pattern in CRITICAL_FALLBACK_PATTERNS:
            if pattern in norm_path:
                return True, f"Critical shared file or configuration modified: '{norm_path}'"

        # Rule 2: Changes directly in the test suite itself (run full suite to ensure integrity)
        if "tests/" in norm_path and not norm_path.startswith("agent/tests/"):
            return True, f"Test suite definition modified directly: '{norm_path}'"

        # Rule 3: File does not match any recognized service
        matched_any_service = False
        for service_prefix in SERVICE_TEST_MAP.keys():
            if service_prefix in norm_path:
                matched_any_service = True
                break

        if not matched_any_service:
            return True, f"Unmapped or unknown file modified: '{norm_path}'"

    return False, "All modified files safely mapped to isolated service test suites."
