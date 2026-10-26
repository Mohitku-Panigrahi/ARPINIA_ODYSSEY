# POD B PHASE B6 - SOURCE BASIS

## ENVIRONMENTAL UNCERTAINTY IN DRIFT MODELLING
- **Title**: OpenDrift: a generic framework for trajectory modelling
- **Authors**: Dagestad, K.-F., Röhrs, J., Breivik, Ø., & Ådlandsvik, B.
- **Year**: 2018
- **DOI/Reference**: 10.5194/gmd-11-1405-2018
- **Principle Supported**: Sub-grid scale turbulent diffusion and forcing error parameterization via random walk (wind_uncertainty, current_uncertainty).
- **Odyssey Implementation**: B6 uses the OpenDrift internal random walk configurations by injecting a varying andom_seed per ensemble run, maintaining constant macroscopic standard deviations.
- **Limitation**: Does not inject macroscopic non-zero-mean bias fields without structural modifications.

## RELEASE-TIME UNCERTAINTY
- **Title**: Uncertainty Analysis of Oil Spill Trajectory Modeling
- **Authors**: Standard Operational Practice at NOAA/OR&R
- **Year**: N/A (Standard heuristic)
- **Reference**: Operational practice
- **Principle Supported**: Spill age is inherently uncertain due to detection delays.
- **Odyssey Implementation**: Perturbs 	0 backward using a bounded clipped normal distribution.
- **Limitation**: Does not yet continuously leak oil over time; shifts the instant point release.

## STATISTICAL CONVERGENCE IN ENSEMBLES
- **Title**: SOURCE BASIS INCOMPLETE
- **Authors**: Internal Odyssey Design
- **Odyssey Implementation**: Checkpoints every N runs; stops when Top-K Top-1/Top-3/Presence/Mean-Rank stabilities vary by less than a tolerance epsilon for consecutive checks.

## BINOMIAL PROPORTION CONFIDENCE INTERVALS
- **Title**: Probable error of a mean
- **Authors**: Wilson, E. B.
- **Year**: 1927
- **DOI/Reference**: 10.1080/01621459.1927.10502953
- **Principle Supported**: The Wilson score interval is an improvement over the normal approximation interval for binomial proportions, especially for extreme probabilities and small N.
- **Odyssey Implementation**: Used to provide 95% confidence bounds around Top-1, Top-3, and Presence rate frequency point estimates.
