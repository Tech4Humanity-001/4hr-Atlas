# Atlas GATE4 Baseline — Extras / Reconciliation Ledger

This document **supplements** `docs/ATLAS-GATE4-BASELINE.md`.

It does not replace, recalculate, or reinterpret the historical baseline. The purpose is to capture the additional facts that appeared around the GATE4 work and must remain available for the eventual practical reconciliation.

## 1. Historical GATE4 state — retained values

The baseline document records:

- 489 canonical subtopics
- 0 implemented
- 0 partial
- 0 not started
- 0 blocked / failed
- 0 ready
- 0.0% implementation rate
- 10 implementation records
- 5 work queues
- 489 pending records reported in each queue
- 2,445 queue entries on the reported queue counts
- 62 requirements
- 516 expected stories
- 0 stories actually analysed

These values are historical evidence, not a statement about today's repository.

## 2. Additional repository/application evidence to reconcile

The Atlas repository README identifies an existing production service whose original role includes:

- FastAPI API under `/api/v1`
- health endpoint
- themes and taxonomy
- opportunities
- deep-match
- rescore / WIN_SCORE
- Control Room queues
- database-backed Atlas entities
- Docker/deployment configuration
- unit and API integration tests

The GATE4 reconstruction must therefore not assume that a zero educational implementation means the Atlas application itself is empty. The educational implementation is a capability layer over an already-existing application.

## 3. Later SUB-0001 implementation claim

A later engineering report claimed that `SUB-0001` — **Working Memory Optimisation** — had been implemented as an educational workflow using the existing Atlas FastAPI architecture.

The report claimed the following educational endpoints:

- `POST /api/v1/educational/lessons`
- `POST /api/v1/educational/activities`
- `POST /api/v1/educational/assessments`
- `POST /api/v1/educational/marking`
- `POST /api/v1/educational/feedback`
- `POST /api/v1/educational/progress`
- `POST /api/v1/educational/credentials`
- `POST /api/v1/educational/subjects/{subject_id}/run-end-to-end`
- `POST /api/v1/educational/subtopics/{subtopic_id}`
- `GET /api/v1/educational/subjects`
- `GET /api/v1/educational/lessons/{lesson_id}`

The report also claimed a complete SUB-0001 lifecycle of:

`lesson → activity → assessment → marking → feedback → progress → credential`

with a sample reported final score of `87.5`, grade `PASS`, and certificate issuance.

**Important:** these are claims to reconcile against repository and deployment evidence. They are not promoted to verified implementation merely because they were reported later.

## 4. Later educational implementation artifacts claimed

The later report claimed these files or changes existed:

- `tests/test_educational_workflow.py`
- `EDUCATIONAL_WORKFLOW.md`
- `IMPLEMENTATION_SUMMARY.md`
- `verify_implementation.py`
- changes in `app/core/config.py`
- changes in `app/main.py`
- changes in `app/api/routes.py`

The report stated that Python syntax checks passed for the three application files and that six educational tests existed.

Again, these are reconciliation targets rather than assumed facts.

## 5. Requirement coverage that must not disappear

The GATE3 requirements model contained seven capability domains and 62 requirements:

1. Lesson Design — 9
2. Learner Experience — 9
3. Assessment Architecture — 8
4. Media Capabilities — 8
5. Credentials System — 8
6. Delivery System — 8
7. Learner Lifecycle — 12

All 62 were marked REQUIRED in the reported GATE3 model. This does **not** mean every requirement is already implemented; it means they must remain visible when reconciling actual implementation.

## 6. Capability checklist for future reconciliation

The actual system should be checked against the following, without assuming completion:

### Learning
- courses
- lessons
- learning content
- objectives
- examples
- activities
- reflection / conclusion

### Pathways
- standard path
- personalised path
- dip path
- choice points
- branching
- recommendation logic
- adaptation rules

### Assessment
- assessment definitions
- questions
- question bank
- adaptive logic
- response capture
- marking
- feedback
- remediation
- mastery tracking

### Media
- images
- diagrams
- audio
- voice
- video
- interactive assets
- narration

### Credentials
- micro-credentials
- badges
- certificates
- achievement rules
- evidence
- verification
- issuance
- learner credential records

### Delivery / lifecycle
- catalogue
- course delivery
- lesson delivery
- enrolment
- authentication
- learner access
- assessment delivery
- credential delivery
- notifications
- support/community
- CRM/follow-up
- discovery
- orientation
- practice
- reflection
- mastery
- application
- return / follow-up

### Operational
- accessibility
- evidence/provenance
- analytics
- integrations
- deployment
- monitoring
- tests / QA

## 7. Source and identity constraints

The canonical identity remains:

- Theme: `THE-01`
- Topic: `TOPIC-01`
- Subtopics: `SUB-0001` through `SUB-0489`
- Atlas paths: `ATLAS-001` through `ATLAS-489`
- Expected story population: 516

The unresolved story source remains a condition to carry forward. It is not permission to invent stories and is not a reason to erase or downgrade unrelated implementation evidence.

## 8. What the zeroes mean

The zero values in the historical GATE4 baseline are deliberately retained because they may expose a reconstruction problem rather than a genuine absence of implementation.

In particular, the following must eventually be distinguished:

- **zero verified implementation**
- **not inspected**
- **not represented in the GATE4 records**
- **actually absent**
- **later implemented**
- **implemented but not deployed**
- **deployed but not verified**
- **claimed but unsupported**

Do not collapse these states into a single zero.

## 9. Queue integrity

The five historical queue names were:

- Adaptive Assessment
- Video Content
- Credential Completion
- Accessibility Compliance
- QA Completion

The historical report showed 489 items in each queue. Those counts are preserved as baseline evidence. They should not be treated as proof that every one of the 489 subtopics actually requires every queue's capability.

The later GATE4 instruction explicitly required queues to reflect **actual outstanding work**, using the existing applicability/requirements records. That distinction is important for the eventual queue rebuild.

## 10. Required reconciliation sequence

When this ledger is consumed, the practical sequence is:

**historical baseline → repository evidence → database/application evidence → deployed evidence → SUB-0001 evidence → current implementation state → corrected production queues**

No earlier gate needs to be rerun merely because this reconciliation is performed.

## 11. Preservation rule

This file is deliberately additive. Do not merge its claims into the historical baseline in a way that changes the baseline values.

The two documents serve different purposes:

- `ATLAS-GATE4-BASELINE.md` = immutable historical baseline
- `ATLAS-GATE4-BASELINE-EXTRAS.md` = later evidence, claims, and reconciliation targets

That separation prevents the historical record from being rewritten while still retaining the additional engineering context needed to move forward.
