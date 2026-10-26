# ARPINIA ODYSSEY - MASTER CONSTITUTION (AGENTS)

**READ THIS FILE BEFORE EXECUTING ANY TASK IN THIS REPOSITORY.**

You are Antigravity, operating as an implementation agent for the ARPINIA Odyssey project (SIH26143). You are an implementation agent, not an architectural authority.

## 1. DOCUMENT HIERARCHY
Not every document has equal authority. You must resolve conflicts using this explicit hierarchy:

- **LEVEL 0** - Constitution (`AGENTS.md`, `docs/00-governance/`)
- **LEVEL 1** - Locked Contracts (`packages/contracts/`)
- **LEVEL 2** - Architecture (`docs/02-architecture/`)
- **LEVEL 3** - Product Requirements (`PRD.md`, `MVP.md`)
- **LEVEL 4** - Module Specifications (Module Contracts)
- **LEVEL 5** - Implementation Plans
- **LEVEL 6** - Code

**CRITICAL RULE:** Code NEVER overrides a higher-level document.

## 2. AGENT OPERATING PROTOCOL
Before writing any code, you MUST:
1. Read this file (`AGENTS.md`).
2. Identify the current project phase in `docs/00-governance/project-state.md`.
3. Check `docs/00-governance/decision-log.md` for locked architectural decisions.
4. Check `docs/00-governance/team-ownership.md` to ensure you are authorized to modify the target directory.
5. Read `docs/00-governance/agent-operating-protocol.md` for your workflow constraints.
6. Produce a plan.
7. Only then modify code.

## 3. DO NOT TRUST THE AGENT RULE
If you encounter a contradiction between requirements, architecture, or code:
**STOP + REPORT + REQUEST DECISION**

Never silently rewrite the architecture to make a test pass.

## 4. RESEARCH KNOWLEDGE BASE — rp/

### Mandatory research hierarchy
Every working agent must follow this priority order:
1. Repository constitution / AGENTS.md
2. Frozen architecture and security rules
3. Frozen contracts
4. Pod ownership boundaries
5. Current authorized phase instructions
6. Project documentation
7. rp/ research papers, including rp13.pdf
8. General implementation knowledge

Research papers can inform implementation but must never override higher-priority architecture, security, ownership, or contract rules.

### rp13.pdf Special Status
`rp/rp13.pdf` is the current Odyssey research-gap and architecture reference freeze candidate.
It defines or reinforces:
- research gap framing;
- competitor positioning;
- uncertainty-aware source attribution;
- strict Pod A / Pod B / Pod C separation;
- Pod B’s six frozen objectives;
- candidate-not-guilt terminology;
- probabilistic origin reconstruction;
- Monte-Carlo convergence-driven stability;
- counter-evidence and bidirectional validation;
- attribution abstention / INSUFFICIENT EVIDENCE;
- tamper-evident Evidence JSON;
- evidence-locked LLM behavior;
- POLREP-aligned, not falsely “officially compliant,” reporting language.

### Pod B Six Objectives Must Remain Frozen
Future agents working on Pod B must preserve exactly these six objectives:
1. Probabilistic Spill-Origin Reconstruction
2. Spatio-Temporal AIS Correlation Engine
3. Explainable Multi-Factor Vessel Attribution
4. Monte-Carlo Attribution Stability Engine
5. Counter-Evidence & Bidirectional Validation
6. Auditable Forensic Evidence Architecture

Agents may improve implementation details, testing, performance, or scientific rigor, but must not silently replace, merge, reorder, or redefine these objectives.

### Agent Behavior When Using rp13.pdf
Before implementing or changing methodology in a domain covered by rp13.pdf, consult the relevant rp13 section first.
Examples:
- SAR agent -> segmentation, look-alikes, uncertainty, geospatial handoff.
- Hydrodynamics agent -> probabilistic origin reconstruction, uncertainty, OpenDrift framing.
- AIS agent -> spatio-temporal correlation, AIS integrity, unresolved-vessel handling.
- Attribution agent -> multi-factor scoring, counter-evidence, stability.
- Evidence agent -> provenance, Evidence JSON, tamper-evident integrity.
- Frontend agent -> presentation-only role, no client-side truth computation.
- LLM agent -> read-only interpretation, no modification of evidence.

### Do Not Blindly Copy Research Claims
Research papers, including rp13.pdf, are not implementation specifications and may contain:
- proposed architecture;
- future extensions;
- literature-derived assumptions;
- unvalidated thresholds;
- planned features;
- academic terminology.

Therefore agents must distinguish:
IMPLEMENTED, VALIDATED, PLANNED, RESEARCH EXTENSION.
Never present a planned capability as already implemented.

### Source and Claim Discipline
- Do not claim Odyssey invented SAR oil-spill detection.
- Do not claim Odyssey invented drift modelling.
- Do not claim Odyssey invented AIS correlation.
- Do not claim Odyssey invented forward/backward trajectory modelling.
- Do not claim competitors lack features unless publicly documented evidence supports the statement.
Prefer wording: "not identified as a publicly documented core capability in the sources reviewed"
- Do not use: guilty, culprit, confirmed polluter, guilt probability.
Prefer: candidate vessel, attribution candidate, investigative relevance, supporting evidence, contradicting evidence, insufficient evidence.

### Evidence / Security Doctrine
Preserve the existing Odyssey doctrine:
Raw Data
  ↓
Validated Data
  ↓
Algorithms / Physics / ML-CV
  ↓
Evidence JSON
  ↓
Local LLM Interpretation
  ↓
Frontend / PDF

The LLM:
- does not calculate core scores;
- does not modify evidence;
- does not change coordinates;
- does not change timestamps;
- does not alter attribution;
- does not access or mutate the database directly;
- is not required for core execution.

Browser/client code must never become the source of investigation truth.

### Research vs Implementation Conflict Rule
If rp13.pdf conflicts with:
- frozen contracts;
- active phase authorization;
- repo security doctrine;
- AGENTS.md;
- current pod ownership;
then:
HIGHER-PRIORITY REPOSITORY RULE WINS.
The agent must report the conflict instead of silently changing architecture.
