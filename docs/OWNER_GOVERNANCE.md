# Owner governance memory

The project separates authority from implementation. **Owner decisions** are durable records of what the owner decided, why it was decided, and the scope to which it applies. **Agent recommendations** are suggestions that become authoritative only after an owner disposition of `APPROVED`. The authority order is: owner decision → governance rule → approved recommendation → task → implementation → verification.

The primary research dashboard does **not** render or poll the governance memory. The governance summary endpoint remains available as a bounded read-only surface for governance tooling, while the research dashboard stays limited to research results, evidence, and system observability. The governance layer does not expose credentials, internal prompts, or the complete coordination history. Writes to these tables are trusted database operations; the public API is read-only.

Material changes must preserve the trace `OWNER DECISION → TASK → COMMIT → RESULT → VERIFICATION`. Frozen research parameters remain governed by the experiment ledger and may not be changed by an agent after seeing results.
