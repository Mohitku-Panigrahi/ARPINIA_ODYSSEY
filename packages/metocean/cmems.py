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
from packages.metocean.models import CurrentVector, MetOceanPoint

class CMEMSReader:
    def __init__(self, filepath: str, target_depth_m: float = 0.49):
        self.filepath = filepath
        self.target_depth_m = target_depth_m
        try:
            self.ds = nc.Dataset(filepath, 'r')
        except OSError:
            raise InvalidDatasetError(f"Could not open CMEMS dataset at {filepath}")
            
        self._validate_variables()
        self._load_coordinates()
        
        # Select depth index closest to target_depth_m
        depths = self.ds.variables['depth'][:]
        self.depth_idx = np.argmin(np.abs(depths - self.target_depth_m))
        self.actual_depth = depths[self.depth_idx]
        
        # Extract variables at the selected depth
        uo_var = self.ds.variables['uo']
        vo_var = self.ds.variables['vo']
        
        # Determine dimension mapping. Usually (time, depth, lat, lon)
        # We need to slice at depth_idx
        dims = uo_var.dimensions
        if 'depth' in dims:
            depth_dim_idx = dims.index('depth')
            if depth_dim_idx == 1:
                uo_data = uo_var[:, self.depth_idx, :, :]
                vo_data = vo_var[:, self.depth_idx, :, :]
            else:
                raise InvalidDatasetError("Unsupported CMEMS dimension ordering.")
        else:
            uo_data = uo_var[:]
            vo_data = vo_var[:]
        
        fill_u = getattr(uo_var, '_FillValue', getattr(uo_var, 'missing_value', None))
        fill_v = getattr(vo_var, '_FillValue', getattr(vo_var, 'missing_value', None))
        
        self.u_interpolator = GridInterpolator(
            self.times_sec, self.lats, self.lons, uo_data, fill_value=fill_u
        )
        self.v_interpolator = GridInterpolator(
            self.times_sec, self.lats, self.lons, vo_data, fill_value=fill_v
        )

    def _validate_variables(self):
        required = ['longitude', 'latitude', 'time', 'uo', 'vo']
        for req in required:
            if req not in self.ds.variables:
                raise MissingVariableError(f"Required variable '{req}' missing from CMEMS dataset.")
                
        # Validate units
        units_uo = getattr(self.ds.variables['uo'], 'units', '')
        if 'm s-1' not in units_uo and 'm/s' not in units_uo and 'm s**-1' not in units_uo:
            raise UnsupportedUnitError(f"Unsupported uo units: {units_uo}")

    def _load_coordinates(self):
        self.lons = self.ds.variables['longitude'][:]
        self.lats = self.ds.variables['latitude'][:]
        
        time_var = self.ds.variables['time']
        cf_times = cftime.num2date(time_var[:], units=time_var.units, calendar=getattr(time_var, 'calendar', 'standard'))
        self.times_sec = np.array([
            datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo=timezone.utc).timestamp() 
            for t in cf_times
        ])

    def get_current(self, target: MetOceanPoint) -> CurrentVector:
        """Get the interpolated surface current vector at the specified point and time."""
        lon = target.point.lon
        # Normalize longitude if dataset is 0..360
        if self.lons.max() > 180 and lon < 0:
            lon += 360.0
            
        target_sec = target.timestamp.timestamp()
        
        u = self.u_interpolator.get_value(target_sec, target.point.lat, lon)
        v = self.v_interpolator.get_value(target_sec, target.point.lat, lon)
        
        return CurrentVector(u=u, v=v)

    def close(self):
        if self.ds:
            self.ds.close()
