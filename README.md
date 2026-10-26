
<div align="center">

<img src="assets/banner.svg" width="100%" alt="ARPINIA ODYSSEY"/>

<br/>

<p>
  <img src="https://img.shields.io/badge/STATUS-ACTIVE_DEVELOPMENT-06b6d4?style=for-the-badge&labelColor=030712&logo=satellite-dish&logoColor=06b6d4" alt="Status"/>
  <img src="https://img.shields.io/badge/SIH26143-DISASTER_MANAGEMENT-a855f7?style=for-the-badge&labelColor=030712" alt="SIH26143"/>
  <img src="https://img.shields.io/badge/GOLDEN_SCENARIO-FROZEN-f59e0b?style=for-the-badge&labelColor=030712" alt="Golden Scenario"/>
  <img src="https://img.shields.io/badge/ARCHITECTURE-ALGORITHM_FIRST-22c55e?style=for-the-badge&labelColor=030712" alt="Architecture"/>
</p>

<p>
  <img src="https://img.shields.io/github/last-commit/RudraNarayanMishra2142/arpinia-odyssey?style=flat-square&color=06b6d4&labelColor=0c1a2e" alt="Last Commit"/>
  <img src="https://img.shields.io/github/commit-activity/w/RudraNarayanMishra2142/arpinia-odyssey?style=flat-square&color=a855f7&labelColor=0c1a2e" alt="Commit Activity"/>
  <img src="https://img.shields.io/github/repo-size/RudraNarayanMishra2142/arpinia-odyssey?style=flat-square&color=f59e0b&labelColor=0c1a2e" alt="Repository Size"/>
</p>

### **FROM OCEAN OBSERVATION TO EVIDENCE-BACKED MARITIME INTELLIGENCE**

**ARPINIA ODYSSEY** is an algorithm-first, AI-assisted maritime forensic investigation platform for oil-spill attribution, developed for **Smart India Hackathon 2026 — SIH26143**.

<br/>

> **SEE THE SPILL. RECONSTRUCT THE PAST. CORRELATE THE VESSELS. QUANTIFY THE UNCERTAINTY.**

</div>

---

# 🌊 ARPINIA ODYSSEY

Oil spills can be detected from satellite imagery.

The harder question is:

> **Where did the spill originate, which vessels could have been responsible, and how strong is the available evidence?**

ARPINIA Odyssey is designed to transform that investigation into a structured, reproducible computational workflow.

The platform brings together:

- 🛰️ Sentinel-1 SAR imagery
- 🧠 Computer-vision-based spill segmentation
- 🌊 Meteorological & oceanographic data
- ⏪ Backward drift / hindcasting
- 🚢 AIS trajectory analysis
- 🗺️ Geospatial computation
- 📊 Attribution scoring
- 📐 Uncertainty & stability analysis
- 🤖 Local LLM interpretation
- 📄 ARPINIA Odyssey forensic reporting

But everything is governed by one architectural principle:

> ## 🔒 THE LLM DOES NOT PRODUCE THE INVESTIGATION TRUTH.

The investigation truth is generated **before the LLM is involved**.

---

# ⚡ THE CORE IDEA

Traditional workflows often stop at:

```text
Detect → Display
````

ARPINIA Odyssey is designed as:

```text
┌──────────────────────┐
│   SATELLITE / DATA   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   SPILL DETECTION    │
│   & SEGMENTATION     │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  SPILL GEOMETRY      │
│  EXTRACTION          │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ METOCEAN CONDITIONS  │
│ WIND + CURRENTS      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ BACKWARD HINDCASTING │
│ / DRIFT SIMULATION   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ PROBABILISTIC ORIGIN │
│ REGION               │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ AIS TRAJECTORY       │
│ CORRELATION          │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ CANDIDATE FILTERING  │
│ & ATTRIBUTION        │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ UNCERTAINTY /        │
│ STABILITY ANALYSIS   │
└──────────┬───────────┘
           ↓
