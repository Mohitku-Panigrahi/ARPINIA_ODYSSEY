import math
import numpy as np
from datetime import datetime, timezone
import cftime
from scipy.interpolate import RegularGridInterpolator

from packages.metocean.exceptions import (
    TemporalCoverageError,
    SpatialCoverageError,
    MissingDataError,
    InterpolationError
)

class GridInterpolator:
    """
    Handles spatial and temporal subsetting and trilinear interpolation
    (time, lat, lon) over rectilinear grids.
    """
    def __init__(self, times, lats, lons, values, fill_value=None):
        """
        times: 1D array of unix timestamps (seconds)
        lats: 1D array of latitudes (must be strictly ascending or descending)
        lons: 1D array of longitudes (strictly ascending)
        values: 3D array of values (time, lat, lon)
        fill_value: Value representing missing data
        """
        self.times = np.array(times)
        self.lats = np.array(lats)
        self.lons = np.array(lons)
        self.values = np.array(values)
        self.fill_value = fill_value
        
        # Check if arrays are empty
        if len(self.times) == 0 or len(self.lats) == 0 or len(self.lons) == 0:
            raise InterpolationError("One or more dimension arrays are empty.")
            
        # RegularGridInterpolator requires strictly ascending coordinates
        if self.lats[-1] < self.lats[0]:
            # Descending (like ERA5)
            self.lats = self.lats[::-1]
            self.values = self.values[:, ::-1, :]
            
        # Handle nan/fill_value before interpolation?
        # Actually, if we just want strictly no extrapolation and fail on missing:
        # If the interpolated cell contains NaN, the result is NaN. 
        # We will detect NaN after interpolation and raise MissingDataError.
        if self.fill_value is not None:
            # Replace fill_value with NaN to let scipy interpolate as NaN
            self.values = np.where(self.values == self.fill_value, np.nan, self.values)
            
        try:
            self.interpolator = RegularGridInterpolator(
                (self.times, self.lats, self.lons),
                self.values,
                method='linear',
                bounds_error=True,
                fill_value=None # bounds_error=True overrides this
            )
        except Exception as e:
            raise InterpolationError(f"Failed to build interpolator: {str(e)}")

    def get_value(self, target_time: float, target_lat: float, target_lon: float) -> float:
        """
        Interpolates the value at the given time, lat, lon.
        """
        try:
            val = self.interpolator((target_time, target_lat, target_lon))
        except ValueError as e:
            # SciPy raises ValueError on bounds error
            if "out of bounds" in str(e).lower():
                # Determine which dimension is out of bounds
                if target_time < self.times[0] or target_time > self.times[-1]:
                    raise TemporalCoverageError(f"Time {target_time} is outside coverage [{self.times[0]}, {self.times[-1]}]")
                else:
                    raise SpatialCoverageError(f"Point ({target_lat}, {target_lon}) is outside spatial coverage.")
            raise InterpolationError(str(e))
            
        # Extract scalar
        val = float(val)
        
        if math.isnan(val):
            raise MissingDataError(f"Missing data (NaN/fill) encountered at {target_lat}, {target_lon}, time {target_time}")
            
        return val
