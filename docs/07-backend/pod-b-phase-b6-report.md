# POD B PHASE B6 - MONTE-CARLO ATTRIBUTION STABILITY ENGINE

## OBJECTIVE
Quantify attribution stability by evaluating whether a candidate remains highly ranked when physically plausible uncertainty in reconstruction inputs is introduced. This avoids treating a nominal single-run winner as a confirmed polluter.

## ARCHITECTURE
- **Orchestration Layer**: Uses the StabilityRunner to repeatedly invoke frozen B3, B4, and B5 engines.
- **Uncertainty Generation**: Uses OpenDrift's native wind_uncertainty and current_uncertainty turbulent diffusion sub-grid algorithms, parameterized in m/s, driven by a deterministic per-run andom_seed derived from a master_seed. Release time is perturbed externally via a clipped normal offset applied to 	0.
- **Streaming Aggregation**: Uses Welford's online algorithm to compute running means and variances (O(1) space per candidate). Retains a sparse rank-count histogram for exact median extraction to guarantee pure O(K_rank * C) space, independent of ensemble size R. Large OpenDrift simulation state is discarded per-run.
- **Convergence Stopping**: Monitored iteratively across Top-K candidates. Requires multiple consecutive checks to remain below threshold (configured patience). Checks ?Top-1, ?Top-3, ?Presence, and ?Mean Rank.

## UNCERTAINTY VARIABLES
1. **Wind/Current Perturbation**: Handled as internal random walk parameterization in B3 via wind_uncertainty_std_ms and current_uncertainty_std_ms. Units: m/s. Mean: 0. Stochastically perturbed at each step.
2. **Release Time**: Shifted via a bounded, clipped normal distribution relative to detection.
3. **Boundary/Seed Geometry**: Deferred, pending Pod A segmentation uncertainty models.

## METRICS
- **Top-1 / Top-3 Stability**: Proportion of valid runs where the candidate ranked #1 or <= #3.
- **Presence Rate**: Proportion of valid runs where the candidate survived B4 filtering (was present).
- **Conditional Top-1 Given Present**: Top-1 frequency given that the candidate survived B4.
- **Conditional Top-1 Given Ranked**: Top-1 frequency given that the candidate was ranked by B5.
- **Absence Semantics**: "Absent" means B4 excluded the vessel entirely (0% evidence coverage). "Insufficient Evidence" means it survived B4 but B5 rejected it due to coverage floors. "Ranked" means it successfully entered the leaderboard.

## DATA STRUCTURES & COMPLEXITY
- **Aggregation Space Complexity**: O(C * K_rank) where C is the size of the global candidate universe and K_rank is the number of distinct ranks. 
- **Time Complexity**: O(R * cost(B3)) where R is the number of ensemble runs.

## SECURITY & PROVENANCE
- Fully deterministic (master_seed).
- Tested for reproducible RNG, valid run tracking, convergence patience, and streaming aggregation correctness.
- No public-source copying; fully original orchestration layer.
- Secrets/hardcoded paths: None.
- Strict enums prevent tyops.

## LIMITATIONS
- True truncated normal for 	0 perturbation relies on a clipped Gaussian to avoid introducing SciPy as a heavy backend dependency for one function.
- Real Golden B6 Validation relies on simulated/mocked B3 fallback due to local environment missing actual NetCDF CMEMS current velocity forcing files. Therefore real performance tracking relies on the mocked execution.
