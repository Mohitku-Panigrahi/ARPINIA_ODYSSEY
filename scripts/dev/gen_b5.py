import json
import os
from datetime import datetime, timezone, timedelta
import numpy as np

# Load Odyssey Modules
from packages.geo.models import Point
from packages.ais.models import AISObservation, TrajectorySegment, VesselTrajectory
from packages.reconstruction.engine import ReconstructionEngine
from packages.ais.correlation import CorrelationEngine
from packages.attribution.config import AttributionConfig
from packages.attribution.scoring import AttributionEngine
import csv

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
    ais_path = 'data/raw/golden-scenario-v1/ais/synthetic_ais_tracks.csv'
    home_dir = os.path.expanduser('~')
    era5_path = os.path.join(home_dir, 'odyssey-data-test', 'era5_sih_zenodo_alpha_20180813_20180816.nc')
    cmems_path = os.path.join(home_dir, 'odyssey-data-test', 'cmems_sih_zenodo_alpha_20180813_20180816.nc')
    
    t0 = datetime(2018, 8, 15, 15, 44, 0, tzinfo=timezone.utc)
    origin_lat, origin_lon = 33.44, 33.388 # From SAR
    poly = [
        Point(lat=origin_lat-0.005, lon=origin_lon-0.005),
        Point(lat=origin_lat+0.005, lon=origin_lon-0.005),
        Point(lat=origin_lat+0.005, lon=origin_lon+0.005),
        Point(lat=origin_lat-0.005, lon=origin_lon+0.005)
    ]
    
    trajectories = parse_ais_csv(ais_path)
    
    config = {
        'particle_count': 100,
        'duration': timedelta(hours=48),
        'time_step': timedelta(hours=1),
        'random_seed': 42,
        'wind_uncertainty': 0.0,
        'current_uncertainty': 0.0
    }
    b3 = ReconstructionEngine(era5_path, cmems_path, config)
    b3_res = b3.run_backward(poly, t0)
    
    b4 = CorrelationEngine(b3_res['time_slices'])
    cands, _ = b4.correlate(trajectories)
    
    from packages.ais.models import B4Result
    b4_res_real = B4Result(
        scenario_id="SIH-ZENODO-ALPHA", ais_source="mock", source_mode="mock", raw_artifact_hash="hash",
        requested_time_window={}, requested_bbox={}, vessel_count=0, observation_count=0,
        candidate_count=len(cands), candidates=cands, excluded=[], warnings=[], limitations=[], provenance={}
    )
    
    b5 = AttributionEngine(AttributionConfig())
    b5_res = b5.score_candidates(b4_res_real, b3_res['time_slices'])
    
    with open('b5_output.json', 'w') as f:
        json.dump(b5_res.model_dump(), f, indent=2, default=str)
    
    print("B5 Output Generated")

if __name__ == '__main__':
    main()
