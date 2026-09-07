# Dashboard live-only data contract

The dashboard must display only values obtained from the backend and current system state. There are no placeholders, dummy values, mock values, fabricated signals, fabricated confidence, or representative market numbers.

When a backend value is unavailable, stale, invalid, or not supported by the current schema, the UI must show an explicit `UNAVAILABLE`, `STALE`, or `DEGRADED` state with the reason and timestamp. It must not substitute zero, a hardcoded sample, a guessed value, or a previous unrelated result.

Research status must be sourced from persisted research metadata/results where available. A status may be hardcoded only as a temporary, explicitly documented compatibility measure; the preferred implementation is a backend status view/table so status cannot silently drift from the ledger.

Trading remains disabled unless a separately approved execution phase is recorded in the coordination ledger.
