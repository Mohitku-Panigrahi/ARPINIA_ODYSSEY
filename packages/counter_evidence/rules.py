from .models import CounterEvidenceItem, Polarity, Computability, Severity
from .config import CounterEvidenceConfig
from packages.attribution.models import CandidateAttribution, AttributionRanking
from packages.ais.models import CandidateVessel, B4Result
from packages.stability.models import CandidateStability, StabilityClass
from typing import Dict, Optional
import uuid

class CounterEvidenceEngine:
    def __init__(self, config: CounterEvidenceConfig):
        self.config = config

    def _make_item(self, candidate_id: str, category: str, polarity: Polarity, severity: Severity,
                   computability: Computability, summary: str, source_module: str, source_fields: list,
                   quant_val: float = None, thresh_val: float = None) -> CounterEvidenceItem:
        return CounterEvidenceItem(
            evidence_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            category=category,
            polarity=polarity,
            severity=severity,
            confidence=1.0,
            computability=computability,
            summary=summary,
            quantitative_value=quant_val,
            threshold_reference=thresh_val,
            source_module=source_module,
            source_fields=source_fields,
            algorithm_version=self.config.algorithm_version,
            limitations=[]
        )

    def evaluate_spatial(self, cand_b4: CandidateVessel) -> CounterEvidenceItem:
        if not cand_b4.features_available.spatial_overlap:
            return self._make_item(
                cand_b4.mmsi, "SPATIAL_COMPATIBILITY", Polarity.UNKNOWN, Severity.NONE,
                Computability.MISSING_INPUT, "Spatial data unavailable for candidate.", "B4", ["features_available.spatial_overlap"]
            )
        
        has_95 = cand_b4.intersects_95_region.value if cand_b4.intersects_95_region.status == "AVAILABLE" else None
        has_50 = cand_b4.intersects_50_region.value if cand_b4.intersects_50_region.status == "AVAILABLE" else None
        
        if has_95 is None:
            return self._make_item(
                cand_b4.mmsi, "SPATIAL_COMPATIBILITY", Polarity.UNKNOWN, Severity.NONE,
                Computability.MISSING_INPUT, "Probability region intersections unavailable.", "B4", ["intersects_95_region"]
            )

        if not has_95:
            return self._make_item(
                cand_b4.mmsi, "SPATIAL_COMPATIBILITY", Polarity.CONTRADICTING, Severity.HIGH,
                Computability.COMPUTABLE, f"Candidate remained entirely outside the P95 origin region.",
                "B4", ["intersects_95_region"], 0.0, 1.0
            )
        elif has_50:
             return self._make_item(
                cand_b4.mmsi, "SPATIAL_COMPATIBILITY", Polarity.SUPPORTING, Severity.LOW,
                Computability.COMPUTABLE, f"Candidate intersected the high-probability P50 origin region.",
                "B4", ["intersects_50_region"], 1.0, 1.0
            )
        else:
             return self._make_item(
                cand_b4.mmsi, "SPATIAL_COMPATIBILITY", Polarity.NEUTRAL, Severity.NONE,
                Computability.COMPUTABLE, f"Candidate intersected outer probability regions only.",
                "B4", ["intersects_95_region", "intersects_50_region"], 0.5, None
            )

    def evaluate_temporal(self, cand_b4: CandidateVessel) -> CounterEvidenceItem:
        if not cand_b4.features_available.temporal_match:
            return self._make_item(
                cand_b4.mmsi, "TEMPORAL_COMPATIBILITY", Polarity.UNKNOWN, Severity.NONE,
                Computability.MISSING_INPUT, "Temporal data unavailable for candidate.", "B4", ["features_available.temporal_match"]
            )
        
        tir = cand_b4.time_inside_region_seconds
        if tir.status != "AVAILABLE" or tir.value is None:
            return self._make_item(
                cand_b4.mmsi, "TEMPORAL_COMPATIBILITY", Polarity.UNKNOWN, Severity.NONE,
                Computability.MISSING_INPUT, "Time inside region unavailable.", "B4", ["time_inside_region_seconds"]
            )

        hrs = tir.value / 3600.0
        if hrs == 0.0:
             return self._make_item(
                cand_b4.mmsi, "TEMPORAL_COMPATIBILITY", Polarity.CONTRADICTING, Severity.MODERATE,
                Computability.COMPUTABLE, f"Candidate had no temporal overlap (0 hours) with release window inside region.",
                "B4", ["time_inside_region_seconds"], hrs, 0.0
            )
        elif hrs > self.config.temporal_support_overlap_hours:
             return self._make_item(
                cand_b4.mmsi, "TEMPORAL_COMPATIBILITY", Polarity.SUPPORTING, Severity.LOW,
                Computability.COMPUTABLE, f"Candidate has significant temporal overlap ({hrs:.1f} hours).",
                "B4", ["time_inside_region_seconds"], hrs, self.config.temporal_support_overlap_hours
            )
        else:
             return self._make_item(
                cand_b4.mmsi, "TEMPORAL_COMPATIBILITY", Polarity.NEUTRAL, Severity.NONE,
                Computability.COMPUTABLE, f"Candidate has marginal temporal overlap ({hrs:.1f} hours).",
                "B4", ["time_inside_region_seconds"], hrs, None
            )

    def evaluate_alibi(self, cand_b4: CandidateVessel) -> CounterEvidenceItem:
        dist = cand_b4.closest_approach_km.value if cand_b4.closest_approach_km.status == "AVAILABLE" else None
        
        if dist is not None and dist > self.config.spatial_contradiction_min_distance_km:
            has_major_gap = any(g.duration_seconds > self.config.temporal_contradiction_gap_hours * 3600 for g in cand_b4.gap_analysis)
            if not has_major_gap:
                 return self._make_item(
                    cand_b4.mmsi, "TRAJECTORY_ALIBI_LIKE", Polarity.CONTRADICTING, Severity.HIGH,
                    Computability.COMPUTABLE, "Reported trajectory provides continuous counter-evidence against source compatibility.",
                    "B4", ["closest_approach_km", "gap_analysis"]
                )
            else:
                 return self._make_item(
                    cand_b4.mmsi, "TRAJECTORY_ALIBI_LIKE", Polarity.UNKNOWN, Severity.NONE,
                    Computability.NOT_APPLICABLE, "AIS gaps exist; cannot establish continuous alibi.",
                    "B4", ["gap_analysis"]
                )
        return self._make_item(
            cand_b4.mmsi, "TRAJECTORY_ALIBI_LIKE", Polarity.NEUTRAL, Severity.NONE,
            Computability.NOT_APPLICABLE, "Candidate was in plausible range; alibi not established.",
            "B4", ["closest_approach_km"]
        )

    def evaluate_stability(self, cand_b6: CandidateStability) -> CounterEvidenceItem:
        if cand_b6.stability_class == StabilityClass.INSUFFICIENT_ENSEMBLE_EVIDENCE:
            return self._make_item(
                cand_b6.mmsi, "MONTE_CARLO_STABILITY", Polarity.UNKNOWN, Severity.NONE,
                Computability.MISSING_INPUT, "Insufficient ensemble runs to assess stability.", "B6", ["stability_class"]
            )
            
        pr = cand_b6.presence_rate
        if pr < self.config.stability_presence_contradiction_threshold:
            return self._make_item(
                cand_b6.mmsi, "MONTE_CARLO_STABILITY", Polarity.CONTRADICTING, Severity.MODERATE,
                Computability.COMPUTABLE, f"Low attribution stability; candidate present in only {pr*100:.0f}% of perturbations.",
                "B6", ["presence_rate"], pr, self.config.stability_presence_contradiction_threshold
            )
            
        t1 = cand_b6.top1_stability
        if t1 > self.config.stability_top1_support_threshold:
            return self._make_item(
                cand_b6.mmsi, "MONTE_CARLO_STABILITY", Polarity.SUPPORTING, Severity.LOW,
                Computability.COMPUTABLE, f"High attribution stability; candidate is Top-1 in {t1*100:.0f}% of perturbations.",
                "B6", ["top1_stability"], t1, self.config.stability_top1_support_threshold
            )
            
        return self._make_item(
            cand_b6.mmsi, "MONTE_CARLO_STABILITY", Polarity.NEUTRAL, Severity.NONE,
            Computability.COMPUTABLE, "Candidate stability is intermediate.",
            "B6", ["top1_stability", "presence_rate"]
        )

    def evaluate_evidence_coverage(self, cand_b5: CandidateAttribution) -> CounterEvidenceItem:
        cov = cand_b5.evidence_coverage.value
        if cov < self.config.min_evidence_coverage:
            return self._make_item(
                cand_b5.mmsi, "EVIDENCE_COVERAGE", Polarity.UNKNOWN, Severity.NONE,
                Computability.COMPUTABLE, f"Substantial evidence unavailable (coverage {cov:.2f}).",
                "B5", ["evidence_coverage"], cov, self.config.min_evidence_coverage
            )
        return self._make_item(
            cand_b5.mmsi, "EVIDENCE_COVERAGE", Polarity.NEUTRAL, Severity.NONE,
            Computability.COMPUTABLE, f"Evidence coverage is adequate ({cov:.2f}).",
            "B5", ["evidence_coverage"], cov, self.config.min_evidence_coverage
        )

    def evaluate_closest_approach(self, cand_b4: CandidateVessel) -> CounterEvidenceItem:
        ca = cand_b4.closest_approach_km
        if ca.status != "AVAILABLE" or ca.value is None:
            return self._make_item(
                cand_b4.mmsi, "CLOSEST_APPROACH", Polarity.UNKNOWN, Severity.NONE,
                Computability.MISSING_INPUT, "Closest approach distance unavailable.", "B4", ["closest_approach_km"]
            )

        dist = ca.value
        if dist > self.config.closest_approach_contradiction_km:
            return self._make_item(
                cand_b4.mmsi, "CLOSEST_APPROACH", Polarity.CONTRADICTING, Severity.HIGH,
                Computability.COMPUTABLE, f"Closest approach ({dist:.1f} km) contradicts release origin.",
                "B4", ["closest_approach_km"], dist, self.config.closest_approach_contradiction_km
            )
        elif dist < self.config.closest_approach_support_km:
             return self._make_item(
                cand_b4.mmsi, "CLOSEST_APPROACH", Polarity.SUPPORTING, Severity.LOW,
                Computability.COMPUTABLE, f"Very close approach ({dist:.1f} km) supports release hypothesis.",
                "B4", ["closest_approach_km"], dist, self.config.closest_approach_support_km
            )
        else:
             return self._make_item(
                cand_b4.mmsi, "CLOSEST_APPROACH", Polarity.NEUTRAL, Severity.NONE,
                Computability.COMPUTABLE, f"Closest approach ({dist:.1f} km) is intermediate.",
                "B4", ["closest_approach_km"], dist, None
            )

    def evaluate_candidate(self, cand_b4: CandidateVessel, cand_b5: CandidateAttribution, cand_b6: CandidateStability) -> tuple:
        items = [
            self.evaluate_spatial(cand_b4),
            self.evaluate_temporal(cand_b4),
            self.evaluate_alibi(cand_b4),
            self.evaluate_closest_approach(cand_b4),
            self.evaluate_stability(cand_b6) if cand_b6 else None,
            self.evaluate_evidence_coverage(cand_b5) if cand_b5 else None
        ]
        items = [i for i in items if i is not None]
        return items
