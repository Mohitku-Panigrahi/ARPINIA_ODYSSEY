# DATABASE SCHEMA & ISOLATION

## Engine
PostgreSQL with PostGIS extension.

## Core Entities
1. **Incidents**: Stores SAR metadata, upload timestamps, and spill polygons (Geometry).
2. **Investigations**: Tracks pipeline state, links to Incidents.
3. **AIS_Tracks**: Spatiotemporal points for vessels (Geometry, MMSI, Timestamp).
4. **Candidates**: Computed subset of vessels matching drift profiles.
5. **Evidence_Records**: The finalized Evidence JSON stored as `JSONB`.

## Security & Isolation
- **LLM Restriction**: The Local LLM HAS NO DIRECT DATABASE ACCESS. It only receives the Evidence JSON payload over HTTP.
- **Network**: Port 5432 is strictly bound to the `backend-net` Docker network. The frontend cannot query the DB directly.
