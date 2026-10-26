import math
from packages.geo.models import Point

# Mean spherical Earth radius in meters
EARTH_RADIUS_METERS = 6371008.8

def calculate_distance(p1: Point, p2: Point) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine great-circle distance.
    
    Returns:
        Distance in meters (float).
    """
    lat1, lon1 = math.radians(p1.lat), math.radians(p1.lon)
    lat2, lon2 = math.radians(p2.lat), math.radians(p2.lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    
    # Clip 'a' to [0, 1] to avoid math domain errors due to float precision
    a = max(0.0, min(1.0, a))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS_METERS * c
