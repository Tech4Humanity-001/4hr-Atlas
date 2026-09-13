# Runtime Truth Acceptance Tests

These are executable design acceptance criteria for the Runtime Truth Layer.

| ID | Test | Pass condition |
|---|---|---|
| RTT-001 | Intent identity | Every execution begins with a unique intent ID |
| RTT-002 | Authority | Missing authority produces BLOCKED, not fabricated permission |
| RTT-003 | Ownership | Every active execution has an owner or explicit routing state |
| RTT-004 | Receipt | Every material state transition emits a receipt |
| RTT-005 | Evidence | Produced outputs can point to supporting evidence |
| RTT-006 | Validation | Evidence can be independently validated |
| RTT-007 | Claim separation | `done`/reply cannot directly create COMPLETED |
| RTT-008 | Outcome | Completion requires intended outcome evidence |
| RTT-009 | Telemetry | Material change has observable telemetry or is marked DEGRADED |
| RTT-010 | Ledger | Authoritative history is append-only and replayable |
| RTT-011 | Projection | Derived state can be rebuilt from authoritative events |
| RTT-012 | Recovery | Recovery appends new events and preserves original history |
| RTT-013 | Provider neutrality | Contract works independently of model/provider |
| RTT-014 | Provenance | Imported events retain source actor/runtime provenance |
| RTT-015 | Quarantine | Unsafe or untrusted execution cannot silently become valid |
| RTT-016 | Dependency | Missing dependency is explicit and has a recovery path where authorised |
| RTT-017 | Freshness | Mutable truth is revalidated before consequential action |
| RTT-018 | Distribution | Completed value has an explicit destination/consumer |

## Minimum proof package

A release claiming Runtime Truth compliance should provide:

- test results for RTT-001 through RTT-018
- commit or deployment receipt
- representative ledger events
- representative evidence references
- validation output
- replay/recovery demonstration
- telemetry showing the resulting state

No proof package means the compliance claim is not REAL.
