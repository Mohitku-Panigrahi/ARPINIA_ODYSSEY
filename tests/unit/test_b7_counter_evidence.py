import pytest
from datetime import datetime, timezone, timedelta
from packages.counter_evidence import CounterEvidenceEngine, CounterEvidenceConfig, CounterEvidenceStatus, Polarity, Severity, Computability
from packages.ais.models import CandidateVessel, B4Result, AnalyticalResult, FeatureAvailability, GapAnalysis
from packages.attribution.models import CandidateAttribution, AttributionRanking, EvidenceCoverage
from packages.stability.models import CandidateStability, StabilityClass, WilsonInterval

def test_config_validation():
    with pytest.raises(ValueError):
        CounterEvidenceConfig(spatial_support_max_distance_km=100.0, spatial_contradiction_min_distance_km=50.0)
    
    with pytest.raises(ValueError):
        CounterEvidenceConfig(spatial_contradiction_min_distance_km=float('inf'))

def test_missing_data_semantics():
    config = CounterEvidenceConfig()
    engine = CounterEvidenceEngine(config)
    
    cand_b4 = CandidateVessel(
        mmsi="123", trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
        closest_approach_km=AnalyticalResult(status="UNAVAILABLE", value=None),
        closest_approach_time=AnalyticalResult(status="UNAVAILABLE", value=None),
        intersects_50_region=AnalyticalResult(status="UNAVAILABLE", value=None),
        intersects_80_region=AnalyticalResult(status="UNAVAILABLE", value=None),
        intersects_95_region=AnalyticalResult(status="UNAVAILABLE", value=None),
        time_inside_region_seconds=AnalyticalResult(status="UNAVAILABLE", value=None),
        features_available=FeatureAvailability(spatial_overlap=False, temporal_match=False, closest_approach=False, ais_continuity=False)
    )
    
    b4_res = B4Result(scenario_id="s1", ais_source="mock", source_mode="mock", requested_time_window={}, requested_bbox={}, vessel_count=1, observation_count=1, candidate_count=1, candidates=[cand_b4], excluded=[], warnings=[], limitations=[], provenance={}, raw_artifact_hash="hash")
    b5_rank = AttributionRanking(scenario_id="s1", configuration_version="1", attribution_algorithm_version="1", ranked_candidates=[], insufficient_evidence_candidates=[], d_ref_km=50.0)
    
    res = engine.analyze("s1", b4_res, b5_rank, [])
    
    c_res = res.candidates[0]
    assert c_res.overall_counter_evidence_status == CounterEvidenceStatus.INSUFFICIENT_EVIDENCE
    assert c_res.unknown_count > 0
    assert c_res.contradiction_count == 0
    assert c_res.support_count == 0

def test_spatial_temporal_alibi():
    config = CounterEvidenceConfig(spatial_contradiction_min_distance_km=50.0)
    engine = CounterEvidenceEngine(config)
    
    cand_b4 = CandidateVessel(
        mmsi="123", trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
        closest_approach_km=AnalyticalResult(status="AVAILABLE", value=100.0),
        closest_approach_time=AnalyticalResult(status="AVAILABLE", value="2018-08-15T15:00:00Z"),
        intersects_50_region=AnalyticalResult(status="AVAILABLE", value=False),
        intersects_80_region=AnalyticalResult(status="AVAILABLE", value=False),
        intersects_95_region=AnalyticalResult(status="AVAILABLE", value=False),
        time_inside_region_seconds=AnalyticalResult(status="AVAILABLE", value=0.0),
        gap_analysis=[], # no gaps -> perfect alibi
        features_available=FeatureAvailability(spatial_overlap=True, temporal_match=True, closest_approach=True, ais_continuity=True)
    )
    
    b4_res = B4Result(scenario_id="s1", ais_source="mock", source_mode="mock", requested_time_window={}, requested_bbox={}, vessel_count=1, observation_count=1, candidate_count=1, candidates=[cand_b4], excluded=[], warnings=[], limitations=[], provenance={}, raw_artifact_hash="hash")
    b5_rank = AttributionRanking(scenario_id="s1", configuration_version="1", attribution_algorithm_version="1", ranked_candidates=[], insufficient_evidence_candidates=[], d_ref_km=50.0)
    
    res = engine.analyze("s1", b4_res, b5_rank, [])
    c = res.candidates[0]
    
    cats = [i.category for i in c.contradicting_items]
    assert "SPATIAL_COMPATIBILITY" in cats
    assert "TEMPORAL_COMPATIBILITY" in cats
    assert "TRAJECTORY_ALIBI_LIKE" in cats
    assert "CLOSEST_APPROACH" in cats
    
    assert c.overall_counter_evidence_status == CounterEvidenceStatus.STRONG_COUNTER_EVIDENCE

