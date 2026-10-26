from pydantic import BaseModel, Field, model_validator
import math

class CounterEvidenceConfig(BaseModel):
    algorithm_version: str = "B7_1.0.0"
    configuration_version: str = "1.0.0"
    
    spatial_contradiction_min_distance_km: float = Field(default=50.0, ge=0.0)
    spatial_support_max_distance_km: float = Field(default=10.0, ge=0.0)
    
    temporal_contradiction_gap_hours: float = Field(default=12.0, ge=0.0)
    temporal_support_overlap_hours: float = Field(default=2.0, ge=0.0)
    
    closest_approach_contradiction_km: float = Field(default=75.0, ge=0.0)
    closest_approach_support_km: float = Field(default=15.0, ge=0.0)
    
    min_evidence_coverage: float = Field(default=0.5, ge=0.0, le=1.0)
    
    stability_presence_contradiction_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    stability_top1_support_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    @model_validator(mode='after')
    def check_logical_bounds(self):
        if self.spatial_support_max_distance_km > self.spatial_contradiction_min_distance_km:
            raise ValueError("Support distance cannot exceed contradiction distance.")
        if self.closest_approach_support_km > self.closest_approach_contradiction_km:
            raise ValueError("Support closest approach cannot exceed contradiction distance.")
        if not math.isfinite(self.spatial_contradiction_min_distance_km) or not math.isfinite(self.closest_approach_contradiction_km):
            raise ValueError("Values must be finite")
        return self
