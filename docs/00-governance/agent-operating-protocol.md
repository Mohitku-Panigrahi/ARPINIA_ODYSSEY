# ARPINIA ODYSSEY — AGENT OPERATING PROTOCOL

## 1. MANDATORY WORKFLOW
Every AI agent or automated worker interacting with this repository MUST follow this sequence:

1. **RECEIVE TASK**
2. **READ CONSTITUTION + CONTRACTS**
3. **INSPECT REPOSITORY**
4. **IDENTIFY AUTHORITY + OWNERSHIP** (Ensure you are not crossing Pod boundaries)
5. **CREATE PLAN**
6. **IMPLEMENT**
7. **TEST**
8. **SECURITY CHECK**
9. **CONTRACT CHECK** (Ensure output schemas match `packages/contracts`)
10. **REPORT**

## 2. "DO NOT TRUST THE AGENT" BOUNDARIES
You are an implementation agent, not an architectural authority.

**AGENT MAY:**
- Inspect, reason, and plan.
- Implement code within assigned Pod boundaries.
- Test and refactor implementation code.
- Report problems and contradictions.

**AGENT MAY NOT:**
- Redefine product requirements or architecture.
- Change frozen contracts (`evidence.schema.json`, `llm-interpretation.schema.json`).
- Change Pod ownership boundaries.
- Declare a security exception.
- Fabricate missing information, dataset identifiers, or checksums.
- Silently substitute datasets.
- Silently replace mathematical algorithms with LLM prompts.

## 3. CONTRADICTION RESOLUTION
If requirements conflict, or if existing code violates a contract:
**STOP → REPORT → REQUEST DECISION.** Do not silently "fix" the architecture.
