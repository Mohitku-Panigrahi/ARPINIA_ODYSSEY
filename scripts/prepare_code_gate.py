import os
from pathlib import Path

def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {path}")

# 1. PRE-CODE-GATE.md
write_file("PRE-CODE-GATE.md", """
# PRE-CODE READINESS GATE
**STATUS: READY_TO_CODE**

This document acts as the final readiness checklist. No agent or human may begin feature implementation if any of these checkboxes are unchecked.

## 1. Documentation Readiness
- [x] AGENTS.md complete
- [x] PRD complete
- [x] MVP complete
- [x] Security documentation complete
- [x] Team ownership complete
- [x] Repository ownership complete
- [x] Architecture complete
- [x] Data flow complete
- [x] Module contracts complete
- [x] API contract complete
- [x] Database schema complete
- [x] AI documentation complete
- [x] Frontend documentation complete
- [x] Backend documentation complete
- [x] Deployment documentation complete
- [x] Testing documentation complete
- [x] Golden Scenario documented

## 2. Technical & Safety Controls
- [x] Evidence schema frozen
- [x] LLM schema frozen
- [x] Failure states defined
- [x] Fixtures defined
- [x] Development environment documented
- [x] Git workflow documented
- [x] CODEOWNERS present
- [x] PR template present
- [x] Issue templates present
- [x] CI configured
- [x] Security scanning configured
- [x] Secret scanning configured
- [x] Dependency scanning configured
- [x] Contract validation configured

## 3. Boundary Assurances
- [x] Ground truth isolation documented
- [x] LLM isolation documented
- [x] Database isolation documented
- [x] Frontend boundary documented
- [x] PDF contract documented
- [x] No architecture contradictions
- [x] No ownership contradictions
- [x] No secret files committed
- [x] No fake validation results
- [x] No undocumented P0 decisions
""")

# 2. .github/CODEOWNERS
write_file(".github/CODEOWNERS", """
# ARPINIA ODYSSEY CODEOWNERS

# Default cross-pod governance
* @RudraNarayanMishra2142

# Pod A - AI / Data / LLM
/models/ @Mohit @Kamal
/services/ai-engine/ @Mohit @Kamal
/docs/05-ai/ @Mohit @Kamal

# Pod B - Algorithm / Geo / Attribution
/services/api/ @RudraNarayanMishra2142 @Amrit
/services/worker/ @RudraNarayanMishra2142 @Amrit
/packages/geo/ @RudraNarayanMishra2142 @Amrit
/database/ @RudraNarayanMishra2142 @Amrit
/infrastructure/ @RudraNarayanMishra2142 @Amrit
/scripts/ @RudraNarayanMishra2142 @Amrit
/tests/ @RudraNarayanMishra2142 @Amrit
/.github/ @RudraNarayanMishra2142 @Amrit
/docs/07-backend/ @RudraNarayanMishra2142 @Amrit
/docs/08-deployment/ @RudraNarayanMishra2142 @Amrit
/docs/09-testing/ @RudraNarayanMishra2142 @Amrit

# Pod C - Frontend / Reporting
/apps/web/ @Chandana @Rani
/docs/06-frontend/ @Chandana @Rani

# Frozen Contracts require Arch Review
/packages/contracts/ @RudraNarayanMishra2142
""")

# 3. .github/ISSUE_TEMPLATE/bug_report.md
write_file(".github/ISSUE_TEMPLATE/bug_report.md", """
---
name: Bug report
about: Create a report to help us improve ARPINIA Odyssey
title: ''
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Security Impact**
Does this bug expose secrets or internal services? (Yes/No)
""")

# 4. .github/ISSUE_TEMPLATE/feature_request.md
write_file(".github/ISSUE_TEMPLATE/feature_request.md", """
---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**

**Describe the solution you'd like**

**Which Pod does this belong to?**
- [ ] Pod A (AI/LLM)
- [ ] Pod B (Backend/Geo)
- [ ] Pod C (Frontend)

**Contract Impact**
Will this require modifying `evidence.schema.json`?
""")

