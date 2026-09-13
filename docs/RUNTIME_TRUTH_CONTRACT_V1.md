# Runtime Truth Contract v1

## Purpose

The Runtime Truth Layer is a provider-neutral contract for proving agent, human, tool and service execution.

CCCC is an optional interoperability adapter, not Atlas' system of truth.

## Core invariant

**No receipt = not REAL.**

- Receipt without evidence = PARTIAL.
- Evidence without validation = INCOMPLETE.
- Validation without outcome = INCOMPLETE.
- Outcome without telemetry = DEGRADED.
- Missing authority, dependency, safety or credentials = BLOCKED.
- Unsafe, poisoned, exposed-secret or repeatedly failing execution = QUARANTINED.

## Implemented lifecycle

```text
INTENT -> ACCEPTED -> STARTED -> EXECUTING -> VALIDATING -> REAL
                                           |             |
                                           v             v
                                        BLOCKED       OUTCOME
                                                         |
                                                         v
                                                     DEGRADED
                                                         |
                                                         v
                                                    TELEMETRY
                                                         |
                                                         v
                                                        REAL
```

Recovery is append-only:

```text
BLOCKED | DEGRADED | QUARANTINED -> RECOVERING -> STARTED / EXECUTING
```

## Truth distinctions

Claim, receipt, evidence, validation, outcome and telemetry are separate facts.

A reply such as `done` is a claim/event. It cannot establish REAL execution truth.

## Provider neutrality

The runtime, model and tool are execution attributes, not the truth model. The contract applies across GPT/Codex, Claude, Gemini, Grok, MCP-connected agents, deterministic software, humans, devices and external services.

## Ledger authority

The event ledger is authoritative. Dashboards, indexes, caches, notifications, projections and memories are derived views. Replay reconstructs state from ledger events. Recovery never rewrites prior history.

## Ownership and authority

Every meaningful execution has an owner. Sensitive events require authority; missing authority is recorded as BLOCKED with a recovery requirement rather than fabricated permission. Policy blockers identify the missing dependency or freshness proof.

## Dependency, freshness and distribution

Declared dependencies must be explicitly ready before START/EXECUTE. Consequential actions requiring fresh mutable truth must carry explicit freshness revalidation. An outcome must carry evidence, confirm `achieved=true`, and identify a destination or consumer. An outcome is DEGRADED until material telemetry confirms the resulting change.

## CCCC relationship

CCCC delivery/read/reply events may be ingested through the adapter with source provenance. They do not become business completion merely because CCCC reports `done`.

CCCC must remain optional. Atlas assigns its own intent, receipt, evidence, validation, outcome and telemetry semantics.

## Version

Runtime Truth Contract v1.1
