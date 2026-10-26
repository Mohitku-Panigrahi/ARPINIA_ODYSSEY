#!/usr/bin/env python3
"""
ARPINIA ODYSSEY — PATH OWNERSHIP ENFORCEMENT
Validates that Pull Request authors only modify files within their assigned Pod boundaries.
Enforces Project Lead approval for frozen contracts, ground truth, and shared architecture.
"""

import sys
import os
import fnmatch
from typing import List, Tuple, Dict

# Verified Team Identities
LEAD_USERS = {"RudraNarayanMishra2142"}
POD_A_USERS = {"Mohitku-Panigrahi", "kamal-loachan"}
POD_B_USERS = {"amritkaur78190-sketch"}
POD_C_USERS = {"chandana-2204", "panditrani83-crypto"}

# Pod A Allowed Patterns (AI / Computer Vision / Segmentation / LLM Engine)
POD_A_ALLOWED_PATTERNS = [
    "models/*",
    "models/**",
    "services/ai-engine/*",
    "services/ai-engine/**",
    "docs/05-ai/*",
    "docs/05-ai/**",
    "tests/unit/test_ai_*.py",
    "tests/unit/test_sar_*.py",
    "tests/unit/test_model_*.py",
    "tests/unit/test_cv_*.py",
    "tests/unit/test_llm_*.py",
]

# Pod B Allowed Patterns (Explicit Core Analytics, MetOcean, Physics, Attribution, API, Worker, Database, Infrastructure, Tooling)
# Note: Pod B does NOT own packages/contracts/** or broad /packages/**.
POD_B_ALLOWED_PATTERNS = [
    "packages/geo/*",
    "packages/geo/**",
    "packages/metocean/*",
    "packages/metocean/**",
    "packages/reconstruction/*",
    "packages/reconstruction/**",
    "packages/ais/*",
    "packages/ais/**",
    "packages/attribution/*",
    "packages/attribution/**",
    "packages/stability/*",
    "packages/stability/**",
    "packages/counter_evidence/*",
    "packages/counter_evidence/**",
    "packages/forward_validation/*",
    "packages/forward_validation/**",
    "packages/evidence/*",
    "packages/evidence/**",
    "packages/shared/*",
    "packages/shared/**",
    "services/api/*",
    "services/api/**",
    "services/worker/*",
    "services/worker/**",
    "database/*",
    "database/**",
    "infrastructure/*",
    "infrastructure/**",
    "scripts/dev/*",
    "scripts/dev/**",
    "scripts/golden/*",
    "scripts/golden/**",
    "scripts/validation/*",
    "scripts/validation/**",
    "docs/07-backend/*",
    "docs/07-backend/**",
    "docs/08-deployment/*",
    "docs/08-deployment/**",
    "tests/unit/test_geo.py",
    "tests/unit/test_metocean.py",
    "tests/unit/test_reconstruction*.py",
    "tests/unit/test_ais*.py",
    "tests/unit/test_attribution*.py",
    "tests/unit/test_b4*.py",
    "tests/unit/test_stability*.py",
    "tests/unit/test_b7*.py",
    "tests/unit/test_b8*.py",
    "tests/unit/test_null_semantics.py",
    "tests/unit/test_golden_synthetic_ais.py",
    "tests/unit/test_leakage.py",
    "tests/unit/test_tamper_detection.py",
    "tests/fixtures/*",
    "tests/fixtures/**",
    "artifacts/golden/*",
    "artifacts/golden/**",
    "artifacts/audits/*",
    "artifacts/audits/**",
]

# Pod C Allowed Patterns (Frontend, Web App, UI, Dossier, Visualization)
POD_C_ALLOWED_PATTERNS = [
    "apps/web/*",
    "apps/web/**",
    "docs/06-frontend/*",
    "docs/06-frontend/**",
    "tests/unit/test_web_*.py",
    "tests/unit/test_ui_*.py",
    "tests/unit/test_frontend_*.py",
]

# Sensitive / Lead-controlled paths
GROUND_TRUTH_PATTERNS = [
    "data/samples/golden-scenario-v1/ground_truth.json",
    "*/ground_truth.json",
    "**/ground_truth.json",
]

CONTRACT_PATTERNS = [
    "packages/contracts/*",
    "packages/contracts/**",
]

