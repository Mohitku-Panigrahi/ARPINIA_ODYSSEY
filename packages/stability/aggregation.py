import math
from typing import Dict, List, Optional
from packages.attribution.models import AttributionRanking
from .models import CandidateStability, CandidateRunResult, CandidateStatus, StabilityClass, WilsonInterval

class RunningStats:
    def __init__(self):
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0
        
    def update(self, value: float):
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.M2 += delta * delta2
        
    def variance(self):
        if self.count < 2:
            return 0.0
        return self.M2 / (self.count - 1)
        
    def std(self):
        return math.sqrt(self.variance())

def calculate_wilson_interval(successes: int, n: int, z: float = 1.96) -> WilsonInterval:
    if n == 0:
        return WilsonInterval(estimate=0.0, lower_bound=0.0, upper_bound=0.0, confidence_level=0.95)
    
    phat = successes / n
    denominator = 1 + z**2 / n
    center = phat + z**2 / (2 * n)
    spread = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    
    return WilsonInterval(
        estimate=phat,
        lower_bound=max(0.0, (center - spread) / denominator),
        upper_bound=min(1.0, (center + spread) / denominator),
        confidence_level=0.95
    )

class CandidateAggregator:
    def __init__(self, mmsi: str):
        self.mmsi = mmsi
        self.present_count = 0
        self.ranked_count = 0
        self.insufficient_evidence_count = 0
        self.top1_count = 0
        self.top3_count = 0
        self.score_stats = RunningStats()
        self.rank_stats = RunningStats()
        self.rank_counts: Dict[int, int] = {}
        
    def add_run(self, result: CandidateRunResult):
        if result.status == CandidateStatus.ABSENT:
            return
            
        self.present_count += 1
        
        if result.status == CandidateStatus.INSUFFICIENT_EVIDENCE:
            self.insufficient_evidence_count += 1
        else:
            self.ranked_count += 1
            
        if result.rank is not None:
            self.rank_stats.update(result.rank)
            self.rank_counts[result.rank] = self.rank_counts.get(result.rank, 0) + 1
            
            if result.rank == 1:
                self.top1_count += 1
            if result.rank <= 3:
                self.top3_count += 1
                
        if result.attribution_score is not None:
            self.score_stats.update(result.attribution_score)
            
    def compute_median_rank(self) -> Optional[float]:
        if self.ranked_count == 0:
            return None
            
        sorted_ranks = sorted(self.rank_counts.keys())
        total = 0
        ranks_unrolled = []
        # Since K_rank is small (max number of candidates, usually < 100)
        # we can unroll it to find median, or do it mathematically.
        for r in sorted_ranks:
            ranks_unrolled.extend([r] * self.rank_counts[r])
            
        n = len(ranks_unrolled)
        if n % 2 == 1:
            return float(ranks_unrolled[n//2])
        else:
            return (ranks_unrolled[n//2 - 1] + ranks_unrolled[n//2]) / 2.0

class StabilityAggregator:
    def __init__(self, min_valid_runs: int = 10, min_valid_fraction: float = 0.5):
        self.valid_runs = 0
        self.attempted_runs = 0
        self.candidates: Dict[str, CandidateAggregator] = {}
        self.nominal_ranking: Optional[AttributionRanking] = None
        self.min_valid_runs = min_valid_runs
        self.min_valid_fraction = min_valid_fraction
        
    def set_nominal(self, ranking: AttributionRanking):
        self.nominal_ranking = ranking
        
    def add_attempt(self):
        self.attempted_runs += 1
        
    def add_valid_run(self, candidate_results: List[CandidateRunResult]):
        self.valid_runs += 1
        
        for res in candidate_results:
            if res.status != CandidateStatus.ABSENT:
                if res.mmsi not in self.candidates:
                    self.candidates[res.mmsi] = CandidateAggregator(res.mmsi)
                self.candidates[res.mmsi].add_run(res)
                
    def get_candidate_stability(self, mmsi: str) -> CandidateStability:
        agg = self.candidates.get(mmsi)
        
        # Nominal mapping
        nom_rank = None
        nom_score = None
        nom_cov = None
        if self.nominal_ranking:
            for i, r in enumerate(self.nominal_ranking.ranked_candidates):
                if r.mmsi == mmsi:
                    nom_rank = i + 1
                    nom_score = r.attribution_relevance_score
                    nom_cov = r.evidence_coverage.value
                    break
            
            if nom_rank is None:
                for r in self.nominal_ranking.insufficient_evidence_candidates:
                    if r.mmsi == mmsi:
                        nom_score = r.attribution_relevance_score
                        nom_cov = r.evidence_coverage.value
                        break
        
        if not agg or self.valid_runs == 0:
            return CandidateStability(
                mmsi=mmsi, nominal_rank=nom_rank, nominal_score=nom_score, nominal_coverage=nom_cov,
                presence_rate=0.0, ranked_rate=0.0, insufficient_evidence_rate=0.0,
                top1_stability=0.0, top3_stability=0.0, conditional_top1_given_present=0.0, conditional_top1_given_ranked=0.0,
                top1_wilson_ci=calculate_wilson_interval(0, self.valid_runs), top3_wilson_ci=calculate_wilson_interval(0, self.valid_runs), presence_wilson_ci=calculate_wilson_interval(0, self.valid_runs),
                mean_rank=None, median_rank=None, rank_std=None, mean_score=None, score_std=None,
                stability_class=StabilityClass.INSUFFICIENT_ENSEMBLE_EVIDENCE
            )
            
        presence_rate = agg.present_count / self.valid_runs
        ranked_rate = agg.ranked_count / self.valid_runs
        insufficient_evidence_rate = agg.insufficient_evidence_count / self.valid_runs
        
        top1_stability = agg.top1_count / self.valid_runs
        top3_stability = agg.top3_count / self.valid_runs
        
        cond_top1_present = agg.top1_count / agg.present_count if agg.present_count > 0 else 0.0
        cond_top1_ranked = agg.top1_count / agg.ranked_count if agg.ranked_count > 0 else 0.0
        
        # Stability class
        if self.valid_runs < self.min_valid_runs or (self.valid_runs / max(1, self.attempted_runs)) < self.min_valid_fraction:
            sclass = StabilityClass.INSUFFICIENT_ENSEMBLE_EVIDENCE
        elif presence_rate < 0.2:
            sclass = StabilityClass.INSUFFICIENT_ENSEMBLE_EVIDENCE
        elif top1_stability >= 0.8:
            sclass = StabilityClass.HIGH_STABILITY
        elif top1_stability >= 0.5:
            sclass = StabilityClass.MODERATE_STABILITY
        elif top3_stability >= 0.5:
            sclass = StabilityClass.LOW_STABILITY
        else:
            sclass = StabilityClass.UNSTABLE
            
        return CandidateStability(
            mmsi=mmsi,
            nominal_rank=nom_rank,
            nominal_score=nom_score,
            nominal_coverage=nom_cov,
            presence_rate=presence_rate,
            ranked_rate=ranked_rate,
            insufficient_evidence_rate=insufficient_evidence_rate,
            top1_stability=top1_stability,
            top3_stability=top3_stability,
            conditional_top1_given_present=cond_top1_present,
            conditional_top1_given_ranked=cond_top1_ranked,
            top1_wilson_ci=calculate_wilson_interval(agg.top1_count, self.valid_runs),
            top3_wilson_ci=calculate_wilson_interval(agg.top3_count, self.valid_runs),
            presence_wilson_ci=calculate_wilson_interval(agg.present_count, self.valid_runs),
            mean_rank=agg.rank_stats.mean if agg.ranked_count > 0 else None,
            median_rank=agg.compute_median_rank(),
            rank_std=agg.rank_stats.std() if agg.ranked_count > 1 else 0.0,
            mean_score=agg.score_stats.mean if agg.present_count > 0 else None,
            score_std=agg.score_stats.std() if agg.present_count > 1 else 0.0,
            stability_class=sclass
        )
        
    def get_all_stabilities(self) -> List[CandidateStability]:
        res = [self.get_candidate_stability(mmsi) for mmsi in self.candidates]
        res.sort(key=lambda x: (-x.top1_stability, -x.top3_stability, -x.presence_rate, x.mmsi))
        return res
