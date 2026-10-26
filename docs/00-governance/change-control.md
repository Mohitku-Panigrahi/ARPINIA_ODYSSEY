# ARPINIA ODYSSEY — CHANGE CONTROL

Changes to Architecture (Level 2) or Contracts (Level 1) follow a strict lifecycle.

## The Change Process
1. **Request:** A Pod identifies a missing field or architectural block.
2. **Architecture Review:** The Principal Architect (Rudra) evaluates the request against ADR-001.
3. **Contract Change:** The JSON Schema or API Contract is updated.
4. **Version Bump:** Schema versions increment (e.g., `v1.0.0` -> `v1.1.0`).
5. **Affected Pods Notified:** Consumers of the contract are alerted.
6. **Tests Updated:** `scripts/governance/` and `tests/` are aligned to the new contract.

## Forbidden Actions
- Pod 3 (Frontend) cannot demand Pod 2 (Backend) add random JSON fields without this process.
- Pod 1 (AI) cannot silently alter the SAR bounding box format passed to Pod 2.
