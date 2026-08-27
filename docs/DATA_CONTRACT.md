# Data Contract v1

## Raw depth event
Every captured event must preserve:
- symbol
- exchange event timestamp
- local receive timestamp
- stream/event type
- first update ID (`U`)
- final update ID (`u`)
- previous-final/update linkage when supplied by the exchange
- bids and asks exactly as received
- collector instance/session identifier
- archive sequence/order

Raw records are append-only and immutable.

## Book state
A reconstructed state is valid only when snapshot initialization and every incremental update satisfy the exchange sequence rules. A detected gap triggers rebuild; the affected interval is contaminated.

## Contamination
Half-open interval convention: `[t_start, t_end)`.

Invalidity classes:
- `DATA_INVALID`
- `FEATURE_INVALID`
- `LABEL_INVALID`

Reasons include:
- `DATA_GAP`
- `BOOK_REBUILD`
- `FEATURE_WINDOW_CONTAMINATION`
- `LABEL_WINDOW_CONTAMINATION`

Any feature or label window intersecting a contaminated interval is invalidated.

## Research entities
Candidate events must retain immutable IDs and timestamps. Labels record barrier parameters, outcome, MFE, MAE, time-to-target and time-to-stop. Hypotheses record hypothesis ID, parent hypothesis ID, stage, experiment family, generation method and creation timestamp.
