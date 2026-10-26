# POD B PHASE B5 — SCIENTIFIC SOURCE BASIS

This document establishes the scientific and operational foundation for the B5 Explainable Multi-Factor Vessel Attribution scoring logic.

## 1. Spatial-Temporal Collision Compatibility (F1 & F2)

**SOURCE**:
*Review of oil spill tracking and attribution methods*
*Authors*: Operational Oil Spill tracking guidance, maritime forensic standards.
*Claim Supported*: Identifying a polluter relies heavily on overlapping suspected vessel trajectories with the simulated "back-tracked" origin footprint at the estimated time of release.
*Odyssey Design Decision*: B5 implements Spatial Compatibility (F1) based on time-dependent intersection with OpenDrift probability tiers (P50/P80/P95). F2 strictly evaluates temporal alignment. 
*Limitation*: Cannot prove a discharge occurred; only proves the vessel was physically present within the feasible release area at the feasible time.

## 2. Geometric Near-Miss / Closest Approach (F4)

**SOURCE**:
*Haversine distance and geometric proximity in maritime domains*
*Concept Used*: When discrete grid evaluation misses a narrow intersection due to spatial discretization or minor positional error, geometric closest approach provides continuous relevance.
*Odyssey Design Decision*: F4 uses an exponential decay exp(-distance / d_ref) where d_ref is the characteristic radius of the P95 probability field. This bounds the score smoothly and prevents arbitrary cutoff discontinuities.
*Limitation*: F4 and F1 describe the same physical geometry (spatial proximity) and share a combined "Spatial-Geometric" evidence budget to prevent double-counting.

## 3. AIS Data Continuity and Reliability (F5)

**SOURCE**:
*AIS Dark Vessel and Gap Analysis*
*Claim Supported*: Vessels with large transponder gaps (e.g., > 4 hours) present significantly higher uncertainty in their actual tracks. Interpolation across such gaps is mathematically unreliable.
*Odyssey Design Decision*: F5 acts strictly as an **Evidence Coverage** modifier rather than a direct attribution penalty. A vessel is not scored as "more guilty" for having a gap, but its overall attribution relevance is marked as having lower evidence coverage (lower confidence).
*Limitation*: Non-transmission can be intentional (dark vessel) or accidental (satellite coverage drop); B5 does not distinguish intent.
