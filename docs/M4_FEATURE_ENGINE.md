# M4 — Feature Engine

Status: **IMPLEMENTED**

M4 provides real-time microstructure features from the validated M2 local order book, with a bounded in-memory feature store, validation, performance counters, and tests.

## Features

- Mid price
- Spread and spread in basis points
- Microprice
- Top-of-book imbalance
- N-level depth and depth imbalance
- 1-second signed depth order-flow proxy
- 1-second realized volatility from log mid-price returns
- Book pressure

The roadmap explicitly calls for Spread, Microprice, Imbalance, Depth Features, Order Flow, and Volatility; the feature set also exposes Book Pressure for the downstream dashboard/feature view. 

## Integrity boundary

Feature computation rejects an update when the supplied book has not yet applied that update. Invalid/crossed books, non-finite values, negative depth/spread, and out-of-range imbalances are rejected.

## Feature store

`InMemoryFeatureStore` maintains the latest snapshot per symbol and a bounded history. It is intentionally in-process for the M4 hot path; durable historical storage remains a later storage concern.

## Performance

`FeaturePerformance` records accepted/rejected computations, total compute time, mean compute time, and maximum compute time. The engine performs no network, model, or LLM work in the hot path.

## Tests

Coverage includes core feature formulas, order-flow baseline behavior, bounded store semantics, validation failures, and synchronization guards.

## Scope

M4 is feature generation only. It does not generate trading signals, place orders, or use exchange credentials.
