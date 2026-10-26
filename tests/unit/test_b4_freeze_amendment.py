import pytest
from datetime import datetime, timezone
import numpy as np
from packages.geo.models import Point
from packages.ais.models import AISObservation, CandidateVessel
from packages.ais.correlation import CorrelationEngine
from packages.ais.pipeline import AISPipeline

def test_closest_approach_centroid_handling():
    obs = [
        AISObservation(
            source="TEST",
            mmsi="123456789",
            timestamp_utc=datetime(2018, 8, 15, 12, 0, tzinfo=timezone.utc),
            latitude=33.40,
            longitude=33.40
        ),
        AISObservation(
            source="TEST",
            mmsi="123456789",
            timestamp_utc=datetime(2018, 8, 15, 12, 10, tzinfo=timezone.utc),
            latitude=33.42,
            longitude=33.42
        )
    ]
    pipeline = AISPipeline()
    trajs = pipeline.build_trajectories(pipeline.clean_and_group(obs))
    
    t_slices = [{
        "timestamp": datetime(2018, 8, 15, 12, 5, tzinfo=timezone.utc),
        "probability_data": {
            "status": "success",
            "centroid": Point(lat=33.41, lon=33.41),
            "lon_bins": [33.39, 33.41, 33.43],
            "lat_bins": [33.39, 33.41, 33.43],
            "grid": np.array([[0.1, 0.2], [0.3, 0.4]]),
            "thresholds": {"50": 0.5, "80": 0.2, "95": 0.05}
        }
    }]
    
    engine = CorrelationEngine(t_slices)
    cands, excl = engine.correlate(trajs)
    
    assert len(cands) == 1
    cand = cands[0]
    
    assert cand.closest_approach_km is not None
    assert cand.closest_approach_km.status == "AVAILABLE"
    assert cand.closest_approach_km.value > 0

