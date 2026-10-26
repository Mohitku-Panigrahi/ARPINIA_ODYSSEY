# ARPINIA ODYSSEY — GOLDEN SCENARIO RESEARCH

## 1. Re-Evaluation Based on SIH26143 Guidelines
Our prior research selected the **MT Emerald (Feb 2021)** incident as the Golden Scenario. However, a rigorous audit against SIH26143 constraints reveals a critical reproducibility flaw: Historical AIS for the Eastern Med is commercial. 

SIH guidelines explicitly provide:
1. MarineCadastre / AccessAIS (US waters)
2. Sentinel-1 SAR Oil Spill Dataset via Zenodo
3. Permission to use `SYNTHETIC_DEMO` AIS if historical AIS is unavailable.

## 2. Status of MT Emerald
**Status: RESEARCH_VALIDATION_ONLY**
MT Emerald remains our scientific benchmark for attribution stability. However, because its historical AIS is locked behind commercial paywalls (Spire/exactEarth), it fails the "reproducible by anyone" test. It cannot be the primary Golden Scenario.

## 3. New Candidate: SIH-Zenodo-Alpha
We select a high-confidence, confirmed oil slick scene from the **Zenodo Sentinel-1 SAR Oil Spill Dataset**.
- **SAR**: Verified Zenodo open-access SAR scene.
- **MetOcean**: ERA5 / Copernicus Marine (Globally accessible).
- **AIS**: `SYNTHETIC_DEMO`. We will generate a mathematically realistic AIS dataset for the exact temporal/spatial bounding box of the SAR scene. It will include 1 primary candidate, 5 distractors, and realistic SOG/COG distributions.
- **Ground Truth**: The Zenodo mask provides the SAR ground truth. The Synthetic AIS generation script provides the attribution ground truth (which is strictly isolated from the inference engine).

## 4. Scoring: SIH-Zenodo-Alpha
1. Dataset accessibility (20/20) - Fully open.
2. Metadata completeness (15/15) - Zenodo + ERA5 are perfect.
3. Geographic suitability (15/15) - Flexible.
4. Temporal suitability (15/15) - Flexible.
5. Availability of AIS (15/15) - Explicitly Synthetic Demo (SIH approved).
6. Oil-spill segmentation quality (10/10) - Pre-annotated ground truth.
7. Backward drift demo (5/5) - Fully supported by ERA5.
8. SIH demonstration (5/5) - Perfectly aligned.
**Total: 100/100**
