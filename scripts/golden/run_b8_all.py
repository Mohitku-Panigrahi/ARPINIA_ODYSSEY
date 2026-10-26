import json
import os
import sys
from datetime import datetime, timezone, timedelta
from packages.geo.models import Point
from packages.forward_validation.config import ForwardValidationConfig
from packages.forward_validation.engine import ForwardValidationEngine
from packages.ais.models import B4Result, CandidateVessel
from pydantic import BaseModel

def main():
    if not os.path.exists("b5_output.json"):
        print("Waiting for B5...")
        return
        
    with open("b5_output.json", "r") as f:
        b5_data = json.load(f)
        
    cands = b5_data.get("rankings", [])
    
    # Run B8 for all candidates
    home_dir = os.path.expanduser('~')
    era5_path = os.path.join(home_dir, 'odyssey-data-test', 'era5_sih_zenodo_alpha_20180813_20180816.nc')
    cmems_path = os.path.join(home_dir, 'odyssey-data-test', 'cmems_sih_zenodo_alpha_20180813_20180816.nc')
    
    b8_config = ForwardValidationConfig()
    b8_engine = ForwardValidationEngine(b8_config, era5_path, cmems_path)
    
    origin_lat, origin_lon = 33.44, 33.388 # From SAR
    slick_polygon = [
        Point(lat=origin_lat-0.005, lon=origin_lon-0.005),
        Point(lat=origin_lat+0.005, lon=origin_lon-0.005),
        Point(lat=origin_lat+0.005, lon=origin_lon+0.005),
        Point(lat=origin_lat-0.005, lon=origin_lon+0.005)
    ]
    
    b8_results = {}
    for c_data in cands:
        # Construct a CandidateVessel from dict
        # Since c_data is an AttributionRanking, it contains 'candidate' object
        cand_dict = c_data['candidate']
        cand = CandidateVessel(**cand_dict)
        
        try:
            res = b8_engine.evaluate_candidate(cand, slick_polygon)
            b8_results[cand.mmsi] = res.model_dump()
        except Exception as e:
            print(f"B8 error for {cand.mmsi}: {e}")
            
    with open("b8_output.json", "w") as f:
        json.dump(b8_results, f, indent=2, default=str)
        
    print("B8 Output Generated for all candidates")

if __name__ == '__main__':
    main()
