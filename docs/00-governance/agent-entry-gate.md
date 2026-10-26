# AI AGENT ENTRY GATE

Every AI coding agent entering this repository MUST execute this strict protocol:

1. **Read AGENTS.md**: Understand the repository constitution.
2. **Read PRE-CODE-GATE.md** and **SECURITY.md**: Understand readiness and constraints.
3. **Identify Task**: Clarify the specific requested feature/fix.
4. **Identify Owning Pod**: Refer to `team-ownership.md` to ensure authorization.
5. **Read Context**: Read PRD, MVP, architecture, and relevant contracts.
6. **Check RP/RESEARCH-INDEX.md**: Identify if any research papers in `rp/` contain methodologies relevant to the assigned task. If so, read them.
7. **Inspect Implementation**: Examine the current code state.
8. **Check Contracts**: Do NOT modify `packages/contracts/` without explicit approval.
9. **Check Ownership**: Do NOT modify files outside your assigned Pod.
10. **Check Security**: Ensure changes do not expose internal ports, DB, or leak secrets.
11. **Create Plan**: Propose an execution plan. Differentiate between experimental research methodologies and frozen project architecture. 
12. **Execute**: Only modify files once the plan is verified against security rules.

**RESEARCH USAGE RULES:**
- Methodologies found in `rp/` are reference only.
- They MUST NOT automatically override frozen contracts, architecture, or schemas.
- If a methodology contradicts the "Algorithm-First, AI-Assisted" design, DO NOT implement it. Instead, log it in `rp/RESEARCH-FINDINGS.md`.

**STOP CONDITIONS:**
If the task requires altering frozen schemas, fabricating data, exposing the DB, mixing LLM logic into deterministic physics, or blindly applying a research paper against architectural rules, you MUST halt and request human clarification.