SHARED_LEAD_PATTERNS = [
    ".github/*",
    ".github/**",
    "AGENTS.md",
    "PRE-CODE-GATE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "requirements.txt",
    "requirements-dev.txt",
    "data/samples/golden-scenario-v1/*",
    "data/samples/golden-scenario-v1/**",
    "docs/00-governance/*",
    "docs/00-governance/**",
    "docs/09-testing/*",
    "docs/09-testing/**",
    "rp/*",
    "rp/**",
    "tests/integration/*",
    "tests/integration/**",
    "tests/e2e/*",
    "tests/e2e/**",
]


def matches_any_pattern(file_path: str, patterns: List[str]) -> bool:
    normalized = file_path.replace("\\", "/").lstrip("./")
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def validate_path_ownership(author: str, changed_files: List[str]) -> Tuple[bool, List[str]]:
    violations = []
    
    # Normalize author
    author_clean = author.strip().lstrip("@")
    
    # Identify Pod
    if author_clean in LEAD_USERS:
        pod = "LEAD"
    elif author_clean in POD_A_USERS:
        pod = "POD_A"
    elif author_clean in POD_B_USERS:
        pod = "POD_B"
    elif author_clean in POD_C_USERS:
        pod = "POD_C"
    else:
        violations.append(
            f"UNKNOWN_CONTRIBUTOR_REVIEW_REQUIRED: User '@{author_clean}' is not recognized in team registry."
        )
        return False, violations

    print(f"[*] Validating Pull Request from @{author_clean} (Role: {pod})")
    print(f"[*] Total files changed: {len(changed_files)}")

    # Project Lead has unrestricted write authority across all paths
    if pod == "LEAD":
        print("[+] Project Lead override active: Unrestricted access permitted.")
        return True, []

    for file_path in changed_files:
        normalized_path = file_path.replace("\\", "/").lstrip("./")
        if not normalized_path:
            continue

        # 1. Ground Truth Protection Gate
        if matches_any_pattern(normalized_path, GROUND_TRUTH_PATTERNS):
            violations.append(
                f"GROUND_TRUTH_CHANGE_DETECTED: Unauthorized modification of Ground Truth reference '{normalized_path}'. Project Lead approval required."
            )
            continue

        # 2. Frozen Contract Protection Gate (packages/contracts/** is Lead-only)
        if matches_any_pattern(normalized_path, CONTRACT_PATTERNS):
            violations.append(
                f"CONTRACT_CHANGE_DETECTED: Unauthorized modification of frozen contract '{normalized_path}'. Project Lead approval required."
            )
            continue

        # 3. Shared Governance & Infrastructure Gate
        if matches_any_pattern(normalized_path, SHARED_LEAD_PATTERNS):
            violations.append(
                f"SHARED_PATH_APPROVAL_REQUIRED: Unauthorized modification of shared governance/infrastructure '{normalized_path}'. Project Lead approval required."
            )
            continue

        # 4. Pod-Specific Allowed Paths Check
        allowed = False
        if pod == "POD_A":
            allowed = matches_any_pattern(normalized_path, POD_A_ALLOWED_PATTERNS)
        elif pod == "POD_B":
            allowed = matches_any_pattern(normalized_path, POD_B_ALLOWED_PATTERNS)
        elif pod == "POD_C":
            allowed = matches_any_pattern(normalized_path, POD_C_ALLOWED_PATTERNS)

        if not allowed:
            # Check if it's an unclassified test or another pod's path
            if normalized_path.startswith("tests/"):
                violations.append(
                    f"SHARED_PATH_APPROVAL_REQUIRED: Unclassified test or shared test path '{normalized_path}'. Project Lead approval required."
                )
            else:
                violations.append(
                    f"CROSS_POD_APPROVAL_REQUIRED: Contributor @{author_clean} ({pod}) is not authorized to modify '{normalized_path}'."
                )

    is_valid = (len(violations) == 0)
    return is_valid, violations


def main():
    if len(sys.argv) < 2:
        print("Usage: check_path_ownership.py <author> [file1 file2 ...]")
        sys.exit(1)

    author = sys.argv[1]
    
    if len(sys.argv) > 2:
        changed_files = sys.argv[2:]
    else:
        # Read from environment or git diff if not passed directly
        changed_files_env = os.environ.get("CHANGED_FILES", "")
        if changed_files_env:
            changed_files = changed_files_env.split()
        else:
            changed_files = []

    is_valid, violations = validate_path_ownership(author, changed_files)

    if is_valid:
        print(f"\n[PASS] All {len(changed_files)} changed files are within authorized boundaries for @{author}.")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Found {len(violations)} path ownership violation(s):")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)


if __name__ == "__main__":
    main()
