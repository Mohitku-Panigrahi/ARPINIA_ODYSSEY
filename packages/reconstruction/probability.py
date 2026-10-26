import numpy as np
from typing import List, Dict, Any, Tuple
from packages.geo.models import Point

class ProbabilityFieldGenerator:
    def __init__(self, lon_min: float, lon_max: float, lat_min: float, lat_max: float, resolution: float = 0.01):
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.resolution = resolution
        
        self.lon_bins = np.arange(lon_min, lon_max + resolution, resolution)
        self.lat_bins = np.arange(lat_min, lat_max + resolution, resolution)

    def generate(self, lons: np.ndarray, lats: np.ndarray) -> Dict[str, Any]:
        H, xedges, yedges = np.histogram2d(lons, lats, bins=(self.lon_bins, self.lat_bins))
        
        total_particles = np.sum(H)
        if total_particles == 0:
            return {"status": "empty"}
            
        prob_grid = H / total_particles
        
        sorted_probs = np.sort(prob_grid.flatten())[::-1]
        cumulative_probs = np.cumsum(sorted_probs)
        
        def get_threshold(target: float) -> float:
            idx = np.searchsorted(cumulative_probs, target)
            if idx >= len(sorted_probs):
                return 0.0
            return sorted_probs[idx]
            
        threshold_50 = get_threshold(0.50)
        threshold_80 = get_threshold(0.80)
        threshold_95 = get_threshold(0.95)
        
        lon_centers = (xedges[:-1] + xedges[1:]) / 2
        lat_centers = (yedges[:-1] + yedges[1:]) / 2
        
        LON, LAT = np.meshgrid(lon_centers, lat_centers, indexing='ij')
        centroid_lon = np.average(LON, weights=prob_grid)
        centroid_lat = np.average(LAT, weights=prob_grid)

        return {
            "status": "success",
            "grid": prob_grid,
            "lon_bins": self.lon_bins,
            "lat_bins": self.lat_bins,
            "centroid": Point(lon=float(centroid_lon), lat=float(centroid_lat)),
            "thresholds": {
                "50": float(threshold_50),
                "80": float(threshold_80),
                "95": float(threshold_95)
            }
        }
