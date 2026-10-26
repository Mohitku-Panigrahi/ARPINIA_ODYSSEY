# Backend Development Rules

## Architecture
- `services/api/` handles HTTP, auth, and DB orchestration.
- `services/worker/` handles long-running jobs (OpenDrift, AIS queries) via Redis/Celery.

## Security
1. **No Direct Ground Truth:** The worker MUST NEVER open `data/samples/golden-scenario-v1/ground_truth.json`.
2. **Input Validation:** All payloads must be Pydantic-validated.
3. **No Shell Injection:** Use strict param bindings for PostGIS. Never use `os.system` with user input.
4. **Logging:** Never log raw environment variables, passwords, or LLM API keys. Use structured JSON logging.
