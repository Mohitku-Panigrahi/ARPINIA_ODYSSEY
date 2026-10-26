# ARPINIA ODYSSEY â€” POD B
## PHASE B3 VALIDATION REPORT: BACKWARD RECONSTRUCTION

**Date:** 2026-08-28
**Subsystem:** Pod B (Backward Reconstruction)
**Phase:** B3 MVP

### 1. Objectives Achieved
The deterministic environmental forcing layer from Phase B2 has been integrated into a fully operational Backward Lagrangian Reconstruction pipeline using OpenDrift. This phase focused on physically robust, un-extrapolated, and reproducible advection from observed slick geometries backward in time.

### 2. Model Selection and Rationale
We selected `opendrift.models.oceandrift.OceanDrift` over `OpenOil` for the B3 MVP. 
- **Rationale**: Reversing time on complex oil weathering processes (evaporation, emulsification, dispersion) is thermodynamically and algorithmically unstable, leading to unbounded divergence. The `OceanDrift` class focuses exclusively on robust deterministic advection (currents and windage) which behaves safely under time reversal.

### 3. Missing Data Policy Enforcement
OpenDrift's default behavior is to substitute zeros for missing environmental data (`fallback=0`). This violates our strict doctrine.
- **Implementation**: The pipeline forces `environment:fallback:x_wind=None` and equivalent parameters for all velocity variables.
- **Result**: Particles that stray outside the validated spatio-temporal boundary of the B2 NetCDF fixtures, or encounter `NaN` fill values, are immediately stranded or deactivated, preventing hallucinated particle tracks. 

### 4. Polygon Seeding and Spatio-Temporal Boundaries
- **Seeding Mechanism**: The engine accepts a valid GeoJSON-equivalent Polygon (e.g. from Pod A's final mask) and executes `seed_within_polygon()`.
- **Time Semantics**: All public interfaces accept and maintain standard timezone-aware UTC `datetime` objects. They are converted strictly to offset-naive UTC purely for internal OpenDrift compatibility to prevent offset comparison crashes.

### 5. Probability Field Generation
Outputs are processed by the `ProbabilityFieldGenerator` utilizing 2D histograms with a configurable resolution (default 0.01 degrees). 
- **Output Contract**: Generates time slices spanning the backward duration (`t0, t-1h, ..., t-48h`).
- **Metrics**: Each time slice includes the particle grid density, spatial centroid, and exact probability thresholds required to draw High (50%), Medium (80%), and Broad (95%) confidence envelopes.

### 6. Golden Scenario Validation & Sensitivity Tests
A rigorous B3 pipeline sensitivity test was executed using the B2 `ERA5` and `Copernicus Marine (CMEMS)` datasets for the `SIH-ZENODO-ALPHA` target scenario.

- **Baseline Run**: `wind_uncertainty=0.0`, `current_uncertainty=0.0`
- **Perturbed Run**: `wind_uncertainty=2.0`, `current_uncertainty=0.1`

**Results (T-48h):**
- Baseline Centroid: Lat 33.6986, Lon 33.2220
- Perturbed Centroid: Lat 33.6974, Lon 33.2217
- The trajectories accurately diverged strictly according to the induced uncertainty parameters, proving the deterministic core and random seed configurations behave as designed.

### 7. Contract Output
The B3 module (`packages/reconstruction/engine.py`) returns a validated `Dict` that directly maps to the Evidence JSON schema, containing:
- Model versions and parameters
- Random seed provenance
- 48 hourly time slices, each containing probability density fields, centroids, and mass thresholds.

### 8. Final Status
The OpenDrift B3 pipeline is hardened, respects physical boundaries, and operates strictly on evidence. 

**B3 STATUS: B3_COMPLETE**

## B3 Freeze Record

Phase:
B3 — OpenDrift Backward Reconstruction

Frozen objective:
Probabilistic Spill-Origin Reconstruction

Status:
B3_FREEZE_APPROVED

OpenDrift:
1.14.10

Model:
OceanDrift

ERA5:
VERIFIED

ERA5 SHA256:
fc2d10e33b047872a3229ee52aaaa388cde746bc0b393aa018251a68456e1e7f

CMEMS:
VERIFIED

CMEMS SHA256:
f0c2a627f4f7cd7290df1ca1fe978cf94b774419fb41bb0ec3dd77aaedec16df

Probability normalization:
PASS

Invalid particle exclusion:
PASS

50/80/95 probability-mass regions:
PASS

No missing?zero fallback:
PASS

No extrapolation:
PASS

UTC boundary:
PASS

Sensitivity suite:
PASS

Reproducibility:
PASS

Regression tests:
PASS

Secrets:
NONE

Frozen contracts changed:
NO

Known limitations:
- This is not exact source determination; 
- Current forcing is finite-resolution model data; 
- CMEMS forcing is daily; 
- Backward trajectories amplify uncertainty; 
- B3 controlled sensitivity is not full Monte-Carlo attribution; 
- Advanced oil weathering is not reversed in the current baseline; 
- No vessel attribution occurs in B3; 
- Final quality depends on Pod A geometry and forcing quality.
