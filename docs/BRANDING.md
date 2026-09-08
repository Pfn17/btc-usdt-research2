# HyperHan Lab — Public Archive Brand Specification

**Brand:** HyperHan Lab
**Dashboard:** HyperHan Research Archive
**Engine:** HyperHan Research Engine
**Vault:** HyperHan Research Vault
**Primary archive statement:** No validated edge.
**Research principle:** Find edges. Reject noise.

## Positioning

HyperHan Lab is a systematic crypto-research portfolio and evidence archive. The public dashboard is not a signal product, AI product, exchange interface, or promise of profitability. It documents market evidence, failed and pending research, data quality, and execution controls.

## Visual direction

The public archive uses a restrained exchange-terminal language: near-black background, charcoal panels, thin neutral borders, compact spacing, small radii, tabular numerals, and a limited yellow accent. It intentionally avoids neon cyan, purple gradients, glassmorphism, glowing cards, oversized marketing typography, and assistant or agent identity in the public interface.

| Token | Value | Use |
|---|---|---|
| Background | `#0B0E11` | Application background |
| Surface | `#181A20` | Panels and cards |
| Border | `#2B3139` | Dividers and table boundaries |
| Primary accent | `#F0B90B` | Active controls and archive accent |
| Success | `#0ECB81` | Healthy or verified state only |
| Danger | `#F6465D` | Error, rejected, or disabled state |
| Text | `#EAECEF` | Primary text |
| Muted text | `#929AA5` | Secondary information |

## Public naming rules

Agent names, model names, provider names, internal RPC names, and implementation lineage names must not appear as public-facing dashboard labels. Public labels use neutral terms such as **Reference specification**, **Independent specification**, **Frozen study**, and **Research only**. Internal lineage names remain in Git, migrations, raw evidence, and the coordination ledger for auditability.

## Product rules

Dashboard labels and status must come from the backend or frozen research state. Branding may be static, but market values, observations, confidence, expected move, research outcomes, and availability states may never be placeholders, dummy data, mocks, or fabricated values. The dashboard is an archive of live evidence, not an AI product page or trading-signal sales surface.

The owner monitors the project through the dashboard rather than source code. The dashboard must therefore make live health, unavailable states, research failure, study status, cutoff context, and execution state visible without exposing private implementation details.

This specification may be revised through a significant, versioned batch with a new commit and ledger reference.
