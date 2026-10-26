from pydantic import BaseModel, Field, model_validator

class MonteCarloConfig(BaseModel):
    algorithm_version: str = "v1.0.0"
    configuration_version: str = "mc_v1"
    
    master_seed: int = Field(default=42)
    
    minimum_runs: int = Field(default=10, gt=0)
    maximum_runs: int = Field(default=100, gt=0)
    convergence_check_interval: int = Field(default=10, gt=0)
    convergence_tolerance: float = Field(default=0.05, gt=0.0)
    convergence_patience: int = Field(default=2, gt=0)
    minimum_valid_run_fraction: float = Field(default=0.5, gt=0.0, le=1.0)
    
    # Distributions
    wind_uncertainty_std_ms: float = Field(default=2.0, ge=0.0)
    current_uncertainty_std_ms: float = Field(default=0.1, ge=0.0)
    
    release_time_std_hours: float = Field(default=2.0, ge=0.0)
    release_time_min_offset_hours: float = Field(default=-6.0)
    release_time_max_offset_hours: float = Field(default=0.0) # Assume spill happened before detection
    
    @model_validator(mode='after')
    def validate_cross_fields(self):
        if self.minimum_runs > self.maximum_runs:
            raise ValueError("minimum_runs cannot be > maximum_runs")
        if self.release_time_min_offset_hours > self.release_time_max_offset_hours:
            raise ValueError("Min release offset cannot be > max offset")
        return self
