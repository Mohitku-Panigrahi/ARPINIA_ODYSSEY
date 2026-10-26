import pytest
import json
import hashlib
from packages.evidence.builder import EvidenceBuilder, get_canonical_json

def test_tamper_detection_hashes():
    """Ensure that modifying any value in the JSON changes the canonical hash."""
    builder = EvidenceBuilder()
    builder.add_candidate({"mmsi": 123456789, "score": 0.95})
    
    canonical_1 = get_canonical_json(builder.evidence)
    hash_1 = hashlib.sha256(canonical_1).hexdigest()
    
    # Tamper the data
    builder.evidence["candidates"][0]["score"] = 0.99
    
    canonical_2 = get_canonical_json(builder.evidence)
    hash_2 = hashlib.sha256(canonical_2).hexdigest()
    
    assert hash_1 != hash_2, "Tampered evidence produced identical SHA256 hash"

def test_canonicalization_determinism():
    """Ensure identical data produces identical JSON across runs."""
    data = {"b": 2, "a": 1, "c": [3, 2, 1], "d": None}
    
    can_1 = get_canonical_json(data)
    can_2 = get_canonical_json(data)
    
    assert can_1 == can_2
    assert can_1 == b'{"a":1,"b":2,"c":[3,2,1],"d":null}'

