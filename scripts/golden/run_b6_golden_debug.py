import os
import psutil
import time
import json
import hashlib
import numpy as np
import csv
import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', filename='b6_debug.log', filemode='w')

from packages.geo.models import Point
from packages.reconstruction.engine import ReconstructionEngine
from packages.ais.models import AISObservation, VesselTrajectory, TrajectorySegment
from packages.ais.correlation import CorrelationEngine
from packages.attribution.config import AttributionConfig
from packages.attribution.scoring import AttributionEngine
from packages.stability.config import MonteCarloConfig
from packages.stability.runner import StabilityRunner

def parse_ais_csv(csv_path):
    trajectories = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mmsi = row['MMSI']
            if mmsi not in trajectories:
                trajectories[mmsi] = []
            
            obs = AISObservation(
                source='CSV',
                mmsi=str(mmsi),
                timestamp_utc=datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00')),
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                sog_knots=float(row['SOG']) if row['SOG'] else None,
                cog_degrees=float(row['COG']) if row['COG'] else None,
                heading_degrees=float(row['heading']) if row['heading'] else None
            )
            trajectories[mmsi].append(obs)
            
    res = []
    for mmsi, obs_list in trajectories.items():
        obs_list.sort(key=lambda o: o.timestamp_utc)
        
        segments = []
        for i in range(len(obs_list)-1):
            o1, o2 = obs_list[i], obs_list[i+1]
            dt = (o2.timestamp_utc - o1.timestamp_utc).total_seconds()
            
            # basic haversine
            lat1, lon1 = np.radians(o1.latitude), np.radians(o1.longitude)
            lat2, lon2 = np.radians(o2.latitude), np.radians(o2.longitude)
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            r = 6371000
            dist = c * r
            
            segments.append(TrajectorySegment(
                start_obs=o1, end_obs=o2,
                duration_seconds=dt, distance_meters=dist,
                is_interpolated=False, interpolated_gap=(dt > 3600)
            ))
            
        res.append(VesselTrajectory(
            mmsi=str(mmsi),
            observations=obs_list,
            segments=segments,
            first_timestamp=obs_list[0].timestamp_utc,
            last_timestamp=obs_list[-1].timestamp_utc
        ))
    return res

def main():
    logging.info("Starting run...")
    sar_path = 'data/raw/golden-scenario-v1/sar/S1A_IW_GRDH_1SDV_20180815T154400.tif'
    ais_path = 'data/raw/golden-scenario-v1/ais/synthetic_ais_tracks.csv'
    home_dir = os.path.expanduser('~')
    era5_path = os.path.join(home_dir, 'odyssey-data-test', 'era5_sih_zenodo_alpha_20180813_20180816.nc')
    cmems_path = os.path.join(home_dir, 'odyssey-data-test', 'cmems_sih_zenodo_alpha_20180813_20180816.nc')
    
    t0 = datetime(2018, 8, 15, 15, 44, 0, tzinfo=timezone.utc)
    
    origin_lat, origin_lon = 33.44, 33.388
    poly = [
        Point(lat=origin_lat-0.005, lon=origin_lon-0.005),
        Point(lat=origin_lat+0.005, lon=origin_lon-0.005),
        Point(lat=origin_lat+0.005, lon=origin_lon+0.005),
        Point(lat=origin_lat-0.005, lon=origin_lon+0.005)
    ]
    
    trajectories = parse_ais_csv(ais_path)
    
    def b3_factory(config):
        return ReconstructionEngine(era5_path, cmems_path, config)
        
    base_b3_config = {
        'particle_count': 100,
        'duration': timedelta(hours=48),
        'time_step': timedelta(hours=1),
    }
    
    mc_config = MonteCarloConfig(
        maximum_runs=25,
        convergence_patience=2,
        convergence_check_interval=25,
        wind_uncertainty_std=2.0,
        current_uncertainty_std=0.1,
        time_perturbation_std=3600
    )
    
    runner = StabilityRunner(mc_config, b3_factory, base_b3_config, trajectories, AttributionConfig(), "SIH-ZENODO-ALPHA")
    
    logging.info("Starting ensemble...")
    t_start = time.perf_counter()
    b6_res = runner.run_ensemble(t0, poly)
    t_end = time.perf_counter()
    logging.info("Ensemble done!")
    
    results = b6_res.model_dump()
    with open('b6_real_golden_output.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logging.info("Done!")

if __name__ == '__main__':
    main()
