from .config import AttributionConfig
from .models import FactorResult, EvidenceCoverage, CandidateAttribution, AttributionRanking
from .scoring import AttributionEngine

__all__ = [
    "AttributionConfig",
    "FactorResult",
    "EvidenceCoverage",
    "CandidateAttribution",
    "AttributionRanking",
    "AttributionEngine"
]

from .explanation import generate_explanation
__all__.append('generate_explanation')
