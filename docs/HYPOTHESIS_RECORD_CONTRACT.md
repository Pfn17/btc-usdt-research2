# Hypothesis Record Contract v1

## Purpose

The Hypothesis Record is the canonical research memory for every trading hypothesis.

The dashboard is only a presentation layer. The record must remain understandable if the dashboard is unavailable, and a new agent must be able to reconstruct why a hypothesis existed without relying on chat history.

## Non-negotiable rule

**No hypothesis without a Hypothesis Record.**

A record must be created before result data is queried for that hypothesis.

The record must distinguish:

- where the idea came from;
- what problem it was intended to test;
- why the mechanism was considered plausible;
- what is inference versus documented external reference;
- exact variables and equations;
- frozen parameters and temporal rules;
- entry/exit semantics;
- declared costs;
- validation and promotion gates;
- implementation and dataset lineage;
- final decision.

## Origin taxonomy

Use one of:

- `EXTERNAL_REFERENCE` — the hypothesis explicitly derives from an identifiable paper, article, book, documented strategy, or other external source.
- `INTERNAL_HYPERHAN` — generated from project-internal reasoning with no external source claimed.
- `DERIVED_FROM_EXISTING_HYPOTHESIS` — materially derived from an existing project hypothesis; parent identity is mandatory.
- `RESEARCH_RECOMBINATION` — combines documented project mechanisms; parent identities are mandatory.
- `NOT_RECOVERABLE_FROM_CURRENT_RECORD` — historical hypothesis where the origin cannot be established from the surviving project record. Do not guess.
- `UNKNOWN` — temporary state only; must be resolved or explicitly retained as an audit limitation.

An external reference must never be implied merely because a mechanism resembles a known academic concept.

## Required mathematical memory

At minimum record:

1. variable definitions;
2. units;
3. lookback/window definition;
4. threshold calculation;
5. signal inequality/equality rules;
6. direction mapping;
7. entry rule;
8. exit rule;
9. overlap rule;
10. invalid-data rule;
11. cost equations;
12. evaluation equations;
13. confidence/statistical method.

If a formula cannot be recovered exactly, record `NOT_RECOVERABLE` instead of reconstructing it from memory.

## Freeze boundary

The following must be frozen before OOS outcome observation:

- hypothesis identity;
- mechanism;
- feature construction;
- threshold/parameter rule;
- entry;
- exit;
- overlap;
- data cutoff/boundary;
- cost model;
- statistical gate;
- multiple-testing family.

Any material change creates a new record version and normally a new hypothesis identity.

## Lineage

Every executed result must be traceable:

`hypothesis → preregistration → implementation → migration/commit → dataset/cutoff → result → replay → decision`

A result may not inherit provenance from a similar function.

## Decision memory

Historical decisions are append-only. A KILL or INCONCLUSIVE result is not rewritten to make a later implementation look better.

Corrections create a new record version and explain the correction.

## Dashboard rule

The dashboard may render this record progressively:

`origin → rationale → mechanism → equations → frozen rules → evidence → result → decision → provenance`

The dashboard must never become the only copy of this information.
