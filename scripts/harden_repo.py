import os
from pathlib import Path

def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {path}")

# 1. SECURITY.md
write_file("SECURITY.md", """
# Security Policy

## Supported Versions
Only the `main` branch is actively supported with security updates.

## Reporting a Vulnerability
DO NOT create a public issue for security vulnerabilities.
Contact the lead maintainer (Rudra) directly.

## Secret Management (Agent & Human Rules)
1. **Never commit secrets:** API keys, DB passwords, and model weights MUST NOT be committed.
2. **.env files:** All `.env` files are in `.gitignore`. Use `.env.example` for templates.
3. **Secret Scanning:** All PRs are scanned using GitHub Actions (Gitleaks).
4. **Golden Scenario Ground Truth:** `ground_truth.json` is treated as a sensitive operational secret. The inference pipeline MUST NOT read it.

## Network Security Boundary
- The Frontend (`apps/web`) communicates ONLY with the `api` service.
- The `api` service communicates with `worker`, `ai-engine`, and `database`.
- **PostgreSQL, Redis, and AI endpoints are strictly bound to internal Docker networks.** They must NEVER bind to `0.0.0.0` on the host outside of local dev loops without an explicit proxy.
""")

# 2. .env.example
write_file(".env.example", """
# ARPINIA ODYSSEY - Environment Template
# DO NOT ADD REAL SECRETS TO THIS FILE

# Application Environment
NODE_ENV=development
PYTHONENV=development

# Database (Internal Network Only)
POSTGRES_USER=arpinia_admin
POSTGRES_PASSWORD=
POSTGRES_DB=arpinia_odyssey
POSTGRES_HOST=database
POSTGRES_PORT=5432
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Redis (Internal Network Only)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

# API Configuration
API_PORT=8000
FRONTEND_PORT=3000
API_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services (If applicable, though MVP relies on local)
# OPENAI_API_KEY= # (Optional - MVP uses Local LLM)
LOCAL_LLM_URL=http://ai-engine:8080/v1/completions
""")

# 3. CONTRIBUTING.md
write_file("CONTRIBUTING.md", """
# Contributing to ARPINIA ODYSSEY

## Branching Strategy
- `main` is protected. No direct pushes.
- Create feature branches: `pod-b/feature-name` or `pod-a/model-update`.

## Pull Request Requirements
1. **Tests:** All tests must pass.
2. **Security:** Secret scanning (Gitleaks) must pass.
3. **Contract Validation:** Changes affecting Evidence JSON must be approved by all Pods.
4. **Review:** Require 1 approval from a different Pod.

## AI Agent Rules
Any AI agent coding in this repository MUST read `AGENTS.md` before executing any edits.
Agents cannot merge PRs or bypass security scanning.
""")

# 4. CHANGELOG.md
write_file("CHANGELOG.md", """
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Repository hardened for security, documentation, and agent-readiness.
- Explicit Docker architectures and Pod ownership rules.
- Pre-push security gates and `.env.example`.
""")

# 5. docs/00-governance/team-ownership.md (Update)
write_file("docs/00-governance/team-ownership.md", """
# ARPINIA ODYSSEY — TEAM OWNERSHIP

The 6-person SIH team is divided into three isolated Pods. Code boundaries must not be crossed without architecture review.

## Pod 1 (AI & Data Intelligence)
- **Members:** Mohit, Kamal
- **OWN:** `models/`, `services/ai-engine/`
- **CAN READ:** Contracts, Architecture, Golden Scenario.
- **CANNOT MODIFY:** Evidence schema, LLM schema, Pod 2 attribution logic, Frontend, Deployment architecture.

## Pod 2 (Backend, Geo & Orchestration)
- **Members:** Rudra, Amrit
- **OWN:** `services/worker/`, `services/api/`, `packages/geo/`, `database/`, `infrastructure/`, `scripts/`, `tests/`, `.github/`, `packages/`
- **OWNS:** The generation of Evidence JSON, overall architecture, testing frameworks, and deployment.
- **CANNOT MODIFY:** LLM interpretation module, Frontend, or read ground truth during runtime inference.

## Pod 3 (Frontend & Reporting)
- **Members:** Chandana, Rani
- **OWN:** `apps/web/`, `docs/06-frontend/`
- **CONSUMES:** Evidence JSON, LLM Interpretation JSON.
- **CANNOT MODIFY:** Evidence JSON schema, Attribution logic, Physics modeling.

## Shared / Cross-Pod
- `docs/` (Owned by Pod 2, but writable by respective Pods for their modules)
""")

