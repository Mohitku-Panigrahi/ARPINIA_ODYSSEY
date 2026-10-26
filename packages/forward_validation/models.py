from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

class ForwardConsistencyStatus(str, Enum):
    CONSISTENT = "CONSISTENT"
    PARTIALLY_CONSISTENT = "PARTIALLY_CONSISTENT"
    INCONSISTENT = "INCONSISTENT"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class ReleaseHypothesis(BaseModel):
    model_config = ConfigDict(frozen=True)
    candidate_id: str
    release_lat: float
    release_lon: float
    release_time: datetime
    derivation_method: str
    source_fields: List[str]
    uncertainty_limitations: List[str]

class ForwardSimulationSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    hypothesis: ReleaseHypothesis
    forward_duration_seconds: float
    final_centroid_lat: Optional[float]
    final_centroid_lon: Optional[float]
    centroid_distance_km: Optional[float]
    overlap_metric: Optional[float]
    status: ForwardConsistencyStatus
    supporting_observations: List[str]
    contradicting_observations: List[str]

class CandidateForwardConsistency(BaseModel):
    model_config = ConfigDict(frozen=True)
    candidate_id: str
    status: ForwardConsistencyStatus
    hypotheses_tested: int
    best_hypothesis: Optional[ForwardSimulationSummary]
    centroid_distance_km: Optional[float]
    overlap_metric: Optional[float]
    supporting_observations: List[str]
    contradicting_observations: List[str]
    limitations: List[str]
    provenance: Dict[str, Any]

class ForwardValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    scenario_id: str
    algorithm_version: str
    configuration_version: str
    candidates: List[CandidateForwardConsistency]
    provenance: Dict[str, Any]
    limitations: List[str]
