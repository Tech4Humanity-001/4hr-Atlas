# Atlas Outcome Loop v0.1

Atlas is operated as a closed loop, not a collection of disconnected features.

## Live flow

1. Read live estate context.
2. Inspect current opportunities and evidence state.
3. Rank actionable work using WIN_SCORE, deadline and evidence gaps.
4. Return a prioritized action plan.
5. Push work into the Control Room queues.
6. A connected AI context reads the current state before acting.
7. Human-authorized work produces an external outcome or a recorded blocker.
8. The next context reads the changed estate state rather than restarting from memory.

## Current API outcomes

- `GET /api/v1/estate-context` gives the current estate state.
- `GET /api/v1/action-plan` gives prioritized work and next actions.
- `GET /api/v1/opportunities` exposes the underlying opportunity set.
- `GET /api/v1/opportunities/{id}` exposes evidence requirements, funder intelligence and partner state.
- `POST /api/v1/opportunities/{id}/rescore` refreshes WIN_SCORE.
- `POST /api/v1/control-room/rebuild` converts scored opportunities into operational queues.
- `GET /api/v1/control-room/queues` exposes the resulting work.

## Product rule

A feature is not considered complete merely because an endpoint exists. It must feed another useful step in the outcome chain or provide evidence that the chain is blocked.

## Current known live opportunity

The seeded opportunity data includes MRFF 2026 Mental Health Research Grant Opportunity GO8415, closing 16 September 2026. The data identifies it as an Australian government opportunity and links it to Atlas themes including Cognitive Performance and Neurodiversity and AI.

This is data state, not a claim that an application has been submitted.
