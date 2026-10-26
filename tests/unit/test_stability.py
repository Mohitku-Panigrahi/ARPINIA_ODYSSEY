import pytest
from datetime import datetime, timezone
import numpy as np
from packages.geo.models import Point
from packages.stability.config import MonteCarloConfig
from packages.stability.runner import StabilityRunner
from packages.stability.models import CandidateRunResult, CandidateStatus
from packages.stability.aggregation import StabilityAggregator
from packages.attribution.config import AttributionConfig
from packages.attribution.models import AttributionRanking, CandidateAttribution, EvidenceCoverage, FactorResult
from packages.ais.models import VesselTrajectory, AISObservation

def mock_b3_factory(config):
    class MockReconstructionEngine:
        def __init__(self, c):
            self.config = c
        def run_backward(self, seed_polygon, t0):
            grid = np.zeros((10, 10))
            seed = self.config.get('random_seed', 0)
            np.random.seed(seed)
            shift_x = np.random.randint(-1, 2)
            shift_y = np.random.randint(-1, 2)
            cx, cy = 5 + shift_x, 5 + shift_y
            cx = max(0, min(9, cx))
            cy = max(0, min(9, cy))
            grid[cy, cx] = 0.6
            t_slice = {
                "timestamp": t0,
                "probability_data": {
                    "status": "success", "lon_bins": np.linspace(33.0, 34.0, 11),
                    "lat_bins": np.linspace(33.0, 34.0, 11), "grid": grid,
                    "thresholds": {"50": 0.5, "80": 0.2, "95": 0.05}, "centroid": Point(lat=33.5, lon=33.5)
                }
            }
            return {"time_slices": [t_slice]}
    return MockReconstructionEngine(config)

def test_math_invariants_single_candidate():
    agg = StabilityAggregator()
    # Mock candidate present in 40/100 runs, always rank 1
    for i in range(100):
        if i < 40:
            res = [CandidateRunResult(run_id=str(i), mmsi="1", rank=1, attribution_score=0.9, evidence_coverage=1.0, status=CandidateStatus.RANKED)]
        else:
            res = [CandidateRunResult(run_id=str(i), mmsi="1", rank=None, attribution_score=None, evidence_coverage=None, status=CandidateStatus.ABSENT)]
        agg.add_valid_run(res)
    
    stab = agg.get_candidate_stability("1")
    assert stab.presence_rate == 0.4
    assert stab.top1_stability == 0.4
    assert stab.top3_stability == 0.4
    assert stab.conditional_top1_given_present == 1.0
    assert stab.conditional_top1_given_ranked == 1.0
    assert stab.mean_rank == 1.0
    assert stab.median_rank == 1.0

def test_insufficient_evidence_appearance():
    agg = StabilityAggregator()
    # Mock candidate present in 1 run but INSUFFICIENT_EVIDENCE
    agg.add_valid_run([CandidateRunResult(run_id="1", mmsi="1", rank=None, attribution_score=0.2, evidence_coverage=0.1, status=CandidateStatus.INSUFFICIENT_EVIDENCE)])
    stab = agg.get_candidate_stability("1")
    assert stab.presence_rate == 1.0
    assert stab.ranked_rate == 0.0
    assert stab.insufficient_evidence_rate == 1.0
    assert stab.conditional_top1_given_present == 0.0
    assert stab.conditional_top1_given_ranked == 0.0

def test_convergence_patience():
    mc = MonteCarloConfig(minimum_runs=10, maximum_runs=100, convergence_check_interval=10, convergence_tolerance=0.01, convergence_patience=2)
    runner = StabilityRunner(mc, mock_b3_factory, {}, [], AttributionConfig(), "test")
    res = runner.run_ensemble(datetime(2018,8,15,12,tzinfo=timezone.utc), [Point(lat=33.5, lon=33.5)])
    assert res.valid_runs == 30
    assert res.convergence.consecutive_converged_checks == 2

def test_minimum_valid_fraction():
    agg = StabilityAggregator(min_valid_runs=10, min_valid_fraction=0.5)
    agg.attempted_runs = 100
    agg.valid_runs = 10 # 10% valid
    agg.add_valid_run([CandidateRunResult(run_id="1", mmsi="1", rank=1, attribution_score=0.9, evidence_coverage=1.0, status=CandidateStatus.RANKED)] * 10)
    stab = agg.get_candidate_stability("1")
    assert stab.stability_class.value == "INSUFFICIENT_ENSEMBLE_EVIDENCE"

def test_wilson_interval():
    from packages.stability.aggregation import calculate_wilson_interval
    res = calculate_wilson_interval(50, 100)
    assert 0.4 < res.lower_bound < 0.5
    assert 0.5 < res.upper_bound < 0.6
    assert res.estimate == 0.5
