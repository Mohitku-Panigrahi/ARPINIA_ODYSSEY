# POD B — PHASE B2 REPORT

## 1. Objective
Build the deterministic environmental forcing layer required for ARPINIA ODYSSEY's backward drift reconstruction. Validate, normalize, time-align, space-align, and verify units for authoritative ECMWF ERA5 and CMEMS ocean current data. Provide deterministic and reproducible interpolation schemas before providing forcing data to OpenDrift.

## 2. Environmental Data Sources

| Source | Product | Variables | Resolution | Coverage | Purpose |
|--------|---------|-----------|------------|----------|---------|
| ECMWF / CDS | ERA5 | u10, v10 | ~0.25 deg, hourly | Surface | Wind forcing |
| Copernicus Marine (CMEMS) | Global Ocean Physics Reanalysis | uo, vo | ~1/12 deg, daily/hourly | Multi-level, near-surface selected | Ocean current forcing |

## 3. Implemented Components

| Component | Path | Purpose |
|---|---|---|
| Exceptions | `packages/metocean/exceptions.py` | Granular exception domain for missing data, out-of-bounds queries, invalid units, and malformed datasets. |
| Models | `packages/metocean/models.py` | Strict validation wrappers (`WindVector`, `CurrentVector`, `MetOceanPoint`) enforcing naive-timestamp rejection and non-finite value protection. |
| Interpolation | `packages/metocean/interpolation.py` | Grid subsetting and spatial/temporal bilinear/trilinear interpolation rejecting silent extrapolation. |
| ERA5 Reader | `packages/metocean/era5.py` | Adapts ERA5 `.nc` format to canonical `WindVector`. Enforces explicit variables (`u10`, `v10`) and units (`m s**-1`). |
| CMEMS Reader | `packages/metocean/cmems.py` | Adapts CMEMS `.nc` format to canonical `CurrentVector`. Handles selecting nearest depth level (e.g. 0.49m) and variables (`uo`, `vo`). |
| Unit Tests | `tests/unit/test_metocean.py` | Validates time normalization, boundary coverage, interpolation, missing values handling, and determinism using synthesized controlled fixtures. |

## 4. ERA5 Handling
- Reads `longitude`, `latitude`, `time`, `u10`, and `v10`.
- Validates units explicitly (`m s**-1` or `m/s`).
- Detects the descending latitude orientation standard in ERA5 and strictly aligns it for interpolation without flipping the underlying geometry implicitly.

## 5. CMEMS Handling
- Reads `longitude`, `latitude`, `depth`, `time`, `uo`, and `vo`.
- Does not assume depth zero is exactly surface. Programmatically isolates the depth index closest to the user's targeted operational depth (e.g., `target_depth_m=0.49`).
- Validates current velocity units as strictly metric (`m/s`).

## 6. Unit Normalization
- All internal computations standardize on `m/s` for velocities and Decimal Degrees for coordinates. 
- Input units are hard-verified. If unsupported units are discovered, `UnsupportedUnitError` explicitly fails the pipeline.

## 7. Timestamp Handling
- `cftime` conversions normalize grid epoch offsets to standard Unix seconds.
- All querying via `MetOceanPoint` explicitly demands a timezone-aware UTC datetime.
- Naive timestamps throw `ValueError`.

## 8. Spatial Handling
- Bounds are explicitly asserted by the interpolator. Queries falling outside the geographic bounding box of the dataset safely throw `SpatialCoverageError`.
- Evaluates longitudinal offsets properly to account for 0-360 vs -180-180 dataset standards.

## 9. Interpolation Policy
- Trilinear (Bilinear Spatial + Linear Temporal) via Scipy's `RegularGridInterpolator`.
- `bounds_error=True`: Out-of-bounds queries strictly fail. **No silent extrapolation** is performed at grid edges.

## 10. Missing Data Policy
- Grid points containing NetCDF `_FillValue` or `missing_value` are mapped directly to `np.nan`.
- If an interpolation query yields `NaN` (due to touching a masked cell or land), `MissingDataError` explicitly stops execution rather than returning `0.0`.

## 11. Golden Scenario Compatibility
- SAR detection time: `2018-08-13T15:44Z`
- Required forcing window: `2018-08-13T15:44Z` through `2018-08-15T15:44Z`
- Golden ERA5 / CMEMS temporal/spatial coverage: *(Currently represented by local unit-test fixtures to ensure reproducibility before pulling the 1GB payload.)*
- **COMPATIBLE** (architecture fully supports the required bounding box and time limits).

## 12. Dataset Provenance
- Fixture generation (`scripts/generate_fixtures.py`) ensures test grids accurately represent ECMWF and Copernicus formatting logic.
- Real datasets for the Golden Scenario will be processed exclusively upon manual extraction and storage in `data/raw/`.

## 13. Checksums
- `ERA5_wind_20180813_20180815.nc`: MOCK DATA PLACEHOLDER
- `CMEMS_currents_20180813_20180815.nc`: MOCK DATA PLACEHOLDER
*(Actual SHA-256 hashes must be calculated upon final extraction of the physical multi-GB assets.)*

## 14. Tests
- Total 4 macro-suites (Strictness, CMEMS reading, ERA5 reading, Coverage bounding). All pass seamlessly.

## 15. Security Review
- Zero credentials or API keys exist in source code.
- Filepath parameters do not support remote protocol deserialization or shell commands.

## 16. Performance / Storage Notes
- Data is parsed dynamically. The `GridInterpolator` loads data arrays. If physical assets exceed RAM bounds during full production execution, `dask` / `xarray` lazy-chunk loading should be introduced.

## 17. Known Limitations
- Does not currently support live downloading via CDS or Copernicus API—requires static assets.
- If the NetCDF grid is massive, memory efficiency requires localized spatial subsetting before handing arrays to the interpolator.

## 18. Files Changed
- `packages/metocean/exceptions.py`
- `packages/metocean/models.py`
- `packages/metocean/interpolation.py`
- `packages/metocean/era5.py`
- `packages/metocean/cmems.py`
- `packages/metocean/__init__.py`
- `tests/unit/test_metocean.py`
- `scripts/generate_fixtures.py`
- `docs/07-backend/pod-b-phase-b2-report.md`

## 19. Git Diff Review
- Clean addition of `packages/metocean/` files and their accompanying tests. No untracked data payload binaries introduced. No frozen frontend, ML, or contracts were affected.

## 20. Phase Status
B2_COMPLETE
