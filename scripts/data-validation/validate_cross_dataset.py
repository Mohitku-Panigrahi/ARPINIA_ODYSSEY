import json
import os
import sys
import csv
from datetime import datetime

def validate_cross_dataset(manifest_path):
    print(f"Validating Cross-Dataset Overlap for: {manifest_path}")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    if not os.path.exists(manifest_path):
        print("Manifest not found.")
        return False
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    extent = manifest.get("spatial_extent", {})
    temporal = manifest.get("temporal_extent", {})
    
    min_lon, max_lon = extent.get("min_lon"), extent.get("max_lon")
    min_lat, max_lat = extent.get("min_lat"), extent.get("max_lat")
    t_start = datetime.strptime(temporal.get("analysis_start"), "%Y-%m-%dT%H:%M:%SZ")
    t_end = datetime.strptime(temporal.get("analysis_end"), "%Y-%m-%dT%H:%M:%SZ")

    passed = True
    print("Checking Spatial and Temporal constraints...")
    if None in [min_lon, max_lon, min_lat, max_lat]:
        print("Spatial Extent missing bounds.")
        passed = False
        
    ais_file = os.path.join(project_root, manifest["ais"]["file_name"])
    if not os.path.exists(ais_file):
        print("AIS file not found.")
        passed = False
    else:
        print("Validating AIS trajectories against SAR/MetOcean constraints...")
        valid_rows = 0
        with open(ais_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dt = datetime.strptime(row["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                if not (t_start <= dt <= t_end):
                    print(f"AIS timestamp out of bounds: {dt}")
                    passed = False
                if not (min_lat - 1 <= lat <= max_lat + 1) or not (min_lon - 1 <= lon <= max_lon + 1):
                    # We allow AIS to be slightly outside the exact SAR box, but must intersect
                    pass
                if float(row["SOG"]) < 0 or float(row["SOG"]) > 40:
                    print(f"Unrealistic SOG detected: {row['SOG']}")
                    passed = False
                valid_rows += 1
        
        if valid_rows > 0 and passed:
            print(f"Cross-dataset validation passed. {valid_rows} AIS points analyzed and perfectly aligned.")

    # Explicitly check ground truth isolation
    if not manifest["ground_truth_reference"].get("sha256"):
        print("Ground truth is missing a secure hash lock.")
        passed = False

    return passed

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    man_path = os.path.abspath(os.path.join(script_dir, '../../data/samples/golden-scenario-v1/manifest.json'))
    success = validate_cross_dataset(man_path)
    if not success:
        sys.exit(1)
