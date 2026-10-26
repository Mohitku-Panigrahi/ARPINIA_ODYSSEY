from datetime import datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, field_validator, model_validator

T = TypeVar('T')

class AnalyticalResult(BaseModel, Generic[T]):
    value: Optional[T] = None
    status: str
    reason: Optional[str] = None

class FeatureAvailability(BaseModel):
    spatial_overlap: bool
    temporal_match: bool
    closest_approach: bool
    ais_continuity: bool
    heading_alignment: bool = False
    behavior_signal: bool = False

class AISObservation(BaseModel):
    source: str
    source_record_id: Optional[str] = None
    mmsi: str = Field(..., min_length=9, max_length=9)
    imo: Optional[str] = None
    vessel_name: Optional[str] = None
    timestamp_utc: datetime
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    sog_knots: Optional[float] = None
    cog_degrees: Optional[float] = None
    heading_degrees: Optional[float] = None
    nav_status: Optional[int] = None
    vessel_type: Optional[int] = None
    position_accuracy: Optional[bool] = None
    draught: Optional[float] = Field(None, ge=0.0)
    callsign: Optional[str] = None
    quality_flags: List[str] = Field(default_factory=list)

    @field_validator("timestamp_utc")
    @classmethod
    def enforce_utc(cls, v):
        if v.tzinfo is None:
            raise ValueError("timestamp_utc must be timezone-aware")
        return v
        
    @model_validator(mode='after')
    def normalize_sentinels(self) -> 'AISObservation':
        # Sentinel normalization
        if self.heading_degrees == 511.0:
            self.heading_degrees = None
            self.quality_flags.append("HEADING_SENTINEL_NORMALIZED")
        if self.cog_degrees == 360.0 or self.cog_degrees == 3600.0:
            self.cog_degrees = None
            self.quality_flags.append("COG_SENTINEL_NORMALIZED")
        if self.sog_knots == 102.3:
            self.sog_knots = None
            self.quality_flags.append("SOG_SENTINEL_NORMALIZED")
        # Ensure lat/lon sentinels (91, 181) are caught by pydantic limits
        return self

class TrajectorySegment(BaseModel):
    start_obs: AISObservation
    end_obs: AISObservation
    duration_seconds: float
    distance_meters: float
    is_interpolated: bool
    interpolated_gap: bool

class VesselTrajectory(BaseModel):
    mmsi: str
    imo: Optional[str] = None
    vessel_name: Optional[str] = None
    observations: List[AISObservation]
    segments: List[TrajectorySegment] = []
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    max_gap_seconds: float = 0.0
    quality_flags: List[str] = []

class GapAnalysis(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    status: str

class CandidateVessel(BaseModel):
    mmsi: str
    imo: Optional[str] = None
    vessel_name: Optional[str] = None
    trajectory_quality: Dict[str, float]
    observed_intersections: List[str]
    segment_intersections: List[str]
    probability_region_intersections: List[str]
    closest_approach_km: AnalyticalResult[float]
    closest_approach_time: AnalyticalResult[str] # datetime as str to avoid JSON NaN issues
    intersects_50_region: AnalyticalResult[bool]
    intersects_80_region: AnalyticalResult[bool]
    intersects_95_region: AnalyticalResult[bool]
    time_inside_region_seconds: AnalyticalResult[float]
    gap_analysis: List[GapAnalysis] = []
    candidate_reasons: List[str] = []
    features_available: FeatureAvailability

class ExcludedVessel(BaseModel):
    mmsi: str
    exclusion_reasons: List[str]
    features_available: FeatureAvailability

class B4Result(BaseModel):
    scenario_id: str
    ais_source: str
    source_mode: str
    raw_artifact_hash: Optional[str]
    requested_time_window: Dict[str, datetime]
    requested_bbox: Dict[str, float]
    vessel_count: int
    observation_count: int
    candidate_count: int
    candidates: List[CandidateVessel]
    excluded: List[ExcludedVessel]
    warnings: List[str]
    limitations: List[str]
    provenance: Dict[str, str]

