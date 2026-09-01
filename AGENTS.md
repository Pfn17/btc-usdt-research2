# AGENTS.md — Multi-Agent Coordination Protocol

Project: BTCUSDT Futures Scalping Research (`btc-usdt-research2`)
Version: 1.1
Updated: 2026-09-01

This file is the shared operating contract for ChatGPT and Claude instances working on this project. It must be read before changing repository code, database schema/data, environment configuration, or deployments.

## 1. Team Roles

| Agent | Account / Email | Primary role | Current capability status |
|---|---|---|---|
| **chatgpt** | ChatGPT operator | **Writer / implementer**; also analysis and engineering | GitHub read/write/admin verified in the current session; repository access is live |
| **claude-1** | `hanz.pirdaus@gmail.com` | **Writer / implementer**; also analysis | Historical commits with this author/committer identity are verified in GitHub history; this proves Git metadata, not which AI session physically executed the action |
| **claude-2** | `sopiekples@gmail.com` | **Audit / analysis / criticism / reasoning** | GitHub connector reportedly available, but successful write is not currently proven; do not assume write capability |
| **claude-3** | `parhanfn17@gmail.com` | **Audit / analysis / criticism / reasoning** | Railway, Supabase and Vercel access is available in its session; no GitHub connector was available in the reported session |
| **human** | Project owner | Final authority, product decisions, credentials and approvals | Full owner control |

Role assignment is based on the current project agreement. Actual technical permissions must still be verified from the relevant platform before relying on them.

## 2. Shared Resources

- GitHub repository: `Pfn17/btc-usdt-research2`
- Supabase project ref: `xaqsntunrqvqpzlbeutt`
- Railway project: `calm-integrity`
- Railway service: `btc-usdt-research2`
- Vercel project: `btc-usdt-research2`

Do not create parallel repositories, databases, deployments, or substitute infrastructure unless explicitly approved by the human owner.

## 3. Non-Negotiable Rules

### 3.1 One active writer per resource

Only one writer may actively modify the same resource/area at a time. Before starting work, inspect the coordination ledger. If another agent owns an `in_progress` task covering the same area, stop and coordinate instead of editing concurrently.

### 3.2 Claims are not evidence

Statements such as “done”, “fixed”, “deployed”, or “verified” are claims until supported by evidence another agent can inspect.

Acceptable evidence includes, as applicable:
- Git commit SHA and changed files
- GitHub PR/status data
- Vercel deployment status or deployment ID
- Railway deployment/log status
- Supabase query result or migration result
- test output
- reproducible research artifact/result

### 3.3 Executor and verifier should be different agents

The agent that implements a change should not be the sole verifier of that change. A writer may report `claimed_done`, but final `verified` status requires an independent check by another agent or the human owner.

For repository changes, a typical flow is:

`implement → commit → deploy/CI → independent audit → verified`

### 3.4 Never invent live data or research results

If a live API, database, order book, feature, signal, backtest result, or deployment state cannot be observed, label it unavailable/unverified. Do not manufacture representative values and present them as live results.

### 3.5 Research integrity

The project is for finding repeatable, cost-adjusted short-horizon edge. Accuracy alone is not sufficient evidence of an exploitable edge. Preserve deterministic replay, data integrity, out-of-sample validation, costs/slippage, robustness testing, and experiment lineage.

### 3.6 Frozen experiments stay frozen

Once an experiment family, generation batch, labeling rule, or evaluation rule is locked, do not silently add hypotheses or alter evaluation criteria. Any new hypothesis or rule change must receive a new batch/lineage identifier.

### 3.7 No trading activation

The research system must remain read-only with respect to trading until a separately approved execution phase exists. Dashboard/API work must not introduce live order placement implicitly.

## 4. Coordination Ledger

Use Supabase table `public.agent_coordination_log` as the shared task ledger.

At the beginning of a session, check active coordination items:

