# ARPINIA ODYSSEY — POD B
## PHASE B4.1: REAL AIS ACQUISITION & VALIDATION

### REAL DATA ACQUIRED
No real vessel-level timestamped positions were acquired. Authentication with Global Fishing Watch API succeeded, but the requested dataset (public-global-presence:latest) returned AGGREGATED_PRESENCE (gridded spatial bins via 4Wings API).

### REAL DATA VALIDATED
Blocked by lack of vessel-level tracks. Frozen B4 correlation could not be executed on real data.

### REAL DATA LIMITATIONS
- Real historical AIS is difficult to acquire via free REST APIs.
- The Golden Scenario requires high-density track data to effectively correlate vessel trajectories against B3 spatio-temporal origin fields.

### PROVIDER LIMITATIONS

#### Global Fishing Watch
- **Coverage**: Global.
- **Limitation**: The official REST API returns gridded temporal presence (4wings:v1) rather than raw AIS points for bounding box queries. Raw points require vessel-specific queries (/v3/vessels/{vessel_id}/tracks) or BigQuery access which falls outside the current credential scope.

#### MarineTraffic
- **historical 2018 coverage**: Extensive global archive since Jan 2015.
- **Eastern Mediterranean coverage**: Excellent.
- **vessel-level position availability**: Yes.
- **access method**: Historical AIS API or offline data export.
- **price/subscription requirement**: Paid commercial access required.
- **suitability**: Highly suitable for accurate segment intersection and closest approach analysis.

#### VesselFinder
- **historical 2018 coverage**: Extensive global archive since 2009.
- **Eastern Mediterranean coverage**: Excellent.
- **vessel-level position availability**: Yes.
- **access method**: Historical Data API or offline data dumps.
- **price/subscription requirement**: Paid commercial access required.
- **suitability**: Highly suitable.