╔══════════════════════╗
║   🔒 EVIDENCE JSON   ║
║   SOURCE OF TRUTH    ║
╚══════════╤═══════════╝
           ↓
┌──────────────────────┐
│ LOCAL LLM            │
│ INTERPRETATION ONLY  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ HUMAN-READABLE       │
│ EXPLANATION          │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ NEXT-ACTION          │
│ RECOMMENDATIONS      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ INVESTIGATION UI     │
└──────────┬───────────┘
           ↓
╔══════════════════════╗
║ ARPINIA ODYSSEY PDF  ║
║ FORENSIC DOSSIER     ║
╚══════════════════════╝
```

### The Intelligence Boundary

```text
                DETERMINISTIC INVESTIGATION
┌─────────────────────────────────────────────────────┐
│                                                     │
│  SAR → CV → MetOcean → Physics → AIS → Scoring     │
│                                      ↓              │
│                              Uncertainty Analysis   │
│                                      ↓              │
│                              🔒 Evidence JSON       │
│                                                     │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   LOCAL LLM     │
                  │ INTERPRETATION  │
                  └────────┬────────┘
                           ↓
             Human-readable intelligence
                           ↓
                 Recommended next steps
                           ↓
                    Investigation UI
```

The LLM **does not** determine the vessel.

It receives the structured Evidence JSON and explains what the deterministic investigation engine has already calculated.

---

# 🔒 NON-NEGOTIABLE ARCHITECTURE

ARPINIA Odyssey follows:

> **ALGORITHM-FIRST · AI-ASSISTED**

The investigation pipeline must remain functional without the LLM.

### The LLM MUST NEVER

* ❌ Invent evidence
* ❌ Modify numerical results
* ❌ Modify attribution scores
* ❌ Declare a vessel guilty
* ❌ Replace the physics model
* ❌ Replace AIS analysis
* ❌ Replace deterministic scoring
* ❌ Make unsupported predictions
* ❌ Directly query the database
* ❌ Modify investigation data
* ❌ Become a dependency for core execution

### If the LLM goes offline

```text
LLM OFFLINE
    │
    ▼
Core Investigation
    │
    ├── SAR Analysis       ✓
    ├── Drift Simulation  ✓
    ├── AIS Analysis      ✓
    ├── Attribution       ✓
    └── Evidence JSON     ✓
```

The system continues to function.

---

# 🧠 WHAT THE ALGORITHM ACTUALLY DOES

The core investigation engine is responsible for producing the measurable evidence.

```text
Sentinel-1 SAR
      │
      ▼
Spill Segmentation
      │
      ▼
Spill Polygon + Metadata
      │
      ├── Coordinates
      ├── Timestamp
      ├── Area
      └── Confidence
      │
      ▼
ERA5 + CMEMS
      │
      ▼
Backward Drift / Hindcasting
      │
      ▼
Probabilistic Origin Cloud
      │
      ▼
AIS Spatial + Temporal Filtering
      │
      ▼
Candidate Vessels
      │
      ▼
Attribution Scoring
      │
      ▼
Stability / Uncertainty Analysis
      │
      ▼
🔒 Evidence JSON
```

This output is the **authoritative computational result**.

---

# 🤖 AI INTERPRETATION LAYER

The local LLM operates **after** the Evidence JSON is generated.

Its responsibility is to make complex computational output understandable to a non-technical investigator.

```text
Evidence JSON
      ↓
Local LLM
      ↓
Structured Interpretation JSON
      ↓
Human-readable explanation
      ↓
Recommended next actions
      ↓
