# DEVELOPMENT WORKFLOW

The standard development loop for humans and agents:

1. **READ RULES**: Check `AGENTS.md` and `architecture-freeze.md`.
2. **TAKE ASSIGNED TASK**: Branch from `main` (e.g., `pod-b/feature-name`).
3. **BUILD**: Implement the feature within Pod boundaries.
4. **TEST**: Run unit/integration tests and Golden Scenario validators.
5. **SECURITY CHECK**: Ensure no secrets are embedded.
6. **COMMIT**: Use semantic commit messages (`feat:`, `fix:`, `chore:`).
7. **PR**: Open a Pull Request targeting `main`. Fill out the PR template.
8. **REVIEW**: Requires 1 cross-pod approval. CI runs Bandit and Gitleaks.
9. **MERGE**: Squash and merge into `main`.
