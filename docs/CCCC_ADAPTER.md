# CCCC Adapter Boundary

CCCC is an interoperability and collaboration adapter, not Atlas' source of truth.

## Boundary

```text
Atlas Intent
    |
    v
Runtime Truth Contract
    |
    +---- CCCC adapter ---- Claude / Codex / ChatGPT / other actors
    +---- MCP adapter ----- external agents and tools
    +---- Direct adapter -- humans / devices / services
    |
    v
Authoritative event ledger
```

## Rules

1. CCCC events may be ingested as runtime evidence/events.
2. CCCC delivery, read and reply events must not be interpreted as business completion by themselves.
3. Atlas assigns its own intent, receipt, evidence, validation and outcome semantics.
4. CCCC is optional. Atlas remains functional without it.
5. Adapter failures become explicit runtime states, not silent failures.
6. Imported events retain provenance and source runtime identity.
7. The authoritative ledger remains the source for replay and recovery.

## Completion rule

`reply=done` is a claim/event. It cannot establish `REAL` execution truth by itself. REAL requires the Atlas evidence, validation, outcome and telemetry chain.
