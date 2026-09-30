# Definition of Done — Atlas Course Engine

This is the final acceptance contract. "Done" does not mean the code exists, the CSV has columns, a page renders, or a plan has been written.

## 1. Source is intact
- Authoritative Atlas source is identified.
- Canonical IDs are preserved.
- Complete corpus has been structurally validated.
- Expected 489 subtopics and 516 research stories are confirmed or any discrepancy is explicitly evidenced and explained.
- No source content was silently invented, discarded or overwritten.

## 2. Data and schema are coherent
- Existing valid Atlas/course fields remain usable.
- New lifecycle fields are controlled and documented.
- Runtime state is not improperly stuffed into the canonical CSV.
- Assets, activities, assessments, questions, credentials, events and integrations have appropriate representations.
- Provenance and versioning exist where required.

## 3. The engine actually works
A representative canonical record can execute through the implemented learning pathway rather than merely render configuration:

SOURCE → LESSON → ACTIVITY/PRACTICE → ASSESSMENT → MARKING → FEEDBACK → MASTERY → CREDENTIAL (test mode).

Choice/dip and personalisation are exercised where implemented.

## 4. The learner lifecycle is real
The implemented delivery layer can represent the relevant progression through discovery, enrolment, orientation, learning, practice, assessment, reflection, mastery, credential, application, follow-up and return. Unsupported stages are explicitly marked rather than implied.

## 5. Assets are evidenced
Each claimed generated/available asset has a resolvable reference and status. Specified, generated, QA-approved and live are not conflated. Representative multi-modal generation/integration is actually exercised where those capabilities are claimed.

## 6. Assessment and credentials are safe
Assessment attempts, answers, marking and feedback are persisted appropriately. Mastery follows defined evidence. Credentials are issued only when their rule is satisfied. Test execution cannot accidentally issue real credentials.

## 7. Integrations are proven
Every integration marked integrated/tested has a successful contract or smoke test and recorded evidence. Configuration alone is not evidence.

## 8. Automation is resumable
Workers/agents can resume, avoid duplicate idempotent work, record execution state and preserve receipts/evidence. Failure does not silently become success.

## 9. Quality gates pass
Required unit, integration, contract, end-to-end, data-integrity, security and regression tests pass, or every failure is explicitly recorded with its impact and disposition. No critical acceptance test is silently skipped.

## 10. Status is truthful
No item is TESTED without test evidence. No item is QA_APPROVED without QA evidence. No item is PRODUCTION_READY without the defined readiness gates. No item is LIVE without live evidence. Overall status cannot hide component failures.

## 11. Production boundary is respected
No real external campaign, learner credential issuance, destructive migration, secret exposure, private-service exposure or unnecessary spend occurs during verification without explicit authorization.

## 12. The complete dataset is accounted for
The implementation may use representative records for expensive/external execution, but the complete canonical dataset must pass structural validation and every record must have an accurate implementation state. There must be no unexplained "unknown" or blanket "done" state hiding unimplemented work.

## 13. Evidence package exists
The repository contains:
- implementation matrix
- test expectations
- executable/automatable tests
- execution state
- test results or CI links
- provenance evidence
- integration evidence
- known-gap/blocker register
- final status report

## 14. Final outcome
The project is Done only when a new engineer/agent can inspect the repository and determine, without asking the original human to reconstruct the conversation:

WHAT WAS REQUIRED → WHAT EXISTS → WHAT WAS EXECUTED → WHAT PASSED → WHAT FAILED → WHAT REMAINS → WHY.

If any of those cannot be answered from repository evidence, the project is not Done.
