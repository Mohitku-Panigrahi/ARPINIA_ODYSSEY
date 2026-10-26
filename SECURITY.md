# Security Policy

## Supported Versions
Only the `main` branch is actively supported with security updates.

## Reporting a Vulnerability
DO NOT create a public issue for security vulnerabilities.
Contact the lead maintainer (Rudra) directly.

## Secret Management (Agent & Human Rules)
1. **Never commit secrets:** API keys, DB passwords, and model weights MUST NOT be committed.
2. **.env files:** All `.env` files are in `.gitignore`. Use `.env.example` for templates.
3. **Secret Scanning:** All PRs are scanned using GitHub Actions (Gitleaks).
4. **Golden Scenario Ground Truth:** `ground_truth.json` is treated as a sensitive operational secret. The inference pipeline MUST NOT read it.

## Network Security Boundary
- The Frontend (`apps/web`) communicates ONLY with the `api` service.
- The `api` service communicates with `worker`, `ai-engine`, and `database`.
- **PostgreSQL, Redis, and AI endpoints are strictly bound to internal Docker networks.** They must NEVER bind to `0.0.0.0` on the host outside of local dev loops without an explicit proxy.
