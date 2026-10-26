import pytest
from packages.geo.models import Point
import numpy as np
from datetime import datetime, timezone, timedelta
from packages.ais.models import AISObservation, VesselTrajectory, TrajectorySegment
from packages.ais.correlation import CorrelationEngine

def mock_time_slice(t, t50=0.5, t80=0.2, t95=0.05):
    # Create a grid 10x10 around 33.5, 33.5
    grid = np.zeros((10, 10))
    # Make center (5,5) high prob
    grid[5, 5] = 0.6
    grid[4:7, 4:7] = np.maximum(grid[4:7, 4:7], 0.3)
    grid[3:8, 3:8] = np.maximum(grid[3:8, 3:8], 0.1)
    
    return {
        "timestamp": t,
        "probability_data": {
            "grid": grid,
            "lon_bins": np.linspace(33.0, 34.0, 11),
            "lat_bins": np.linspace(33.0, 34.0, 11),
            "thresholds": {"50": t50, "80": t80, "95": t95},
            "centroid": Point(lat=33.55, lon=33.55)
        }
    }

def test_segment_intersection():
    t0 = datetime(2018, 8, 15, 12, tzinfo=timezone.utc)
    engine = CorrelationEngine([mock_time_slice(t0)])
    
    # Segment passing through center 33.55, 33.55
    obs1 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t0 - timedelta(minutes=10), latitude=33.1, longitude=33.1)
    obs2 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t0 + timedelta(minutes=10), latitude=33.9, longitude=33.9)
    seg = TrajectorySegment(start_obs=obs1, end_obs=obs2, duration_seconds=1200, distance_meters=100000, is_interpolated=True, interpolated_gap=False)
    
    traj = VesselTrajectory(mmsi="111111111", observations=[obs1, obs2], segments=[seg])
    cands, excls = engine.correlate([traj])
    
    assert len(cands) == 1
    assert "SEGMENT_INTERSECTS_ORIGIN" in cands[0].candidate_reasons
    assert "50" in cands[0].segment_intersections

def test_kinematic_reachability():
    t0 = datetime(2018, 8, 15, 12, tzinfo=timezone.utc)
    engine = CorrelationEngine([mock_time_slice(t0)])
    
    # Segment with long gap that could reach the center at t0
    # Start at 33.5, 33.0 at t0 - 2 hours
    # End at 33.5, 34.0 at t0 + 2 hours
    # Distance is about 100km, 4 hours total, 25km/h, very reachable.
    obs1 = AISObservation(source="T", mmsi="222222222", timestamp_utc=t0 - timedelta(hours=2), latitude=33.5, longitude=33.0)
    obs2 = AISObservation(source="T", mmsi="222222222", timestamp_utc=t0 + timedelta(hours=2), latitude=33.5, longitude=34.0)
    seg = TrajectorySegment(start_obs=obs1, end_obs=obs2, duration_seconds=14400, distance_meters=100000, is_interpolated=False, interpolated_gap=True)
    
    traj = VesselTrajectory(mmsi="222222222", observations=[obs1, obs2], segments=[seg])
    cands, excls = engine.correlate([traj])
    
    assert len(cands) == 1
    assert "KINEMATICALLY_REACHABLE_DURING_GAP" in cands[0].candidate_reasons
    
def test_negative_filtering():
    t0 = datetime(2018, 8, 15, 12, tzinfo=timezone.utc)
    engine = CorrelationEngine([mock_time_slice(t0)])
    
    # Completely far away, not reachable
    obs1 = AISObservation(source="T", mmsi="333333333", timestamp_utc=t0 - timedelta(minutes=10), latitude=40.0, longitude=40.0)
    obs2 = AISObservation(source="T", mmsi="333333333", timestamp_utc=t0 + timedelta(minutes=10), latitude=40.1, longitude=40.1)
    seg = TrajectorySegment(start_obs=obs1, end_obs=obs2, duration_seconds=1200, distance_meters=10000, is_interpolated=True, interpolated_gap=False)
    
    traj = VesselTrajectory(mmsi="333333333", observations=[obs1, obs2], segments=[seg])
    cands, excls = engine.correlate([traj])
    
    assert len(cands) == 0
    assert len(excls) == 1

