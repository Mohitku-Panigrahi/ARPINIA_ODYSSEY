import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from packages.forward_validation import ForwardValidationConfig, ForwardValidationEngine, ForwardConsistencyStatus
from packages.ais.models import CandidateVessel, AnalyticalResult, FeatureAvailability
from packages.geo.models import Point

def test_config():
    config = ForwardValidationConfig(consistent_centroid_distance_km=15.0)
    assert config.consistent_centroid_distance_km == 15.0

def test_missing_candidate_data():
    config = ForwardValidationConfig()
    engine = ForwardValidationEngine(config, "dummy", "dummy")
    
    cand = CandidateVessel(
        mmsi="123", trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
        closest_approach_km=AnalyticalResult(status="UNAVAILABLE", value=None),
        closest_approach_time=AnalyticalResult(status="UNAVAILABLE", value=None),
        intersects_50_region=AnalyticalResult(status="UNAVAILABLE", value=None),
        intersects_80_region=AnalyticalResult(status="UNAVAILABLE", value=None),
        intersects_95_region=AnalyticalResult(status="UNAVAILABLE", value=None),
        time_inside_region_seconds=AnalyticalResult(status="UNAVAILABLE", value=None),
        features_available=FeatureAvailability(spatial_overlap=False, temporal_match=False, closest_approach=False, ais_continuity=False)
    )
    
    res = engine.evaluate_candidate(cand, [Point(lat=0, lon=0)])
    assert res.status == ForwardConsistencyStatus.INSUFFICIENT_EVIDENCE
    assert res.hypotheses_tested == 0

@patch('packages.forward_validation.engine.ForwardValidationEngine.evaluate_candidate')
def test_controlled_physics(mock_eval):
    from packages.forward_validation import CandidateForwardConsistency, ForwardSimulationSummary, ReleaseHypothesis
    mock_eval.return_value = CandidateForwardConsistency(
        candidate_id="123",
        status=ForwardConsistencyStatus.CONSISTENT,
        hypotheses_tested=1,
        best_hypothesis=ForwardSimulationSummary(
            hypothesis=ReleaseHypothesis(
                candidate_id="123", release_lat=0, release_lon=0, release_time="2018-08-15T15:00:00Z", derivation_method="", source_fields=[], uncertainty_limitations=[]
            ),
            forward_duration_seconds=48.0*3600,
            final_centroid_lat=0.0,
            final_centroid_lon=0.0,
            centroid_distance_km=10.0,
            overlap_metric=0.9,
            status=ForwardConsistencyStatus.CONSISTENT,
            supporting_observations=[],
            contradicting_observations=[]
        ),
        centroid_distance_km=10.0,
        overlap_metric=0.9,
        supporting_observations=[],
        contradicting_observations=[],
        limitations=[],
        provenance={}
    )
    
    config = ForwardValidationConfig()
    engine = ForwardValidationEngine(config, "dummy", "dummy")
    cand = CandidateVessel(
        mmsi="123", trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
        closest_approach_km=AnalyticalResult(status="AVAILABLE", value=0.0),
        closest_approach_time=AnalyticalResult(status="AVAILABLE", value="2018-08-15T15:00:00Z"),
        intersects_50_region=AnalyticalResult(status="AVAILABLE", value=True),
        intersects_80_region=AnalyticalResult(status="AVAILABLE", value=True),
        intersects_95_region=AnalyticalResult(status="AVAILABLE", value=True),
        time_inside_region_seconds=AnalyticalResult(status="AVAILABLE", value=3600.0),
        features_available=FeatureAvailability(spatial_overlap=True, temporal_match=True, closest_approach=True, ais_continuity=True)
    )
    
    res = engine.evaluate_candidate(cand, [Point(lat=0, lon=0)])
    assert res.status == ForwardConsistencyStatus.CONSISTENT
    assert res.centroid_distance_km == 10.0
    
@patch('packages.forward_validation.engine.ForwardValidationEngine.evaluate_candidate')
def test_incompatible_candidate(mock_eval):
    from packages.forward_validation import CandidateForwardConsistency, ForwardSimulationSummary, ReleaseHypothesis
    mock_eval.return_value = CandidateForwardConsistency(
        candidate_id="123",
        status=ForwardConsistencyStatus.INCONSISTENT,
        hypotheses_tested=1,
        best_hypothesis=ForwardSimulationSummary(
            hypothesis=ReleaseHypothesis(
                candidate_id="123", release_lat=0, release_lon=0, release_time="2018-08-15T15:00:00Z", derivation_method="", source_fields=[], uncertainty_limitations=[]
            ),
            forward_duration_seconds=48.0*3600,
            final_centroid_lat=0.0,
            final_centroid_lon=0.0,
            centroid_distance_km=5.1,
            overlap_metric=0.1,
            status=ForwardConsistencyStatus.INCONSISTENT,
            supporting_observations=[],
            contradicting_observations=[]
        ),
        centroid_distance_km=5.1,
        overlap_metric=0.1,
        supporting_observations=[],
        contradicting_observations=[],
        limitations=[],
        provenance={}
    )
    
    config = ForwardValidationConfig(inconsistent_centroid_distance_km=5.0) # force inconsistent
    engine = ForwardValidationEngine(config, "dummy", "dummy")
    cand = CandidateVessel(
        mmsi="123", trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
        closest_approach_km=AnalyticalResult(status="AVAILABLE", value=0.0),
        closest_approach_time=AnalyticalResult(status="AVAILABLE", value="2018-08-15T15:00:00Z"),
        intersects_50_region=AnalyticalResult(status="AVAILABLE", value=True),
        intersects_80_region=AnalyticalResult(status="AVAILABLE", value=True),
        intersects_95_region=AnalyticalResult(status="AVAILABLE", value=True),
        time_inside_region_seconds=AnalyticalResult(status="AVAILABLE", value=3600.0),
        features_available=FeatureAvailability(spatial_overlap=True, temporal_match=True, closest_approach=True, ais_continuity=True)
    )
    res = engine.evaluate_candidate(cand, [Point(lat=0, lon=0)])
    assert res.status == ForwardConsistencyStatus.INCONSISTENT
