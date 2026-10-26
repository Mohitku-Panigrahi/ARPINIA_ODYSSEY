from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Optional, Dict, Any

class Polarity(str, Enum):
    SUPPORTING = "SUPPORTING"
    CONTRADICTING = "CONTRADICTING"
    UNKNOWN = "UNKNOWN"
    NEUTRAL = "NEUTRAL"

class Computability(str, Enum):
    COMPUTABLE = "COMPUTABLE"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"
    MISSING_INPUT = "MISSING_INPUT"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class Severity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class CounterEvidenceStatus(str, Enum):
    NO_MATERIAL_COUNTER_EVIDENCE = "NO_MATERIAL_COUNTER_EVIDENCE"
    LIMITED_COUNTER_EVIDENCE = "LIMITED_COUNTER_EVIDENCE"
    MATERIAL_COUNTER_EVIDENCE = "MATERIAL_COUNTER_EVIDENCE"
    STRONG_COUNTER_EVIDENCE = "STRONG_COUNTER_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class CounterEvidenceItem(BaseModel):
    model_config = ConfigDict(frozen=True)
    evidence_id: str
    candidate_id: str
    category: str
    polarity: Polarity
    severity: Severity
    confidence: float
    computability: Computability
    summary: str
    quantitative_value: Optional[float] = None
    threshold_reference: Optional[float] = None
    source_module: str
    source_fields: List[str]
    algorithm_version: str
    limitations: List[str]

class CandidateCounterEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)
    candidate_id: str
    supporting_items: List[CounterEvidenceItem]
    contradicting_items: List[CounterEvidenceItem]
    unknown_items: List[CounterEvidenceItem]
    support_count: int
    contradiction_count: int
    unknown_count: int
    contradiction_severity_summary: Dict[Severity, int]
    overall_counter_evidence_status: CounterEvidenceStatus

class CounterEvidenceResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    scenario_id: str
    algorithm_version: str
    configuration_version: str
    candidates: List[CandidateCounterEvidence]
    provenance: Dict[str, Any]
    limitations: List[str]