```sql
select task_id, owner, lane, status, claim, evidence, verified_by, created_at, verified_at
from public.agent_coordination_log
where status in ('in_progress','proposed')
order by created_at desc;
```

Suggested lifecycle:

`proposed → in_progress → claimed_done → verified`

Other terminal states:

`rejected`, `locked`

Required evidence fields:

- `task_id`
- `owner`
- `lane`
- `status`
- `claim`
- `evidence`
- `verified_by`
- `verified_at`

A task is not considered verified merely because its owner changed the status.

## 5. Work Lanes

| Lane | Purpose | Default agents |
|---|---|---|
| **A** | Implementation and live infrastructure work | ChatGPT, Claude 1 |
| **B** | Research, statistics, calculations, model reasoning | ChatGPT, Claude 1/2/3 |
| **C** | Hypothesis generation under immutable experiment batches | Designated agent per batch |
| **D** | Independent QA, audit, criticism and verification | Claude 2, Claude 3, or another agent not responsible for the implementation |

An agent may participate in analysis outside its default lane, but must not silently change its role from auditor to writer or vice versa.

## 6. Current Repository State — 2026-09-01

The current `main` branch contains the M7 dashboard implementation. Recent commits include:

- `b6682627` — `feat(m7): add read-only BTCUSDT research dashboard`
- `decb83d8` — `feat(m7): serve read-only dashboard from FastAPI`
- `474e27d7` — `docs(m7): define dashboard scope and acceptance boundary`
- `dcce99e5` — `test(m7): verify dashboard asset and read-only contract`

These commits are directly observable in GitHub history. Deployment state must still be checked from Vercel/Railway rather than inferred from the commit message.

M7 is considered **implemented but not automatically verified complete** until deployment and runtime checks pass.

## 7. M7 Scope Boundary

M7 is a read-only research dashboard. It may expose available market, integrity, latency, feature and research information through existing safe APIs.

The dashboard must not fabricate unavailable order-book depth, signals, confidence, expected move, or backtest results. If the underlying data/API is not available, show an explicit unavailable/degraded state.

The roadmap's intended dashboard areas are:
- Market Overview
- Order Book Depth
- Integrity Monitor
- Latency Monitor
- Feature Viewer
- Signal Panel
- Research / Backtest

Only areas supported by real underlying data should be presented as live/verified.

## 8. PR / Branch Discipline

Do not merge, close, rebase, or otherwise alter an old PR merely because another agent reports its status in chat.

For PR decisions, inspect the GitHub PR directly and record the evidence. Until independently checked, treat prior chat reports about PR #1 (`fix/futures-integrity-foundation`) as unverified coordination information.

Do not make new work depend on an unverified PR state.

## 9. Handoff Protocol

When an agent reaches a limit, loses access, or hands work to another agent:

1. Commit completed safe work if it is the designated writer.
2. Record the commit SHA and exact state in the coordination ledger.
3. Mark the task `claimed_done` only when implementation is actually complete.
4. Leave unresolved questions explicitly marked `unverified`.
5. The next agent reads the repository and coordination ledger before continuing.
6. The next agent must not redo completed work without a reason.

## 10. Security

Never commit secrets, API keys, service-role keys, exchange credentials, or `.env` contents. Prefer least-privilege credentials. Do not expose Supabase service-role credentials to client-side/dashboard code.

Security findings should be recorded with evidence and handled as a separate task; do not silently weaken RLS or credential boundaries to make a feature work.

## 11. Definition of Done

A task is only fully done when:

1. implementation exists,
2. tests/checks appropriate to the change pass,
3. the change is committed with an identifiable SHA,
4. deployment/runtime state is checked when relevant,
5. an independent agent audits the evidence,
6. the coordination ledger records the verification.

If any of these are missing, use the appropriate intermediate status (`in_progress`, `claimed_done`, or `unverified`) rather than claiming verified completion.
