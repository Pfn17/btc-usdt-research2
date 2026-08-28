# M2 — L2 Collector

Status: **DONE**

M2 implements the BTCUSDT USDⓈ-M Futures Level-2 collector required by the project roadmap.

## Components

- WebSocket depth client: `<symbol>@depth@100ms`
- Bounded event buffer while a REST snapshot is acquired
- REST `/fapi/v1/depth` snapshot
- Snapshot + buffered-event synchronization
- In-memory local order book integration
- Sequence-gap detection
- Automatic resynchronization after a gap
- WebSocket reconnect with bounded exponential backoff
- WebSocket ping/pong keepalive configuration
- Integration/unit tests for buffering, synchronization, gap rejection, and stream URL

## Integrity rule

The local book is marked contaminated until a snapshot has been synchronized with a buffered event spanning `lastUpdateId + 1`. A sequence gap invalidates the book and forces resynchronization.

## Scope boundary

This milestone is market-data collection only. It does not place orders and does not contain trading credentials.

## Acceptance checklist

- [x] WebSocket Client
- [x] Snapshot (REST)
- [x] Event Buffer
- [x] Sync Algorithm
- [x] Local Order Book
- [x] Auto Resync
- [x] Integration Tests
