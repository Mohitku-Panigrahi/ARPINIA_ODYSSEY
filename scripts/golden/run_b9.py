import json
import hashlib
from datetime import datetime, timezone
from packages.evidence.builder import EvidenceBuilder

def main():
    with open("artifacts/golden/certified_b5.json") as f: b5 = json.load(f)
    with open("artifacts/golden/certified_b6.json") as f: b6 = json.load(f)
    with open("artifacts/golden/certified_b7.json") as f: b7 = json.load(f)
    with open("artifacts/golden/certified_b8.json") as f: b8 = json.load(f)

    builder = EvidenceBuilder()
    
    # Merge candidates
    for b5_cand in b5["ranked_candidates"]:
        mmsi = b5_cand["candidate"]["mmsi"]
        
        # find in b6
        b6_cand = next((c for c in b6["candidate_stabilities"] if c.get("mmsi") == mmsi), {})
        # find in b7
        b7_cand = next((c for c in b7["candidates"] if c.get("candidate_id") == mmsi), {})
        # find in b8
        b8_cand = b8.get(mmsi, {})

        cand = {
            "mmsi": mmsi,
            "rank": b5_cand.get("rank"),
            "vessel_name": b5_cand["candidate"].get("vessel_name"),
            "attribution": {
                "score": b5_cand.get("attribution_relevance_score"),
                "stability": b6_cand.get("top1_unconditional", 0.0), # DEPRECATED scalar
                "confidence": b5_cand.get("attribution_relevance_score"),
                "status": "CANDIDATE"
            },
            "evidence_for": [], # DEPRECATED
            "evidence_against": [], # DEPRECATED
            "trajectory": {
                "distance_to_origin_km": b8_cand.get("centroid_distance_km", 0.0),
                "temporal_offset_hours": 0.0,
                "drift_compatibility": 0.0
            },
            "behavior": {},
            "stability": {
                "valid_runs": b6_cand.get("valid_runs", 0),
                "failed_runs": b6_cand.get("failed_runs", 0),
                "presence_rate": b6_cand.get("presence_rate", 0.0),
                "ranked_rate": b6_cand.get("ranked_rate", 0.0),
                "top1_unconditional": b6_cand.get("top1_unconditional", 0.0),
                "top3_unconditional": b6_cand.get("top3_unconditional", 0.0),
                "top1_conditional_given_present": b6_cand.get("top1_conditional_given_present", 0.0),
                "top1_conditional_given_ranked": b6_cand.get("top1_conditional_given_ranked", 0.0),
                "mean_rank": b6_cand.get("mean_rank", 0.0),
                "median_rank": b6_cand.get("median_rank", 0.0),
                "rank_std": b6_cand.get("rank_std", 0.0),
                "mean_score": b6_cand.get("mean_score", 0.0),
                "score_std": b6_cand.get("score_std", 0.0),
                "evidence_coverage_mean": b6_cand.get("evidence_coverage_mean", 0.0),
                "stability_class": b6_cand.get("stability_class", "UNSTABLE"),
                "algorithm_version": b6_cand.get("algorithm_version", "B6_1.0.0"),
                "configuration_version": b6_cand.get("configuration_version", "1.0.0")
            },
            "counter_evidence": {
                "supporting_items": b7_cand.get("supporting_items", []),
                "contradicting_items": b7_cand.get("contradicting_items", []),
                "unknown_items": b7_cand.get("unknown_items", []),
                "overall_counter_evidence_status": b7_cand.get("overall_counter_evidence_status", "INSUFFICIENT_EVIDENCE"),
                "support_count": b7_cand.get("support_count", 0),
                "contradiction_count": b7_cand.get("contradiction_count", 0),
                "unknown_count": b7_cand.get("unknown_count", 0),
                "material_contradiction_count": b7_cand.get("material_contradiction_count", 0),
                "algorithm_version": b7_cand.get("algorithm_version", "B7_1.0.0"),
                "configuration_version": b7_cand.get("configuration_version", "1.0.0")
            }
        }
        
        if "presence_wilson_95" in b6_cand:
            cand["stability"]["presence_wilson_95"] = b6_cand["presence_wilson_95"]
            cand["stability"]["top1_wilson_95"] = b6_cand["top1_wilson_95"]
            cand["stability"]["top3_wilson_95"] = b6_cand["top3_wilson_95"]
            
        if b8_cand.get("consistency_status"):
            cand["forward_consistency"] = b8_cand
        else:
            cand["forward_consistency"] = {
                "hypotheses_tested": 0,
                "consistency_status": "NOT_COMPUTABLE",
                "supporting_observations": [],
                "contradicting_observations": [],
                "limitations": [],
                "algorithm_version": "B8_1.0.0",
                "configuration_version": "1.0.0"
            }
            
        builder.add_candidate(cand)
        
    sha256 = builder.write_canonical("evidence.json")
    print("Generated evidence.json with SHA:", sha256)

if __name__ == '__main__':
    main()