Operational suggestions
```

The interpretation layer may explain:

* What happened
* What the evidence indicates
* Why a vessel received a particular score
* What evidence supports or weakens a candidate
* What uncertainty exists
* What investigators should examine next
* What nearby maritime assets may be relevant for coordination
* What additional information could strengthen the investigation

The LLM **must remain grounded entirely in the Evidence JSON**.

---

# 📊 INVESTIGATION OUTPUT

ARPINIA Odyssey is not intended to simply produce:

```text
VESSEL A = GUILTY
```

Instead, it produces an evidence-backed assessment such as:

```text
┌───────────────────────────────────────────┐
│           INVESTIGATION RESULT            │
├───────────────────────────────────────────┤
│                                           │
│  Primary Candidate: Vessel A              │
│                                           │
│  Attribution Stability: 92%               │
│  Spatial Compatibility: HIGH              │
│  Temporal Compatibility: HIGH             │
│  AIS Continuity: VERIFIED                 │
│  Behavioral Anomaly: MODERATE             │
│                                           │
│  Evidence For: 4                          │
│  Evidence Against: 1                      │
│                                           │
│  ⚠ NOT A LEGAL VERDICT                   │
│                                           │
└───────────────────────────────────────────┘
```

The system communicates **evidence and uncertainty**, not unsupported certainty.

---

# 🛰️ GOLDEN SCENARIO V1

ARPINIA Odyssey uses a frozen benchmark scenario for reproducible development and testing.

| Asset             | Source / Mode                             | Status    |
| ----------------- | ----------------------------------------- | --------- |
| 🛰️ SAR Imagery   | Zenodo — M4D Sentinel-1 Oil Spill Dataset | 🔒 FROZEN |
| 🌬️ Wind          | ECMWF ERA5                                | 🔒 FROZEN |
| 🌊 Ocean Currents | Copernicus Marine Service                 | 🔒 FROZEN |
| 🚢 AIS            | `SYNTHETIC_DEMO`                          | 🔒 FROZEN |
| 🎯 Ground Truth   | Isolated benchmark file                   | 🔒 FROZEN |

### Golden Scenario ID

```text
SIH-ZENODO-ALPHA
```

The benchmark is designed to provide a reproducible environment for validating:

```text
SAR
 ↓
Segmentation
 ↓
Drift
 ↓
AIS Correlation
 ↓
Attribution
 ↓
Evidence JSON
```

Ground truth is isolated from the inference pipeline to prevent accidental data leakage during runtime.

---

# 🏗️ SYSTEM ARCHITECTURE

```text
                         ┌──────────────────────┐
                         │    INVESTIGATOR      │
                         │      BROWSER         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     NEXT.JS WEB      │
                         │   POD C — FRONTEND   │
                         └──────────┬───────────┘
                                    │
                              REST / JSON
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FASTAPI API      │
                         │ POD A — BACKEND/API  │
                         └───────┬───────┬──────┘
                                 │       │
                     ┌───────────┘       └────────────┐
                     ▼                                ▼
          ┌───────────────────┐            ┌───────────────────┐
          │    AI / LLM       │            │ ALGORITHM ENGINE  │
          │   POD A           │            │      POD B        │
          │                   │            │                   │
          │ Local LLM         │            │ OpenDrift         │
          │ Interpretation    │            │ AIS Analysis      │
          │ Backend Services  │            │ Attribution       │
          └─────────┬─────────┘            │ Evidence JSON     │
                    │                      └─────────┬─────────┘
                    │                                │
                    │                         🔒 TRUTH
                    │                                │
                    └──────────────┬─────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │   POSTGRESQL +       │
                         │       POSTGIS        │
                         └──────────────────────┘
```

---

# 👥 DEVELOPMENT PODS

ARPINIA Odyssey is developed by three tightly connected two-person pods.

## 🟣 POD B — ALGORITHM & ATTRIBUTION

**Rudra + Amrit**

### Primary ownership

```text
SAR / Investigation Data
        ↓
Algorithm Pipeline
        ↓
Drift / Hindcasting
        ↓
AIS Correlation
        ↓
Attribution
        ↓
Uncertainty / Stability
        ↓
