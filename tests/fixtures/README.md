# Test Fixtures

All data in this directory is strictly TEST DATA or SYNTHETIC DATA.
Never represent these files as real evidence in the frontend.

## Fixture Index
1. `01_valid_golden_scenario.json` - Valid inputs mock.
2. `02_invalid_sar.json` - SAR payload with missing geometry.
3. `03_missing_metocean.json` - Valid SAR but missing ERA5/CMEMS.
4. `04_empty_ais_candidate_set.json` - Zero AIS candidates found.
5. `05_ais_gap_scenario.json` - Synthetic vessel with deliberate AIS dropout.
6. `06_opendrift_failure.json` - Worker timeout mock.
7. `07_llm_unavailable.json` - LLM 503 fallback mock.

**Note on Ground Truth:** `ground_truth.json` is located safely in `data/samples/golden-scenario-v1/` and is NEVER available to inference tests, only to scoring tests.
