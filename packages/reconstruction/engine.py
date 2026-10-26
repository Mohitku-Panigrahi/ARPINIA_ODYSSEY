import os
import logging
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_netCDF_CF_generic
from packages.geo.models import Point
from packages.reconstruction.probability import ProbabilityFieldGenerator

logger = logging.getLogger(__name__)

class ReconstructionEngine:
    def __init__(self, era5_path: str, cmems_path: str, config: dict):
        self.era5_path = era5_path
        self.cmems_path = cmems_path
        self.config = config

    def run_backward(self, seed_polygon: List[Point], t0: datetime) -> Dict[str, Any]:
        np.random.seed(self.config.get('random_seed', 42))
        
        o = OceanDrift(loglevel=30)
        
        reader_era5 = reader_netCDF_CF_generic.Reader(self.era5_path)
        import xarray as xr
        
        # B3 Repair: Adapt CMEMS uo/vo to OpenDrift expected semantics without mutating file
        ds_cmems = xr.open_dataset(self.cmems_path)
        
        # Isolate the surface layer expected by Golden physics
        if 'depth' in ds_cmems.dims:
            ds_cmems = ds_cmems.sel(depth=0.494025, method='nearest')
            
        rename_dict = {}
        if 'uo' in ds_cmems.variables:
            rename_dict['uo'] = 'x_sea_water_velocity'
        if 'vo' in ds_cmems.variables:
            rename_dict['vo'] = 'y_sea_water_velocity'
            
        if rename_dict:
            ds_cmems = ds_cmems.rename(rename_dict)
            
        # Ensure units are explicit to prevent OpenDrift fallback
        if 'x_sea_water_velocity' in ds_cmems.variables:
            ds_cmems['x_sea_water_velocity'].attrs['units'] = 'm/s'
            ds_cmems['x_sea_water_velocity'].attrs['standard_name'] = 'x_sea_water_velocity'
        if 'y_sea_water_velocity' in ds_cmems.variables:
            ds_cmems['y_sea_water_velocity'].attrs['units'] = 'm/s'
            ds_cmems['y_sea_water_velocity'].attrs['standard_name'] = 'y_sea_water_velocity'
            
        reader_cmems = reader_netCDF_CF_generic.Reader(ds_cmems)
        o.add_reader([reader_era5, reader_cmems])
        
        o.set_config('environment:fallback:x_wind', None)
        o.set_config('environment:fallback:y_wind', None)
        o.set_config('environment:fallback:x_sea_water_velocity', None)
        o.set_config('environment:fallback:y_sea_water_velocity', None)
        
        o.set_config('drift:wind_uncertainty', self.config.get('wind_uncertainty', 0.0))
        o.set_config('drift:current_uncertainty', self.config.get('current_uncertainty', 0.0))

        lons = [p.lon for p in seed_polygon]
        lats = [p.lat for p in seed_polygon]
        
        if t0.tzinfo is None:
            raise ValueError("t0 must be a timezone-aware datetime")
            
        t0_naive = t0.astimezone(timezone.utc).replace(tzinfo=None)
            
        o.seed_within_polygon(
            lons=lons, lats=lats,
            number=self.config.get('particle_count', 1000),
            time=t0_naive
        )
        
        duration = self.config.get('duration', timedelta(hours=48))
        time_step = self.config.get('time_step', timedelta(hours=1))
        
        try:
            o.run(
                duration=duration,
                time_step=-time_step,
                time_step_output=time_step
            )
        except ValueError as e:
            if "Simulation stopped within first timestep" in str(e):
                logger.warning(f"OpenDrift aborted in first timestep (likely out of bounds or missing forcing). {e}")
                raise ValueError("REQUIRED_FORCING_UNAVAILABLE: OpenDrift aborted in first timestep (likely out of bounds or missing forcing).") from e
            else:
                raise
                
        # OpenDrift 1.14 stores results in o.result
        lons_hist = np.array(o.result.lon).T
        lats_hist = np.array(o.result.lat).T
        
        num_timesteps = lons_hist.shape[1]
        expected_timesteps = int(duration.total_seconds() / time_step.total_seconds()) + 1
        if num_timesteps < expected_timesteps:
            raise ValueError(f"REQUIRED_FORCING_UNAVAILABLE: Simulation aborted early. Expected {expected_timesteps} timesteps, got {num_timesteps}.")
        
        num_timesteps = lons_hist.shape[1]
        
        lon_min, lon_max = np.nanmin(lons_hist) - 0.1, np.nanmax(lons_hist) + 0.1
        lat_min, lat_max = np.nanmin(lats_hist) - 0.1, np.nanmax(lats_hist) + 0.1
        
        prob_gen = ProbabilityFieldGenerator(lon_min, lon_max, lat_min, lat_max)
        
        time_slices = []
        for i in range(num_timesteps):
            t_slice = t0 - i * time_step
            lons_slice = lons_hist[:, i]
            lats_slice = lats_hist[:, i]
            
            valid = ~np.isnan(lons_slice)
            lons_valid = lons_slice[valid]
            lats_valid = lats_slice[valid]
            
            total_particles = len(lons_slice)
            valid_count = len(lons_valid)
            invalid_count = total_particles - valid_count
            valid_fraction = valid_count / total_particles if total_particles > 0 else 0.0
            
            if valid_count == 0:
                continue
                
            prob_data = prob_gen.generate(lons_valid, lats_valid)
            
            time_slices.append({
                "timestamp": t_slice,
                "total_particle_count": total_particles,
                "active_valid_particle_count": valid_count,
                "invalid_particle_count": invalid_count,
                "valid_particle_fraction": valid_fraction,
                "probability_data": prob_data
            })
            
        return {
            "scenario_id": self.config.get("scenario_id", "unknown"),
            "observation_time": t0,
            "hindcast_start": t0,
            "hindcast_end": t0 - duration,
            "model": "OceanDrift",
            "model_version": getattr(o, 'version', 'unknown'),
            "particle_count": self.config.get('particle_count', 1000),
            "random_seed": self.config.get('random_seed', 42),
            "timestep": time_step.total_seconds(),
            "time_slices": time_slices
        }
