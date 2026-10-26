import pytest
import math
from pydantic import ValidationError
from packages.attribution.config import AttributionConfig
from packages.attribution.scoring import AttributionEngine
from packages.ais.models import CandidateVessel, B4Result, FeatureAvailability, AnalyticalResult

def create_mock_candidate(mmsi, score_overrides=None):
    base = {
        "mmsi": mmsi,
        "trajectory_quality": {"max_gap_seconds": 100.0},
        "observed_intersections": [],
        "segment_intersections": [],
        "probability_region_intersections": [],
        "closest_approach_km": AnalyticalResult[float](value=1.0, status="AVAILABLE"),
        "closest_approach_time": AnalyticalResult[str](value="2018-08-15T12:00:00Z", status="AVAILABLE"),
        "intersects_50_region": AnalyticalResult[bool](value=True, status="AVAILABLE"),
        "intersects_80_region": AnalyticalResult[bool](value=True, status="AVAILABLE"),
        "intersects_95_region": AnalyticalResult[bool](value=True, status="AVAILABLE"),
        "time_inside_region_seconds": AnalyticalResult[float](value=None, status="NOT_COMPUTABLE"),
        "features_available": FeatureAvailability(spatial_overlap=True, temporal_match=True, closest_approach=True, ais_continuity=True),
        "gap_analysis": [],
        "candidate_reasons": []
    }
    if score_overrides:
        base.update(score_overrides)
    return CandidateVessel(**base)

def test_attribution_basic():
    config = AttributionConfig()
    engine = AttributionEngine(config)
    cv1 = create_mock_candidate("111111111", {"closest_approach_km": AnalyticalResult[float](value=0.0, status="AVAILABLE")})
    b4 = B4Result(scenario_id="test", ais_source="test", source_mode="test", raw_artifact_hash=None, requested_time_window={}, requested_bbox={}, vessel_count=1, observation_count=1, candidate_count=1, candidates=[cv1], excluded=[], warnings=[], limitations=[], provenance={})
    ranking = engine.score_candidates(b4, [])
    assert ranking.ranked_candidates[0].attribution_relevance_score == 1.0

def test_config_validation():
    with pytest.raises(ValidationError):
        AttributionConfig(d_ref_min_km=10.0, d_ref_max_km=5.0)
    with pytest.raises(ValidationError):
        AttributionConfig(max_gap_perfect_seconds=5000, max_gap_zero_seconds=1000)
    with pytest.raises(ValidationError):
        AttributionConfig(weight_f1_spatial=0, weight_f2_temporal=0, weight_f4_closest_approach=0)

def test_f1_null_semantics():
    engine = AttributionEngine()
    
    # Unavailable F1
    cv_unavail = create_mock_candidate("1", {
        "intersects_50_region": AnalyticalResult[bool](value=None, status="UNAVAILABLE"),
        "intersects_80_region": AnalyticalResult[bool](value=None, status="UNAVAILABLE"),
        "intersects_95_region": AnalyticalResult[bool](value=None, status="UNAVAILABLE")
    })
    res_unavail = engine._score_f1_spatial(cv_unavail)
    assert not res_unavail.available
    
    # Available but no overlap F1
    cv_no_overlap = create_mock_candidate("2", {
        "intersects_50_region": AnalyticalResult[bool](value=False, status="AVAILABLE"),
        "intersects_80_region": AnalyticalResult[bool](value=False, status="AVAILABLE"),
        "intersects_95_region": AnalyticalResult[bool](value=False, status="AVAILABLE")
    })
    res_no_overlap = engine._score_f1_spatial(cv_no_overlap)
    assert res_no_overlap.available
    assert res_no_overlap.score == 0.0

def test_f4_invalid_distances():
    engine = AttributionEngine()
    for bad_dist in [-5.0, math.nan, math.inf, -math.inf]:
        cv = create_mock_candidate("1", {"closest_approach_km": AnalyticalResult[float](value=bad_dist, status="AVAILABLE")})
        res = engine._score_f4_closest_approach(cv, 10.0)
        assert not res.available
        assert res.reason == "INVALID_DISTANCE_INPUT"

def test_f5_missing_quality():
    engine = AttributionEngine()
    cv = create_mock_candidate("1", {"trajectory_quality": {}})
    mod, avail = engine._calculate_f5_continuity(cv)
    assert not avail
    assert mod == 0.0

def test_tie_handling_and_stable_mmsi():
    engine = AttributionEngine(AttributionConfig(tie_tolerance=0.05))
    cv1 = create_mock_candidate("333333333") # Score A
    cv2 = create_mock_candidate("111111111") # Score A
    cv3 = create_mock_candidate("222222222") # Score A
    
    b4 = B4Result(scenario_id="test", ais_source="test", source_mode="test", raw_artifact_hash=None, requested_time_window={}, requested_bbox={}, vessel_count=3, observation_count=1, candidate_count=3, candidates=[cv1, cv2, cv3], excluded=[], warnings=[], limitations=[], provenance={})
    ranking = engine.score_candidates(b4, [])
    
    assert len(ranking.ranked_candidates) == 3
    # Same score and coverage -> sorted by MMSI ascending
    assert ranking.ranked_candidates[0].mmsi == "111111111"
    assert ranking.ranked_candidates[1].mmsi == "222222222"
    assert ranking.ranked_candidates[2].mmsi == "333333333"
    assert all(r.status == "EFFECTIVELY_TIED" for r in ranking.ranked_candidates)

