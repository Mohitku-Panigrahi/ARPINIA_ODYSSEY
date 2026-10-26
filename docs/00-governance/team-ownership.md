# ARPINIA ODYSSEY — TEAM OWNERSHIP & ACCESS CONTROL

This document establishes the official repository ownership model, access boundaries, and review governance for the ARPINIA ODYSSEY project (SIH26143).

---

## 1. Team Registry & Identities

| Role | Member Name | GitHub Username | Primary Responsibility |
| :--- | :--- | :--- | :--- |
| **Project Lead** | Rudra Narayan Mishra | `@RudraNarayanMishra2142` | Overall Architecture, Lead Review, Contracts, Cross-Pod Governance |
| **Pod A** | Mohit | `@Mohitku-Panigrahi` | Computer Vision, SAR Preprocessing & Segmentation, Local LLM |
| **Pod A** | Kamal | `@kamal-loachan` | Model Validation, Look-Alike Filtering, Inference Backend |
| **Pod B** | Amrit | `@amritkaur78190-sketch` | Reconstruction, AIS Correlation, Attribution, Stability, Backend Services |
| **Pod C** | Chandana | `@chandana-2204` | Frontend Dashboard, Map UI, Responsive UX |
| **Pod C** | Rani | `@panditrani83-crypto` | Investigation Workflow, Dossier/PDF Export, Uncertainty Visuals |

---

## 2. Access Model Principles

1. **Read-All**: Every team member has read access to the entire repository for complete transparency and architectural awareness.
2. **Pod-Scoped Contribution**: Pod members contribute strictly through pull requests to their owned directories.
3. **Protected Main**: Direct pushes to `main` by normal collaborators are blocked.
4. **Code Owner Reviews**: Pull requests require approvals from the designated path Code Owners.
5. **Path-Ownership CI Gate**: Automated CI checks block pull requests modifying paths outside the author's Pod boundary.
6. **Lead Authority**: The Project Lead (`@RudraNarayanMishra2142`) has universal write, review, and override authority across all paths.

---

## 3. Path Ownership Matrix

| Path Pattern | Primary Owner | Other Pod Access | Lead Approval Required? |
| :--- | :--- | :--- | :--- |
| `/models/**` | **Pod A** (`@Mohitku-Panigrahi`, `@kamal-loachan`) | Read Only | Required if Cross-Pod |
| `/services/ai-engine/**` | **Pod A** (`@Mohitku-Panigrahi`, `@kamal-loachan`) | Read Only | Required if Cross-Pod |
| `/docs/05-ai/**` | **Pod A** (`@Mohitku-Panigrahi`, `@kamal-loachan`) | Read Only | Required if Cross-Pod |
| `/packages/geo/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/metocean/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/reconstruction/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/ais/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/attribution/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/stability/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/counter_evidence/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/forward_validation/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/evidence/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/packages/shared/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/services/api/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/services/worker/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/database/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/infrastructure/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/scripts/dev/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/scripts/golden/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/scripts/validation/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/docs/07-backend/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| `/docs/08-deployment/**` | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| Pod B Unit Tests (`tests/unit/test_geo.py`, `test_metocean.py`, etc.) | **Pod B** (`@amritkaur78190-sketch`) | Read Only | Required if Cross-Pod |
| Pod A Unit Tests (`tests/unit/test_ai_*.py`, `test_sar_*.py`, etc.) | **Pod A** (`@Mohitku-Panigrahi`, `@kamal-loachan`) | Read Only | Required if Cross-Pod |
| Pod C Unit Tests (`tests/unit/test_web_*.py`, `test_ui_*.py`, etc.) | **Pod C** (`@chandana-2204`, `@panditrani83-crypto`) | Read Only | Required if Cross-Pod |
| `/apps/web/**` | **Pod C** (`@chandana-2204`, `@panditrani83-crypto`) | Read Only | Required if Cross-Pod |
| `/docs/06-frontend/**` | **Pod C** (`@chandana-2204`, `@panditrani83-crypto`) | Read Only | Required if Cross-Pod |
| `/packages/contracts/**` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/.github/**` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/AGENTS.md`, `PRE-CODE-GATE.md`, `SECURITY.md` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/requirements.txt`, `requirements-dev.txt` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/data/samples/golden-scenario-v1/**` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/docs/00-governance/**` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/docs/09-testing/**` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/rp/**` | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |
| `/tests/integration/**`, `/tests/e2e/**`, Unclassified Tests | **Project Lead** (`@RudraNarayanMishra2142`) | Read Only | **ALWAYS REQUIRED** |

---

## 4. Enforcement Mechanisms

1. **GitHub CODEOWNERS**: Automatically requests reviews from Pod owners and Project Lead upon PR creation.
2. **GitHub Actions (`path-ownership.yml`)**: Analyzes `git diff` against base branch. Fails PRs if unauthorized paths are detected.
3. **Branch Protection on `main`**: Requires 1 passing code-owner review, all CI status checks (Path Ownership, Secret Scanning, Schema Validation, Unit Tests) to be green, dismisses stale approvals, and disables direct pushes or force pushes.
