import pytest
import math
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

from packages.geo.exceptions import (
    InvalidCoordinateError,
    InvalidBoundingBoxError,
    InvalidTrajectoryError,
    InvalidTimestampError
)
from packages.geo.models import Point, BoundingBox, TrajectoryPoint, Trajectory
from packages.geo.distance import calculate_distance
from packages.geo.spatial import is_point_in_bbox, is_trajectory_in_bbox

# --- Valid Inputs ---
def test_valid_point():
    p = Point(lat=45.0, lon=-120.0)
    assert p.lat == 45.0
    assert p.lon == -120.0
    assert p.to_geojson() == {"type": "Point", "coordinates": [-120.0, 45.0]}

def test_valid_bbox():
    bbox = BoundingBox(min_lon=-10.0, min_lat=-10.0, max_lon=10.0, max_lat=10.0)
    assert bbox.min_lon == -10.0
    
def test_valid_trajectory():
    dt1 = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)
    dt2 = datetime(2026, 8, 28, 12, 1, 0, tzinfo=timezone.utc)
    p1 = TrajectoryPoint(point=Point(lat=0.0, lon=0.0), timestamp=dt1)
    p2 = TrajectoryPoint(point=Point(lat=0.1, lon=0.1), timestamp=dt2)
    traj = Trajectory(points=[p1, p2])
    assert len(traj.points) == 2
    assert traj.to_geojson() == {"type": "LineString", "coordinates": [[0.0, 0.0], [0.1, 0.1]]}

def test_timestamp_normalization():
    # ISO string with Z
    p1 = TrajectoryPoint(point={"lat": 0.0, "lon": 0.0}, timestamp="2026-08-28T12:00:00Z")
    assert p1.timestamp.tzinfo == timezone.utc
    
    # ISO string with offset
    p2 = TrajectoryPoint(point={"lat": 0.0, "lon": 0.0}, timestamp="2026-08-28T12:00:00+00:00")
    assert p2.timestamp.tzinfo == timezone.utc
    
    # Unix timestamp (which assumes UTC)
    p3 = TrajectoryPoint(point={"lat": 0.0, "lon": 0.0}, timestamp=1609459200) # 2021-01-01 00:00:00 UTC
    assert p3.timestamp.tzinfo == timezone.utc
    
    # Naive datetime (should be rejected)
    with pytest.raises(InvalidTimestampError) as exc_info:
        TrajectoryPoint(point={"lat": 0.0, "lon": 0.0}, timestamp=datetime(2026, 8, 28, 12, 0, 0))
    assert "Timezone-naive timestamps are not allowed" in str(exc_info.value)
    
    # String without timezone (naive string, rejected)
    with pytest.raises(InvalidTimestampError) as exc_info:
        TrajectoryPoint(point={"lat": 0.0, "lon": 0.0}, timestamp="2026-08-28T12:00:00")
    assert "Timezone-naive timestamps are not allowed" in str(exc_info.value)

# --- Boundary Inputs ---
def test_boundary_coordinates():
    p1 = Point(lat=90.0, lon=180.0)
    p2 = Point(lat=-90.0, lon=-180.0)
    assert p1.lat == 90.0
    assert p2.lat == -90.0
    
def test_zero_area_bbox():
    bbox = BoundingBox(min_lon=10.0, min_lat=10.0, max_lon=10.0, max_lat=10.0)
    assert bbox.min_lon == 10.0

def test_single_point_trajectory_valid():
    traj = Trajectory(points=[TrajectoryPoint(point=Point(lat=0.0, lon=0.0), timestamp="2026-08-28T12:00:00Z")])
    assert len(traj.points) == 1
    assert traj.to_geojson() == {"type": "LineString", "coordinates": [[0.0, 0.0]]}

# --- Invalid Inputs ---
def test_invalid_coordinates():
    with pytest.raises(InvalidCoordinateError) as exc_info:
        Point(lat=91.0, lon=0)
    assert "Latitude must be between -90 and 90" in str(exc_info.value)
    
    with pytest.raises(InvalidCoordinateError) as exc_info:
        Point(lat=0, lon=-181.0)
    assert "Longitude must be between -180 and 180" in str(exc_info.value)

