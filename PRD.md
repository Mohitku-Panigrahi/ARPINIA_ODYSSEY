# ARPINIA ODYSSEY — PRODUCT REQUIREMENTS DOCUMENT

Project Code: SIH26143
Status: LOCKED
Version: 1.1

---

# 1. PRODUCT VISION

ARPINIA Odyssey is a deterministic maritime investigation platform that converts multi-source geospatial evidence into an auditable, uncertainty-aware vessel attribution package, with a local LLM used only for interpretation.

**Non-Goals:** Legal verdicts, global real-time surveillance, autonomous enforcement, LLM-driven truth.

---

# 2. CORE WORKFLOW & FEATURES

**FR-01 — Incident Creation**: User uploads SAR imagery and metadata.
**FR-02 — SAR Analysis**: Deterministic segmentation of oil spills.
**FR-03 — Environmental Context**: Wind and current associations.
**FR-04 — Backward Drift**: Physics-based probabilistic origin estimation.
**FR-05 — AIS Candidate Retrieval**: Spatiotemporal vessel tracking.
**FR-06 — Attribution Analysis**: Deterministic ranking based on proximity, drift compatibility, and behavioral anomalies.
**FR-07 — Uncertainty / Stability**: Quantifying score robustness against environmental variations.

---

# 3. THE EVIDENCE JSON & PDF WORKFLOW

**FR-08 — Evidence JSON Contract**:
The core engine produces a strictly typed `Evidence JSON`. This is the absolute source of truth.

**FR-09 — LLM Interpretation**:
The LLM consumes the Evidence JSON to produce human-readable summaries and next-step recommendations. It cannot alter the underlying data.

**FR-10 — PDF Report Generation**:
The pipeline combines `Evidence JSON` + `LLM Interpretation` + `Frontend Template` to generate an ARPINIA ODYSSEY branded PDF. The PDF relies strictly on the structured evidence for numerical data.
