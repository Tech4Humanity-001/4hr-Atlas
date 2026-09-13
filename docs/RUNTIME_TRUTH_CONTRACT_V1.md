# Runtime Truth Contract v1

## Purpose

The Runtime Truth Layer establishes a provider-neutral contract for proving agent, human, tool and service execution.

CCCC is treated as a reference implementation and interoperability adapter, not as the system of truth.

## Core invariant

**No receipt = not REAL.**

Additional truth states:

- Receipt without evidence = PARTIAL
- Evidence without validation = UNVERIFIED
- Validation without outcome = INCOMPLETE
- Outcome without telemetry = DEGRADED
- Missing authority, dependency, safety or credentials = BLOCKED
- Unsafe, poisoned, exposed-secret or repeatedly failing execution = QUARANTINED

## Lifecycle

```text
INTENT
  -> ROUTED
  -> ACCEPTED
  -> STARTED
  -> EXECUTING
  -> PRODUCED
  -> EVIDENCED
  -> VALIDATED
  -> DELIVERED
  -> OBSERVED
  -> CONSUMED
  -> COMPLETED
```

Failure/recovery states are orthogonal where required:

```text
FAILED | BLOCKED | DEGRADED | QUARANTINED | RECOVERING
```

## Truth distinctions

A claim, receipt, evidence record, validation result and outcome are different objects.

- **Claim:** an actor says something happened.
- **Receipt:** the system records a state transition.
- **Evidence:** an artefact or observation supports the transition.
- **Validation:** evidence is checked against the required acceptance criteria.
- **Outcome:** the intended value/result was actually achieved.
- **Telemetry:** the resulting change remains observable.

A reply such as `done` is an event or claim. It is not proof of completion.

## Provider neutrality

The contract applies equally to:

- GPT / Codex
- Claude
- Gemini
- Grok
- Perplexity
- Cursor
- Goose
- MCP-connected agents
- deterministic software
- humans
- devices
- external services

The runtime, model and tool are attributes of an execution actor. They do not define the truth model.

## Ledger authority

The immutable event ledger is authoritative. Dashboards, indexes, caches, notifications, search projections and agent memories are derived views.

If a projection disagrees with the ledger, the projection is wrong.

Memory is advisory only and must be refreshed before acting on mutable truth.

## Receipt minimum

A receipt should identify, where available:

- receipt_id
- intent_id
- actor_id
- runtime_id
- model_id
- event
- state_before
- state_after
- timestamp
- evidence references
- authority reference
- parent receipt
- replayability

## Replay and recovery

An execution is not proven if it cannot be reconstructed from authoritative events and evidence.

Recovery must preserve the original history and create new receipts for recovery actions. Failed or stale projections must be rebuildable from the ledger.

## Ownership and authority

Every meaningful execution should have an owner, evidence, dependency context and lifecycle state.

No authority means BLOCKED. A blocker is not automatically a stop condition: the runtime should identify the missing authority/dependency and continue through an authorised recovery path where possible.

## CCCC relationship

CCCC demonstrates useful collaboration primitives including immutable events, actor/runtime abstraction, delivery/read/reply distinctions and a single-writer event model. Those primitives can be consumed through an adapter.

The Runtime Truth Layer deliberately adds the stronger execution chain:

```text
claim != receipt != evidence != validation != outcome
```

CCCC must not become a hard dependency of Atlas unless a future architecture decision explicitly requires it.

## Acceptance tests

An implementation claiming compliance must demonstrate:

1. An intent receives a unique identifier.
2. Ownership and authority are resolved or explicitly marked BLOCKED.
3. Execution emits observable state transitions.
4. Each material transition has a receipt.
5. Produced results reference evidence.
6. Evidence can be validated independently.
7. Completion cannot be asserted from an agent reply alone.
8. The ledger can reconstruct the execution history.
9. Derived state can be rebuilt from authoritative events.
10. Recovery creates a new auditable chain rather than rewriting history.
11. The same contract works across different models and runtimes.
12. Telemetry confirms material outcome where telemetry is available.

## Version

Runtime Truth Contract v1.0
