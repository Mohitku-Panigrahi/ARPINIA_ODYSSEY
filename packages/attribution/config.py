from pydantic import BaseModel, Field, model_validator

class AttributionConfig(BaseModel):
    configuration_version: str = "odyssey_multifactor_v1"
    attribution_algorithm_version: str = "v1.0.0"
    
    weight_f1_spatial: float = Field(default=0.4, ge=0.0)
    weight_f2_temporal: float = Field(default=0.3, ge=0.0)
    weight_f4_closest_approach: float = Field(default=0.3, ge=0.0)
    
    p50_spatial_score: float = Field(default=1.0, ge=0.0, le=1.0)
    p80_spatial_score: float = Field(default=0.75, ge=0.0, le=1.0)
    p95_spatial_score: float = Field(default=0.50, ge=0.0, le=1.0)
    
    d_ref_min_km: float = Field(default=1.0, gt=0.0)
    d_ref_max_km: float = Field(default=100.0, gt=0.0)
    
    max_gap_perfect_seconds: float = Field(default=3600.0, ge=0.0)
    max_gap_zero_seconds: float = Field(default=14400.0, ge=0.0)
    
    tie_tolerance: float = Field(default=0.05, ge=0.0, le=1.0)
    minimum_evidence_coverage: float = Field(default=0.30, ge=0.0, le=1.0)
    
    @model_validator(mode='after')
    def validate_cross_fields(self):
        if self.d_ref_min_km > self.d_ref_max_km:
            raise ValueError("d_ref_min_km cannot be greater than d_ref_max_km")
        if self.max_gap_perfect_seconds >= self.max_gap_zero_seconds:
            raise ValueError("max_gap_perfect_seconds must be strictly less than max_gap_zero_seconds")
        if (self.weight_f1_spatial + self.weight_f2_temporal + self.weight_f4_closest_approach) <= 0:
            raise ValueError("Total potential attribution weight must be strictly positive")
        return self
