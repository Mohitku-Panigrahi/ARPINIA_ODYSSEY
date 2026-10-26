import pytest
import numpy as np
from datetime import datetime, timezone, timedelta
from packages.geo.models import Point
from packages.reconstruction.engine import ReconstructionEngine

import os
@pytest.fixture
def engine():
    # Use the golden scenario NetCDF files which were validated in B2.1
    config = {
        'particle_count': 100,
        'random_seed': 123,
        'duration': timedelta(hours=2),
        'time_step': timedelta(hours=1),
    }
    
    era5_default = os.path.join(os.path.expanduser("~"), "odyssey-data-test", "era5_sih_zenodo_alpha_20180813_20180816.nc")
    cmems_default = os.path.join(os.path.expanduser("~"), "odyssey-data-test", "cmems_sih_zenodo_alpha_20180813_20180816.nc")
    
    era5 = os.getenv("ODYSSEY_ERA5_PATH", era5_default)
    cmems = os.getenv("ODYSSEY_CMEMS_PATH", cmems_default)
    
    return ReconstructionEngine(
        era5_path=era5,
        cmems_path=cmems,
        config=config
    )

def test_timezone_boundary(engine):
    # Verify the external interface requires aware datetimes.
    # We pass naive datetime, it should NOT crash, but we are supposed to reject naive.
    # Wait, the prompt says "Reject naive datetime supplied at the public/internal B3 contract boundary."
    # Let me check engine.py
    polygon = [Point(lat=33.5, lon=33.5), Point(lat=33.6, lon=33.5), Point(lat=33.6, lon=33.6), Point(lat=33.5, lon=33.6)]
    
    naive_t = datetime(2018, 8, 15, 15, 44, 0)
    aware_t = datetime(2018, 8, 15, 15, 44, 0, tzinfo=timezone.utc)
    
    # engine.py needs to raise ValueError on naive
    with pytest.raises(ValueError, match="timezone-aware"):
        engine.run_backward(polygon, naive_t)

    # Aware should pass and return valid slices
    res = engine.run_backward(polygon, aware_t)
    assert res is not None
    assert len(res['time_slices']) > 0
    assert res['time_slices'][0]['active_valid_particle_count'] > 0
    # verify prob mass normalization
    grid = res['time_slices'][0]['probability_data']['grid']
    assert np.isclose(np.sum(grid), 1.0)

def test_reproducibility(engine):
    polygon = [Point(lat=33.5, lon=33.5), Point(lat=33.6, lon=33.5), Point(lat=33.6, lon=33.6), Point(lat=33.5, lon=33.6)]
    t0 = datetime(2018, 8, 15, 15, 44, 0, tzinfo=timezone.utc)
    
    res1 = engine.run_backward(polygon, t0)
    res2 = engine.run_backward(polygon, t0)
    
    assert res1['random_seed'] == res2['random_seed']
    assert len(res1['time_slices']) > 0
    # Check probability grids
    for s1, s2 in zip(res1['time_slices'], res2['time_slices']):
        assert np.allclose(s1['probability_data']['grid'], s2['probability_data']['grid'])
        assert np.isclose(np.sum(s1['probability_data']['grid']), 1.0)

def test_out_of_bounds_missing_forcing(engine):
    # Configure an engine outside valid space
    
    # Valid coverage is approx [33.1, 33.8] x [33.2, 33.7]
    # Let's seed completely outside
    polygon = [Point(lat=40.0, lon=40.0), Point(lat=40.1, lon=40.0), Point(lat=40.1, lon=40.1)]
    t0 = datetime(2018, 8, 15, 15, 44, 0, tzinfo=timezone.utc)
    
    # Missing forcing must throw a hard REQUIRED_FORCING_UNAVAILABLE error, not return an empty array silently.
    with pytest.raises(ValueError, match="REQUIRED_FORCING_UNAVAILABLE"):
        engine.run_backward(polygon, t0)

