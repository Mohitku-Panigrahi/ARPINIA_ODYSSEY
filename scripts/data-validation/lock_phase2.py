import os
import hashlib
import json
import csv
from datetime import datetime, timedelta

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

# 1. Ensure Directories
os.makedirs("data/raw/golden-scenario-v1/ais", exist_ok=True)
os.makedirs("data/samples/golden-scenario-v1", exist_ok=True)

# 2. Generate Independent Synthetic AIS
ais_file = "data/raw/golden-scenario-v1/ais/synthetic_ais_tracks.csv"
true_mmsi = "123456789"
distractor_mmsis = ["223456780", "323456781", "423456782", "523456783"]

with open(ais_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["MMSI", "timestamp", "latitude", "longitude", "SOG", "COG", "heading", "vessel_type", "length", "width"])
    
    start_time = datetime(2018, 8, 13, 15, 44, 0)
    
    # Generate True Culprit (Independently intersecting the region)
    for i in range(48):
        dt = start_time + timedelta(hours=i)
        lat = 33.2 + (i * 0.01)
        lon = 33.1 + (i * 0.012)
        writer.writerow([true_mmsi, dt.strftime("%Y-%m-%dT%H:%M:%SZ"), f"{lat:.4f}", f"{lon:.4f}", "12.5", "45.0", "45", "Tanker", "250", "40"])
        
    # Generate Distractors
    for mmsi in distractor_mmsis:
        for i in range(0, 48, 2):
            dt = start_time + timedelta(hours=i)
            lat = 33.7 - (i * 0.008)
            lon = 33.8 - (i * 0.015)
            writer.writerow([mmsi, dt.strftime("%Y-%m-%dT%H:%M:%SZ"), f"{lat:.4f}", f"{lon:.4f}", "14.0", "220.0", "220", "Cargo", "200", "32"])

ais_hash = get_sha256(ais_file)

# 3. Generate Isolated Ground Truth
gt_file = "data/samples/golden-scenario-v1/ground_truth.json"
gt_data = {
    "scenario_id": "SIH-ZENODO-ALPHA",
    "true_source_mmsi": true_mmsi,
    "spill_origin": {"lat": 33.4400, "lon": 33.3880},
    "spill_time": "2018-08-14T15:44:00Z",
    "validation_notes": "Ground truth is isolated from production attribution engine."
}
with open(gt_file, "w") as f:
    json.dump(gt_data, f, indent=2)
gt_hash = get_sha256(gt_file)

# 4. Update Manifest
manifest_path = "data/samples/golden-scenario-v1/manifest.json"
with open(manifest_path, 'r') as f:
    manifest = json.load(f)

manifest["status"] = "ALL_DATASETS_LOCKED"
manifest["validation_status"] = "READY_FOR_CROSS_VALIDATION"
manifest["ais"]["file_name"] = ais_file
manifest["ais"]["sha256"] = ais_hash
manifest["ground_truth_reference"]["sha256"] = gt_hash

with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"✅ Phase 2 Lock Complete. AIS Hash: {ais_hash}, GT Hash: {gt_hash}")
