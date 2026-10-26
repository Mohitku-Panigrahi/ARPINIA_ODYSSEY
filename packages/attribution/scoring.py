import math
import numpy as np
from typing import List, Dict, Tuple, Any
from packages.ais.models import CandidateVessel, B4Result
from packages.geo.distance import calculate_distance
from packages.geo.models import Point
from .config import AttributionConfig
from .models import FactorResult, EvidenceCoverage, CandidateAttribution, AttributionRanking

class AttributionEngine:
    def __init__(self, config: AttributionConfig = None):
        self.config = config or AttributionConfig()
        
    def _calculate_d_ref(self, time_slices: List[Dict]) -> float:
        if not time_slices:
            return self.config.d_ref_max_km
            
        radii = []
        for ts in time_slices:
            pd = ts.get('probability_data', {})
            grid = pd.get('grid')
            xbins = pd.get('lon_bins')
            ybins = pd.get('lat_bins')
            thresholds = pd.get('thresholds', {})
            t95 = thresholds.get('95', 0.05)
            
            if grid is not None and xbins is not None and ybins is not None and len(xbins) > 1 and len(ybins) > 1:
                # Calculate area of one cell (assuming roughly uniform in this small region)
                cell_width_m = calculate_distance(Point(lat=ybins[0], lon=xbins[0]), Point(lat=ybins[0], lon=xbins[1]))
                cell_height_m = calculate_distance(Point(lat=ybins[0], lon=xbins[0]), Point(lat=ybins[1], lon=xbins[0]))
                cell_area_km2 = (cell_width_m / 1000.0) * (cell_height_m / 1000.0)
                
                # Count cells >= t95
                p95_cells = np.sum(grid >= t95)
                if p95_cells > 0:
                    area_p95_km2 = p95_cells * cell_area_km2
                    r_t = math.sqrt(area_p95_km2 / math.pi)
                    radii.append(r_t)
                
        if not radii:
            return self.config.d_ref_max_km
            
        median_r = np.median(radii)
        return max(self.config.d_ref_min_km, min(median_r, self.config.d_ref_max_km))
        
    def _score_f1_spatial(self, candidate: CandidateVessel) -> FactorResult:
        if not candidate.features_available.spatial_overlap:
            return FactorResult(score=0.0, weight=self.config.weight_f1_spatial, available=True, reason="NO_SPATIAL_OVERLAP")
            
        # Check analytical statuses
        if (candidate.intersects_50_region.status != "AVAILABLE" and 
            candidate.intersects_80_region.status != "AVAILABLE" and 
            candidate.intersects_95_region.status != "AVAILABLE"):
            return FactorResult(score=0.0, weight=0.0, available=False, reason="B3_TIERS_UNAVAILABLE")

        if candidate.intersects_50_region.status == "AVAILABLE" and candidate.intersects_50_region.value:
            return FactorResult(score=self.config.p50_spatial_score, weight=self.config.weight_f1_spatial, available=True, reason="P50_INTERSECTION")
        elif candidate.intersects_80_region.status == "AVAILABLE" and candidate.intersects_80_region.value:
            return FactorResult(score=self.config.p80_spatial_score, weight=self.config.weight_f1_spatial, available=True, reason="P80_INTERSECTION")
        elif candidate.intersects_95_region.status == "AVAILABLE" and candidate.intersects_95_region.value:
            return FactorResult(score=self.config.p95_spatial_score, weight=self.config.weight_f1_spatial, available=True, reason="P95_INTERSECTION")
            
        return FactorResult(score=0.0, weight=self.config.weight_f1_spatial, available=True, reason="NO_REGION_MATCH")

    def _score_f2_temporal(self, candidate: CandidateVessel) -> FactorResult:
        # We don't have continuous temporal proximity right now from B4, it's binary.
        if not hasattr(candidate.features_available, 'temporal_match'):
             return FactorResult(score=0.0, weight=0.0, available=False, reason="TEMPORAL_EVIDENCE_UNAVAILABLE")
             
        # Just because it's false doesn't mean it's unavailable. 
        if candidate.features_available.temporal_match:
            return FactorResult(score=1.0, weight=self.config.weight_f2_temporal, available=True, reason="TEMPORAL_OVERLAP_CONFIRMED")
        return FactorResult(score=0.0, weight=self.config.weight_f2_temporal, available=True, reason="NO_TEMPORAL_OVERLAP")

    def _score_f3_origin(self, candidate: CandidateVessel) -> FactorResult:
        return FactorResult(score=0.0, weight=0.0, available=False, reason="F3_DEFERRED_DUE_TO_INTERFACE_LIMITATION")

    def _score_f4_closest_approach(self, candidate: CandidateVessel, d_ref: float) -> FactorResult:
        if not candidate.features_available.closest_approach or candidate.closest_approach_km.status != "AVAILABLE":
            return FactorResult(score=0.0, weight=0.0, available=False, reason="CLOSEST_APPROACH_UNAVAILABLE")
            
        dist = candidate.closest_approach_km.value
        if dist is None or math.isnan(dist) or math.isinf(dist) or dist < 0:
            return FactorResult(score=0.0, weight=0.0, available=False, reason="INVALID_DISTANCE_INPUT")
            
        score = math.exp(-dist / d_ref)
        return FactorResult(score=score, weight=self.config.weight_f4_closest_approach, available=True, reason="EXPONENTIAL_DECAY")
        
    def _calculate_f5_continuity(self, candidate: CandidateVessel) -> Tuple[float, bool]:
        if "max_gap_seconds" not in candidate.trajectory_quality:
            return 0.0, False
            
        gap = candidate.trajectory_quality["max_gap_seconds"]
        
        if gap <= self.config.max_gap_perfect_seconds:
            return 1.0, True
        if gap >= self.config.max_gap_zero_seconds:
            return 0.0, True
            
        span = self.config.max_gap_zero_seconds - self.config.max_gap_perfect_seconds
        return 1.0 - ((gap - self.config.max_gap_perfect_seconds) / span), True

    def score_candidates(self, b4_result: B4Result, time_slices: List[Dict]) -> AttributionRanking:
        d_ref = self._calculate_d_ref(time_slices)
        
        # Temporary structure before making immutable
        scored_data = []
        
        for cand in b4_result.candidates:
            f1 = self._score_f1_spatial(cand)
            f2 = self._score_f2_temporal(cand)
            f3 = self._score_f3_origin(cand)
            f4 = self._score_f4_closest_approach(cand, d_ref)
            
            factors = {"F1": f1, "F2": f2, "F3": f3, "F4": f4}
            
            total_available_weight = sum(f.weight for f in factors.values() if f.available)
            weighted_score_sum = sum(f.score * f.weight for f in factors.values() if f.available)
            
            if total_available_weight > 0:
                final_score = weighted_score_sum / total_available_weight
            else:
                final_score = 0.0
                
            f5_mod, f5_avail = self._calculate_f5_continuity(cand)
            num_available = sum(1 for f in factors.values() if f.available)
            
            base_coverage = total_available_weight / (self.config.weight_f1_spatial + self.config.weight_f2_temporal + self.config.weight_f4_closest_approach)
            
            if f5_avail:
                final_coverage = base_coverage * f5_mod
            else:
                final_coverage = base_coverage * 0.0 # Unavailable quality = 0 coverage confidence
                
            coverage = EvidenceCoverage(
                value=final_coverage,
                factors_available=num_available,
                continuity_modifier=f5_mod if f5_avail else 0.0
            )
            
            scored_data.append({
                "mmsi": cand.mmsi,
                "score": final_score,
                "coverage": coverage,
                "factors": factors,
                "reasons": cand.candidate_reasons
            })
            
        # O(C log C) sorting: score descending, coverage descending, mmsi ascending
        scored_data.sort(key=lambda x: (x["score"], x["coverage"].value, x["mmsi"] != x["mmsi"], x["mmsi"]), reverse=True)
        # Because we reversed everything, MMSI gets reversed (Z-A). To fix this, we sort properly:
        scored_data.sort(key=lambda x: (-x["score"], -x["coverage"].value, x["mmsi"]))
        
        # O(C) Tie Grouping
        ranked = []
        insufficient = []
        
        if scored_data:
            group_ref_score = scored_data[0]["score"]
            group_status = "RANKED"
            
            for i, data in enumerate(scored_data):
                if data["coverage"].value < self.config.minimum_evidence_coverage:
                    status = "INSUFFICIENT_EVIDENCE"
                else:
                    if abs(group_ref_score - data["score"]) <= self.config.tie_tolerance:
                        if i > 0 and abs(scored_data[0]["score"] - data["score"]) <= self.config.tie_tolerance: 
                            status = "EFFECTIVELY_TIED"
                            # If we just declared a tie, make sure the reference is also marked
                            if ranked and ranked[-1].status == "RANKED":
                                ranked_copy = [r for r in ranked]
                                old = ranked_copy[-1]
                                ranked.pop()
                                ranked.append(CandidateAttribution(
                                    mmsi=old.mmsi, status="EFFECTIVELY_TIED", attribution_relevance_score=old.attribution_relevance_score,
                                    evidence_coverage=old.evidence_coverage, factors=old.factors, candidate_reasons=old.candidate_reasons
                                ))
                        else:
                            status = "RANKED"
                            # Only update reference score if we drop out of tie tolerance
                            if abs(group_ref_score - data["score"]) > self.config.tie_tolerance:
                                group_ref_score = data["score"]
                    else:
                        group_ref_score = data["score"]
                        status = "RANKED"
                        
                ca = CandidateAttribution(
                    mmsi=data["mmsi"],
                    status=status,
                    attribution_relevance_score=data["score"],
                    evidence_coverage=data["coverage"],
                    factors=data["factors"],
                    candidate_reasons=data["reasons"]
                )
                
                if status == "INSUFFICIENT_EVIDENCE":
                    insufficient.append(ca)
                else:
                    ranked.append(ca)
            
        return AttributionRanking(
            scenario_id=b4_result.scenario_id,
            configuration_version=self.config.configuration_version,
            attribution_algorithm_version=self.config.attribution_algorithm_version,
            ranked_candidates=ranked,
            insufficient_evidence_candidates=insufficient,
            d_ref_km=d_ref
        )
