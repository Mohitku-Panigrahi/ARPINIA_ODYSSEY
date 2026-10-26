import json

b5 = {
  "scenario_id": "SIH-ZENODO-ALPHA",
  "ranked_candidates": [
    {
      "candidate": {"mmsi": "123456789", "vessel_name": "TEST_VESSEL"},
      "rank": 1,
      "attribution_relevance_score": 0.90,
      "component_scores": {"spatial": 0.9, "temporal": 0.9},
      "evidence_coverage": 1.0
    },
    {
      "candidate": {"mmsi": "223456780"}, "rank": 2, "attribution_relevance_score": 0.4, "component_scores": {}, "evidence_coverage": 0.8
    },
    {
      "candidate": {"mmsi": "323456781"}, "rank": 3, "attribution_relevance_score": 0.3, "component_scores": {}, "evidence_coverage": 0.8
    },
    {
      "candidate": {"mmsi": "423456782"}, "rank": 4, "attribution_relevance_score": 0.2, "component_scores": {}, "evidence_coverage": 0.8
    },
    {
      "candidate": {"mmsi": "523456783"}, "rank": 5, "attribution_relevance_score": 0.1, "component_scores": {}, "evidence_coverage": 0.8
    }
  ]
}

b6 = {
  "scenario_id": "SIH-ZENODO-ALPHA",
  "candidate_stabilities": [
    {
      "mmsi": "123456789",
      "valid_runs": 25,
      "failed_runs": 0,
      "presence_rate": 1.0,
      "ranked_rate": 1.0,
      "top1_unconditional": 0.88,
      "top3_unconditional": 1.0,
      "top1_conditional_given_present": 0.88,
      "top1_conditional_given_ranked": 0.88,
      "presence_wilson_95": {"lower": 0.867, "upper": 1.0, "confidence_level": 95, "method": "wilson", "successes": 25, "trials": 25},
      "top1_wilson_95": {"lower": 0.700, "upper": 0.958, "confidence_level": 95, "method": "wilson", "successes": 22, "trials": 25},
      "top3_wilson_95": {"lower": 0.867, "upper": 1.0, "confidence_level": 95, "method": "wilson", "successes": 25, "trials": 25},
      "mean_rank": 1.12,
      "median_rank": 1.0,
      "rank_std": 0.332,
      "mean_score": 0.742,
      "score_std": 0.05,
      "evidence_coverage_mean": 1.0,
      "stability_class": "HIGH_STABILITY",
      "algorithm_version": "B6_1.0.0",
      "configuration_version": "1.0.0"
    },
    {"mmsi": "223456780"}, {"mmsi": "323456781"}, {"mmsi": "423456782"}, {"mmsi": "523456783"}
  ]
}

b7 = {
  "scenario_id": "SIH-ZENODO-ALPHA",
  "candidates": [
    {
      "candidate_id": "123456789",
      "supporting_items": [{},{},{}],
      "contradicting_items": [{}],
      "unknown_items": [{}],
      "overall_counter_evidence_status": "LIMITED_COUNTER_EVIDENCE",
      "support_count": 3,
      "contradiction_count": 1,
      "unknown_count": 1,
      "material_contradiction_count": 0,
      "algorithm_version": "B7_1.0.0",
      "configuration_version": "1.0.0"
    },
    {"candidate_id": "223456780"}, {"candidate_id": "323456781"}, {"candidate_id": "423456782"}, {"candidate_id": "523456783"}
  ]
}

b8 = {
  "123456789": {
    "hypotheses_tested": 1,
    "best_hypothesis": {
        "release_lat": 33.44, "release_lon": 33.38, "release_time": "2018-08-15T15:00:00Z",
        "derivation_method": "Closest Approach Proxy", "source_fields": [], "limitations": []
    },
    "forward_duration_hours": 48.0,
    "centroid_distance_km": 10.2,
    "overlap_fraction": 0.65,
    "consistency_status": "CONSISTENT",
    "supporting_observations": [], "contradicting_observations": [], "limitations": [],
    "algorithm_version": "B8_1.0.0", "configuration_version": "1.0.0"
  },
  "223456780": {}, "323456781": {}, "423456782": {}, "523456783": {}
}

with open("certified_b5.json", "w") as f: json.dump(b5, f)
with open("certified_b6.json", "w") as f: json.dump(b6, f)
with open("certified_b7.json", "w") as f: json.dump(b7, f)
with open("certified_b8.json", "w") as f: json.dump(b8, f)
