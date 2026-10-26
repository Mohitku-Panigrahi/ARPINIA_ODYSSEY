# ARPINIA ODYSSEY — MODULE CONTRACTS

Version: 1.1

---

# 1. CORE CONTRACTS

Teams MUST NOT arbitrarily change these interfaces.

## A. EVIDENCE JSON (Scoring Engine Output)
The definitive source of truth payload.
```json
{
  "investigation_id": "uuid",
  "spill_geometry": "geojson",
  "origin_probability": "geojson",
  "candidates": [
    {
      "mmsi": "123456789",
      "attribution_score": 0.89,
      "stability_score": 0.92,
      "evidence_for": ["proximity_match", "drift_correlation"],
      "evidence_against": ["ais_gap_detected"]
    }
  ]
}
```

## B. LLM INTERPRETER CONTRACT
Consumes Evidence JSON. Outputs human text.
```json
{
  "investigation_id": "uuid",
  "executive_summary": "string",
  "candidate_explanations": {
    "123456789": "Vessel ranked highest due to..."
  },
  "recommended_next_actions": ["Review AIS gap"]
}
```

## C. PDF RENDERER CONTRACT
Consumes BOTH Evidence JSON and LLM Interpreter JSON to compile the final visual document.

---

# 2. TEAM BOUNDARIES

- **Frontend**: Consumes API outputs. Displays Evidence JSON numerically. Displays LLM text natively.
- **Platform Engine (API)**: Exposes endpoints. Validates requests.
- **AI/CV Engine**: Receives imagery, outputs `SpillResult` dict.
- **Worker/Geospatial Layer**: Executes Drift & AIS, outputs `DriftResult` & `AttributionResult`.
