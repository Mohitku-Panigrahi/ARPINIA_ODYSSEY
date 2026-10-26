# ARPINIA ODYSSEY — MVP SPECIFICATION

Version: 1.1
Status: LOCKED

---

# 1. MVP OBJECTIVE

Demonstrate a reliable, deterministic investigation pipeline over flashy AI. The MVP must use a single validated "Golden Scenario" to prove end-to-end functionality.

---

# 2. MUST HAVE (P0)

- Historical SAR incident ingestion.
- Spill geometry extraction (SAR segmentation).
- Environmental validation (static dataset association).
- Backward drift simulation (origin probability cloud).
- AIS candidate retrieval and filtering.
- Deterministic candidate ranking and attribution scoring.
- Generation of the canonical **Evidence JSON**.
- Basic UI displaying map, candidates, and deterministic evidence.

---

# 3. SHOULD HAVE (P1)

- Local LLM Interpretation layer (consuming Evidence JSON).
- Uncertainty/Stability scoring visualizations.
- ARPINIA Odyssey Branded PDF Report Generation.
- Explainable evidence UI (evidence for / against).

---

# 4. NICE TO HAVE (P2)

- Interactive timeline animations.
- Advanced Deck.gl 3D visualizations.
- Automated anomaly detection flagging.

---

# 5. DEFERRED (Out of Scope for MVP)

- Real-time global satellite ingestion.
- Commercial live AIS API integration.
- Distributed Kubernetes infrastructure.
- External LLM API dependencies.

---

# 6. FAILURE CONDITIONS

- MVP fails if the LLM outage breaks the core analysis.
- MVP fails if UI displays fabricated data or fake attribution scores.
