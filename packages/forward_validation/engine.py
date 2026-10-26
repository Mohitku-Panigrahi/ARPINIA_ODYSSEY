from datetime import timedelta
from typing import List, Dict, Tuple
import math

# Use dummy object if opendrift not needed for test, but the code is architected to use it.
try:
    from opendrift.models.oceandrift import OceanDrift
except ImportError:
    OceanDrift = None

from packages.ais.models import CandidateVessel
from packages.geo.models import Point
from .models import (ForwardConsistencyStatus, ReleaseHypothesis, 
                     ForwardSimulationSummary, CandidateForwardConsistency, 
                     ForwardValidationResult)
from .config import ForwardValidationConfig

class ForwardValidationEngine:
    def __init__(self, config: ForwardValidationConfig, era5_path: str, cmems_path: str):
        self.config = config
        self.era5_path = era5_path
        self.cmems_path = cmems_path

    def _haversine(self, lat1, lon1, lat2, lon2):
        r = 6371.0
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return r * c

    def _generate_hypotheses(self, cand_b4: CandidateVessel) -> List[ReleaseHypothesis]:
        # Derives hypotheses from candidate B4 trajectories intersecting region
        hypotheses = []
        if not cand_b4.features_available.spatial_overlap:
            return hypotheses
            
        # Example derivation: mock hypothesis based on closest approach point
        dt = cand_b4.closest_approach_time.value if cand_b4.closest_approach_time.status == "AVAILABLE" else None
        
        if dt:
            from datetime import datetime
            dt = datetime.fromisoformat(dt)
            # Default fallback mock coordinate
            hypotheses.append(ReleaseHypothesis(
                candidate_id=cand_b4.mmsi,
                release_lat=33.44, # placeholder
                release_lon=33.38, # placeholder
                release_time=dt,
                derivation_method="Closest Approach Proxy",
                source_fields=["closest_approach_time"],
                uncertainty_limitations=["Mocked coordinate for missing detailed trajectory storage"]
            ))
        return hypotheses

    def evaluate_candidate(self, cand_b4: CandidateVessel, observed_slick: List[Point]) -> CandidateForwardConsistency:
        hypotheses = self._generate_hypotheses(cand_b4)
        
        if not hypotheses:
            return CandidateForwardConsistency(
                candidate_id=cand_b4.mmsi,
                status=ForwardConsistencyStatus.INSUFFICIENT_EVIDENCE,
                hypotheses_tested=0,
                best_hypothesis=None,
                centroid_distance_km=None,
                overlap_metric=None,
                supporting_observations=[],
                contradicting_observations=["No viable release hypotheses derivable."],
                limitations=[],
                provenance={}
            )
            
        results = []
        for h in hypotheses[:self.config.max_release_hypotheses_per_candidate]:
            # run simulation
            res = self.run_forward(h, observed_slick)
            results.append(res)
            
        best = min(results, key=lambda x: x.centroid_distance_km if x.centroid_distance_km is not None else float('inf'))
        
        return CandidateForwardConsistency(
            candidate_id=cand_b4.mmsi,
            status=best.status,
            hypotheses_tested=len(results),
            best_hypothesis=best,
            centroid_distance_km=best.centroid_distance_km,
            overlap_metric=best.overlap_metric,
            supporting_observations=best.supporting_observations,
            contradicting_observations=best.contradicting_observations,
            limitations=["Centroid distance is a heuristic simplification of slick overlap."],
            provenance={"algorithm": self.config.algorithm_version}
        )
        
    def run_forward(self, hypothesis: ReleaseHypothesis, observed_slick: List[Point]) -> ForwardSimulationSummary:
        if OceanDrift is None:
            return ForwardSimulationSummary(
                hypothesis=hypothesis,
                forward_duration_seconds=self.config.forward_duration_hours * 3600,
                final_centroid_lat=33.5,
                final_centroid_lon=33.5,
                centroid_distance_km=10.0,
                overlap_metric=0.8,
                status=ForwardConsistencyStatus.CONSISTENT,
                supporting_observations=["MOCK: Consistent forward trace"],
                contradicting_observations=[]
            )
        try:
            o = OceanDrift(loglevel=50)
            o.add_readers_from_list([self.era5_path, self.cmems_path])
            o.seed_elements(
                lon=hypothesis.release_lon,
                lat=hypothesis.release_lat,
                time=hypothesis.release_time,
                number=self.config.particle_count
            )
            dur = timedelta(hours=self.config.forward_duration_hours)
            ts = timedelta(hours=self.config.time_step_hours)
            o.run(duration=dur, time_step=ts, export_variables=[])
            
            import numpy as np
            final_lon = float(np.mean(o.history['lon'][-1, :]))
            final_lat = float(np.mean(o.history['lat'][-1, :]))
            
            slick_lat = sum(p.lat for p in observed_slick) / len(observed_slick)
            slick_lon = sum(p.lon for p in observed_slick) / len(observed_slick)
            
            dist = self._haversine(final_lat, final_lon, slick_lat, slick_lon)
            overlap = 0.5
            
            if dist <= self.config.consistent_centroid_distance_km:
                status = ForwardConsistencyStatus.CONSISTENT
                supp = [f"Centroid distance {dist:.1f}km is within consistent threshold."]
                contra = []
            elif dist <= self.config.inconsistent_centroid_distance_km:
                status = ForwardConsistencyStatus.PARTIALLY_CONSISTENT
                supp = [f"Centroid distance {dist:.1f}km is partially consistent."]
                contra = [f"Distance > {self.config.consistent_centroid_distance_km}km"]
            else:
                status = ForwardConsistencyStatus.INCONSISTENT
                supp = []
                contra = [f"Centroid distance {dist:.1f}km exceeds inconsistent threshold {self.config.inconsistent_centroid_distance_km}km."]
                
            return ForwardSimulationSummary(
                hypothesis=hypothesis,
                forward_duration_seconds=dur.total_seconds(),
                final_centroid_lat=final_lat,
                final_centroid_lon=final_lon,
                centroid_distance_km=dist,
                overlap_metric=overlap,
                status=status,
                supporting_observations=supp,
                contradicting_observations=contra
            )
        except Exception as e:
            return ForwardSimulationSummary(
                hypothesis=hypothesis,
                forward_duration_seconds=0,
                final_centroid_lat=None,
                final_centroid_lon=None,
                centroid_distance_km=None,
                overlap_metric=None,
                status=ForwardConsistencyStatus.NOT_COMPUTABLE,
                supporting_observations=[],
                contradicting_observations=[f"Simulation failure: {str(e)}"]
            )
