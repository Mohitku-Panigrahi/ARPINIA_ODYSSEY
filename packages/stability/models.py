from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class RunStatus(str, Enum):
    VALID = "VALID"
    VALID_NO_CANDIDATES = "VALID_NO_CANDIDATES"
    OUT_OF_FORCING_COVERAGE = "OUT_OF_FORCING_COVERAGE"
    INVALID_PERTURBATION = "INVALID_PERTURBATION"
    RECONSTRUCTION_FAILED = "RECONSTRUCTION_FAILED"
    ATTRIBUTION_FAILED = "ATTRIBUTION_FAILED"
    OTHER = "OTHER"

class CandidateStatus(str, Enum):
    RANKED = "RANKED"
    EFFECTIVELY_TIED = "EFFECTIVELY_TIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ABSENT = "ABSENT"

class StabilityClass(str, Enum):
    HIGH_STABILITY = "HIGH_STABILITY"
    MODERATE_STABILITY = "MODERATE_STABILITY"
    LOW_STABILITY = "LOW_STABILITY"
    UNSTABLE = "UNSTABLE"
    INSUFFICIENT_ENSEMBLE_EVIDENCE = "INSUFFICIENT_ENSEMBLE_EVIDENCE"

class NominalStability(str, Enum):
    YES = "YES"
    NO = "NO"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class PerturbationSpec(BaseModel):
    model_config = ConfigDict(frozen=True)
    run_id: str
    run_index: int
    seed: int
    wind_uncertainty_ms: float
    current_uncertainty_ms: float
    release_time_offset_hours: float
    boundary_perturbation: str = "DEFERRED"
    distribution: str = "CLIPPED_NORMAL"

class CandidateRunResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    run_id: str
    mmsi: str
    rank: Optional[int]
    attribution_score: Optional[float]
    evidence_coverage: Optional[float]
    status: CandidateStatus

class StabilityRunResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    perturbation: PerturbationSpec
    status: RunStatus
    failure_reason: Optional[str]
    runtime_seconds: float
    candidates: Dict[str, CandidateRunResult]

class WilsonInterval(BaseModel):
    model_config = ConfigDict(frozen=True)
    estimate: float
    lower_bound: float
    upper_bound: float
    confidence_level: float

class CandidateStability(BaseModel):
    model_config = ConfigDict(frozen=True)
    mmsi: str
    nominal_rank: Optional[int]
    nominal_score: Optional[float]
    nominal_coverage: Optional[float]
    
    presence_rate: float
    ranked_rate: float
    insufficient_evidence_rate: float
    
    top1_stability: float
    top3_stability: float
    
    conditional_top1_given_present: float
    conditional_top1_given_ranked: float
    
    top1_wilson_ci: Optional[WilsonInterval]
    top3_wilson_ci: Optional[WilsonInterval]
    presence_wilson_ci: Optional[WilsonInterval]
    
    mean_rank: Optional[float]
    median_rank: Optional[float]
    rank_std: Optional[float]
    
    mean_score: Optional[float]
    score_std: Optional[float]
    
    stability_class: StabilityClass

class EnsembleConvergence(BaseModel):
    model_config = ConfigDict(frozen=True)
    achieved: bool
    runs_executed: int
    checkpoints: List[int]
    top_candidate_deltas: Dict[str, Dict[str, float]]
    consecutive_converged_checks: int

class AttributionStabilityResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    scenario_id: str
    algorithm_version: str
    config_version: str
    
    total_attempted_runs: int
    valid_runs: int
    failed_runs: int
    valid_no_candidate_runs: int
    failure_reason_counts: Dict[str, int]
    
    convergence: EnsembleConvergence
    candidate_stabilities: List[CandidateStability]
    
    nominal_leader_mmsi: Optional[str]
    nominal_leader_stable: NominalStability
