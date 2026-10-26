from packages.geo.models import Point, BoundingBox, Trajectory

def is_point_in_bbox(point: Point, bbox: BoundingBox) -> bool:
    """
    Check if a geographic point lies within a bounding box.
    Boundary matches are considered inside.
    """
    return (bbox.min_lat <= point.lat <= bbox.max_lat) and \
           (bbox.min_lon <= point.lon <= bbox.max_lon)

def is_trajectory_in_bbox(trajectory: Trajectory, bbox: BoundingBox, partial: bool = False) -> bool:
    """
    Check if a trajectory is within a bounding box.
    
    Args:
        trajectory: The trajectory to check.
        bbox: The bounding box.
        partial: If True, returns True if ANY point of the trajectory is in the bbox.
                 If False, returns True only if ALL points are in the bbox.
    """
    if partial:
        return any(is_point_in_bbox(pt.point, bbox) for pt in trajectory.points)
    else:
        return all(is_point_in_bbox(pt.point, bbox) for pt in trajectory.points)
