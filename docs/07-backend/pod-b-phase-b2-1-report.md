# POD B — PHASE B2.1 REPORT

## 1. Objective
Prove that the existing B2 MetOcean implementation works correctly against real authoritative environmental data (ECMWF ERA5 and CMEMS Global Ocean Physics Reanalysis) covering the frozen Golden Scenario: SIH-ZENODO-ALPHA (2018-08-13T15:44:00Z to 2018-08-15T15:44:00Z).

## 2. ERA5 Physical Artifact Validation
- **Product:** `reanalysis-era5-single-levels`
- **Variables:** `u10`, `v10`
- **Units:** `m s**-1`
- **Spatial Coverage:** Lat `[32.5, 34.5]`, Lon `[32.5, 34.5]`
- **Temporal Coverage:** `2018-08-13T00:00:00Z` to `2018-08-16T23:00:00Z`
- **File Size:** `73489 bytes`
- **SHA256:** `fc2d10e33b047872a3229ee52aaaa388cde746bc0b393aa018251a68456e1e7f`
- **Missing/Fill Value:** `_FillValue=nan`
- **B2 Reader Compatibility:** `PASS` (A narrowly justified patch was applied to `packages/metocean/era5.py` to support `valid_time` as equivalent to `time`).
- **Interpolation:** `PASS` (Temporal and spatial interpolation succeed across the grid).

## 3. CMEMS Physical Artifact Validation
- **Product:** `cmems_mod_glo_phy_my_0.083deg_P1D-m` (Global Ocean Physics Reanalysis)
- **Variables:** `uo`, `vo`, `depth`, `time`, `latitude`, `longitude`
- **Selected Depth:** `0.49402499198913574` meters (Shallowest available scientifically appropriate depth)
- **Units:** `m s-1`
- **Spatial Coverage:** Lat `[32.41666793823242, 34.5]`, Lon `[32.33333206176758, 34.58333206176758]`
- **Temporal Coverage:** `2018-08-13` to `2018-08-16` (Daily resolution, 12:00:00 UTC)
- **File Size:** `39514 bytes`
- **SHA256:** `f0c2a627f4f7cd7290df1ca1fe978cf94b774419fb41bb0ec3dd77aaedec16df`
- **Missing/Fill Value:** `_FillValue=-32767`
- **B2 Reader Compatibility:** `PASS` (Out-of-the-box compatibility without modifications).
- **Interpolation:** `PASS` (Temporal interpolation handles the daily resolution accurately across the 15:44 UTC timestamps without extrapolation).

## 4. Provenance
- ERA5: Acquired via `cdsapi` from Copernicus Climate Data Store. 
- CMEMS: Acquired via `copernicusmarine` from Copernicus Marine Service.
- Both subsets bracket the Golden Scenario spatial and temporal bounds completely, with a modest buffer reserved for B3 trajectory drift.

## 5. Security
- Complied with security policy: Did NOT scrape restricted services, bypass authentication, use unofficial mirrors, or hardcode/log private access tokens. Valid credentials were used via configuration file.

## 6. Status
- ERA5 Golden: **COMPATIBLE**
- CMEMS Golden: **COMPATIBLE**
- **B2_1_COMPLETE**
