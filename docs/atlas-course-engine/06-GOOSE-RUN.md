# Goose 2 — Execute the Atlas Course Engine Full Run

## Mission
Execute the implementation contract in this directory against the actual repository. Do not use chat history as a substitute for repository inspection.

## Start
1. Read every file under docs/atlas-course-engine.
2. Inspect the repository and identify the actual Atlas source, canonical course CSV/data, current engine, tests, services and integrations.
3. Reconcile the implementation matrix with reality. Do not erase existing work.
4. Create/update an execution-state record and evidence as work proceeds.

## Execution loop
For each requirement in dependency order:

INSPECT → MAP → IMPLEMENT → TEST → REPAIR → RETEST → RECORD EVIDENCE → CONTINUE.

Do not stop after producing a plan. Do not ask the user to approve ordinary reversible engineering work.

## Dependency order
1. source/corpus integrity
2. schema and canonical identity
3. validators and status model
4. course/lesson engine
5. content and asset registry
6. activities/pathways/personalisation
7. assessment/questions/marking/feedback
8. mastery/credentials
9. delivery/learner lifecycle
10. CRM/support/marketing/demand adapters
11. measurement/analytics
12. provenance/versioning/regeneration
13. MCP/agent automation/observability
14. QA/security/regression
15. complete-dataset structural validation
16. representative end-to-end execution
17. production-readiness assessment

## Rules
- Preserve authoritative content and IDs.
- Prefer additive/reversible changes.
- Do not replace working components without evidence.
- Do not fabricate missing content or research.
- Do not call something tested unless the test ran.
- Do not call something live unless it is actually live.
- Do not perform irreversible production actions.
- Use test/staging/dry-run for externally consequential actions.
- Reuse existing infrastructure where possible.
- Do not add needless CSV columns; first determine whether an existing field can carry the requirement or whether a related entity is the correct location.

## Stop conditions
Stop only for a real blocker: missing credential/permission that cannot be resolved, destructive irreversible action, external spend, or an external service restriction that cannot be safely worked around. Record the blocker and continue all independent work.

## Final proof
Run the acceptance tests, reconcile every requirement row, and produce a final evidence report. Explicitly distinguish IMPLEMENTED+VERIFIED, IMPLEMENTED+UNVERIFIED, DESIGNED/SCHEMA, CONTENT ONLY, BLOCKED and NOT IMPLEMENTED.
