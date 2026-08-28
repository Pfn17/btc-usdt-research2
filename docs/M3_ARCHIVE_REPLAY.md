# M3 — Archive & Replay

Status: **DONE**

Implemented against the M3 roadmap requirements: Raw Immutable Archive, metadata (receive time and sequence identifiers), Replay Engine, Deterministic Rebuild, Backfill Tools, and Replay Tests.

## Data contract

Each archived depth event stores the original raw WebSocket payload plus symbol, exchange event time, local receive time (`receive_time_ns`), Binance sequence range (`U`/`u`), and SHA-256 checksum.

## Archive

The writer is append-only and rotates by UTC date:

`data/raw/BTCUSDT/YYYY-MM-DD/depth.jsonl`

Raw payloads are encoded as hex inside JSONL so the original bytes can be recovered exactly. Checksums are verified on read.

## Replay

`ReplayEngine` applies archived `DepthUpdate` events to the existing M2 `OrderBook`. It preserves the archived receive timestamp and fails on sequence gaps instead of producing a potentially invalid book.

## Backfill

`backfill_snapshot()` fetches a current REST depth snapshot and writes a timestamped JSON snapshot under `data/snapshots/<SYMBOL>/` for recovery/rebuild workflows.

## Tests

Tests cover archive round-trip integrity, receive-time preservation, deterministic replay, and decoding archived raw events.

## Scope

M3 remains research/market-data only. No trading credentials or order execution are introduced.
