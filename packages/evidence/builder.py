import json
import hashlib
from datetime import datetime, timezone

def get_canonical_json(data: dict) -> bytes:
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
        allow_nan=False
    ).encode('utf-8')

class EvidenceBuilder:
    def __init__(self, schema_version="1.1.0", scenario_id="SIH-ZENODO-ALPHA", dataset_mode="SYNTHETIC_DEMO"):
        self.evidence = {
            "schema_version": schema_version,
            "evidence_schema_version": schema_version,
            "case_id": "CASE-SIH-001",
            "investigation_id": "INV-SIH-001",
            "scenario_id": scenario_id,
            "dataset_mode": dataset_mode,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": {
                "pipeline_status": "EVIDENCE_READY",
                "attribution_status": "SUFFICIENT",
                "overall_confidence": 0.88
            },
            "incident": {
                "detected_at": "2018-08-15T15:44:00Z",
                "location": {"latitude": 33.44, "longitude": 33.388},
                "geometry": {}
            },
            "sar": {
                "source": "Sentinel-1",
                "scene_id": "S1A_IW_GRDH_1SDV_20180815T154400",
                "acquisition_timestamp": "2018-08-15T15:44:00Z",
                "processing_version": "1.0",
                "spill_geometry": {},
                "area_km2": 15.2,
                "segmentation": {},
                "look_alike_assessment": {}
            },
            "environment": {},
            "drift": {},
            "ais": {},
            "candidates": [],
            "decision_support": {},
            "limitations": ["synthetic AIS used for Golden demonstration", "B8 forward consistency not independent attribution proof"],
            "provenance": {
                "input_hashes": [
                    "10c2c749b349fd4b35ff6c859385b9fa1f0e853c4a349f107886bdb2514d54c3",
                    "fc81fb429db9766bb7e82b3d87db1c2b53c7c2be6d2a4175b9bf92305537554e",
                    "fc2d10e33b047872a3229ee52aaaa388cde746bc0b393aa018251a68456e1e7f",
                    "f0c2a627f4f7cd7290df1ca1fe978cf94b774419fb41bb0ec3dd77aaedec16df"
                ],
                "source_datasets": [],
                "algorithm_versions": ["B1_1.0", "B2_1.0", "B3_1.0", "B4_1.0", "B5_1.0", "B6_1.0.0", "B7_1.0.0", "B8_1.0.0", "B9_1.0.0"],
                "model_versions": [],
                "configuration_hash": "dummy_config",
                "global_b6_ensemble_metadata": {
                    "runs_attempted": 25,
                    "convergence": True,
                    "convergence_run": 25,
                    "convergence_patience": 2,
                    "uncertainty_semantics": "MC",
                    "release_time_distribution": "UNIFORM"
                }
            }
        }
        
    def add_candidate(self, cand_dict):
        self.evidence["candidates"].append(cand_dict)
        
    def write_canonical(self, filepath: str):
        payload = get_canonical_json(self.evidence)
        with open(filepath, 'wb') as f:
            f.write(payload)
        sha256 = hashlib.sha256(payload).hexdigest()
        with open(filepath.replace('.json', '.sha256'), 'w') as f:
            f.write(sha256)
        return sha256
