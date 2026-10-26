class MetOceanError(Exception):
    """Base exception for all MetOcean errors."""
    pass

class MissingVariableError(MetOceanError):
    """Raised when a required environmental variable is missing from the dataset."""
    pass

class UnsupportedUnitError(MetOceanError):
    """Raised when the dataset uses units that cannot be safely converted."""
    pass

class TemporalCoverageError(MetOceanError):
    """Raised when the requested time is outside the dataset's coverage."""
    pass

class SpatialCoverageError(MetOceanError):
    """Raised when the requested location is outside the dataset's coverage."""
    pass

class MissingDataError(MetOceanError):
    """Raised when the data at the requested coordinates is a fill value/NaN."""
    pass

class InvalidDatasetError(MetOceanError):
    """Raised when the dataset file is malformed or unreadable."""
    pass

class InterpolationError(MetOceanError):
    """Raised when interpolation fails (e.g., due to insufficient points)."""
    pass
