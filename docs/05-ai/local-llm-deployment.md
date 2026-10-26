# Local LLM Deployment & Safety

## Architecture
The LLM is deployed as a strictly internal service (`ai-engine`). It does not have public internet exposure.
It consumes Evidence JSON and outputs `llm-interpretation.schema.json`.

## Safety & Boundaries
1. **No External API Access:** The LLM does not query external databases or the internet.
2. **One-Way Data Flow:** Evidence JSON -> LLM. The LLM cannot alter evidence values, ranking, or drift physics.
3. **Schema Validation:** The output of the LLM is intercepted and validated against `llm-interpretation.schema.json` before being served to the frontend.
4. **Fallback:** If the LLM is offline, times out, or hallucinates schema-breaking JSON, the API returns a safe fallback indicating "Interpretation Unavailable" while retaining the core numerical Evidence JSON.

## Hardware Profile
- **Target:** CPU fallback with quantized weights (e.g., Llama 3 8B Q4_K_M).
- **RAM Minimum:** 16GB.
- **GPU (Optional):** CUDA integration supported but not mandated for CI.
