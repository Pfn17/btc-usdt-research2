# Owner governance memory

The project separates authority from implementation. **Owner decisions** are durable records of what the owner decided, why it was decided, and the scope to which it applies. **Agent recommendations** are suggestions that become authoritative only after an owner disposition of `APPROVED`. The authority order is: owner decision → governance rule → approved recommendation → task → implementation → verification.

The public dashboard reads only the bounded summary of the latest active owner decision and latest approved recommendation. It does not expose credentials, internal prompts, or the complete coordination history. Writes to these tables are trusted database operations; the public API is read-only.

Material changes must preserve the trace `OWNER DECISION → TASK → COMMIT → RESULT → VERIFICATION`. Frozen research parameters remain governed by the experiment ledger and may not be changed by an agent after seeing results.
