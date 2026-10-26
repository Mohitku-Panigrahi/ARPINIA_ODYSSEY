# Contributing to ARPINIA ODYSSEY

## Branching Strategy
- `main` is protected. No direct pushes.
- Create feature branches: `pod-b/feature-name` or `pod-a/model-update`.

## Pull Request Requirements
1. **Tests:** All tests must pass.
2. **Security:** Secret scanning (Gitleaks) must pass.
3. **Contract Validation:** Changes affecting Evidence JSON must be approved by all Pods.
4. **Review:** Require 1 approval from a different Pod.

## AI Agent Rules
Any AI agent coding in this repository MUST read `AGENTS.md` before executing any edits.
Agents cannot merge PRs or bypass security scanning.
