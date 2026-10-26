# ARPINIA ODYSSEY — DECISION LOG (ADR)

## ADR-001 — Algorithm-First Architecture
**Status:** ACCEPTED
**Decision:** Deterministic algorithms and validated ML/CV generate investigation truth. The LLM is strictly for interpretation.
**Reason:** Prevent hallucination and preserve reproducibility.
**Impact:** LLM cannot influence Evidence JSON.

## ADR-002 — Evidence JSON is Immutable
**Status:** ACCEPTED
**Decision:** The Evidence JSON contract (`packages/contracts/evidence.schema.json`) is the strict output of Pod 2 and the strict input to the LLM. It cannot be altered dynamically.

## ADR-003 — Golden Scenario V1 Frozen
**Status:** ACCEPTED
**Decision:** `SIH-ZENODO-ALPHA` is locked. It pairs Zenodo SAR with `SYNTHETIC_DEMO` AIS to ensure 100% reproducibility without commercial blockers.

## ADR-004 — Pod Ownership
**Status:** ACCEPTED
**Decision:** 3 isolated Pods (AI, Backend, Frontend). Cross-pod commits are forbidden without architecture review.

## ADR-005 — Frontend Stack
**Status:** ACCEPTED
**Decision:** Next.js (React) locked for `apps/web`.

## ADR-006 — Local LLM
**Status:** ACCEPTED
**Decision:** LLM execution must support localized/isolated execution to maintain data security and pipeline compliance.

## ADR-007 — Deployment Architecture
**Status:** ACCEPTED
**Decision:** Dockerized microservices orchestrated via `docker-compose`. Dependencies locked to Python 3.11, Node 22 LTS, PostgreSQL + PostGIS, Redis.
