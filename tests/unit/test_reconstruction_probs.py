import os
import sys
from datetime import datetime, timezone, timedelta
import numpy as np

repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_path)

from packages.geo.models import Point
from packages.reconstruction.engine import ReconstructionEngine
from packages.reconstruction.models import ReconstructionConfig
from packages.reconstruction.probability import ProbabilityFieldGenerator

def test_probability_normalization():
    print("Testing Probability Normalization...")
    lons = np.random.uniform(33.0, 34.0, 1000)
    lats = np.random.uniform(33.0, 34.0, 1000)
    
    gen = ProbabilityFieldGenerator(32.0, 35.0, 32.0, 35.0, 0.1)
    res = gen.generate(lons, lats)
    
    assert res['status'] == 'success'
    mass = np.sum(res['grid'])
    assert abs(mass - 1.0) < 1e-6, f"Normalization failed, mass={mass}"
    print("Probability Normalization: PASS")
    
def test_region_nesting():
    print("Testing Region Nesting...")
    lons = np.random.normal(33.5, 0.1, 10000)
    lats = np.random.normal(33.5, 0.1, 10000)
    
    gen = ProbabilityFieldGenerator(32.0, 35.0, 32.0, 35.0, 0.05)
    res = gen.generate(lons, lats)
    grid = res['grid']
    t50 = res['thresholds']['50']
    t80 = res['thresholds']['80']
    t95 = res['thresholds']['95']
    
    # Masks
    m50 = grid >= t50
    m80 = grid >= t80
    m95 = grid >= t95
    
    # Assert nesting: m50 implies m80 implies m95
    assert np.all(m80[m50]), "50% region not fully contained in 80% region"
    assert np.all(m95[m80]), "80% region not fully contained in 95% region"
    
    # Assert masses
    mass50 = np.sum(grid[m50])
    mass80 = np.sum(grid[m80])
    mass95 = np.sum(grid[m95])
    
    # The calculated threshold might overshoot slightly because of discrete cells
    assert mass50 >= 0.49, f"Mass 50 is {mass50}"
    assert mass80 >= 0.79, f"Mass 80 is {mass80}"
    assert mass95 >= 0.94, f"Mass 95 is {mass95}"
    print("Region Nesting: PASS")

if __name__ == '__main__':
    test_probability_normalization()
    test_region_nesting()