def test_ais_gap():
    config = CounterEvidenceConfig(spatial_contradiction_min_distance_km=50.0)
    engine = CounterEvidenceEngine(config)
    
    cand_b4 = CandidateVessel(
        mmsi="123", trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
        closest_approach_km=AnalyticalResult(status="AVAILABLE", value=100.0),
        closest_approach_time=AnalyticalResult(status="AVAILABLE", value="2018-08-15T15:00:00Z"),
        intersects_50_region=AnalyticalResult(status="AVAILABLE", value=False),
        intersects_80_region=AnalyticalResult(status="AVAILABLE", value=False),
        intersects_95_region=AnalyticalResult(status="AVAILABLE", value=False),
        time_inside_region_seconds=AnalyticalResult(status="AVAILABLE", value=0.0),
        gap_analysis=[GapAnalysis(start_time=datetime(2018,1,1), end_time=datetime(2018,1,2), duration_seconds=86400, start_lat=0, start_lon=0, end_lat=0, end_lon=0, status="GAP")],
        features_available=FeatureAvailability(spatial_overlap=True, temporal_match=True, closest_approach=True, ais_continuity=True)
    )
    
    b4_res = B4Result(scenario_id="s1", ais_source="mock", source_mode="mock", requested_time_window={}, requested_bbox={}, vessel_count=1, observation_count=1, candidate_count=1, candidates=[cand_b4], excluded=[], warnings=[], limitations=[], provenance={}, raw_artifact_hash="hash")
    b5_rank = AttributionRanking(scenario_id="s1", configuration_version="1", attribution_algorithm_version="1", ranked_candidates=[], insufficient_evidence_candidates=[], d_ref_km=50.0)
    
    res = engine.analyze("s1", b4_res, b5_rank, [])
    c = res.candidates[0]
    
    alibi_unknown = next((i for i in c.unknown_items if i.category == "TRAJECTORY_ALIBI_LIKE"), None)
    assert alibi_unknown is not None
    assert alibi_unknown.polarity == Polarity.UNKNOWN

def test_high_stability_support():
    config = CounterEvidenceConfig()
    engine = CounterEvidenceEngine(config)
    cand_b4 = CandidateVessel(
        mmsi="123", trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
        closest_approach_km=AnalyticalResult(status="AVAILABLE", value=10.0),
        closest_approach_time=AnalyticalResult(status="AVAILABLE", value="2018-08-15T15:00:00Z"),
        intersects_50_region=AnalyticalResult(status="AVAILABLE", value=True),
        intersects_80_region=AnalyticalResult(status="AVAILABLE", value=True),
        intersects_95_region=AnalyticalResult(status="AVAILABLE", value=True),
        time_inside_region_seconds=AnalyticalResult(status="AVAILABLE", value=36000.0),
        gap_analysis=[],
        features_available=FeatureAvailability(spatial_overlap=True, temporal_match=True, closest_approach=True, ais_continuity=True)
    )
    b4_res = B4Result(scenario_id="s1", ais_source="mock", source_mode="mock", requested_time_window={}, requested_bbox={}, vessel_count=1, observation_count=1, candidate_count=1, candidates=[cand_b4], excluded=[], warnings=[], limitations=[], provenance={}, raw_artifact_hash="hash")
    
    cand_b5 = CandidateAttribution(mmsi="123", status="RANKED", attribution_relevance_score=0.9, evidence_coverage=EvidenceCoverage(value=1.0, details={}, factors_available=4, continuity_modifier=1.0), factors={}, candidate_reasons=[])
    b5_rank = AttributionRanking(scenario_id="s1", configuration_version="1", attribution_algorithm_version="1", ranked_candidates=[cand_b5], insufficient_evidence_candidates=[], d_ref_km=50.0)
    
    cand_b6 = CandidateStability(mmsi="123", presence_rate=1.0, ranked_rate=1.0, insufficient_evidence_rate=0, top1_stability=1.0, top3_stability=1.0, conditional_top1_given_present=1.0, conditional_top1_given_ranked=1.0, stability_class=StabilityClass.HIGH_STABILITY, top1_wilson_ci=None, top3_wilson_ci=None, presence_wilson_ci=None, nominal_rank=None, nominal_score=None, nominal_coverage=None, mean_rank=1.0, median_rank=1.0, rank_std=0.0, mean_score=1.0, score_std=0.0)
    
    res = engine.analyze("s1", b4_res, b5_rank, [cand_b6])
    c = res.candidates[0]
    
    assert c.contradiction_count == 0
    assert c.support_count > 0
    assert c.overall_counter_evidence_status == CounterEvidenceStatus.NO_MATERIAL_COUNTER_EVIDENCE