🔒 Evidence JSON
```

### Responsibilities

* Core investigation algorithms
* OpenDrift integration
* Backward drift modelling
* AIS spatial-temporal analysis
* Candidate filtering
* Attribution scoring
* Uncertainty analysis
* Evidence JSON generation
* Algorithm validation
* Deterministic test fixtures

> **Pod B owns the investigation truth.**

---

## 🔵 POD A — AI & BACKEND INTELLIGENCE

**Mohit + Kamal**

### Primary ownership

```text
Evidence JSON
      ↓
Local LLM
      ↓
Interpretation JSON
      ↓
Backend API
      ↓
Frontend Delivery
```

### Responsibilities

* Local LLM training/inference
* LLM interpretation layer
* Strict Evidence JSON ingestion
* Interpretation JSON generation
* FastAPI backend
* API integration
* Service communication
* Required backend ports
* LLM isolation and fallback behavior

> **Pod A interprets the evidence but does not create or modify it.**

---

## 🟡 POD C — FRONTEND & VISUALIZATION

**Rani + Chandana**

### Primary ownership

```text
Backend Data
      ↓
Investigation Interface
      ↓
Maps + Timeline + Evidence
      ↓
Human-readable Investigation View
      ↓
ARPINIA Odyssey PDF
```

### Responsibilities

* Web interface
* Investigation dashboard
* Maps
* Vessel visualization
* Spill visualization
* Coordinates
* Date & timestamp display
* Investigation timeline
* Candidate ranking interface
* Evidence presentation
* LLM explanation presentation
* PDF dossier UI/design
* Responsive and production-quality UX

> **Pod C owns how the investigation is experienced, not how the evidence is calculated.**

---

# 🔗 POD INTEGRATION CONTRACT

The three pods meet at clearly defined boundaries.

```text
             ┌─────────────────────────┐
             │       POD B             │
             │ ALGORITHM & ATTRIBUTION │
             └────────────┬────────────┘
                          │
                          ▼
                🔒 EVIDENCE JSON
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
     ┌─────────────────┐       ┌─────────────────┐
     │      POD A      │       │      POD C      │
     │ AI + BACKEND    │       │    FRONTEND     │
     └────────┬────────┘       └────────┬────────┘
              │                         │
              ▼                         ▼
      Interpretation JSON       Investigation UI
```

No pod should silently redefine another pod's contract.

---

# 📦 REPOSITORY STRUCTURE

```text
arpinia-odyssey/
│
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
│
├── apps/
│   └── web/
│       └── ...
│
├── services/
│   ├── api/
│   ├── ai-engine/
│   └── worker/
│
├── database/
│   ├── migrations/
│   ├── seeds/
│   └── schema/
│
├── models/
│   ├── segmentation/
│   └── ...
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── samples/
│   └── README.md
│
├── packages/
│   ├── contracts/
│   │   ├── evidence.schema.json
│   │   └── llm-interpretation.schema.json
│   ├── geo/
│   └── shared/
│
├── infrastructure/
│   ├── docker/
│   ├── deployment/
│   └── nginx/
│
├── scripts/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
│
├── docs/
│   ├── 00-governance/
│   ├── 01-product/
│   ├── 02-architecture/
│   ├── 03-data/
│   ├── 04-api/
│   ├── 05-ai/
│   ├── 06-frontend/
│   ├── 07-backend/
│   ├── 08-deployment/
│   └── 09-testing/
│
├── AGENTS.md
├── PRD.md
├── MVP.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── README.md
└── .env.example
```

---

# 🔐 FROZEN CONTRACTS

The following contracts define communication between system components.

### Evidence Contract

```text
packages/contracts/evidence.schema.json
```

This is the **deterministic source of truth**.

```text
Algorithms
    ↓
Evidence JSON
    ↓
Validation
    ↓
API / LLM / Frontend
```

No downstream component may rewrite the underlying numerical evidence.

### LLM Contract

```text
packages/contracts/llm-interpretation.schema.json
```

This defines what the local LLM is allowed to return.

```text
Evidence JSON
     ↓
Local LLM
     ↓
