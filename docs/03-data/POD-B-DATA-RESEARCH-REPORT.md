# POD B — DATA RESEARCH & VALIDATION REPORT

## 1. Objective
To investigate and identify the most authoritative, reproducible, and legally accessible datasets that will allow the Pod B deterministic investigation engine (MetOcean, OpenDrift, AIS attribution) to be tested against realistic maritime conditions without violating scientific validity.

## 2. SIH Dataset Requirements
- **AIS**: MarineCadastre or real AIS if available. Otherwise, synthetic AIS for the oil-spill region.
- **SAR**: Zenodo Sentinel-1 SAR Oil Spill Dataset as the baseline approved source.
These baseline sources must not be replaced merely for a "better looking" demo.

## 3. Current Golden Scenario
- **Status**: SIH-ZENODO-ALPHA (Frozen).
- The baseline SAR scene, spatial coordinates, timestamps, and metocean sources are locked. 
- Ground truth remains strictly isolated for offline scoring and will not be leaked into the pipeline.

## 4. AIS Dataset Candidates
| Dataset | Type | Source | Access | Coverage | Format | License | Suitability |
|---------|------|--------|--------|----------|--------|---------|-------------|
| **MarineCadastre** | REAL_AIS | US Govt | Public | US Waters | CSV / GeoParquet | Public Domain | High (If scenario is US) |
| **Danish Maritime Authority (DMA)** | REAL_AIS | Danish Govt | Public | Danish Waters | CSV | Open Data | High (European scenarios) |
| **Global Fishing Watch** | REAL_AIS | GFW / Google | Registration | Global (Fishing) | CSV/Parquet | CC BY | Medium (Restricted to fishing vessels) |
| **Synthetic Generator** | SYNTHETIC_DEMO | Internal | Internal | Targeted | JSON/CSV | Internal | High (For testing edge cases and attribution limits) |

## 5. SAR Dataset Candidates
| Dataset | Sensor | Source | Access | Format | Relevance |
|---------|--------|--------|--------|--------|-----------|
| **Zenodo (M4D Oil Spill)** | Sentinel-1 | Zenodo | Public | GeoTIFF | Baseline (Oil spill segmentation) |
| **Copernicus Data Space Ecosystem** | Sentinel-1 GRD | ESA/Copernicus | Public (API) | SAFE/GeoTIFF | High (Validation & secondary demonstrations) |
| **Alaska Satellite Facility (ASF)** | Sentinel-1 GRD | NASA ASF | Public | GeoTIFF | High (Alternative open data access for validation) |

## 6. Wind Dataset Candidates
| Dataset | Source | Variables | Resolution | Format | Suitability |
|---------|--------|-----------|------------|--------|-------------|
| **ECMWF ERA5** | Copernicus Climate Data Store | u10, v10 | Hourly, ~31km | NetCDF / GRIB | Highest (Authoritative reanalysis) |
| **NOAA GFS / CFSR** | NOAA NCEI | u10, v10 | Hourly, ~0.5 deg | GRIB2 | High (Alternative to ERA5) |

## 7. Ocean Current Dataset Candidates
| Dataset | Source | Variables | Resolution | Format | Suitability |
|---------|--------|-----------|------------|--------|-------------|
| **CMEMS Global Ocean Physics Reanalysis** | Copernicus Marine Service | eastward, northward velocity | Daily/Monthly, 1/12 deg | NetCDF | Highest (Global drift modelling) |
| **HYCOM** | HYCOM Consortium | u, v | 3-hourly, 1/12 deg | NetCDF | High |

## 8. Research Papers Consulted
| Paper | Topic | Key relevance | Dataset/method supported |
|-------|-------|---------------|--------------------------|
| `RP-001` | Literature Review | Baseline understanding of SAR/AIS pipeline | OpenDrift & SAR integration |
| `RP-003` | Hydrodynamic backtracking | Validating backward drift physics | Monte Carlo backtracking methodology |
| `RP-004` | Feasibility & Datasets | Identifying practical datasets | Sentinel-1 feasibility & MetOcean constraints |
| `RP-007` | Uncertainty-aware attribution | Scoring candidate vessels robustly | Deterministic attribution scoring logic |

