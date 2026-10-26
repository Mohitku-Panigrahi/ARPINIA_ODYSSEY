import json
import os
import sys

def validate_physical_files(manifest_path):
    print(f"Validating Physical Files for: {manifest_path}")
    if not os.path.exists(manifest_path):
        print("Manifest not found.")
        return False
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    if manifest.get("validation_status") != "READY_FOR_FREEZE_PHASE_1":
        print("Manifest marked as NOT_READY.")
        
    # Phase 1 only validates SAR and Metocean
    required = ["sar", "metocean"]
    passed = True
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Check SAR
    sar = manifest.get("sar", {})
    if not sar.get("sha256"):
        print("SAR: Missing SHA-256 checksum.")
        passed = False
    elif not os.path.exists(os.path.join(project_root, sar.get("file_name", ""))):
         print("SAR: File physically missing.")
         passed = False
    else:
        print("SAR: Checksum and physical file present.")

    # Check Metocean
    met = manifest.get("metocean", {})
    if not met.get("era5_sha256") or not met.get("copernicus_sha256"):
        print("METOCEAN: Missing SHA-256 checksums.")
        passed = False
    else:
        for f in met.get("era5_files", []) + met.get("copernicus_files", []):
            if not os.path.exists(os.path.join(project_root, f)):
                print(f"METOCEAN: File physically missing -> {f}")
                passed = False
        if passed:
             print("METOCEAN: Checksums and physical files present.")
            
    return passed

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    man_path = os.path.abspath(os.path.join(script_dir, '../../data/samples/golden-scenario-v1/manifest.json'))
    success = validate_physical_files(man_path)
    if not success:
        sys.exit(1)
