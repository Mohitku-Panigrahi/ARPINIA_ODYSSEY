from typing import List, Dict, Any
from packages.attribution.models import AttributionRanking
from packages.ais.models import B4Result, CandidateVessel
from packages.stability.models import CandidateStability
from .models import CounterEvidenceResult, CandidateCounterEvidence, CounterEvidenceItem, Polarity, Severity, CounterEvidenceStatus
from .config import CounterEvidenceConfig
from .rules import CounterEvidenceEngine as RulesEngine

class CounterEvidenceEngine:
    def __init__(self, config: CounterEvidenceConfig = None):
        self.config = config or CounterEvidenceConfig()
        self.rules_engine = RulesEngine(self.config)

    def analyze(self, scenario_id: str,
                b4_result: B4Result,
                b5_ranking: AttributionRanking,
                b6_stabilities: List[CandidateStability]) -> CounterEvidenceResult:
        
        b5_map = {c.mmsi: c for c in b5_ranking.ranked_candidates + b5_ranking.insufficient_evidence_candidates}
        b6_map = {c.mmsi: c for c in b6_stabilities}
        
        candidates_ce = []
        for cand_b4 in b4_result.candidates:
            mmsi = cand_b4.mmsi
            cand_b5 = b5_map.get(mmsi)
            cand_b6 = b6_map.get(mmsi)
            
            items = self.rules_engine.evaluate_candidate(cand_b4, cand_b5, cand_b6)
            
            supporting = [i for i in items if i.polarity == Polarity.SUPPORTING]
            contradicting = [i for i in items if i.polarity == Polarity.CONTRADICTING]
            unknown = [i for i in items if i.polarity == Polarity.UNKNOWN]
            
            sev_summary = {s: 0 for s in Severity}
            for i in contradicting:
                sev_summary[i.severity] += 1
                
            if sev_summary[Severity.HIGH] > 0:
                status = CounterEvidenceStatus.STRONG_COUNTER_EVIDENCE
            elif sev_summary[Severity.MODERATE] > 0:
                status = CounterEvidenceStatus.MATERIAL_COUNTER_EVIDENCE
            elif sev_summary[Severity.LOW] > 0:
                status = CounterEvidenceStatus.LIMITED_COUNTER_EVIDENCE
            elif len(unknown) >= 3 or not cand_b5 or cand_b5.evidence_coverage.value < self.config.min_evidence_coverage:
                status = CounterEvidenceStatus.INSUFFICIENT_EVIDENCE
            else:
                status = CounterEvidenceStatus.NO_MATERIAL_COUNTER_EVIDENCE
                
            candidates_ce.append(CandidateCounterEvidence(
                candidate_id=mmsi,
                supporting_items=supporting,
                contradicting_items=contradicting,
                unknown_items=unknown,
                support_count=len(supporting),
                contradiction_count=len(contradicting),
                unknown_count=len(unknown),
                contradiction_severity_summary=sev_summary,
                overall_counter_evidence_status=status
            ))
            
        return CounterEvidenceResult(
            scenario_id=scenario_id,
            algorithm_version=self.config.algorithm_version,
            configuration_version=self.config.configuration_version,
            candidates=candidates_ce,
            provenance={"b4_hash": getattr(b4_result, 'raw_artifact_hash', None), "b5_version": getattr(b5_ranking, 'attribution_algorithm_version', None)},
            limitations=["Counter-evidence does not establish innocence and supporting evidence does not establish guilt."]
        )
