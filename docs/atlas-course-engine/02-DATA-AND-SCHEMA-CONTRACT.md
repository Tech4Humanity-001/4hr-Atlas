# Atlas Course Engine — Data and Schema Contract

## Canonical course record
The canonical course index must retain existing Atlas fields and add only fields required for lifecycle, implementation and references. Avoid unnecessary duplication.

Required identity/provenance concepts:
- atlas_id / canonical_id
- theme/topic/subtopic identity
- research_story_id where applicable
- source_version
- source_hash or equivalent change marker where practical
- provenance/reference fields

Required learning concepts:
- lesson_duration
- introduction
- overall_discussion
- example
- lesson/content reference
- activity references
- pathway/choice/dip configuration
- personalisation/adaptation configuration
- post_activity/action

Required lifecycle dimensions:
source_status, content_status, curriculum_status, lesson_status, asset_status, activity_status, assessment_status, question_status, marking_status, feedback_status, mastery_status, credential_status, delivery_status, personalisation_status, crm_status, support_status, marketing_status, demand_status, publishing_status, measurement_status, analytics_status, qa_status, governance_status, version_status, regeneration_status, integration_status, execution_status, observability_status, security_status.

Implementation maturity:
SOURCE_ONLY | SPECIFICATION | SCHEMA | CONFIGURED | BUILT | GENERATED | INTEGRATED | TESTED | PRODUCTION | LIVE.

Controlled exception states:
BLOCKED | FAILED | REQUIRES_REGENERATION.

## Assets
Each asset should have asset_id, asset_type, asset_role, source/reference, generator/producer, version, status, QA status, location/reference, timestamps and provenance.

## Runtime separation
Learner events, answers, attempts, progress, analytics, execution logs, queues, secrets and operational telemetry belong in runtime stores, not the canonical CSV.

## Versioning
Never silently overwrite authoritative source. Generated artifacts should be addressable by version where regeneration matters.

## Overall status
Derive overall status from component states. Never manually set an overall status that contradicts evidence.