LLM Interpretation JSON
```

The interpretation cannot become upstream evidence.

---

# 🛡️ SECURITY & RESILIENCE

ARPINIA Odyssey is designed as a production-oriented system rather than a disposable hackathon demo.

### Core principles

```text
SECURITY > CONVENIENCE
CORRECTNESS > SPEED
CONTRACTS > ASSUMPTIONS
DETERMINISTIC EVIDENCE > AI CLAIMS
REPRODUCIBILITY > CLEVERNESS
INTEGRATION > ISOLATED FEATURES
```

### Security boundaries

* Database is not directly exposed to the browser.
* Secrets are never shipped to the frontend.
* Internal services remain behind backend boundaries.
* LLM does not receive direct database access.
* LLM cannot modify Evidence JSON.
* Inputs must be validated at service boundaries.
* API contracts must be validated before integration.
* Sensitive configuration belongs in environment variables.
* Production deployment must use HTTPS.
* Authentication and authorization must be enforced at the appropriate service boundary.
* Generated evidence must remain traceable to its source data.

---

# 🧪 VALIDATION PHILOSOPHY

A feature is not considered complete merely because the interface looks correct.

Every module must be validated across:

```text
┌──────────────────────┐
│ Functional Correctness│
├──────────────────────┤
│ Contract Compliance  │
├──────────────────────┤
│ Integration           │
├──────────────────────┤
│ Failure Handling      │
├──────────────────────┤
│ Security              │
├──────────────────────┤
│ Reproducibility       │
└──────────────────────┘
```

Particular attention is given to:

* Broken API connections
* Incorrect JSON payloads
* Missing fields
* Invalid timestamps
* Coordinate mismatches
* Spatial reference errors
* AIS temporal misalignment
* Physics failures
* Empty candidate sets
* LLM failures
* Frontend/backend contract mismatches
* PDF generation failures
* Data provenance problems

---

# 🚀 DEVELOPMENT PHILOSOPHY

ARPINIA Odyssey is being built as a **serious product prototype**, not merely a collection of AI-generated code.

Before implementation:

```text
Understand
    ↓
Read the Constitution
    ↓
Read the Architecture
    ↓
Read the Contracts
    ↓
Understand Module Ownership
    ↓
Understand Inputs / Outputs
    ↓
Implement
    ↓
Test
    ↓
Integrate
    ↓
Audit
```

Every AI coding agent working inside this repository must treat:

```text
AGENTS.md
PRD.md
MVP.md
Architecture Documents
Module Contracts
API Contracts
JSON Schemas
Security Rules
```

as the project's governing specification.

---

# 🧭 INVESTIGATION EXPERIENCE

The final investigator experience is designed around a single workflow:

```text
┌──────────────────────────────────────────┐
│           NEW INVESTIGATION              │
│                                          │
│     Select / Upload SAR Scene            │
└────────────────────┬─────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│             INVESTIGATE                  │
│                                          │
│  Spill → Drift → AIS → Attribution       │
└────────────────────┬─────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│          EVIDENCE RESULTS                │
│                                          │
│  Origin • Candidates • Scores • Stability│
└────────────────────┬─────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│         AI INTERPRETATION                │
│                                          │
│  Explanation • Context • Next Actions    │
└────────────────────┬─────────────────────┘
                     ↓
┌──────────────────────────────────────────┐
│          FORENSIC DOSSIER                │
│                                          │
│       DOWNLOAD ARPINIA ODYSSEY PDF       │
└──────────────────────────────────────────┘
```

---

# 📄 FORENSIC DOSSIER

The final report combines deterministic evidence with human-readable interpretation.

```text
                 ARPINIA ODYSSEY
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
    EVIDENCE JSON          LLM INTERPRETATION
          │                       │
          │                       │
          └───────────┬───────────┘
                      ▼
               REPORT GENERATOR
                      │
                      ▼
             SHA-256 / PROVENANCE
                      │
                      ▼
             📄 PDF DOSSIER
