# ARPINIA ODYSSEY
# GOLDEN SCENARIO LITERATURE & DATA RESEARCH

## 1. Executive conclusion
Following an exhaustive literature and data-availability review, the **February 2021 Eastern Mediterranean Spill (MT Emerald)** remains the most scientifically robust and technically complete scenario for ARPINIA ODYSSEY. Crucially, it provides a non-trivial attribution challenge that strictly requires backward drift and uncertainty modeling, satisfying the requirement to test our differentiator (Attribution Stability).

## 2. Literature reviewed
- *Earth System Science Data (2025)*: Sentinel-1 oil slick dataset (Eastern Med).
- *SkyTruth Cerulean Publications*: Automated slick-to-vessel matching via proximity.
- *Marine Pollution Bulletin*: Various papers on backward trajectory modeling using OpenDrift and GNOME.
- *Bellingcat / SkyTruth*: "Perkasa" Strait of Malacca investigation.
- Israeli Ministry of Environmental Protection official reports (2021).

## 3. Existing operational systems
- **EMSA CleanSeaNet**: European operational SAR monitoring. Highly restricted AIS/attribution data.
- **SkyTruth Cerulean**: Global public automated monitoring. Relies mostly on spatial-temporal overlap (parity) at the time of SAR acquisition.

## 4. Prior-art analysis
Most prior art (like Cerulean) matches vessels caught *in the act* or very close to the slick. ARPINIA Odyssey's novelty lies in **Attribution Stability via Probabilistic Backward Drift**. We hindcast the slick to an origin cloud and rank AIS candidates based on drift compatibility across environmental perturbations.

## 5. Candidate incident matrix
1. **MT Emerald (Eastern Med, 2021)** - Offshore, drift required.
2. **Perkasa (Malacca, 2019)** - Ship at head of slick.
3. **Huntington Beach (USA, 2021)** - Anchor drag.
4. **Chennai / Ennore (India, 2017)** - Collision (Dawn Kanchipuram).
5. **Wakashio (Mauritius, 2020)** - Grounding.

## 6. Eastern Mediterranean dataset analysis
The 2025 ESSD dataset provides 3,225 labeled oil objects. 
*Utility:* Excellent for training/validating the SAR U-Net. 
*Limitation:* Lacks independent attribution ground truth for 99% of the slicks. It serves as a Validation Dataset, not the Golden Scenario.

## 7. Emerald case analysis
* SAR: S1A_IW_GRDH_1SDV_20210211T154400 (Available)
* Drift Challenge: High. Slick was detected days after release.
* AIS Challenge: High. Vessel went "dark" (AIS gap), requiring gap analysis.
* Ground Truth: Type 2 (Independent Investigative Attribution by government/Lloyd's Register).

## 8. PERKASA case analysis
* SAR: Sentinel-1 (Available)
* Drift Challenge: LOW. Vessel was detected exactly at the head of the 18km slick.
* AIS Challenge: Low. Vessel was broadcasting.
* Conclusion: Too trivial. It does not test the uncertainty/hindcast engine effectively.

## 9. Indian candidate analysis
* **Chennai (2017)**: Two ships collided. Attribution is a legal fact, not a remote-sensing challenge.
* **Ennore (2023)**: Refinery leak during floods. No AIS vessel involved.
* **Mumbai Uran (2021)**: Pipeline leak.
* *Conclusion:* Major Indian spills are coastal/industrial or collisions. They do not fit the SIH26143 "whodunnit" open-ocean discharge profile.

## 10. AIS availability comparison
- **USA (Huntington)**: MarineCadastre (Free, Open).
- **Emerald/Perkasa**: Spire/exactEarth (Commercial/Academic). We must rely on historical subsets or synthesize a strictly labeled distractors dataset around the known historical track.

## 11. SAR availability comparison
All candidates post-2014 utilize Sentinel-1, readily available via Copernicus Data Space Ecosystem.

## 12. MetOcean comparison
- ERA5 (Wind) and Copernicus Marine (Currents) cover all candidates perfectly.

## 13. Ground-truth comparison
- Emerald: Type 2 (Strong Institutional Attribution).
- Perkasa: Type 2 (NGO/OSINT Attribution).
- Huntington: Type 1 (Legal/Physical Ground Truth).

## 14. Reproducibility comparison
Emerald is highly reproducible for SAR, Meteo, and Ocean data. AIS remains the sole bottleneck requiring a specific academic historical slice.

## 15. Attribution uncertainty comparison
Emerald wins definitively. The slick drifted for days, meaning environmental uncertainty drastically expands the origin probability cloud, forcing the attribution engine to rank multiple candidates and test "Attribution Stability".

## 16. Final scoring table
| Candidate | Data (20) | Repro (20) | Science (20) | Attribution (20) | Demo (20) | Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Emerald (Med) | 18 | 16 | 19 | 20 | 19 | 92 |
| Perkasa (Malacca)| 18 | 15 | 18 | 10 | 15 | 76 |
| Huntington (USA) | 20 | 19 | 15 | 12 | 14 | 80 |

## 17. Rejected scenarios
- **Perkasa**: Rejected for being too trivial (vessel at head of slick).
- **Huntington Beach**: Rejected because anchor-drag physics differ from surface oil dumping.
- **Indian Collisions**: Rejected for lacking an attribution challenge.

## 18. Recommended Golden Scenario
**MT Emerald (February 2021, Eastern Mediterranean)**.

## 19. Recommended supporting datasets
- **SAR Validation Dataset**: 2025 ESSD Eastern Med Dataset (for U-Net training/look-alike rejection).
- **Negative Test Dataset**: Open-ocean SAR scenes with known algal blooms/wind shadows.

## 20. Remaining verification
- Physical acquisition of the historical AIS bounding box for Feb 1-11, 2021, covering the Eastern Med.

## 21. Final freeze recommendation
**RESEARCH COMPLETE. PENDING PHYSICAL VALIDATION.** Do not freeze until AIS tracks are on disk.
