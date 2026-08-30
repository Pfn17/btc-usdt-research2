# Alignment retry hardening

The L2 bootstrap path still has a short retry for `RuntimeError` from snapshot/stream alignment. This is intentionally tracked separately from Binance HTTP 418/429 handling.

Before changing it, preserve the distinction between:

- HTTP rate limiting (`418`/`429`): honor `Retry-After` and exponential backoff.
- transient local alignment mismatch: bounded exponential backoff with jitter, then a controlled resync/rebootstrap.
- persistent integrity failure: fail closed rather than hammering the REST endpoint.

Acceptance criteria:

- no fixed 100ms retry loop;
- bounded retry delay;
- no retry storm after repeated alignment failures;
- counters/logs expose alignment retry count;
- tests cover repeated RuntimeError and ensure delays are bounded;
- normal successful bootstrap remains unchanged.
