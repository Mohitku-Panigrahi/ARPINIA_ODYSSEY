# ARPINIA ODYSSEY — GOLDEN SCENARIO V1 (SIH-ZENODO-ALPHA)

## 1. Scenario Overview
**Type:** Software Demonstration & Validation Case
**STATUS:** `READY_FOR_FREEZE 🔒`
Golden Scenario V1 is completely locked. It utilizes an authoritative Zenodo SAR scene paired with mathematically constructed independent `SYNTHETIC_DEMO` AIS data and real historical MetOcean forcing.

## 2. Spatial Extent (Locked)
Extracted directly from the verified SAR asset.
- **CRS:** EPSG:4326
- **Min Lon:** 33.1
- **Max Lon:** 33.8
- **Min Lat:** 33.2
- **Max Lat:** 33.7

## 3. Temporal Extent (Locked)
- **Scene Acquisition Timestamp:** 2018-08-15T15:44:00Z
- **Analysis Start (Hindcast Window):** 2018-08-13T15:44:00Z
- **Analysis End:** 2018-08-15T15:44:00Z
- **Timezone:** UTC

## 4. SAR Asset (Locked)
- **Source:** Zenodo (M4D Oil Spill Dataset)
- **Record:** https://zenodo.org/records/10848057
- **File:** `S1A_IW_GRDH_1SDV_20180815T154400.tif`
- **SHA-256:** `10c2c749b349fd4b35ff6c859385b9fa1f0e853c4a349f107886bdb2514d54c3`
- **Ground Truth:** Associated Zenodo segmentation mask.

## 5. MetOcean Assets (Locked)
- **Wind:** ECMWF ERA5 (Hourly, 10m u/v).
  - File: `ERA5_wind_20180813_20180815.nc`
  - SHA-256: `aeab34b0812a9c6f4bed17596bd89c34f8487b39e3253c7557cc8c9d34c61c10`
- **Currents:** Copernicus Marine Service (Global/Regional Physics Reanalysis).
  - File: `CMEMS_currents_20180813_20180815.nc`
  - SHA-256: `9d39e5963f6d0586d173e66b216c53a8ee15a5f0d12a5ceddcb27f681227f257`

## 6. AIS Asset (Locked)
- **Source:** ARPINIA Synthetic Generator
- **Mode:** `SYNTHETIC_DEMO_AIS`
- **Integrity Rule:** Independent generation prior to OpenDrift simulation.
- **File:** `synthetic_ais_tracks.csv`
- **SHA-256:** `fc81fb429db9766bb7e82b3d87db1c2b53c7c2be6d2a4175b9bf92305537554e`

## 7. Anti-Leakage Ground Truth Strategy
- `data/samples/golden-scenario-v1/ground_truth.json` contains the true synthetic MMSI (`123456789`) and original spill coordinates.
- **CRITICAL RULE:** The attribution engine MUST NOT read this file. It is exclusively for the `validate_scenario.py` and Pytest evaluation frameworks to score the engine's final Evidence JSON.
