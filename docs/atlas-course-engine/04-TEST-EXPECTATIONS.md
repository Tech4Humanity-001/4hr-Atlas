# Atlas Course Engine — Test Expectations

Tests are evidence, not decoration. A test is successful only when it exercises the claimed behaviour and produces a reproducible result.

## Expected test layers

### T-DATA-001 / T-DATA-002 — corpus integrity
Expected: canonical records load without loss; IDs are unique and stable; required fields conform; expected 489 subtopics and 516 research stories are either confirmed or an explicit source discrepancy is recorded.

### T-SCHEMA-001
Expected: every canonical record validates against the current schema; controlled enum values reject unknown lifecycle states; backward-compatible existing fields remain readable.

### T-CONT-001
Expected: a representative lesson renders from canonical source without invented source facts and retains provenance.

### T-ASSET-001
Expected: asset registry can create/version/validate an asset reference and distinguish specified, generated, QA and live states.

### T-ACT-001
Expected: activity can be presented, completed, scored or recorded as appropriate, and produces a learner event.

### T-ASSESS-001
Expected: assessment can present questions, capture an attempt, persist answers, apply configured rules and return an outcome without treating configuration as execution.

### T-MARK-001
Expected: deterministic marking produces the expected score/outcome; AI-assisted marking, if present, records the model/configuration and remains distinguishable from human verification.

### T-MAST-001
Expected: mastery changes only when its defined evidence/rule is satisfied; insufficient evidence does not advance mastery.

### T-CRED-001
Expected: credential is issued only when the configured achievement rule is satisfied; test mode must never issue a real external credential.

### T-PATH-001
Expected: standard and alternate/dip choices resolve correctly; personalised path selection is traceable and reproducible for a test profile.

### T-LIFE-001
Expected: learner lifecycle events produce the intended state transitions and invalid transitions are rejected or quarantined.

### T-PROV-001
Expected: a generated lesson/asset/assessment can be traced back to its Atlas source and version.

### T-REGEN-001
Expected: changing an upstream source/configuration identifies affected descendants and marks regeneration/review where required without destroying prior versions.

### T-INT-001
Expected: each claimed integration has a smoke/contract test. Configuration-only existence is insufficient.

### T-AGENT-001
Expected: worker can resume after interruption, does not duplicate an idempotent operation, records execution state and leaves evidence.

### T-SEC-001
Expected: secret scanner finds no committed secrets; private endpoints are not exposed by the test harness; production/destructive actions are guarded.

### T-STATUS-001
Expected: impossible states are rejected, e.g. LIVE without publication evidence or TESTED without a test result.

### T-E2E-001
Expected: at least one representative canonical subtopic traverses source → lesson → activity → assessment → marking → feedback → mastery → credential in test mode.

## Completion expectation
A green unit suite is not sufficient. The acceptance suite must prove the complete implemented pathway and the canonical corpus structure.
