# POD B PHASE B5 — REPORT

## Objective
Implement a multi-factor, explainable vessel attribution scoring model that ranks physical candidates based on available evidence, producing a relevance score distinct from evidence coverage.

## Inputs & Architecture
- **Input**: B4 Candidate summaries (frozen B1-B4 outputs).
- **Processing**: Pure offline, feature-based scoring (O(C * F)).
- **Ranking**: Timsort (O(C log C)).
- **Data Structures**: Immutable Pydantic models (CandidateAttribution, FactorResult), Hash Maps for feature loops.

## Feature Definitions & Missing Data Treatment
1. **F1 Spatial Compatibility**: Maps P50/P80/P95 to heuristic strengths (1.0, 0.75, 0.50). Missing overlap scores 0.0.
2. **F2 Temporal Compatibility**: Maps B4's 	emporal_match to 1.0.
3. **F3 Origin Compatibility**: Deferred due to current B4 interface limitation (B4 does not preserve slice-by-slice intersection arrays).
4. **F4 Closest Approach**: Continuous relevance via exp(-distance / d_ref). d_ref is derived dynamically from the median P95 grid area.
5. **F5 AIS Continuity**: Serves as an Evidence Coverage modifier based on max_gap_seconds. Perfect (<1h) -> 1.0 coverage multiplier, zero (>4h) -> 0.0 coverage.
6. **F6 Behavior**: Deferred.

**Missing Data**: Missing factor results are marked vailable=False and their weights are removed from the normalization denominator. This prevents missing features from artificially pushing the score to zero, while properly degrading the Evidence Coverage fraction.

## Tie Handling & Abstention
- **Abstention**: Candidates with evidence_coverage < 0.3 are automatically excluded to INSUFFICIENT_EVIDENCE.
- **Ties**: If score differences fall below 	ie_tolerance (0.05), candidates are marked EFFECTIVELY_TIED and sorted by coverage.

## Performance
- **Time Complexity**: Feature Evaluation O(C * F), Ranking O(C log C).
- **Space Complexity**: O(C * F). No heavy raw AIS arrays are kept in memory for B5.
- **Golden Benchmark**: Scored 1 candidate in < 0.01s.
- **NOAA Real AIS Benchmark**: Executed correctly (0 overlapping candidates).
- **Peak Memory**: Near-zero delta above B4.

## Trust & Security
- **Security**: No tokens required. No database queries.
- **Provenance**: Designed from mathematical specifications. No copied code.

## Known Limitations
- F3 is deferred; currently, persistence over moving probability slices is not evaluated, only strict spatial bounding overlap (F1).
