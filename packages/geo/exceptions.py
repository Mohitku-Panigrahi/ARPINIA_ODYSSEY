class GeoError(Exception):
    """Base exception for all geospatial errors."""
    pass

class InvalidCoordinateError(GeoError):
    """Raised when coordinates fall outside valid bounds [-90, 90] or [-180, 180] or are NaN/Inf."""
    pass

class InvalidBoundingBoxError(GeoError):
    """Raised when a bounding box has invalid extents or inverted coordinates."""
    pass

class InvalidTrajectoryError(GeoError):
    """Raised when a trajectory has insufficient points or invalid timestamps."""
    pass

class InvalidTimestampError(GeoError):
    """Raised when a timestamp cannot be parsed or normalized."""
    pass
