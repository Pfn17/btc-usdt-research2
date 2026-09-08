# Owner Dashboard-First Visibility

**Owner requirement:** the owner monitors the project through the dashboard and does not inspect the implementation code or hidden backend state. The dashboard is therefore an operational control surface, not merely a presentation layer.

Every material backend state must have an honest dashboard representation: data freshness, collector status, unavailable responses, research status, failed hypotheses, execution state, and the timestamp or cutoff of displayed evidence. A blank, stale, or unavailable backend response must remain visibly unavailable. The interface must never replace missing data with a placeholder, mock, dummy, or optimistic status.

Dashboard-first does not mean the dashboard may redefine research truth. The backend, frozen specification, SQL function, raw output, Git commit, and coordination ledger remain the source of truth. The dashboard must expose enough status for the owner to detect whether a claim is live, historical, unavailable, unverified, killed, or disabled.

The dashboard may refresh low-cost operational reads. It must not silently start expensive research RPCs on a timer. Research comparisons are explicit, manual, read-only actions with a visible status, one-run boundary, common cutoff, and no execution path.

The owner prioritizes the dashboard because it is the only practical way to monitor a system whose implementation details are not directly inspected. This is a valid product and governance requirement. It does not justify adding decorative UI or concealing uncertainty; it requires making uncertainty and system state easier to see.
