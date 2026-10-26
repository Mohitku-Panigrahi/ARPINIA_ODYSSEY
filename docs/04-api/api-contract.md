# ARPINIA ODYSSEY — API CONTRACT

Version: v1.2

---

# 1. ENDPOINTS

**Investigations & Upload**
- `POST /api/v1/incidents`
  *(Accepts SAR imagery. Max upload limit: 500MB. Supported formats: .tif, .zip)*
- `POST /api/v1/incidents/{id}/investigate`
  *(Triggers async worker jobs (OpenDrift, AIS queries). Returns `job_id`)*
- `GET /api/v1/investigations/jobs/{job_id}/status`
  *(Used by frontend for status polling. Returns % complete and current stage)*

**Structured Data (DETERMINISTIC)**
- `GET /api/v1/investigations/{id}/evidence`
  *(Returns the canonical Evidence JSON containing geometry, scores, and candidates)*

**Interpretation (LLM)**
- `GET /api/v1/investigations/{id}/interpretation`
  *(Returns the LLM-generated text explaining the evidence. Fails gracefully if LLM offline)*

**Reporting**
- `POST /api/v1/investigations/{id}/report`
- `GET /api/v1/reports/{id}`

**Health & Ops**
- `GET /api/v1/health`
  *(Returns status of Postgres, Redis, and API)*

---

# 2. ASYNC JOBS & POLLING
Because OpenDrift and SAR segmentation are computationally heavy, the `/investigate` endpoint is strictly asynchronous. The frontend receives a `job_id` and must poll `/status` until `EVIDENCE_READY` is achieved.

---

# 3. EVIDENCE VS INTERPRETATION BOUNDARY
**Crucial Conceptual Separation:**
- `/evidence`: Serves the deterministic truth. The frontend relies on this for ALL numerical visualization, map rendering, and ranking.
- `/interpretation`: Serves the Local LLM's explanation of the evidence. The frontend must NEVER treat this as authoritative numerical evidence.

---

# 4. ERROR FORMAT & SECURITY

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable explanation",
    "recoverable": true
  }
}
```
All endpoints require Auth. Public APIs must NEVER expose internal service credentials. Frontend state must handle loading, partial success, and LLM-unavailable gracefully.
