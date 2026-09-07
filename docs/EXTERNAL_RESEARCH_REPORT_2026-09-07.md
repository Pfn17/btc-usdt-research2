# External Research Report — H-SW1

**Received:** 2026-09-07 11:01 local task time  
**Source:** Attachment supplied by the project owner, attributed to an external Claude session  
**Repository writer:** Manus  
**Verification state:** **UNVERIFIED**

## Scope

The attachment proposes a new swing-lite hypothesis named `H-SW1` in family `fam-swing-v1`. It describes a 24-hour holding horizon, agreement between the prior 24-hour return and the sign of the last three funding events, and a period-concentration check.

The attachment reports an initial result of `N=37`, gross EV approximately `+14.73 bps`, net EV approximately `+4.73 bps`, win rate `54.05%`, and a wide net confidence interval. It also reports inconsistent quarterly results and labels the outcome `inconclusive_underpowered_period_unstable`.

## Verification boundary

This report is not treated as an official experiment result because the following evidence was not supplied to this GitHub writer session:

- the frozen H-SW1 specification file;
- the registry row or migration that froze H-SW1;
- the exact Supabase function definition;
- the exact function invocation and cutoff timestamp;
- raw result rows or a machine-readable export;
- independent verification by another agent;
- a committed database backup containing the claimed registry and result.

The current repository ledger does not contain H-SW1 as a committed experiment specification. The current writer session also cannot assume live Supabase state without a query or export that is independently inspectable.

## Decision for this handoff

**Do not implement H-SW1. Do not add it to the dashboard. Do not interpret the reported positive point estimate as an edge. Do not retune its horizon, funding lookback, or period split.**

The report itself recommends not passing the specification to Manus for implementation. That recommendation is consistent with the repository's frozen-experiment and no-horizon-shopping rules.

If the project owner later wants H-SW1 to become an official research family, the next step is evidence preservation and independent verification, not code generation. The exact frozen specification, registry row, function definition, query, cutoff, raw output, and backup must first be committed or exported with checksums.

## Agent handoff

The next writer should read this document before acting on any H-SW1 request. Treat every numerical result above as an external claim until the evidence listed in the verification boundary is available. H-FB1, H-FB2, and the funding-family decisions in `docs/EXPERIMENT_LEDGER.md` remain unchanged.