```

The PDF should clearly distinguish:

**Calculated Evidence** from **AI Interpretation**.

The report must never make an AI-generated statement appear to be an independently measured fact.

---

# 🧰 TECHNOLOGY STACK

<div align="center">

| Layer          | Technology                                      |
| -------------- | ----------------------------------------------- |
| Frontend       | Next.js · React                                 |
| Visualization  | Web GIS / Map visualization                     |
| Backend        | Python · FastAPI                                |
| Physics        | OpenDrift                                       |
| Geospatial     | PostgreSQL · PostGIS                            |
| AI / CV        | PyTorch · U-Net / compatible segmentation model |
| LLM            | Local LLM                                       |
| Data           | Sentinel-1 · AIS · ERA5 · CMEMS                 |
| Infrastructure | Docker                                          |
| Contracts      | JSON Schema                                     |
| Testing        | Pytest + integration / E2E testing              |

</div>

---

# 🗺️ DEVELOPMENT ROADMAP

```text
PHASE 01
FOUNDATION
   │
   ├── Repository
   ├── Governance
   ├── Contracts
   └── Environments
   │
   ▼
PHASE 02
DATA + ALGORITHM
   │
   ├── SAR
   ├── MetOcean
   ├── AIS
   ├── Drift
   └── Attribution
   │
   ▼
PHASE 03
EVIDENCE ENGINE
   │
   └── 🔒 Evidence JSON
   │
   ▼
PHASE 04
AI + BACKEND
   │
   ├── Local LLM
   ├── Interpretation
   └── API
   │
   ▼
PHASE 05
FRONTEND
   │
   ├── Investigation UI
   ├── Maps
   ├── Timeline
   └── Evidence
   │
   ▼
PHASE 06
INTEGRATION
   │
   ├── End-to-end pipeline
   ├── Failure testing
   └── Security audit
   │
   ▼
PHASE 07
SHOWCASE
   │
   ├── Golden Scenario
   ├── Live Investigation
   ├── Forensic PDF
   └── SIH Demonstration
```

---

# 🎯 PROJECT OBJECTIVE

The objective is not to build another maritime map.

It is to build an investigation workflow capable of transforming fragmented maritime observations into:

```text
DATA
  ↓
COMPUTATION
  ↓
EVIDENCE
  ↓
INTERPRETATION
  ↓
ACTION
```

with every critical computational step remaining:

**traceable · explainable · testable · reproducible**

---

# ⚠️ IMPORTANT LIMITATION

ARPINIA Odyssey is an **investigative decision-support prototype**.

It does not independently establish legal guilt or replace qualified investigators, scientific validation, or official enforcement procedures.

Attribution scores represent computational evidence and uncertainty under the model assumptions and available data.

They are **not legal verdicts**.

---

# 🏁 THE ARPINIA ODYSSEY PRINCIPLE

<div align="center">

```text
╔══════════════════════════════════════════════════╗
║                                                  ║
║              OBSERVE THE OCEAN                  ║
║                      ↓                           ║
║              RECONSTRUCT THE PAST               ║
║                      ↓                           ║
║              CORRELATE THE VESSELS              ║
║                      ↓                           ║
║              QUANTIFY UNCERTAINTY               ║
║                      ↓                           ║
║              PRESERVE THE EVIDENCE              ║
║                      ↓                           ║
║              HELP THE INVESTIGATOR              ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

### **ARPINIA ODYSSEY**

**Not AI deciding the truth.**

**Algorithms establish the evidence.**

**AI helps humans understand it.**

</div>

---

<div align="center">

<br/>

**Built for Smart India Hackathon 2026 · SIH26143**

<br/>

`ALGORITHM-FIRST` · `AI-ASSISTED` · `EVIDENCE-DRIVEN` · `REPRODUCIBLE`

<br/>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ARPINIA ODYSSEY**

*From Ocean Observation to Evidence-Backed Maritime Intelligence.*

</div>
```
# ARPINIA_ODYSSEY
