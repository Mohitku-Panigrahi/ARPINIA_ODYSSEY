import pytest
from datetime import datetime, timezone, timedelta
from packages.ais.models import AISObservation
from packages.ais.pipeline import AISPipeline
from pydantic import ValidationError

def test_ais_schema():
    # Valid
    obs = AISObservation(
        source="TEST",
        mmsi="123456789",
        timestamp_utc=datetime(2018, 8, 15, 12, tzinfo=timezone.utc),
        latitude=33.5,
        longitude=33.5
    )
    assert obs.mmsi == "123456789"

    # Invalid MMSI length
    with pytest.raises(ValidationError):
        AISObservation(
            source="TEST",
            mmsi="123",
            timestamp_utc=datetime(2018, 8, 15, 12, tzinfo=timezone.utc),
            latitude=33.5,
            longitude=33.5
        )

    # Naive datetime
    with pytest.raises(ValidationError):
        AISObservation(
            source="TEST",
            mmsi="123456789",
            timestamp_utc=datetime(2018, 8, 15, 12),
            latitude=33.5,
            longitude=33.5
        )

    # Invalid coordinates
    with pytest.raises(ValidationError):
        AISObservation(
            source="TEST",
            mmsi="123456789",
            timestamp_utc=datetime(2018, 8, 15, 12, tzinfo=timezone.utc),
            latitude=95.0,
            longitude=33.5
        )

def test_duplicate_removal():
    pipeline = AISPipeline()
    t0 = datetime(2018, 8, 15, 12, tzinfo=timezone.utc)
    obs1 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t0, latitude=33.0, longitude=33.0)
    obs2 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t0, latitude=33.0, longitude=33.0)
    
    res = pipeline.clean_and_group([obs1, obs2])
    assert len(res["111111111"]) == 1

def test_impossible_speed():
    pipeline = AISPipeline(max_speed_knots=40.0)
    t0 = datetime(2018, 8, 15, 12, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=1)
    
    # 1 degree lat is ~111km. Doing that in 1 second is impossible.
    obs1 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t0, latitude=33.0, longitude=33.0)
    obs2 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t1, latitude=34.0, longitude=33.0)
    
    res = pipeline.clean_and_group([obs1, obs2])
    assert len(res["111111111"]) == 1

def test_short_gap_interpolation():
    pipeline = AISPipeline(max_interpolation_gap_seconds=3600.0)
    t0 = datetime(2018, 8, 15, 12, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=1800) # 30 mins
    
    obs1 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t0, latitude=33.0, longitude=33.0)
    obs2 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t1, latitude=33.1, longitude=33.1)
    
    grouped = pipeline.clean_and_group([obs1, obs2])
    trajectories = pipeline.build_trajectories(grouped)
    
    assert len(trajectories) == 1
    traj = trajectories[0]
    assert len(traj.segments) == 1
    assert traj.segments[0].is_interpolated == True
    assert traj.segments[0].interpolated_gap == False

def test_long_gap_no_interpolation():
    pipeline = AISPipeline(max_interpolation_gap_seconds=3600.0)
    t0 = datetime(2018, 8, 15, 12, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=7200) # 2 hours
    
    obs1 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t0, latitude=33.0, longitude=33.0)
    obs2 = AISObservation(source="T", mmsi="111111111", timestamp_utc=t1, latitude=33.2, longitude=33.2)
    
    grouped = pipeline.clean_and_group([obs1, obs2])
    trajectories = pipeline.build_trajectories(grouped)
    
    traj = trajectories[0]
    assert traj.segments[0].is_interpolated == False
    assert traj.segments[0].interpolated_gap == True
    assert "LOW_SAMPLING_DENSITY" in traj.quality_flags

