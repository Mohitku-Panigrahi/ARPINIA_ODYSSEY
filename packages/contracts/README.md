# ARPINIA ODYSSEY - CONTRACTS

**THESE SCHEMAS ARE THE COMMUNICATION PROTOCOL BETWEEN INDEPENDENT SUBSYSTEMS.**

## SACRED DIRECTORY WARNING
Breaking or modifying a contract in this directory requires a formal Architecture Change Request (see docs/00-governance/change-control.md). 

- Pod 1 (AI), Pod 2 (Backend), and Pod 3 (Frontend) rely completely on the structural guarantees provided by these JSON schemas.
- Do NOT casually add, rename, or delete fields.
- Do NOT bypass these schemas.

If a change is required:
1. Request architecture review.
2. Update the schema here.
3. Bump the schema version.
4. Update the test suites.

## SEMANTIC DEFINITIONS

- **attribution score != guilt**: The attribution score measures physical and trajectory alignment based on environmental data, not legal responsibility.
- **stability != guilt probability**: Attribution stability is robustness under modeled environmental uncertainty, not probability of guilt.
- **counter-evidence != innocence**: Evidence contradicting a candidate hypothesis does not automatically clear the vessel; it highlights physical or temporal limits.
- **forward consistency != independent proof**: Forward physical simulation consistency relies on backward reconstructed hypotheses; it is not an independent proof of source.
- **unknown != contradicting evidence**: Missing or unknown evidence must never be serialized or treated as contradicting evidence.