def test_performance_scaling():
    import time
    config = CounterEvidenceConfig()
    engine = CounterEvidenceEngine(config)
    
    for n in [5, 50, 500, 5000]:
        cands_b4 = []
        cands_b5 = []
        cands_b6 = []
        for i in range(n):
            mmsi = str(i)
            cands_b4.append(CandidateVessel(
                mmsi=mmsi, trajectory_quality={}, observed_intersections=[], segment_intersections=[], probability_region_intersections=[],
                closest_approach_km=AnalyticalResult(status="AVAILABLE", value=10.0),
                closest_approach_time=AnalyticalResult(status="AVAILABLE", value="2018-08-15T15:00:00Z"),
                intersects_50_region=AnalyticalResult(status="AVAILABLE", value=True),
                intersects_80_region=AnalyticalResult(status="AVAILABLE", value=True),
                intersects_95_region=AnalyticalResult(status="AVAILABLE", value=True),
                time_inside_region_seconds=AnalyticalResult(status="AVAILABLE", value=36000.0),
                gap_analysis=[],
                features_available=FeatureAvailability(spatial_overlap=True, temporal_match=True, closest_approach=True, ais_continuity=True)
            ))
            cands_b5.append(CandidateAttribution(mmsi=mmsi, status="RANKED", attribution_relevance_score=0.9, evidence_coverage=EvidenceCoverage(value=1.0, details={}, factors_available=4, continuity_modifier=1.0), factors={}, candidate_reasons=[]))
            cands_b6.append(CandidateStability(mmsi=mmsi, presence_rate=1.0, ranked_rate=1.0, insufficient_evidence_rate=0, top1_stability=1.0, top3_stability=1.0, conditional_top1_given_present=1.0, conditional_top1_given_ranked=1.0, stability_class=StabilityClass.HIGH_STABILITY, top1_wilson_ci=None, top3_wilson_ci=None, presence_wilson_ci=None, nominal_rank=None, nominal_score=None, nominal_coverage=None, mean_rank=1.0, median_rank=1.0, rank_std=0.0, mean_score=1.0, score_std=0.0))
            
        b4_res = B4Result(scenario_id="s1", ais_source="mock", source_mode="mock", requested_time_window={}, requested_bbox={}, vessel_count=n, observation_count=n, candidate_count=n, candidates=cands_b4, excluded=[], warnings=[], limitations=[], provenance={}, raw_artifact_hash="hash")
        b5_rank = AttributionRanking(scenario_id="s1", configuration_version="1", attribution_algorithm_version="1", ranked_candidates=cands_b5, insufficient_evidence_candidates=[], d_ref_km=50.0)
        
        t0 = time.perf_counter()
        res = engine.analyze("s1", b4_res, b5_rank, cands_b6)
        t1 = time.perf_counter()
        
        assert len(res.candidates) == n
        print(f"\n{n}-candidate runtime: {t1-t0:.3f}s")

if __name__ == '__main__':
    pytest.main(['-s', __file__])
