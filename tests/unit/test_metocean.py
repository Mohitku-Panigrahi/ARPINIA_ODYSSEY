import pytest
from datetime import datetime, timezone, timedelta
import math
import numpy as np

from packages.geo.models import Point
from packages.metocean.models import WindVector, CurrentVector, MetOceanPoint
from packages.metocean.exceptions import (
    TemporalCoverageError, SpatialCoverageError, MissingDataError
)
from packages.metocean.era5 import ERA5Reader
from packages.metocean.cmems import CMEMSReader

def test_models_strictness():
    # Naive timestamp should fail
    with pytest.raises(ValueError, match="timezone-aware"):
        MetOceanPoint(point=Point(lat=0, lon=0), timestamp=datetime(2018, 8, 13))
        
    # Non-finite should fail
    with pytest.raises(ValueError, match="finite"):
        WindVector(u=float('inf'), v=1.0)

def test_era5_reader_metadata_and_coverage():
    reader = ERA5Reader('tests/fixtures/era5_fixture.nc')
    
    dt = datetime(2018, 8, 13, 16, 0, 0, tzinfo=timezone.utc)
    target = MetOceanPoint(point=Point(lat=33.5, lon=33.5), timestamp=dt)
    
    # Exact point in grid (lat 33.5, lon 33.5, time 16:00 is exactly in our fixture)
    wind = reader.get_wind(target)
    assert math.isclose(wind.u, 5.0)
    assert math.isclose(wind.v, -2.0)
    
    # Determinism
    wind2 = reader.get_wind(target)
    assert wind.u == wind2.u and wind.v == wind2.v
    
    # Interpolation point
    target_interp = MetOceanPoint(point=Point(lat=33.3, lon=33.7), timestamp=dt + timedelta(minutes=30))
    wind_interp = reader.get_wind(target_interp)
    assert math.isclose(wind_interp.u, 5.0)
    
    # Out of bounds time
    with pytest.raises(TemporalCoverageError):
        reader.get_wind(MetOceanPoint(point=Point(lat=33.5, lon=33.5), timestamp=dt - timedelta(days=1)))
        
    # Out of bounds space
    with pytest.raises(SpatialCoverageError):
        reader.get_wind(MetOceanPoint(point=Point(lat=35.0, lon=33.5), timestamp=dt))
        
    reader.close()

def test_cmems_reader_and_missing_data():
    reader = CMEMSReader('tests/fixtures/cmems_fixture.nc', target_depth_m=0.49)
    assert math.isclose(reader.actual_depth, 0.49, rel_tol=1e-5)
    
    dt = datetime(2018, 8, 13, 16, 0, 0, tzinfo=timezone.utc)
    target = MetOceanPoint(point=Point(lat=33.4, lon=33.5), timestamp=dt)
    
    current = reader.get_current(target)
    assert math.isclose(current.u, 0.5, rel_tol=1e-5)
    assert math.isclose(current.v, 0.1, rel_tol=1e-5)
    
    reader.close()

def test_golden_scenario_compatibility():
    # Golden Scenario bounds
    # 2018-08-13T15:44Z to 2018-08-15T15:44Z
    # Lon: 33.1 to 33.8
    # Lat: 33.2 to 33.7
    
    # Our fixture covers: 2018-08-13 15:00 to 17:00
    # Lon 33.1 to 33.9
    # Lat 33.1 to 33.7
    
    reader = ERA5Reader('tests/fixtures/era5_fixture.nc')
    
    # Inside the fixture
    t1 = datetime(2018, 8, 13, 15, 44, 0, tzinfo=timezone.utc)
    p1 = MetOceanPoint(point=Point(lat=33.3, lon=33.4), timestamp=t1)
    wind = reader.get_wind(p1)
    assert wind.u == 5.0
    
    # The fixture does NOT cover 2018-08-15 (intentionally, to test coverage failure if we ask for it)
    t_fail = datetime(2018, 8, 15, 15, 44, 0, tzinfo=timezone.utc)
    p_fail = MetOceanPoint(point=Point(lat=33.3, lon=33.4), timestamp=t_fail)
    with pytest.raises(TemporalCoverageError):
        reader.get_wind(p_fail)
        
    reader.close()
