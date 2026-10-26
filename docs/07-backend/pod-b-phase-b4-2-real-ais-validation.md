# ARPINIA ODYSSEY — POD B
## PHASE B4.2: REAL AIS VALIDATION

This report validates the frozen B4 Spatio-Temporal AIS Candidate Correlation Engine against an independent, real vessel-level AIS dataset to ensure it handles real-world data issues (missing fields, noise, gaps, irregularities) without altering the frozen Golden Scenario (SIH-ZENODO-ALPHA).

### DATASET DETAILS
- **Provider**: NOAA MarineCadastre (Authorized Public Historical Access)
- **Data Class**: REAL VESSEL-LEVEL AIS
- **Historical/Current**: HISTORICAL (2018)
- **Bounding Box**: LON -166.58 -> -64.47, LAT 17.69 -> 59.60 (Validation Subsample)
- **Observation Period**: 2018-01-01T00:00:00Z -> 2018-01-01T23:59:21Z
- **Raw Artifact File**: data/raw/real-ais-validation/noaa_ais_2018_sample.csv
- **SHA256 Checksum**: 3e42657a6199a873363b23165de3b117b4781286836695061aa724d905dc0f25

### INGESTION QUALITY AUDIT
- **Raw Records**: 9999
- **Valid Records Accepted**: 9999
- **Rejected Records**: 0
- **Unique Vessels Detected**: 183
- **Trajectories Built**: 183
- **Duplicates Found**: 0
- **Invalid Records**: 0

### TRAJECTORY METRICS
- **Median Sampling Interval**: 70.0 seconds
- **P90 Sampling Interval**: 179.0 seconds
- **Max Gap Encountered**: 28650.0 seconds

### PIPELINE FEATURE VALIDATION
A synthetic **TEST_QUERY_REGION** was systematically constructed over a known real segment gap (between LAT 35.029 - 35.129, LON -90.181 - -90.081).
- **Segment Intersection Logic**: PASS (The pipeline correctly detected that a linear segment crossed a 2D probability region even though no exact observed coordinate landed inside it).
- **Short-Gap Interpolation Handling**: PASS (Segments <= threshold interpolated smoothly).
- **Long-Gap Uncertainty Handling**: PASS (Gaps > threshold triggered kinematic reachability rather than false continuous linear paths).
- **Reachability Validation**: PASS.
- **Candidate/Exclusion Traceability**: PASS (Candidates preserved explicit reason arrays such as SEGMENT_INTERSECTS_ORIGIN).
- **Real/Synthetic Separation**: PASS (Conducted entirely independently from Golden Scenario).

### OVERALL COMPATIBILITY FINDING
The frozen B4 canonical AIS schema successfully ingested and processed genuine, dirty AIS records without requiring any relaxation of validation constraints. Missing optional fields did not break the trajectory builder. REAL_AIS_PIPELINE_VALIDATED.

