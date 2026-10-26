# ARPINIA ODYSSEY — FAILURE STATES MATRIX

No system fails silently. ARPINIA Odyssey enforces explicit failure handling across 7 dimensions.

## 1. Missing Data
**State:** `ERR_DATA_MISSING`
**Action:** Pipeline halts. API returns 400. LLM is not invoked.

## 2. Model Timeout
**State:** `ERR_MODEL_TIMEOUT`
**Action:** Worker marks task as FAILED. Retries up to 3 times before abandoning with 504.

## 3. Database Failure
**State:** `ERR_DB_UNAVAILABLE`
**Action:** API rejects new incidents with 503. Worker pauses queue.

## 4. MetOcean Desync
**State:** `ERR_ENVIRONMENTAL_DESYNC`
**Action:** If wind/current data does not overlap the SAR bounding box, attribution fails safely and logs a spatial exception.

## 5. AIS Gap Exceeds Threshold
**State:** `WARN_EXTREME_AIS_GAP`
**Action:** Pipeline continues, but Candidate Attribution stability score is heavily penalized, and LLM is flagged to report high uncertainty.

## 6. Zero Candidates Found
**State:** `INFO_NO_CANDIDATES`
**Action:** Pipeline completes successfully. Evidence JSON records 0 candidates. LLM reports an inconclusive search (dark vessel with no AIS footprint).

## 7. Contract Violation
**State:** `ERR_CONTRACT_VIOLATION`
**Action:** If a Pod's output fails to validate against `evidence.schema.json`, the payload is rejected instantly by the API/message broker.