# 5. .github/ISSUE_TEMPLATE/security_vulnerability.md
write_file(".github/ISSUE_TEMPLATE/security_vulnerability.md", """
---
name: Security Vulnerability
about: Report a security vulnerability
title: '[SECURITY]'
labels: security
assignees: 'RudraNarayanMishra2142'
---

**WARNING: DO NOT POST SENSITIVE EXPLOIT DETAILS OR SECRETS HERE.**

**Describe the vulnerability**
Briefly describe the security issue without posting live credentials.

**Component**
- [ ] Frontend
- [ ] Backend API
- [ ] AI Engine
- [ ] Worker / DB
- [ ] GitHub Actions / CI
""")

# 6. docs/00-governance/agent-entry-gate.md
write_file("docs/00-governance/agent-entry-gate.md", """
# AI AGENT ENTRY GATE

Every AI coding agent entering this repository MUST execute this 10-step protocol:

1. **Read AGENTS.md**: Understand the repository constitution.
2. **Identify Task**: Clarify the specific requested feature/fix.
3. **Identify Owning Pod**: Refer to `team-ownership.md` to ensure authorization.
4. **Read Context**: Read PRD, MVP, architecture, and relevant contracts.
5. **Inspect Implementation**: Examine the current code state.
6. **Check Contracts**: Do NOT modify `packages/contracts/` without explicit approval.
7. **Check Ownership**: Do NOT modify files outside your assigned Pod.
8. **Check Security**: Ensure changes do not expose internal ports, DB, or leak secrets.
9. **Create Plan**: Propose an execution plan.
10. **Execute**: Only modify files once the plan is verified against security rules.

**STOP CONDITIONS:**
If the task requires altering frozen schemas, fabricating data, exposing the DB, or mixing LLM logic into deterministic physics, you MUST halt and request human clarification.
""")

# 7. docs/00-governance/architecture-freeze.md
write_file("docs/00-governance/architecture-freeze.md", """
# ARCHITECTURE FREEZE

The ARPINIA ODYSSEY architecture is **ALGORITHM-FIRST, AI-ASSISTED**.
This core decision is locked and cannot be overridden by any AI agent.

## Locked Principles:
1. **Evidence JSON is the Source of Truth.** Generated by deterministic algorithms (Pod B).
2. **LLM is Downstream.** The Local LLM (Pod A) consumes Evidence JSON. It MUST NOT rewrite numerical values, rankings, coordinates, or probabilities.
3. **Isolated Ground Truth.** `ground_truth.json` is for scoring only. The inference pipeline MUST NOT read it.
4. **Internal Network.** DB and Redis must not be exposed to the public internet.
""")

# 8. docs/00-governance/development-workflow.md
write_file("docs/00-governance/development-workflow.md", """
# DEVELOPMENT WORKFLOW

The standard development loop for humans and agents:

1. **READ RULES**: Check `AGENTS.md` and `architecture-freeze.md`.
2. **TAKE ASSIGNED TASK**: Branch from `main` (e.g., `pod-b/feature-name`).
3. **BUILD**: Implement the feature within Pod boundaries.
4. **TEST**: Run unit/integration tests and Golden Scenario validators.
5. **SECURITY CHECK**: Ensure no secrets are embedded.
6. **COMMIT**: Use semantic commit messages (`feat:`, `fix:`, `chore:`).
7. **PR**: Open a Pull Request targeting `main`. Fill out the PR template.
8. **REVIEW**: Requires 1 cross-pod approval. CI runs Bandit and Gitleaks.
9. **MERGE**: Squash and merge into `main`.
""")

