# Gap and Evidence Register

Goose must maintain this file during execution.

| ID | Requirement | Current reality | Gap | Action | Evidence | Status |
|---|---|---|---|---|---|---|
| GAP-001 | Repository location | Must be discovered | Course-engine source/repo may differ from Atlas source repo | Inspect and record | commit/path | OPEN |

Rules:
- Never remove a gap without evidence.
- Never convert BLOCKED/FAILED into VERIFIED without rerunning the relevant test.
- Record external-service restrictions separately from implementation defects.
- Record deliberate safety skips separately from technical failures.
