import pytest
import math
from datetime import datetime, timezone, timedelta
from packages.ais.models import AISObservation, AnalyticalResult, CandidateVessel
from pydantic import ValidationError

def test_missing_optional_ais_field():
    obs = AISObservation(
        source="TEST",
        mmsi="123456789",
        timestamp_utc=datetime.now(timezone.utc),
        latitude=30.0,
        longitude=40.0
    )
    assert obs.vessel_name is None
    assert obs.sog_knots is None
    assert obs.heading_degrees is None

def test_sentinels_normalization():
    obs = AISObservation(
        source="TEST",
        mmsi="123456789",
        timestamp_utc=datetime.now(timezone.utc),
        latitude=30.0,
        longitude=40.0,
        heading_degrees=511.0,
        cog_degrees=3600.0,
        sog_knots=102.3
    )
    assert obs.heading_degrees is None
    assert obs.cog_degrees is None
    assert obs.sog_knots is None
    assert "HEADING_SENTINEL_NORMALIZED" in obs.quality_flags
    assert "COG_SENTINEL_NORMALIZED" in obs.quality_flags
    assert "SOG_SENTINEL_NORMALIZED" in obs.quality_flags

def test_json_serialization_safety():
    from packages.ais.models import FeatureAvailability
    features = FeatureAvailability(
        spatial_overlap=True, temporal_match=False, closest_approach=True, ais_continuity=True
    )
    
    cand = CandidateVessel(
        mmsi="123456789",
        imo=None,
        vessel_name=None,
        trajectory_quality={"max_gap": 0.0},
        observed_intersections=[],
        segment_intersections=[],
        probability_region_intersections=[],
        closest_approach_km=AnalyticalResult[float](value=None, status="NOT_APPLICABLE", reason="NO_OVERLAP"),
        closest_approach_time=AnalyticalResult[str](value=None, status="NOT_APPLICABLE"),
        intersects_50_region=AnalyticalResult[bool](value=False, status="AVAILABLE"),
        intersects_80_region=AnalyticalResult[bool](value=None, status="UNAVAILABLE"),
        intersects_95_region=AnalyticalResult[bool](value=None, status="NOT_COMPUTABLE"),
        time_inside_region_seconds=AnalyticalResult[float](value=None, status="NOT_COMPUTABLE"),
        features_available=features
    )
    json_str = cand.model_dump_json()
    assert "NaN" not in json_str
    assert "Infinity" not in json_str