def test_nan_infinity_coordinates():
    with pytest.raises(InvalidCoordinateError) as exc_info:
        Point(lat=float('nan'), lon=0)
    assert "Coordinate value must be finite" in str(exc_info.value)

    with pytest.raises(InvalidCoordinateError) as exc_info:
        Point(lat=0, lon=float('inf'))
    assert "Coordinate value must be finite" in str(exc_info.value)

def test_reversed_bbox():
    with pytest.raises(InvalidBoundingBoxError) as exc_info:
        BoundingBox(min_lon=10.0, min_lat=10.0, max_lon=-10.0, max_lat=10.0)
    assert "min_lon cannot be greater than max_lon" in str(exc_info.value)
    
    with pytest.raises(InvalidBoundingBoxError) as exc_info:
        BoundingBox(min_lon=0.0, min_lat=10.0, max_lon=0.0, max_lat=-10.0)
    assert "min_lat cannot be greater than max_lat" in str(exc_info.value)

def test_invalid_timestamp():
    with pytest.raises(InvalidTimestampError) as exc_info:
        TrajectoryPoint(point=Point(lat=0,lon=0), timestamp="not-a-timestamp")
    assert "Invalid timestamp format" in str(exc_info.value)

def test_chronological_trajectory():
    dt1 = datetime(2026, 8, 28, 12, 1, 0, tzinfo=timezone.utc)
    dt2 = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc) # dt2 is before dt1
    p1 = TrajectoryPoint(point=Point(lat=0.0, lon=0.0), timestamp=dt1)
    p2 = TrajectoryPoint(point=Point(lat=0.0, lon=0.0), timestamp=dt2)
    with pytest.raises(InvalidTrajectoryError) as exc_info:
        Trajectory(points=[p1, p2])
    assert "strictly increasing timestamps" in str(exc_info.value)

def test_zero_duration_trajectory_points():
    dt = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)
    p1 = TrajectoryPoint(point=Point(lat=10.0, lon=10.0), timestamp=dt)
    p2 = TrajectoryPoint(point=Point(lat=11.0, lon=11.0), timestamp=dt)
    with pytest.raises(InvalidTrajectoryError) as exc_info:
        Trajectory(points=[p1, p2])
    assert "strictly increasing timestamps" in str(exc_info.value)

def test_strict_type_validation():
    with pytest.raises(ValidationError):
        Point(lat="33.5", lon="34.1") # Strings should be rejected due to strict=True

# --- Determinism & Math ---
def test_distance_determinism():
    p1 = Point(lat=52.2296756, lon=21.0122287) # Warsaw
    p2 = Point(lat=41.8919300, lon=12.5113300) # Rome
    d1 = calculate_distance(p1, p2)
    d2 = calculate_distance(p1, p2)
    d3 = calculate_distance(p2, p1)
    
    assert d1 == d2
    assert d1 == d3
    assert math.isclose(d1, 1315600, rel_tol=1e-3) # Approx 1315 km

def test_spatial_filtering():
    bbox = BoundingBox(min_lon=0.0, min_lat=0.0, max_lon=10.0, max_lat=10.0)
    p_in = Point(lat=5.0, lon=5.0)
    p_out = Point(lat=15.0, lon=5.0)
    p_edge = Point(lat=10.0, lon=10.0)
    
    assert is_point_in_bbox(p_in, bbox) is True
    assert is_point_in_bbox(p_out, bbox) is False
    assert is_point_in_bbox(p_edge, bbox) is True
    
    dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t_in = Trajectory(points=[
        TrajectoryPoint(point=p_in, timestamp=dt),
        TrajectoryPoint(point=Point(lat=6.0, lon=6.0), timestamp=dt + timedelta(seconds=1))
    ])
    t_partial = Trajectory(points=[
        TrajectoryPoint(point=p_in, timestamp=dt),
        TrajectoryPoint(point=p_out, timestamp=dt + timedelta(seconds=1))
    ])
    
    assert is_trajectory_in_bbox(t_in, bbox, partial=False) is True
    assert is_trajectory_in_bbox(t_partial, bbox, partial=False) is False
    assert is_trajectory_in_bbox(t_partial, bbox, partial=True) is True
