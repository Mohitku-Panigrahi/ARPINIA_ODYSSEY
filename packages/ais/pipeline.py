import logging
from typing import List, Dict, Tuple
from packages.ais.models import AISObservation, VesselTrajectory, TrajectorySegment
from packages.geo.distance import calculate_distance
from packages.geo.models import Point

logger = logging.getLogger(__name__)

class AISPipeline:
    def __init__(self, max_interpolation_gap_seconds: float = 3600.0, max_speed_knots: float = 40.0):
        self.max_interpolation_gap_seconds = max_interpolation_gap_seconds
        self.max_speed_knots = max_speed_knots
        
    def clean_and_group(self, observations: List[AISObservation]) -> Dict[str, List[AISObservation]]:
        # 1. Filter out completely invalid records based on Pydantic (already done at ingest)
        # 2. Group by MMSI and sort by time
        grouped: Dict[str, List[AISObservation]] = {}
        for obs in observations:
            if obs.mmsi not in grouped:
                grouped[obs.mmsi] = []
            grouped[obs.mmsi].append(obs)
            
        for mmsi in grouped:
            grouped[mmsi].sort(key=lambda x: x.timestamp_utc)
            
            # Remove exact duplicates and impossible jumps
            cleaned = []
            for obs in grouped[mmsi]:
                if not cleaned:
                    cleaned.append(obs)
                    continue
                    
                prev_obs = cleaned[-1]
                dt = (obs.timestamp_utc - prev_obs.timestamp_utc).total_seconds()
                
                if dt == 0:
                    # Duplicate timestamp
                    obs.quality_flags.append("DUPLICATE")
                    continue
                    
                dist_m = calculate_distance(
                    Point(lat=prev_obs.latitude, lon=prev_obs.longitude),
                    Point(lat=obs.latitude, lon=obs.longitude)
                )
                speed_ms = dist_m / dt if dt > 0 else 0
                speed_knots = speed_ms * 1.94384
                
                if speed_knots > self.max_speed_knots:
                    obs.quality_flags.append("IMPOSSIBLE_SPEED")
                    continue
                    
                cleaned.append(obs)
                
            grouped[mmsi] = cleaned
            
        return grouped

    def build_trajectories(self, grouped_observations: Dict[str, List[AISObservation]]) -> List[VesselTrajectory]:
        trajectories = []
        for mmsi, obs_list in grouped_observations.items():
            if not obs_list:
                continue
                
            first_obs = obs_list[0]
            traj = VesselTrajectory(
                mmsi=mmsi,
                imo=first_obs.imo,
                vessel_name=first_obs.vessel_name,
                observations=obs_list,
                first_timestamp=first_obs.timestamp_utc,
                last_timestamp=obs_list[-1].timestamp_utc,
            )
            
            max_gap = 0.0
            for i in range(1, len(obs_list)):
                prev_obs = obs_list[i-1]
                curr_obs = obs_list[i]
                
                dt = (curr_obs.timestamp_utc - prev_obs.timestamp_utc).total_seconds()
                max_gap = max(max_gap, dt)
                
                dist_m = calculate_distance(
                    Point(lat=prev_obs.latitude, lon=prev_obs.longitude),
                    Point(lat=curr_obs.latitude, lon=curr_obs.longitude)
                )
                
                segment = TrajectorySegment(
                    start_obs=prev_obs,
                    end_obs=curr_obs,
                    duration_seconds=dt,
                    distance_meters=dist_m,
                    is_interpolated=(dt <= self.max_interpolation_gap_seconds),
                    interpolated_gap=(dt > self.max_interpolation_gap_seconds)
                )
                traj.segments.append(segment)
                
            traj.max_gap_seconds = max_gap
            if max_gap > self.max_interpolation_gap_seconds:
                traj.quality_flags.append("LOW_SAMPLING_DENSITY")
                
            trajectories.append(traj)
            
        return trajectories
