import os
import psutil
import time
import json
import hashlib
import numpy as np
import csv
from datetime import datetime, timezone, timedelta

from packages.geo.models import Point
from packages.reconstruction.engine import ReconstructionEngine
from packages.ais.models import AISObservation, VesselTrajectory, TrajectorySegment
from packages.ais.correlation import CorrelationEngine
from packages.attribution.config import AttributionConfig
from packages.attribution.scoring import AttributionEngine
from packages.stability.config import MonteCarloConfig
from packages.stability.runner import StabilityRunner

def get_memory_rss():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def hash_file(filepath):
    if not os.path.exists(filepath):
        return None
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

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
            
            # basic haversine for distance
            lat1, lon1 = np.radians(o1.latitude), np.radians(o1.longitude)
            lat2, lon2 = np.radians(o2.latitude), np.radians(o2.longitude)
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            r = 6371000 # radius of earth in meters
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
    rss_start = get_memory_rss()
    results = {}
    
    # 1. HASHES
    sar_path = 'data/raw/golden-scenario-v1/sar/S1A_IW_GRDH_1SDV_20180815T154400.tif'
    ais_path = 'data/raw/golden-scenario-v1/ais/synthetic_ais_tracks.csv'
    home_dir = os.path.expanduser('~')
    era5_path = os.path.join(home_dir, 'odyssey-data-test', 'era5_sih_zenodo_alpha_20180813_20180816.nc')
    cmems_path = os.path.join(home_dir, 'odyssey-data-test', 'cmems_sih_zenodo_alpha_20180813_20180816.nc')
    
    results['hashes'] = {
        'sar': hash_file(sar_path),
        'ais': hash_file(ais_path),
        'era5': hash_file(era5_path),
        'cmems': hash_file(cmems_path)
    }

    t0 = datetime(2018, 8, 15, 15, 44, 0, tzinfo=timezone.utc)
    
    origin_lat, origin_lon = 33.44, 33.388 # From SAR
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
        
    # PREFLIGHT & REPRODUCIBILITY
    def run_pipeline(seed, wind_unc, cur_unc):
        conf = dict(base_b3_config)
        conf['random_seed'] = seed
        conf['wind_uncertainty'] = wind_unc
        conf['current_uncertainty'] = cur_unc
        
        b3 = b3_factory(conf)
        b3_res = b3.run_backward(poly, t0)
        
        if not b3_res['time_slices']:
            return None
            
        b4 = CorrelationEngine(b3_res['time_slices'])
        cands, _ = b4.correlate(trajectories)
        
        from packages.ais.models import B4Result
        b4_res_real = B4Result(
            scenario_id="mock", ais_source="mock", source_mode="mock", raw_artifact_hash=None,
            requested_time_window={}, requested_bbox={}, vessel_count=0, observation_count=0,
            candidate_count=len(cands), candidates=cands, excluded=[], warnings=[], limitations=[], provenance={}
        )
        
        b5 = AttributionEngine(AttributionConfig())
        b5_res = b5.score_candidates(b4_res_real, b3_res['time_slices'])
        return {
            'b3_grid': b3_res['time_slices'][0]['probability_data']['grid'],
            'b4_cands': cands,
            'b5_res': b5_res
        }

    print("Running same-seed reproducibility...")
    rep1 = run_pipeline(42, 2.0, 0.1)
    rep2 = run_pipeline(42, 2.0, 0.1)
    same_seed_pass = np.allclose(rep1['b3_grid'], rep2['b3_grid']) if rep1 and rep2 else False
    
    print("Running diff-seed sensitivity...")
    rep3 = run_pipeline(99, 2.0, 0.1)
    diff_seed_pass = not np.allclose(rep1['b3_grid'], rep3['b3_grid']) if rep1 and rep3 else False
    
    print("Running zero-uncertainty...")
    z1 = run_pipeline(100, 0.0, 0.0)
    z2 = run_pipeline(101, 0.0, 0.0)
    zero_unc_pass = np.allclose(z1['b3_grid'], z2['b3_grid']) if z1 and z2 else False
    
    results['reproducibility'] = {
        'same_seed': same_seed_pass,
        'diff_seed': diff_seed_pass,
        'zero_unc': zero_unc_pass
    }
    
    # ENSEMBLE
    mc_config = MonteCarloConfig(
        maximum_runs=25,
        convergence_patience=2,
        convergence_check_interval=25,
        wind_uncertainty_std=2.0,
        current_uncertainty_std=0.1,
        time_perturbation_std=3600
    )
    
    runner = StabilityRunner(mc_config, b3_factory, base_b3_config, trajectories, AttributionConfig(), "SIH-ZENODO-ALPHA")
    
    t_start = time.perf_counter()
    b6_res = runner.run_ensemble(t0, poly)
    t_end = time.perf_counter()
    
    rss_end = get_memory_rss()
    
    results['ensemble'] = b6_res.model_dump() if hasattr(b6_res, 'model_dump') else b6_res
    
    # Get metrics safely avoiding KeyErrors
    def safe_mean(key):
        return np.mean(runner.runtimes[key]) if hasattr(runner, 'runtimes') and key in runner.runtimes and runner.runtimes[key] else 0
    def safe_p50(key):
        return np.median(runner.runtimes[key]) if hasattr(runner, 'runtimes') and key in runner.runtimes and runner.runtimes[key] else 0
    def safe_p95(key):
        return np.percentile(runner.runtimes[key], 95) if hasattr(runner, 'runtimes') and key in runner.runtimes and runner.runtimes[key] else 0
        
    results['metrics'] = {
        'total_time': t_end - t_start,
        'rss_start': rss_start,
        'rss_end': rss_end,
        'b3_mean_time': safe_mean('b3'),
        'b3_p50_time': safe_p50('b3'),
        'b3_p95_time': safe_p95('b3'),
        'b4_mean_time': safe_mean('b4'),
        'b5_mean_time': safe_mean('b5'),
    }
    
    with open('b6_real_golden_output.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("Done! Results in b6_real_golden_output.json")

if __name__ == '__main__':
    main()
