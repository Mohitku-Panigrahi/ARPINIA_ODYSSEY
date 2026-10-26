from typing import List
from .models import CandidateAttribution

def generate_explanation(attribution: CandidateAttribution) -> List[str]:
    explanation = []
    
    explanation.append(f"Attribution Relevance: {attribution.attribution_relevance_score:.2f}")
    explanation.append(f"Evidence Coverage: {attribution.evidence_coverage.value:.2f}")
    
    if attribution.status == "INSUFFICIENT_EVIDENCE":
        explanation.append("Status: INSUFFICIENT_EVIDENCE (Below minimum coverage threshold)")
    elif attribution.status == "EFFECTIVELY_TIED":
        explanation.append("Status: EFFECTIVELY_TIED (Score difference within tolerance)")
    else:
        explanation.append(f"Status: {attribution.status}")
        
    explanation.append("\nFactors:")
    for factor_name, factor in attribution.factors.items():
        if factor.available:
            explanation.append(f"  {factor_name}: Score {factor.score:.2f} (Weight {factor.weight:.2f}) - {factor.reason}")
        else:
            explanation.append(f"  {factor_name}: UNAVAILABLE - {factor.reason}")
            
    explanation.append(f"\nContinuity Coverage Modifier: {attribution.evidence_coverage.continuity_modifier:.2f}")
    
    return explanation