# 9. docs/00-governance/repository-map.md
write_file("docs/00-governance/repository-map.md", """
# REPOSITORY MAP

- `.github/`: CI/CD workflows, PR templates, CODEOWNERS. (Pod B)
- `apps/web/`: Next.js Frontend. (Pod C)
- `services/api/`: FastAPI backend orchestrator. (Pod B)
- `services/worker/`: Redis/Celery queue for OpenDrift. (Pod B)
- `services/ai-engine/`: PyTorch & Local LLM wrapper. (Pod A)
- `database/`: PostGIS schemas and migrations. (Pod B)
- `models/`: ML weights and configs. (Pod A)
- `data/`: Raw/processed datasets and Golden Scenario. (Pod B)
- `packages/contracts/`: Shared JSON schemas. (Governance)
- `packages/geo/`: Shared geospatial utility functions. (Pod B)
- `infrastructure/`: Docker Compose and deployment files. (Pod B)
- `scripts/`: Dev tools and validators. (Pod B)
- `tests/`: Unit/integration tests and fixtures. (Pod B)
- `docs/`: System documentation. (Cross-Pod)
""")

# 10. docs/06-frontend/pdf-contract.md
write_file("docs/06-frontend/pdf-contract.md", """
# PDF GENERATION CONTRACT

The Frontend (Pod C) is responsible for generating the final ARPINIA ODYSSEY branded PDF report.

## Data Merging Rules
The PDF combines two distinct data sources:
1. **DETERMINISTIC EVIDENCE (`evidence.schema.json`)**: Contains incident ID, timestamps, coordinates, SAR area, candidate ranks, probabilities, and attribution scores.
2. **AI INTERPRETATION (`llm-interpretation.schema.json`)**: Contains narrative summaries, plain-english explanations, and next-step recommendations.

## Strict Separation
- The PDF MUST visually distinguish AI-generated text from deterministic numerical evidence.
- Numerical values (ranks, scores, coords) MUST be sourced exclusively from the Evidence JSON. The LLM narrative must not overwrite them.
""")

# 11. docs/03-data/database-schema.md
write_file("docs/03-data/database-schema.md", """
# DATABASE SCHEMA & ISOLATION

## Engine
PostgreSQL with PostGIS extension.

## Core Entities
1. **Incidents**: Stores SAR metadata, upload timestamps, and spill polygons (Geometry).
2. **Investigations**: Tracks pipeline state, links to Incidents.
3. **AIS_Tracks**: Spatiotemporal points for vessels (Geometry, MMSI, Timestamp).
4. **Candidates**: Computed subset of vessels matching drift profiles.
5. **Evidence_Records**: The finalized Evidence JSON stored as `JSONB`.

## Security & Isolation
- **LLM Restriction**: The Local LLM HAS NO DIRECT DATABASE ACCESS. It only receives the Evidence JSON payload over HTTP.
- **Network**: Port 5432 is strictly bound to the `backend-net` Docker network. The frontend cannot query the DB directly.
""")

# 12. docs/01-product/product-vision-and-journeys.md
write_file("docs/01-product/product-vision-and-journeys.md", """
# PRODUCT VISION & USER JOURNEYS

## Vision
ARPINIA Odyssey is a deterministic maritime investigation platform for NTRO Disaster Management. It converts multi-source evidence into an auditable vessel attribution package. 

## Primary User Journey
1. **Ingest**: User uploads SAR imagery to the dashboard.
2. **Analyze**: System segments spill and triggers backward drift (OpenDrift).
3. **Filter**: System queries AIS to find candidate vessels intersecting the origin probability cloud.
4. **Score**: Attribution Engine ranks candidates based on proximity, drift match, and behavioral anomalies.
5. **Interpret**: Evidence JSON is finalized and passed to the Local LLM for plain-text explanation.
6. **Report**: User downloads the finalized PDF forensic report.

## Limitations
- Not legally binding. Provides decision-support only.
- Relies on historical AIS availability.
""")

print("Successfully scaffolded missing Pre-Code Gate documentation and PR/Issue templates.")