## 9. Dataset Compatibility Matrix
| Dataset | Spatial | Temporal | Authority | Access | Reproducibility | Pipeline | Storage |
|---------|---------|----------|-----------|--------|-----------------|----------|---------|
| MarineCadastre | 5 | 5 | 5 | 5 | 5 | 4 | 2 (Large) |
| DMA AIS | 5 | 5 | 5 | 5 | 5 | 4 | 2 (Large) |
| ERA5 (Wind) | 5 | 5 | 5 | 4 | 5 | 5 | 3 |
| CMEMS (Current) | 5 | 5 | 5 | 4 | 5 | 5 | 3 |
| Zenodo SAR | 5 | 5 | 5 | 5 | 5 | 5 | 4 |

## 10. Recommended Baseline Dataset
- **SAR**: Zenodo (M4D Oil Spill Dataset)
- **AIS**: SYNTHETIC_DEMO (if real AIS is unavailable for the precise scenario bounds) or MarineCadastre/DMA if bounds overlap.
- **Metocean**: ERA5 (Wind) and CMEMS Global Ocean Physics Reanalysis (Current).

## 11. Recommended Secondary/Validation Datasets
- **SAR**: Copernicus Data Space Ecosystem (Sentinel-1)
- **AIS**: Danish Maritime Authority (DMA) Historical AIS (for testing real-world data loads and anomalies).

## 12. Real AIS Availability
REAL_AIS_AVAILABLE (via MarineCadastre and DMA for specific regions, but coverage depends entirely on the Golden Scenario's geographic location. If the Golden Scenario falls outside these regions, REAL_AIS_RESTRICTED applies for commercial datasets).

## 13. Synthetic AIS Requirements
A scientifically useful generator for `SYNTHETIC_DEMO` must include:
- Realistic SOG (Speed Over Ground) and COG (Course Over Ground) changes based on vessel class.
- Variable timestamp frequency and irregular sampling to simulate real-world AIS gaps.
- Complex navigation behavior (shipping lanes, near-miss trajectories, crossing trajectories).
- Missing messages, stationary vessels, and distractor vessels outside the origin uncertainty region to test attribution filtering strictness.

## 14. Licensing Risks
- Using commercial AIS datasets (e.g., Spire, exactEarth) introduces severe licensing and paywall risks, compromising the open reproducibility requirement of SIH.
- Relying exclusively on open government data (MarineCadastre/DMA) completely mitigates licensing risks but restricts the geographic locations for REAL_AIS scenarios.

## 15. Reproducibility Risks
- Dynamic APIs (where historical data might be purged or altered) risk breaking reproducibility. Static NetCDF/CSV snapshots must be stored or explicitly version-pinned.
- Random seeds in OpenDrift Monte Carlo simulations must be fixed and logged in the Evidence JSON to ensure the exact origin probability cloud can be independently reproduced.

## 16. Scientific Risks
- Resolution mismatch: Using coarse ocean currents (e.g., 1/12 degree) for highly localized coastal oil spills can introduce severe trajectory errors.
- Assuming an AIS gap equates to guilt (dark fleet) without ruling out receiver coverage gaps or interference.

## 17. Storage/Infrastructure Considerations
- Historical AIS CSVs and NetCDF MetOcean files are massive (gigabytes per day).
- Local storage bounds must be enforced.
- The pipeline should subset/crop NetCDF and AIS data geographically *before* persisting it into the deterministic engine.

## 18. Data Acquisition Plan
1. Download fixed boundaries of ERA5 and CMEMS NetCDF files matching the Golden Scenario constraints.
2. Download corresponding SAR masks from Zenodo.
3. Attempt to fetch REAL_AIS for the region. If unavailable/restricted, execute the `SYNTHETIC_DEMO` generator with mathematically rigorous parameters.

## 19. Validation Plan
- Feed the frozen datasets into the pipeline.
- Verify that OpenDrift produces an origin cloud that spatially intersects the ground-truth vessel.
- Validate that the attribution engine ranks the true culprit highest without peeking at the `ground_truth.json`.

## 20. Recommendations for B2+
- Proceed to B2 (MetOcean) with clear validation for NetCDF parsing.
- Ensure the B2 implementations for ERA5 and CMEMS gracefully handle missing variables or NaNs without silently corrupting drift parameters.