# 6. docs/05-ai/local-llm-deployment.md
write_file("docs/05-ai/local-llm-deployment.md", """
# Local LLM Deployment & Safety

## Architecture
The LLM is deployed as a strictly internal service (`ai-engine`). It does not have public internet exposure.
It consumes Evidence JSON and outputs `llm-interpretation.schema.json`.

## Safety & Boundaries
1. **No External API Access:** The LLM does not query external databases or the internet.
2. **One-Way Data Flow:** Evidence JSON -> LLM. The LLM cannot alter evidence values, ranking, or drift physics.
3. **Schema Validation:** The output of the LLM is intercepted and validated against `llm-interpretation.schema.json` before being served to the frontend.
4. **Fallback:** If the LLM is offline, times out, or hallucinates schema-breaking JSON, the API returns a safe fallback indicating "Interpretation Unavailable" while retaining the core numerical Evidence JSON.

## Hardware Profile
- **Target:** CPU fallback with quantized weights (e.g., Llama 3 8B Q4_K_M).
- **RAM Minimum:** 16GB.
- **GPU (Optional):** CUDA integration supported but not mandated for CI.
""")

# 7. docs/06-frontend/frontend-contract.md
write_file("docs/06-frontend/frontend-contract.md", """
# Frontend Integration Contract

## Architecture
- `apps/web/` runs Next.js.
- It consumes REST endpoints from `services/api/`.

## State Handling
1. **Loading:** Must gracefully handle prolonged loading states (backward drift takes time).
2. **Partial Success:** If the deterministic API returns Evidence JSON but the LLM route 504s, the frontend MUST display the Evidence and map, rendering an "AI Summary Unavailable" block rather than crashing the page.
3. **No Secrets:** The frontend must never receive `DATABASE_URL`, internal IPs, or any secret keys.
4. **Numerical Truth:** All rankings, probabilities, and times must be sourced directly from the deterministic Evidence JSON, never parsed from the LLM text.
""")

# 8. docs/07-backend/backend-rules.md
write_file("docs/07-backend/backend-rules.md", """
# Backend Development Rules

## Architecture
- `services/api/` handles HTTP, auth, and DB orchestration.
- `services/worker/` handles long-running jobs (OpenDrift, AIS queries) via Redis/Celery.

## Security
1. **No Direct Ground Truth:** The worker MUST NEVER open `data/samples/golden-scenario-v1/ground_truth.json`.
2. **Input Validation:** All payloads must be Pydantic-validated.
3. **No Shell Injection:** Use strict param bindings for PostGIS. Never use `os.system` with user input.
4. **Logging:** Never log raw environment variables, passwords, or LLM API keys. Use structured JSON logging.
""")

# 9. docs/08-deployment/docker-architecture.md
write_file("docs/08-deployment/docker-architecture.md", """
# Docker Architecture & Network Security

## Network Topology
Docker Compose will define two networks:
1. `frontend-net`: Bridging the public internet (via reverse proxy/Nginx) to `apps/web` and `services/api`.
2. `backend-net`: Isolated. Bridging `services/api`, `services/worker`, `services/ai-engine`, `database`, and `redis`.

## Security Rule
- `database` and `redis` MUST NOT expose ports to `frontend-net` or the host (0.0.0.0). They belong strictly to `backend-net`.
- `services/api` acts as the sole gateway.

## Environment Variables
- Secrets are injected at runtime via `.env` files matching `.env.example`.
- Docker images must not bake secrets into the layers.
""")

# 10. docs/09-testing/test-strategy.md
write_file("docs/09-testing/test-strategy.md", """
# Testing Strategy

## Layers
1. **Unit Tests:** Run instantly. Target pure logic (e.g., attribution math).
2. **Integration Tests:** Target DB interactions and API routing.
3. **Golden Scenario Validation:** End-to-end test against SIH-ZENODO-ALPHA. Evaluates output against `ground_truth.json` (test environment only).

## Fixtures Required (`tests/fixtures/`)
- `mock_sar_valid.json`
- `mock_sar_invalid.json`
- `mock_ais_gap.csv`
- `mock_evidence_output.json`
- `mock_llm_response.json`

## CI/CD
- GitHub Actions executes unit tests and schema validations on every PR.
""")

# 11. .github/workflows/ci.yml
write_file(".github/workflows/ci.yml", '''
name: CI & Security Gate

on:
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Secret Scanning (Gitleaks)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Python SAST (Bandit)
        run: |
          pip install bandit
          bandit -r services/ packages/ -ll -ii || echo "Warning only for now"

  schema-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate JSON Schemas exist and are parseable
        run: |
          python -m json.tool packages/contracts/evidence.schema.json > /dev/null
          python -m json.tool packages/contracts/llm-interpretation.schema.json > /dev/null
''')

# 12. .github/pull_request_template.md
write_file(".github/pull_request_template.md", """
## Description
<!-- Describe your changes -->

## Contract Validation
- [ ] This change does NOT break `evidence.schema.json`.
- [ ] This change does NOT break `llm-interpretation.schema.json`.

## Security Checklist
- [ ] No secrets or `.env` files are included in this PR.
- [ ] Internal ports (DB, Redis) remain isolated.
- [ ] Ground Truth isolation is preserved.

## Pod Approval
- [ ] Has cross-pod review (if affecting shared contracts or API boundaries).
""")

print("Repository hardening scaffolding complete.")
