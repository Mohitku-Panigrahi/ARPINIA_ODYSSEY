# POD B PHASE B4 FREEZE AMENDMENT 001

## 1. Original Defect
During the B1-B4 Foundation Release Audit, an end-to-end benchmark revealed a latent TypeError: 'Point' object is not subscriptable in packages/ais/correlation.py. The closest_approach logic incorrectly assumed the probability grid centroid was a dictionary (centroid['lat']), but ProbabilityFieldGenerator returns a strongly-typed Point object. 

## 2. Affected Code
packages/ais/correlation.py, specifically the correlate method inside the closest approach distance calculation block.

## 3. Scientific Impact & Observable Behavior
This defect caused a fatal crash whenever a vessel's trajectory temporally overlapped with the B3 probability grid and closest approach was calculated. This prevented candidate generation for any matching vessels. The fix restores the intended frozen scientific behavior (calculating Haversine distance to the centroid) by correcting the property access. It does not alter the mathematical logic, thresholds, or correlation semantics.

## 4. Regression Testing
A targeted unit test 	est_b4_freeze_amendment.py::test_closest_approach_centroid_handling was added to verify Point attribute access. The test suite passes (36/36).

## 5. Golden & NOAA Scenario Comparison
Because the defect was a fatal runtime crash, previous full end-to-end runs with real ProbabilityFieldGenerator output (as opposed to mocked dicts in isolated unit tests) would fail. With the amendment:
- **Golden Scenario**: 1000 particles, 24 timesteps, 5 trajectories -> 1 candidate successfully generated.
- **NOAA 9999 Real AIS**: 183 trajectories -> Candidates generated correctly without TypeErrors.
The result is categorized as EXPECTED_BUG_FIX_DIFFERENCE since it enables the pipeline to complete successfully.

## 6. Freeze Reapproval
The original B4 freeze is superseded by this amendment to ensure the code is executable. The B4 algorithm remains scientifically identical to the frozen design.
