from pydantic import BaseModel, Field

class ForwardValidationConfig(BaseModel):
    algorithm_version: str = "B8_1.0.0"
    configuration_version: str = "1.0.0"
    
    max_release_hypotheses_per_candidate: int = 3
    
    # ODYSSEY-DESIGNED CONSISTENCY HEURISTIC
    consistent_centroid_distance_km: float = Field(15.0, ge=0.0)
    inconsistent_centroid_distance_km: float = Field(50.0, ge=0.0)
    
    consistent_overlap_fraction: float = Field(0.1, ge=0.0, le=1.0)
    
    forward_duration_hours: float = 48.0
    particle_count: int = 100
    
    time_step_hours: float = 1.0
