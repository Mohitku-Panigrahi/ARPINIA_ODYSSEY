import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta
from packages.geo import Point, calculate_distance
from packages.ais.models import (
    VesselTrajectory, CandidateVessel, ExcludedVessel, GapAnalysis,
    AnalyticalResult, FeatureAvailability
)

class CorrelationEngine:
    def __init__(self, time_slices: List[dict], max_interpolation_gap_seconds: float = 3600.0, max_reachability_speed_knots: float = 25.0):
        self.time_slices = time_slices
        self.max_gap = max_interpolation_gap_seconds
        self.max_reach_speed = max_reachability_speed_knots
        
    def _interpolate_segment(self, lat1, lon1, lat2, lon2, num_points=20):
        lats = np.linspace(lat1, lat2, num_points)
        lons = np.linspace(lon1, lon2, num_points)
        return lats, lons
        
    def _check_grid_intersection(self, lats, lons, prob_data) -> List[str]:
        grid = prob_data['grid']
        xbins = prob_data['lon_bins']
        ybins = prob_data['lat_bins']
        
        t50 = prob_data['thresholds'].get('50', 1.0)
        t80 = prob_data['thresholds'].get('80', 1.0)
        t95 = prob_data['thresholds'].get('95', 1.0)
        
        intersections = set()
        
        for lat, lon in zip(lats, lons):
            if not (xbins[0] <= lon <= xbins[-1] and ybins[0] <= lat <= ybins[-1]):
                continue
            
            x_idx = np.searchsorted(xbins, lon) - 1
            y_idx = np.searchsorted(ybins, lat) - 1
            
            x_idx = max(0, min(x_idx, len(xbins) - 2))
            y_idx = max(0, min(y_idx, len(ybins) - 2))
            
            val = grid[y_idx, x_idx]
            
            if val >= t50:
                intersections.add("50")
            elif val >= t80:
                intersections.add("80")
            elif val >= t95:
                intersections.add("95")
                
        if "50" in intersections:
            intersections.update(["80", "95"])
        elif "80" in intersections:
            intersections.add("95")
            
        return sorted(list(intersections))

    def correlate(self, trajectories: List[VesselTrajectory]) -> Tuple[List[CandidateVessel], List[ExcludedVessel]]:
        candidates = []
        excluded = []
        
        for traj in trajectories:
            candidate_reasons = set()
            region_ints = set()
            gap_analysis_list = []
            min_dist = float('inf')
            min_time = None
            has_time_overlap = False
            
            for seg in traj.segments:
                t_start = seg.start_obs.timestamp_utc
                t_end = seg.end_obs.timestamp_utc
                
                for t_slice in self.time_slices:
                    slice_time = t_slice['timestamp']
                    if t_start - timedelta(hours=1) <= slice_time <= t_end + timedelta(hours=1):
                        has_time_overlap = True
                        prob_data = t_slice['probability_data']
                        
                        if seg.is_interpolated:
                            lats, lons = self._interpolate_segment(seg.start_obs.latitude, seg.start_obs.longitude, seg.end_obs.latitude, seg.end_obs.longitude)
                            ints = self._check_grid_intersection(lats, lons, prob_data)
                            if ints:
                                candidate_reasons.add("SEGMENT_INTERSECTS_ORIGIN")
                                region_ints.update(ints)
                        else:
                            dt = (slice_time - seg.start_obs.timestamp_utc).total_seconds()
                            if 0 < dt < seg.duration_seconds:
                                max_reach_m = dt * (self.max_reach_speed * 0.514444)
                                centroid = prob_data['centroid']
                                dist_to_centroid = calculate_distance(
                                    Point(lat=seg.start_obs.latitude, lon=seg.start_obs.longitude),
                                    centroid
                                )
                                if dist_to_centroid <= max_reach_m + 10000:
                                    candidate_reasons.add("KINEMATICALLY_REACHABLE_DURING_GAP")
                                    gap_analysis_list.append(GapAnalysis(
                                        start_time=seg.start_obs.timestamp_utc,
                                        end_time=seg.end_obs.timestamp_utc,
                                        duration_seconds=seg.duration_seconds,
                                        start_lat=seg.start_obs.latitude,
                                        start_lon=seg.start_obs.longitude,
                                        end_lat=seg.end_obs.latitude,
                                        end_lon=seg.end_obs.longitude,
                                        status="KINEMATICALLY_PLAUSIBLE_UNOBSERVED_TRANSIT"
                                    ))
                                else:
                                    gap_analysis_list.append(GapAnalysis(
                                        start_time=seg.start_obs.timestamp_utc,
                                        end_time=seg.end_obs.timestamp_utc,
                                        duration_seconds=seg.duration_seconds,
                                        start_lat=seg.start_obs.latitude,
                                        start_lon=seg.start_obs.longitude,
                                        end_lat=seg.end_obs.latitude,
                                        end_lon=seg.end_obs.longitude,
                                        status="KINEMATICALLY_IMPLAUSIBLE_TRANSIT"
                                    ))
                        
                        for obs in [seg.start_obs, seg.end_obs]:
                            dt_obs = abs((obs.timestamp_utc - slice_time).total_seconds())
                            if dt_obs <= 3600:
                                centroid = prob_data['centroid']
                                dist_to_centroid = calculate_distance(
                                    Point(lat=obs.latitude, lon=obs.longitude),
                                    centroid
                                ) / 1000.0
                                
                                if dist_to_centroid < min_dist:
                                    min_dist = dist_to_centroid
                                    min_time = obs.timestamp_utc
            
            if min_dist < 5.0:
                candidate_reasons.add("CLOSEST_APPROACH_WITHIN_THRESHOLD")
                
            features = FeatureAvailability(
                spatial_overlap=len(region_ints) > 0,
                temporal_match=has_time_overlap,
                closest_approach=min_dist != float('inf'),
                ais_continuity=traj.max_gap_seconds < self.max_gap,
                heading_alignment=False,
                behavior_signal=False
            )
            
            ca_km_res = AnalyticalResult[float](value=min_dist, status="AVAILABLE") if min_dist != float('inf') else AnalyticalResult[float](value=None, status="NOT_APPLICABLE", reason="NO_TEMPORALLY_OVERLAPPING_SEGMENT")
            ca_time_res = AnalyticalResult[str](value=min_time.isoformat() if min_time else None, status="AVAILABLE" if min_time else "NOT_APPLICABLE", reason=None if min_time else "NO_TEMPORALLY_OVERLAPPING_SEGMENT")
            
            if not self.time_slices:
                int_50 = AnalyticalResult[bool](value=None, status="UNAVAILABLE", reason="NO_B3_TIME_SLICES")
                int_80 = AnalyticalResult[bool](value=None, status="UNAVAILABLE", reason="NO_B3_TIME_SLICES")
                int_95 = AnalyticalResult[bool](value=None, status="UNAVAILABLE", reason="NO_B3_TIME_SLICES")
                time_inside = AnalyticalResult[float](value=None, status="UNAVAILABLE", reason="NO_B3_TIME_SLICES")
            elif not has_time_overlap:
                int_50 = AnalyticalResult[bool](value=False, status="NOT_APPLICABLE", reason="OUTSIDE_TIME_WINDOW")
                int_80 = AnalyticalResult[bool](value=False, status="NOT_APPLICABLE", reason="OUTSIDE_TIME_WINDOW")
                int_95 = AnalyticalResult[bool](value=False, status="NOT_APPLICABLE", reason="OUTSIDE_TIME_WINDOW")
                time_inside = AnalyticalResult[float](value=0.0, status="NOT_APPLICABLE", reason="OUTSIDE_TIME_WINDOW")
            else:
                int_50 = AnalyticalResult[bool](value="50" in region_ints, status="AVAILABLE")
                int_80 = AnalyticalResult[bool](value="80" in region_ints, status="AVAILABLE")
                int_95 = AnalyticalResult[bool](value="95" in region_ints, status="AVAILABLE")
                time_inside = AnalyticalResult[float](value=None, status="NOT_COMPUTABLE", reason="INSUFFICIENT_OBSERVATIONS_FOR_INTEGRAL")
                
            if candidate_reasons:
                candidates.append(CandidateVessel(
                    mmsi=traj.mmsi,
                    imo=traj.imo,
                    vessel_name=traj.vessel_name,
                    trajectory_quality={"max_gap_seconds": traj.max_gap_seconds, "flags": len(traj.quality_flags)},
                    observed_intersections=[],
                    segment_intersections=list(region_ints),
                    probability_region_intersections=list(region_ints),
                    closest_approach_km=ca_km_res,
                    closest_approach_time=ca_time_res,
                    intersects_50_region=int_50,
                    intersects_80_region=int_80,
                    intersects_95_region=int_95,
                    time_inside_region_seconds=time_inside,
                    gap_analysis=gap_analysis_list,
                    candidate_reasons=list(candidate_reasons),
                    features_available=features
                ))
            else:
                excluded.append(ExcludedVessel(
                    mmsi=traj.mmsi,
                    exclusion_reasons=["NO_ORIGIN_REGION_INTERSECTION", "KINEMATICALLY_UNREACHABLE"],
                    features_available=features
                ))
                
        return candidates, excluded
