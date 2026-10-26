import time
import random
import logging
from datetime import timedelta, datetime
from typing import List, Dict, Optional, Any, Tuple
import numpy as np

from packages.geo.models import Point
from packages.ais.models import VesselTrajectory, B4Result
from packages.ais.correlation import CorrelationEngine
from packages.attribution.config import AttributionConfig
from packages.attribution.scoring import AttributionEngine
from packages.reconstruction.engine import ReconstructionEngine
from packages.reconstruction.models import ReconstructionConfig

from .config import MonteCarloConfig
from .models import (
    PerturbationSpec, CandidateRunResult, StabilityRunResult,
    EnsembleConvergence, AttributionStabilityResult, CandidateStatus, RunStatus, NominalStability
)
from .aggregation import StabilityAggregator

logger = logging.getLogger(__name__)

class StabilityRunner:
    def __init__(
        self, 
        mc_config: MonteCarloConfig,
        b3_engine_factory,
        b3_config_base: dict,
        b4_trajectories: List[VesselTrajectory],
        b5_config: AttributionConfig,
        scenario_id: str
    ):
        self.mc_config = mc_config
        self.b3_engine_factory = b3_engine_factory
        self.b3_config_base = b3_config_base
        self.b4_trajectories = b4_trajectories
        self.b5_config = b5_config
        self.scenario_id = scenario_id
        
        self.aggregator = StabilityAggregator(mc_config.minimum_runs, mc_config.minimum_valid_run_fraction)
        
    def _draw_perturbation(self, run_index: int) -> PerturbationSpec:
        seed = self.mc_config.master_seed + run_index
        rng = random.Random(seed)
        
        normal_val = rng.gauss(
            (self.mc_config.release_time_max_offset_hours + self.mc_config.release_time_min_offset_hours)/2.0, 
            self.mc_config.release_time_std_hours
        )
        rt_offset = max(
            self.mc_config.release_time_min_offset_hours,
            min(self.mc_config.release_time_max_offset_hours, normal_val)
        )
        
        return PerturbationSpec(
            run_id=f"{self.scenario_id}_mc_{run_index}",
            run_index=run_index,
            seed=seed,
            wind_uncertainty_ms=self.mc_config.wind_uncertainty_std_ms,
            current_uncertainty_ms=self.mc_config.current_uncertainty_std_ms,
            release_time_offset_hours=rt_offset,
            boundary_perturbation="DEFERRED",
            distribution="CLIPPED_NORMAL"
        )
        
    def check_convergence(self, checkpoints: List[int], last_stabilities, monitored_mmsis) -> Tuple[bool, Dict[str, Dict[str, float]]]:
        if len(checkpoints) < 2:
            return False, {}
            
        current = self.aggregator.get_all_stabilities()
        if len(current) == 0 and last_stabilities is not None and len(last_stabilities) == 0:
            return True, {}
            
        if not current or last_stabilities is None:
            return False, {}
            
        deltas = {}
        converged = True
        
        for mmsi in monitored_mmsis:
            c_curr = next((x for x in current if x.mmsi == mmsi), None)
            c_prev = next((x for x in last_stabilities if x.mmsi == mmsi), None)
            
            # If changed from present to absent or vice versa across checkpoints
            if bool(c_curr) != bool(c_prev):
                converged = False
                continue
                
            if c_curr and c_prev:
                d_t1 = abs(c_curr.top1_stability - c_prev.top1_stability)
                d_t3 = abs(c_curr.top3_stability - c_prev.top3_stability)
                d_pr = abs(c_curr.presence_rate - c_prev.presence_rate)
                
                # mean rank delta
                mr_c = c_curr.mean_rank or 0.0
                mr_p = c_prev.mean_rank or 0.0
                d_mr = abs(mr_c - mr_p)
                
                deltas[mmsi] = {"top1": d_t1, "top3": d_t3, "presence": d_pr, "mean_rank": d_mr}
                
                if (d_t1 > self.mc_config.convergence_tolerance or
                    d_t3 > self.mc_config.convergence_tolerance or
                    d_pr > self.mc_config.convergence_tolerance or
                    d_mr > 0.5): # e.g. 0.5 rank tolerance
                    converged = False
                
        return converged, deltas

    def run_nominal(self, t0: datetime, seed_polygon: List[Point]):
        logger.info("Running nominal B3-B5...")
        
        t3_0 = time.time()
        b3_conf = dict(self.b3_config_base)
        b3_conf['random_seed'] = self.mc_config.master_seed
        b3_conf['wind_uncertainty'] = 0.0
        b3_conf['current_uncertainty'] = 0.0
        b3 = self.b3_engine_factory(b3_conf)
        b3_res = b3.run_backward(seed_polygon, t0)
        t3_1 = time.time()
        
        t4_0 = time.time()
        b4_eng = CorrelationEngine(b3_res['time_slices'])
        cands, excls = b4_eng.correlate(self.b4_trajectories)
        b4_res = B4Result(
            scenario_id=self.scenario_id, ais_source="nominal", source_mode="mc", raw_artifact_hash=None,
            requested_time_window={}, requested_bbox={}, vessel_count=len(self.b4_trajectories),
            observation_count=0, candidate_count=len(cands), candidates=cands, excluded=excls, warnings=[], limitations=[], provenance={}
        )
        t4_1 = time.time()
        
        t5_0 = time.time()
        b5_eng = AttributionEngine(self.b5_config)
        ranking = b5_eng.score_candidates(b4_res, b3_res['time_slices'])
        t5_1 = time.time()
        
        self.aggregator.set_nominal(ranking)
        
        return ranking, (t3_1-t3_0), (t4_1-t4_0), (t5_1-t5_0)

    def run_ensemble(self, t0: datetime, seed_polygon: List[Point]):
        attempted = 0
        valid = 0
        failed = 0
        valid_no_cands = 0
        failure_reasons = {}
        
        checkpoints = []
        last_stabilities = None
        monitored_mmsis = set()
        
        if self.aggregator.nominal_ranking:
            for r in self.aggregator.nominal_ranking.ranked_candidates[:3]:
                monitored_mmsis.add(r.mmsi)
                
        convergence_achieved = False
        consecutive_converged = 0
        final_deltas = {}
        
        for i in range(self.mc_config.maximum_runs):
            self.aggregator.add_attempt()
            spec = self._draw_perturbation(i)
            attempted += 1
            
            try:
                p_t0 = t0 + timedelta(hours=spec.release_time_offset_hours)
                
                b3_conf = dict(self.b3_config_base)
                b3_conf['random_seed'] = spec.seed
                b3_conf['wind_uncertainty'] = spec.wind_uncertainty_ms
                b3_conf['current_uncertainty'] = spec.current_uncertainty_ms
                
                b3 = self.b3_engine_factory(b3_conf)
                b3_res = b3.run_backward(seed_polygon, p_t0)
                
                if not b3_res.get('time_slices'):
                    failed += 1
                    failure_reasons["RECONSTRUCTION_FAILED"] = failure_reasons.get("RECONSTRUCTION_FAILED", 0) + 1
                    continue
                    
                b4_eng = CorrelationEngine(b3_res['time_slices'])
                cands, excls = b4_eng.correlate(self.b4_trajectories)
                b4_res = B4Result(
                    scenario_id=self.scenario_id, ais_source="ensemble", source_mode="mc", raw_artifact_hash=None,
                    requested_time_window={}, requested_bbox={}, vessel_count=len(self.b4_trajectories),
                    observation_count=0, candidate_count=len(cands), candidates=cands, excluded=excls, warnings=[], limitations=[], provenance={}
                )
                
                b5_eng = AttributionEngine(self.b5_config)
                ranking = b5_eng.score_candidates(b4_res, b3_res['time_slices'])
                
                valid += 1
                if not ranking.ranked_candidates and not ranking.insufficient_evidence_candidates:
                    valid_no_cands += 1
                
                run_res = []
                for j, r in enumerate(ranking.ranked_candidates):
                    status = CandidateStatus.EFFECTIVELY_TIED if r.status == "EFFECTIVELY_TIED" else CandidateStatus.RANKED
                    run_res.append(CandidateRunResult(
                        run_id=spec.run_id, mmsi=r.mmsi, rank=j+1,
                        attribution_score=r.attribution_relevance_score,
                        evidence_coverage=r.evidence_coverage.value, status=status
                    ))
                for r in ranking.insufficient_evidence_candidates:
                    run_res.append(CandidateRunResult(
                        run_id=spec.run_id, mmsi=r.mmsi, rank=None,
                        attribution_score=r.attribution_relevance_score,
                        evidence_coverage=r.evidence_coverage.value, status=CandidateStatus.INSUFFICIENT_EVIDENCE
                    ))
                    
                self.aggregator.add_valid_run(run_res)
                
            except Exception as e:
                logger.error(f"Run {i} failed: {e}")
                failed += 1
                failure_reasons["OTHER"] = failure_reasons.get("OTHER", 0) + 1
                
            if valid > 0 and valid % self.mc_config.convergence_check_interval == 0:
                checkpoints.append(valid)
                current_stabilities = self.aggregator.get_all_stabilities()
                
                for r in current_stabilities[:3]:
                    monitored_mmsis.add(r.mmsi)
                    
                conv, deltas = self.check_convergence(checkpoints, last_stabilities, monitored_mmsis)
                last_stabilities = current_stabilities
                
                if conv:
                    consecutive_converged += 1
                else:
                    consecutive_converged = 0
                    
                if consecutive_converged >= self.mc_config.convergence_patience and valid >= self.mc_config.minimum_runs:
                    convergence_achieved = True
                    final_deltas = deltas
                    break
                    
        stabilities = self.aggregator.get_all_stabilities()
        nom_leader_mmsi = self.aggregator.nominal_ranking.ranked_candidates[0].mmsi if self.aggregator.nominal_ranking and self.aggregator.nominal_ranking.ranked_candidates else None
        nom_stable = NominalStability.INSUFFICIENT_EVIDENCE
        if nom_leader_mmsi:
            nl_stab = next((s for s in stabilities if s.mmsi == nom_leader_mmsi), None)
            if nl_stab:
                if nl_stab.stability_class.value in ["HIGH_STABILITY", "MODERATE_STABILITY"]:
                    nom_stable = NominalStability.YES
                else:
                    nom_stable = NominalStability.NO
                    
        return AttributionStabilityResult(
            scenario_id=self.scenario_id,
            algorithm_version=self.mc_config.algorithm_version,
            config_version=self.mc_config.configuration_version,
            total_attempted_runs=attempted,
            valid_runs=valid,
            failed_runs=failed,
            valid_no_candidate_runs=valid_no_cands,
            failure_reason_counts=failure_reasons,
            convergence=EnsembleConvergence(
                achieved=convergence_achieved,
                runs_executed=valid,
                checkpoints=checkpoints,
                top_candidate_deltas=final_deltas,
                consecutive_converged_checks=consecutive_converged
            ),
            candidate_stabilities=stabilities,
            nominal_leader_mmsi=nom_leader_mmsi,
            nominal_leader_stable=nom_stable
        )
