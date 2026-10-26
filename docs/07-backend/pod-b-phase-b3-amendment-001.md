# ARPINIA ODYSSEY
## B3 FREEZE AMENDMENT 001 — CMEMS/OPENDRIFT READER REPAIR

### ROOT CAUSE
The B6 real-Golden Validation revealed a functional defect in the frozen B3 engine. The underlying OpenDrift generic CF reader (`reader_netCDF_CF_generic`) successfully recognized some variables but lacked automated mapping for the CMEMS non-standard variable names (`uo`, `vo`) to standard OpenDrift environmental vectors (`x_sea_water_velocity`, `y_sea_water_velocity`). Furthermore, the generic reader does not expose targeted dimension slicing (e.g., retrieving the exact 0.494025m surface depth layer validated during Phase B2) without explicit configuration. Consequently, the simulation quietly deactivated elements entirely due to missing required physical forcing vectors, producing 0 valid physical time slices, masking itself behind weak assertions in the test suite (`assert len(time_slices) >= 0`).

### SCOPE OF REPAIR
- **B3 CMEMS/OpenDrift reader integration:** Yes. Replaced the direct file reference with an isolated, locally-executed `xarray` adapter preserving `0.494025m` depth.
- **B3 Error Propagation:** Yes. Implemented strict `REQUIRED_FORCING_UNAVAILABLE` exception raising if `time_slices` yields fewer time-steps than explicitly requested by `duration / time_step`.
- **B3 Tests:** Yes. Rewrote assertions for `test_out_of_bounds_missing_forcing` to expect `ValueError(REQUIRED_FORCING_UNAVAILABLE)` and validated length and active particle count assertions in reproducibility logic.
- **B1-B2 & B4-B6:** No structural changes outside `packages/reconstruction/engine.py` and `tests/unit/test_reconstruction_engine.py`.

### IMPLEMENTATION DETAILS
**Adapter Approach:** Chosen **Option A** (Offline / Local `xarray.Dataset` translation). 
- Avoids Copernicus network dependencies or remote API calls.
- Performs exact dimensional isolation: `ds.sel(depth=0.494025, method='nearest')`.
- Performs variable rename: `uo -> x_sea_water_velocity`, `vo -> y_sea_water_velocity`.
- Hardcodes standard names and units in `xarray` attributes before passing the in-memory construct directly to `reader_netCDF_CF_generic.Reader(ds)`.

### VALIDATION
- **CURRENT COMPONENT MAPPING:** PASS (`uo` mapped to `x_sea_water_velocity`, `vo` to `y_sea_water_velocity`).
- **COMPONENT DIRECTION:** PASS.
- **DEPTH SELECTION:** PASS (Nearest mapped to 0.494025m).
- **TEMPORAL COVERAGE:** PASS (Golden dataset slices bound appropriately, missing coverage rightfully throws `REQUIRED_FORCING_UNAVAILABLE`).
- **NO ZERO-CURRENT FALLBACK:** PASS (Fallback strictly prevented).
- **REAL B3 EXECUTION:** PASS.
- **REGRESSION RESULT:** PASS (50/50 Tests Passed across B1-B6 pipeline).

### RESOLUTION
B3 freeze REOPEN is now CLOSED. B3 is successfully re-certified as `FROZEN_AMENDED`.
B6 Real-Golden Validation is now UNBLOCKED.
