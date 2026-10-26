import math
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from packages.geo.exceptions import (
    InvalidCoordinateError,
    InvalidBoundingBoxError,
    InvalidTrajectoryError,
    InvalidTimestampError
)

class Point(BaseModel):
    """Geographic point representing latitude and longitude."""
    model_config = {'strict': True}
    
    lat: float = Field(..., description="Latitude between -90 and 90")
    lon: float = Field(..., description="Longitude between -180 and 180")

    @field_validator('lat', 'lon')
    @classmethod
    def check_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise InvalidCoordinateError(f"Coordinate value must be finite, got {v}")
        return v

    @field_validator('lat')
    @classmethod
    def check_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise InvalidCoordinateError(f"Latitude must be between -90 and 90, got {v}")
        return v

    @field_validator('lon')
    @classmethod
    def check_lon(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise InvalidCoordinateError(f"Longitude must be between -180 and 180, got {v}")
        return v

    def to_geojson(self) -> Dict[str, Any]:
        """Returns standard GeoJSON Point geometry representation."""
        return {
            "type": "Point",
            "coordinates": [self.lon, self.lat]
        }

class BoundingBox(BaseModel):
    """Geographic bounding box defined by min/max lat/lon."""
    model_config = {'strict': True}
    
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    @model_validator(mode='after')
    def check_bounds(self) -> 'BoundingBox':
        # Validate finitude and limits manually as they share the point constraints
        for v in (self.min_lon, self.max_lon, self.min_lat, self.max_lat):
            if math.isnan(v) or math.isinf(v):
                raise InvalidBoundingBoxError(f"Bounding box values must be finite, got {v}")
        
        if not (-90.0 <= self.min_lat <= 90.0) or not (-90.0 <= self.max_lat <= 90.0):
            raise InvalidBoundingBoxError("Latitude must be between -90 and 90")
        
        if not (-180.0 <= self.min_lon <= 180.0) or not (-180.0 <= self.max_lon <= 180.0):
            raise InvalidBoundingBoxError("Longitude must be between -180 and 180")
            
        if self.min_lat > self.max_lat:
            raise InvalidBoundingBoxError("min_lat cannot be greater than max_lat")
            
        if self.min_lon > self.max_lon:
            # For B1, we explicitly reject inverted/antimeridian crossing boxes to prevent ambiguity
            raise InvalidBoundingBoxError("min_lon cannot be greater than max_lon (antimeridian crossing not supported in basic bbox)")
            
        return self
        
    def to_geojson(self) -> Dict[str, Any]:
        """Returns GeoJSON Polygon representation of the bounding box."""
        return {
            "type": "Polygon",
            "coordinates": [[
                [self.min_lon, self.min_lat],
                [self.max_lon, self.min_lat],
                [self.max_lon, self.max_lat],
                [self.min_lon, self.max_lat],
                [self.min_lon, self.min_lat]
            ]]
        }


class TrajectoryPoint(BaseModel):
    """A single spatio-temporal point."""
    model_config = {'strict': True}
    
    point: Point
    timestamp: datetime

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_and_normalize_time(cls, v: Any) -> datetime:
        if isinstance(v, str):
            try:
                # Basic ISO 8601 parsing
                if v.endswith('Z'):
                    v = v[:-1] + '+00:00'
                dt = datetime.fromisoformat(v)
            except ValueError:
                raise InvalidTimestampError(f"Invalid timestamp format: {v}")
        elif isinstance(v, (int, float)):
            try:
                dt = datetime.fromtimestamp(v, tz=timezone.utc)
            except (ValueError, OSError, OverflowError):
                raise InvalidTimestampError(f"Invalid timestamp value: {v}")
        elif isinstance(v, datetime):
            dt = v
        else:
            raise InvalidTimestampError(f"Unsupported timestamp type: {type(v)}")
            
        if dt.tzinfo is None:
            raise InvalidTimestampError("Timezone-naive timestamps are not allowed. Provide a timezone-aware timestamp.")
        
        return dt.astimezone(timezone.utc)

class Trajectory(BaseModel):
    """A series of chronologically ordered TrajectoryPoints."""
    model_config = {'strict': True}
    
    points: List[TrajectoryPoint]
    
    @model_validator(mode='after')
    def validate_trajectory(self) -> 'Trajectory':
        if len(self.points) < 1:
            raise InvalidTrajectoryError("Trajectory must contain at least 1 point.")
            
        # Ensure chronological ordering (strictly increasing timestamps)
        for i in range(1, len(self.points)):
            if self.points[i].timestamp <= self.points[i-1].timestamp:
                raise InvalidTrajectoryError("Trajectory points must be ordered chronologically with strictly increasing timestamps (zero-duration movement not allowed).")
                
        return self

    def to_geojson(self) -> Dict[str, Any]:
        """Returns standard GeoJSON LineString geometry representation."""
        return {
            "type": "LineString",
            "coordinates": [[pt.point.lon, pt.point.lat] for pt in self.points]
        }
