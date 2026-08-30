# Operations Runbook

## Live-data safety

This system is research/scalping infrastructure. It must never fabricate market data, features, or signals.

- No valid local order book -> no feature.
- Invalid/contaminated/stale data -> no signal.
- Raw archive failure -> fail closed; do not reconnect-loop against Binance.
- Binance HTTP 418/429 -> honor `Retry-After` and use exponential backoff.
- A clean process exit is preferred to an unsafe reconnect loop when required persistence is unavailable.

## Storage

The L2 raw archive is mounted at `/data/raw`. Configure `BTC_ARCHIVE_MIN_FREE_MB` to reserve free space. The worker stops safely when the archive cannot be written.

Capacity and retention must be monitored separately. The free-space guard is a safety mechanism, not a retention policy.

## Session lifecycle

Workers record `last_heartbeat_at`. On startup, stale `running` sessions are recovered:

- heartbeat older than the stale threshold -> stop the session;
- heartbeat is NULL and `started_at` is older than the stale threshold -> stop the session;
- current/healthy sessions must not be stopped.

Graceful shutdown remains enabled, but startup recovery is the authoritative safety net for platform-level termination races.

## Latency semantics

- `latency_ms`: exchange event timestamp -> local receive timestamp.
- `stale_after_ms`: local receive timestamp -> current processing time.

Do not use data age as network latency.

## Verification after storage recovery

1. Resize `/data/raw` volume before restarting the collector.
2. Confirm free space is comfortably above `BTC_ARCHIVE_MIN_FREE_MB`.
3. Start exactly one worker.
4. Verify Binance stream events are received and applied.
5. Verify raw archive files are growing.
6. Verify `feature_snapshots` continue increasing with fresh timestamps.
7. Verify `collector_health` updates without HTTP 4xx spam.
8. Verify exactly one healthy `research_sessions` row is `running`.
9. Perform one controlled redeploy and verify the previous session becomes `stopped` while the new session becomes `running`.
10. Do not enable live order execution as part of these tests.
