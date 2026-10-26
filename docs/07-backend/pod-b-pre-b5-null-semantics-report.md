# ARPINIA ODYSSEY — POD B
## PRE-B5 DATA QUALITY, NULL-SEMANTICS & AIS HANDOFF HARDENING

This report documents the rigorous null-handling semantics added to the B4 Spatio-Temporal AIS Candidate Correlation Engine to explicitly support Phase B5 (Explainable Multi-Factor Vessel Attribution).

### NULL STATUS ENUM
Every nullable analytical value uses explicit states rather than relying on silent \None\s. The valid states are:
- \AVAILABLE\
- \MISSING_SOURCE_DATA\
- \NOT_APPLICABLE\
- \NOT_COMPUTABLE\
- \UNAVAILABLE\
- \INVALID_INPUT\

### REQUIRED FIELDS
The pipeline correctly enforces that missing \stable vessel identifier\, \	imestamp_utc\, \latitude\, or \longitude\ results in observation rejection.

### OPTIONAL FIELDS
Missing source metadata (IMO, vessel_name, SOG, COG, heading) correctly remains missing (represented as \None\ + \MISSING_SOURCE_DATA\) and is never invented or zero-filled.

### AIS SENTINEL NORMALIZATION
Provider-defined unavailable sentinels are explicitly checked and normalized to \None\ + quality flags:
- \Heading == 511.0\ -> \None\ (\HEADING_SENTINEL_NORMALIZED\)
- \COG == 3600.0\ or \360.0\ -> \None\ (\COG_SENTINEL_NORMALIZED\)
- \SOG == 102.3\ -> \None\ (\SOG_SENTINEL_NORMALIZED\)

### ANALYTICAL NULL STATES
Analytical results are now wrapped in \AnalyticalResult[T]\, requiring a distinct \status\ and \eason\.
- \closest_approach_time\ when vessel never enters time window: \status: NOT_APPLICABLE\, \eason: NO_TEMPORALLY_OVERLAPPING_SEGMENT\.
- Gap reachability is distinguished by \KINEMATICALLY_PLAUSIBLE_UNOBSERVED_TRANSIT\ vs \KINEMATICALLY_IMPLAUSIBLE_TRANSIT\.

### BOOLEAN UNKNOWN HANDLING
Booleans strictly distinguish between \False\ (tested negative) and \UNAVAILABLE\ (could not be tested due to missing data/time slices).

### FEATURE AVAILABILITY MASK
Every vessel output exposes a \eatures_available\ block that summarizes evidence presence without computing attribution scores, ensuring B5 receives raw unbiased capabilities.

### STRICT JSON SERIALIZATION
B4 output models strictly enforce serialization that guarantees no \NaN\, \Infinity\, or \-Infinity\ objects are written to the Evidence JSON.

### DATASET AUDIT RESULTS
- **NOAA REAL AIS**: PASS
- **SYNTHETIC GOLDEN**: PASS
- **B1-B4 REGRESSIONS**: NONE
