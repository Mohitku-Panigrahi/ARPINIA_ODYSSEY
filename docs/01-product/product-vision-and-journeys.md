# PRODUCT VISION & USER JOURNEYS

## Vision
ARPINIA Odyssey is a deterministic maritime investigation platform for NTRO Disaster Management. It converts multi-source evidence into an auditable vessel attribution package. 

## Primary User Journey
1. **Ingest**: User uploads SAR imagery to the dashboard.
2. **Analyze**: System segments spill and triggers backward drift (OpenDrift).
3. **Filter**: System queries AIS to find candidate vessels intersecting the origin probability cloud.
4. **Score**: Attribution Engine ranks candidates based on proximity, drift match, and behavioral anomalies.
5. **Interpret**: Evidence JSON is finalized and passed to the Local LLM for plain-text explanation.
6. **Report**: User downloads the finalized PDF forensic report.

## Limitations
- Not legally binding. Provides decision-support only.
- Relies on historical AIS availability.
