from pydantic import BaseModel, Field, field_validator
import math
from datetime import datetime, timezone

from packages.geo.models import Point

class WindVector(BaseModel):
    """Represents a wind vector at a specific location and time."""
    model_config = {'strict': True}
    
    u: float = Field(..., description="Eastward wind component (m/s)")
    v: float = Field(..., description="Northward wind component (m/s)")
    
    @field_validator('u', 'v')
    @classmethod
    def check_finite(cls, val: float) -> float:
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Wind component must be finite, got {val}")
        return val

class CurrentVector(BaseModel):
    """Represents a surface ocean current vector at a specific location and time."""
    model_config = {'strict': True}
    
    u: float = Field(..., description="Eastward current component (m/s)")
    v: float = Field(..., description="Northward current component (m/s)")
    
    @field_validator('u', 'v')
    @classmethod
    def check_finite(cls, val: float) -> float:
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Current component must be finite, got {val}")
        return val

class MetOceanPoint(BaseModel):
    """Encapsulates a spatio-temporal query point for environmental forcing."""
    model_config = {'strict': True}
    
    point: Point
    timestamp: datetime
    
    @field_validator('timestamp')
    @classmethod
    def check_timezone_aware(cls, val: datetime) -> datetime:
        if val.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")
        return val.astimezone(timezone.utc)
