# ARPINIA ODYSSEY — DATA FLOW SPECIFICATION

Version: 1.1

---

# 1. CORE PIPELINE (SYNC & ASYNC)

1. **Raw Data** (Sync Upload)
2. **Validation** (Sync API)
3. **Processing** (Async Worker)
4. **Algorithms: SAR, Drift, AIS** (Async Worker)
5. **Evidence JSON Generation** (Async Worker Output)
   ↳ *[DETERMINISTIC PIPELINE COMPLETE]*
6. **Local LLM Interpretation** (Async Worker / Downstream)
7. **Frontend State Update** (Sync Poll/WebSocket)
8. **PDF Report Generation** (Sync Request)

---

# 2. INCIDENT STATE MACHINE

`CREATED` → `VALIDATING` → `PROCESSING` → `SPILL_DETECTED` → `ENVIRONMENT_READY` → `DRIFT_RUNNING` → `AIS_ANALYSIS` → `ATTRIBUTION_RUNNING` → `EVIDENCE_JSON_READY` → `LLM_INTERPRETATION_OPTIONAL` → `REPORT_READY` → `COMPLETED`

*Failure State:* Any state → `FAILED`. Never silently continue with corrupted data.

---

# 3. SYNCHRONOUS VS ASYNCHRONOUS BOUNDARIES

- **API Layer**: Exclusively synchronous REST endpoints. Triggers async jobs.
- **Investigation Engine**: Strictly asynchronous (Celery/Redis).
- **LLM Layer**: Asynchronous task triggered *only* after `EVIDENCE_JSON_READY`.

---

# 4. LLM FLOW RESTRICTION

`Structured Evidence JSON` → `Validation` → `Prompt Construction` → `Local LLM` → `Human-Readable JSON` → `UI/PDF`
*The LLM result is NEVER fed back into scientific computation.*
