import pytest
import sys

def test_ground_truth_leakage():
    # Ensure ground truth is not accessed by any AIS module
    from packages.ais import pipeline, correlation
    import inspect
    
    pipeline_src = inspect.getsource(pipeline)
    correlation_src = inspect.getsource(correlation)
    
    assert 'ground_truth' not in pipeline_src.lower(), "Leakage: ground_truth found in pipeline"
    assert 'ground_truth' not in correlation_src.lower(), "Leakage: ground_truth found in correlation"
    
    for mod_name in sys.modules.keys():
        if not mod_name.startswith('test_'):
            assert 'ground_truth' not in mod_name.lower()
