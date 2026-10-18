# EcoOps: Autonomous Carbon-Aware DevSecOps for GitLab

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Standards: ISO/IEC 21031 (SCI Aligned)](https://img.shields.io/badge/Standard-SCI%20Aligned-brightgreen)](https://greensoftware.foundation/standards/sci/)
[![Platform: GitLab Duo](https://img.shields.io/badge/Platform-GitLab%20Duo%20Agent-orange)](https://about.gitlab.com/)

**EcoOps** is an autonomous DevSecOps agent built for the **GitLab "Life After Code" (Transcend) Hackathon**. It tackles computational and carbon waste in the post-push lifecycle by combining AST diff analysis, GitLab Dynamic Child Pipelines, and the **Software Carbon Intensity (SCI) Specification (ISO/IEC 21031)** to safely prune redundant CI/CD testing and report auditable operational emissions on every Merge Request.

---

## 1. Why EcoOps? ("Life After Code")

AI code assistants have rapidly accelerated how fast code is written, shifting the bottleneck to everything that happens *after* `git push`:
* Monolithic CI/CD pipelines repeatedly execute 100% of test suites on minor, isolated commits.
* Cloud runners consume millions of vCPU compute-hours on redundant test jobs.
* Development teams lack transparent visibility into the operational energy ($E$) and carbon emissions ($\text{gCO}_2\text{e}$) incurred per pipeline execution.

**EcoOps** automates post-commit optimization with built-in safety fallbacks:
1. **Dynamic Test Pruning:** Maps git diffs to isolated service test suites, reducing runner duration by up to 80–90%.
2. **Fail-Safe Fallback:** If shared/core files, build configurations, or CI definitions change, it automatically runs 100% of the test suite.
3. **Auditable SCI Emissions Report:** Posts transparent, reproducible operational emissions estimates directly into GitLab MR discussions.
4. **GitLab Duo Integration:** Exposed as an autonomous skill/tool within the GitLab Duo Agent Platform.

---

## 2. Architecture & Flow

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ECOOPS ARCHITECTURE                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [Developer pushes MR]                                                                 │
│            │                                                                           │
│            ▼ (GitLab Webhook / CI Trigger)                                             │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. EcoOps Core Service (Google Cloud Run / FastAPI)                              │  │
│  │    • Ingests commit diff & file tree                                             │  │
│  │    • Evaluates AST blast-radius mapping                                          │  │
│  │    • Fail-Safe Check: Core configs modified? ➔ Fallback: Run 100% full suite.    │  │
│  │    • Generates dynamic child pipeline (.gitlab-ci-pruned.yml)                    │  │
│  └──────────────────────────────────┬───────────────────────────────────────────────┘  │
│                                     │                                                  │
│            ┌────────────────────────┴───────────────────────┐                          │
│            ▼                                                ▼                          │
│  ┌──────────────────────────────────┐    ┌──────────────────────────────────────────┐  │
│  │ 2. GitLab Child Pipeline Trigger │    │ 3. GitLab Duo Agent Platform Hook        │  │
│  │    • Runs selected tests only    │    │    • Queries EcoOps tool via MCP/API     │  │
│  │    • Records exact runner duration│   │    • Answers developer queries on energy │  │
│  └─────────────────┬────────────────┘    └──────────────────────────────────────────┘  │
│                    │                                                                   │
│                    ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 4. Auditable MR Markdown Reporter                                                │  │
│  │    • Posts comparative table (Baseline vs. EcoOps)                               │  │
│  │    • Discloses runner duration, power assumptions, grid factor, and delta        │  │
│  │    • Provides 1-click Level 2 human override to force full-suite run             │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Methodology Disclosures (SCI Standards Compliance)

To ensure technical credibility and auditability, EcoOps follows the **Software Carbon Intensity (SCI) Specification (ISO/IEC 21031)** guidelines:

$$\text{Operational Emissions (gCO}_2\text{e)} = E \times I$$
$$\text{Energy } E\text{ (kWh)} = \frac{\text{Runner Duration (hrs)} \times \text{vCPU Count} \times \text{Power Proxy (W)} \times \text{PUE}}{1000}$$

### Transparent Model Disclosures
* **Metric Classification:** Labeled strictly as an **Operational Emissions Estimate per Pipeline Run** ($R = 1\text{ pipeline run}$).
* **Embodied Emissions ($M$):** Excluded from the headline score to avoid unverified hardware amortization assumptions.
* **Power Proxy ($P$):** Modeled at $15.0\text{ W per vCPU}$ at typical CI runner utilization (labeled as an estimate, configurable).
* **Facility PUE:** $1.10$ applied to IT electricity for Google Cloud data center overhead.
* **Grid Factor ($I$):** Sourced from published regional annual averages (e.g. Google Cloud 2025 Regional Environmental Report: $432\text{ gCO}_2\text{e/kWh}$ for `us-central1`, $16\text{ gCO}_2\text{e/kWh}$ for `europe-west9`). Labeled as regional average factors, not live marginal intensity feeds.

---

## 4. Repository Layout

```text
├── LICENSE                   # MIT License (kbytehub0x)
├── README.md                 # Prototype documentation & methodology
├── .gitlab/
│   ├── duo/
│   │   └── agent-config.yml  # GitLab Duo Flow Execution Environment
│   └── agents/
│       └── ecoops/
│           └── config.yaml   # GitLab Duo tool definition schema
├── agent/                    # EcoOps Core Engine
│   ├── app/
│   │   ├── cli.py            # Zero-dependency CLI runner for CI runner jobs
│   │   ├── main.py           # FastAPI Webhook receiver & Duo tool service
│   │   ├── diff_parser.py    # Test selection & child pipeline generator
│   │   ├── fallback_rules.py # Fail-safe safety rules
│   │   ├── sci_model.py      # SCI operational emissions estimation model
│   │   ├── regional_data.py  # Dated, source-attributed regional carbon data
│   │   └── report.py         # Auditable MR Markdown comment generator
│   ├── tests/                # Zero-dependency unit tests
│   │   ├── test_diff_parser.py
│   │   ├── test_fallback_rules.py
│   │   └── test_sci_model.py
│   └── requirements.txt
└── demo-app/                 # Target validation project
    ├── .gitlab-ci.yml        # Parent pipeline triggering child pipeline artifact
    ├── services/
    │   ├── auth/             # Isolated Auth Service
    │   └── billing/          # Isolated Billing Service
    ├── core/                 # Shared Core module (triggers safety fallback)
    └── tests/                # Test suites for demo-app
```

---

## 5. GitLab Duo Agent Platform Integration Guide

To satisfy the hackathon's GitLab Duo requirement, EcoOps integrates through two official channels:

1. **Custom Agent in GitLab AI Catalog (UI Configuration):**
   * Navigate to **Project Settings > AI > Agents** (or the AI Catalog).
   * Create an agent named **EcoOps Carbon Auditor**.
   * Set Model to **Claude 3.5 Sonnet** (via GitLab Duo).
   * Register the `analyze_changes` tool pointing to the EcoOps service endpoint.
   * Provide the system prompt instruct Duo to interpret test diffs and explain the operational emissions estimate.

2. **Duo Flow Execution Environment (`.gitlab/duo/agent-config.yml`):**
   * Configures the container image (`python:3.11-slim`), setup commands, and cache policies for automated Duo agent flow executions in CI.

---

## 6. Local Testing & Verification

Run the complete test suite with Python's built-in `unittest` (zero external dependencies required):

```bash
# Run unit tests on the core engine (all 16 tests pass out of the box)
python3 -m unittest discover -s agent/tests/ -v
```

### Try the Standalone CLI Dynamic Pipeline Generator:

```bash
# Test pruned test generation (Auth service only)
python3 -m agent.app.cli --files "demo-app/services/auth/auth_service.py" --output-yaml "generated-child-pipeline.yml"

# Test fail-safe fallback (Core utilities modified)
python3 -m agent.app.cli --files "demo-app/core/base.py" --output-yaml "generated-child-pipeline.yml"
```

---

## 7. Autonomy Levels (Hackathon Compliance)

* **Level 1 (Human-in-the-Loop):** MR audit comment providing transparent operational emissions estimates and efficiency recommendations.
* **Level 2 (Human-on-the-Loop):** Pruned child pipeline executes automatically, with a 1-click manual UI trigger to override and run 100% of tests.
* **Level 3 (Human-out-of-the-Loop):** Automated regional runner matching for non-blocking scheduled batch workloads across pre-provisioned tagged runners.

---

## 8. License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.  
Copyright (c) 2026 **kbytehub0x**.
