import netCDF4 as nc
import numpy as np
import cftime
from datetime import datetime, timezone

from packages.metocean.exceptions import (
    InvalidDatasetError,
    MissingVariableError,
    UnsupportedUnitError
)
from packages.metocean.interpolation import GridInterpolator
from packages.metocean.models import WindVector, MetOceanPoint

class ERA5Reader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        try:
            self.ds = nc.Dataset(filepath, 'r')
        except OSError:
            raise InvalidDatasetError(f"Could not open ERA5 dataset at {filepath}")
            
        self._validate_variables()
        self._load_coordinates()
        
        # Build interpolators lazily or eagerly depending on size.
        # For B2, we assume the dataset is already subset for the Golden Scenario
        # (or we load the whole grid if small enough).
        u10_var = self.ds.variables['u10']
        v10_var = self.ds.variables['v10']
        
        fill_u = getattr(u10_var, '_FillValue', getattr(u10_var, 'missing_value', None))
        fill_v = getattr(v10_var, '_FillValue', getattr(v10_var, 'missing_value', None))
        
        self.u_interpolator = GridInterpolator(
            self.times_sec, self.lats, self.lons, u10_var[:], fill_value=fill_u
        )
        self.v_interpolator = GridInterpolator(
            self.times_sec, self.lats, self.lons, v10_var[:], fill_value=fill_v
        )

    def _validate_variables(self):
        self.time_var_name = 'valid_time' if 'valid_time' in self.ds.variables else 'time'
        required = ['longitude', 'latitude', self.time_var_name, 'u10', 'v10']
        for req in required:
            if req not in self.ds.variables:
                raise MissingVariableError(f"Required variable '{req}' missing from ERA5 dataset.")
                
        # Validate units
        if 'm s**-1' not in getattr(self.ds.variables['u10'], 'units', '') and \
           'm/s' not in getattr(self.ds.variables['u10'], 'units', ''):
            raise UnsupportedUnitError(f"Unsupported u10 units: {getattr(self.ds.variables['u10'], 'units', 'None')}")

    def _load_coordinates(self):
        self.lons = self.ds.variables['longitude'][:]
        self.lats = self.ds.variables['latitude'][:]
        
        time_var = self.ds.variables[self.time_var_name]
        # Convert cftime to unix timestamps
        cf_times = cftime.num2date(time_var[:], units=time_var.units, calendar=getattr(time_var, 'calendar', 'standard'))
        # Ensure all are converted to standard unix timestamps (seconds since epoch)
        self.times_sec = np.array([
            datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo=timezone.utc).timestamp() 
            for t in cf_times
        ])

    def get_wind(self, target: MetOceanPoint) -> WindVector:
        """Get the interpolated wind vector at the specified point and time."""
        lon = target.point.lon
        # Normalize longitude if dataset is 0..360
        if self.lons.max() > 180 and lon < 0:
            lon += 360.0
            
        target_sec = target.timestamp.timestamp()
        
        u = self.u_interpolator.get_value(target_sec, target.point.lat, lon)
        v = self.v_interpolator.get_value(target_sec, target.point.lat, lon)
        
        return WindVector(u=u, v=v)

    def close(self):
        if self.ds:
            self.ds.close()
