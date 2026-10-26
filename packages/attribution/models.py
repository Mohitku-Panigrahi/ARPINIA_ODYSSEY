from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict

class FactorResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(..., ge=0.0)
    available: bool
    reason: str

class EvidenceCoverage(BaseModel):
    model_config = ConfigDict(frozen=True)
    value: float = Field(..., ge=0.0, le=1.0)
    factors_available: int
    continuity_modifier: float = Field(..., ge=0.0, le=1.0)

class CandidateAttribution(BaseModel):
    model_config = ConfigDict(frozen=True)
    mmsi: str
    status: str
    attribution_relevance_score: float = Field(..., ge=0.0, le=1.0)
    evidence_coverage: EvidenceCoverage
    factors: Dict[str, FactorResult]
    candidate_reasons: List[str]

class AttributionRanking(BaseModel):
    model_config = ConfigDict(frozen=True)
    scenario_id: str
    configuration_version: str
    attribution_algorithm_version: str
    ranked_candidates: List[CandidateAttribution]
    insufficient_evidence_candidates: List[CandidateAttribution]
    d_ref_km: float
