# Atlas Course Engine — Master Scope

## Purpose
This package is the persistent implementation contract for converting the authoritative Atlas corpus into a complete, testable learning product. It exists so requirements do not depend on chat history or human memory.

## Authority
1. Atlas source data is authoritative for source content and canonical identity.
2. Existing repository code is authoritative for what is actually implemented until verified otherwise.
3. This contract is authoritative for required product capability and acceptance criteria.
4. Tests/evidence are authoritative for claims of implementation status.

## Known corpus
- 489 canonical subtopics.
- 516 research stories/content records.
- Existing Atlas fields and content must be preserved.
- Canonical IDs must remain stable unless a migration with explicit evidence is required.

## Product outcome
A learner can discover, enrol, orient, learn, practise, choose/dip, receive adaptive/personalised support where configured, assess, receive feedback, demonstrate mastery, receive an appropriate credential, apply learning, and return for follow-up. The system can measure learning and product outcomes and trace generated material back to Atlas source.

## Capability chain
SOURCE → CURRICULUM → LEARNING DESIGN → CONTENT → ASSETS → ACTIVITIES → ASSESSMENT → MARKING → FEEDBACK → MASTERY → CREDENTIAL → DELIVERY → LEARNER LIFECYCLE → CRM → SUPPORT → MARKETING → DEMAND → PUBLISHING → MEASUREMENT → ANALYTICS → QA → GOVERNANCE → VERSIONING → REGENERATION → INTEGRATION → AGENT AUTOMATION → OBSERVABILITY.

## Architecture rule
Capability-first and vendor-changeable. Vendor/tool names may be adapters, not the canonical data model. CSV is a canonical content/configuration index, not a runtime database, asset store, event log or secret store.

## Existing requirements to preserve
The course model supports the existing one-hour lesson concept, including Introduction, Overall Discussion/context, Example, lesson body, activities/practice, assessment, marking, micro-credential, post-activity/action, choice/dip paths and standard or personalised/adaptive presentation.

## Delivery boundary
The implementation must be production-capable where practical, but full-run verification uses local/test/staging/dry-run for externally consequential operations. Never send real campaigns, issue real learner credentials, alter real learner records, expose private services, spend unnecessarily, delete production data, or expose/rotate secrets without explicit authority.

## Non-negotiable evidence rule
No status may claim TESTED, QA_APPROVED, PRODUCTION_READY or LIVE without corresponding executable evidence.


## Verified source-discovery correction

The canonical 489/516 corpus has now been directly verified in the live T4H Atlas deployment. See `docs/atlas-course-engine/10-SOURCE-DISCOVERY.md` for the evidence and reconciliation. The 516 total is reconciled as 489 canonical subtopic story records plus 27 Ground Zero study-linked stories. The 4hr-Atlas repository remains the implementation/control-plane candidate, not the assumed source CSV location.
