from pydantic import BaseModel, Field
from datetime import timedelta
from typing import Optional

class ReconstructionConfig(BaseModel):
    scenario_id: str = "unknown"
    duration: timedelta = Field(default_factory=lambda: timedelta(hours=48))
    time_step: timedelta = Field(default_factory=lambda: timedelta(hours=1))
    particle_count: int = 1000
    random_seed: int = 42
    wind_uncertainty: float = 0.0
    current_uncertainty: float = 0.0
