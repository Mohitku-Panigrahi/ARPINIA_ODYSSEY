import os
from pathlib import Path
import json

def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Created: {path}")

fixtures = {
    "01_valid_golden_scenario.json": {
        "_meta": {"type": "TEST_DATA", "description": "Valid Golden Scenario inputs mock"},
        "status": "valid"
    },
    "02_invalid_sar.json": {
        "_meta": {"type": "TEST_DATA", "description": "SAR payload with missing geometry"},
        "geometry": None
    },
    "03_missing_metocean.json": {
        "_meta": {"type": "TEST_DATA", "description": "Valid SAR but ERA5 API returns 404"},
        "wind": None
    },
    "04_empty_ais_candidate_set.json": {
        "_meta": {"type": "TEST_DATA", "description": "AIS query returns 0 vessels"},
        "candidates": []
    },
    "05_ais_gap_scenario.json": {
        "_meta": {"type": "SYNTHETIC_DATA", "description": "Vessel with 6-hour AIS gap at origin time"},
        "candidates": [{"mmsi": "999999999", "ais_gap_hours": 6.5}]
    },
    "06_opendrift_failure.json": {
        "_meta": {"type": "TEST_DATA", "description": "OpenDrift worker timeout"},
        "drift_status": "TIMEOUT"
    },
    "07_llm_unavailable.json": {
        "_meta": {"type": "TEST_DATA", "description": "LLM API returns 503 or times out"},
        "llm_status": 503
    }
}

for filename, data in fixtures.items():
    write_json(f"tests/fixtures/{filename}", data)

# Also create README to define them
p = Path("tests/fixtures/README.md")
with open(p, "w", encoding="utf-8") as f:
    f.write("""# Test Fixtures

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
""")
print("Created: tests/fixtures/README.md")
