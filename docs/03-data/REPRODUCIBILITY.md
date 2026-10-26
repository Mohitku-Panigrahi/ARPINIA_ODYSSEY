# ARPINIA ODYSSEY — REPRODUCIBILITY POLICY

## 1. Data Storage Policy
- **NO MASSIVE DATA IN GIT:** Raw SAR scenes (1GB+), NetCDF grids (500MB+), and massive AIS CSVs MUST NOT be committed to the repository.
- **Data Manifests:** The repository tracks data via `manifest.json`, which contains the exact download URLs, parameters, and SHA-256 checksums.

## 2. Reproducing the Environment
- Another developer must be able to run `python scripts/download_assets.py` (to be implemented) which reads the manifest and pulls the exact files.
- For `SYNTHETIC_DEMO` assets, the exact CSV file is mathematically generated using `lock_phase2.py` and its hashes are tracked to prevent arbitrary drift.

## 3. Data Leakage Prevention (Strict Isolation)
- **Isolated Ground Truth:** `ground_truth.json` is strictly for `tests/` and evaluation frameworks.
- **The Blind Fold Rule:** The `services/ai-engine/` and `services/worker/` modules are architecturally blinded to ground truth. The AIS generator executes *independently* of the backward drift engine.

## 4. Checksums
- Every physical asset used in the Golden Scenario (SAR, MetOcean, Synthetic AIS) has a mathematically verified SHA-256 checksum recorded in the manifest.
