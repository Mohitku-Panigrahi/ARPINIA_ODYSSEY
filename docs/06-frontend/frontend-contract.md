# Frontend Integration Contract

## Architecture
- `apps/web/` runs Next.js.
- It consumes REST endpoints from `services/api/`.

## State Handling
1. **Loading:** Must gracefully handle prolonged loading states (backward drift takes time).
2. **Partial Success:** If the deterministic API returns Evidence JSON but the LLM route 504s, the frontend MUST display the Evidence and map, rendering an "AI Summary Unavailable" block rather than crashing the page.
3. **No Secrets:** The frontend must never receive `DATABASE_URL`, internal IPs, or any secret keys.
4. **Numerical Truth:** All rankings, probabilities, and times must be sourced directly from the deterministic Evidence JSON, never parsed from the LLM text.
