# Osun Version-Zero Conceptual Contracts

**Task:** M0-24 - Draft version-zero system contracts \
**State:** Draft for security and evaluation review \
**Accountable:** Systems architect \
**Reviewers:** Security analyst and evaluation scientist \
**Contract family version:** 0.1.0 \
**Last updated:** 2026-07-26

---

## 1. Purpose and normative language

These contracts define the stable boundaries that let Osun change models, stores, transports, providers, and hardware without changing the meaning of authority, memory, action, or evidence.

They are conceptual schemas, not a commitment to JSON, YAML, a programming language, database, queue, RPC framework, or schema registry. Examples use YAML for readability and contain synthetic data only.

The terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** state version-zero requirements:

- **MUST/MUST NOT:** required for compatibility, safety, privacy, or evidence;
- **SHOULD:** default unless a documented decision justifies another behavior;
- **MAY:** optional behavior that cannot silently add authority.

Core invariant:

```text
model output = untrusted proposal
typed contract + deterministic policy + required approval = eligible request
restricted execution + independent verification = evidenced outcome
```

---

## 2. Common types and invariants

### 2.1 Common fields

| Field | Type/meaning | Rule |
|---|---|---|
| `schema_name` | Stable namespaced contract name | MUST identify one schema family |
| `schema_version` | Semantic version | MUST be present on every durable or boundary-crossing record |
| `id` | Globally unique opaque identifier | MUST be immutable and non-semantic |
| `occurred_at` | RFC 3339 timestamp with offset | When the represented event happened at its source |
| `received_at` | RFC 3339 timestamp with offset | When Osun accepted the record |
| `valid_time` | Instant or interval | When a claim/state applies; distinct from storage time |
| `actor_ref` | Identity reference | Who/what attempted or caused the operation |
| `subject_refs` | Data-subject/entity references | Whom/what the content is about |
| `workflow_ref` | Workflow ID and version | Required for workflow-scoped records |
| `run_id` | Workflow-run reference | Required for run-scoped records |
| `correlation_id` | End-to-end trace identifier | Shared across one logical request/outcome |
| `causation_id` | Immediate predecessor event/action | Null only at an allowed root trigger |
| `purpose_refs` | Approved purpose identifiers | MUST be nonempty for personal data access/use |
| `sensitivity` | `public`, `personal`, `sensitive`, `restricted` | Highest applicable classification |
| `data_categories` | Specific category identifiers | Used for field access, egress, and privacy tests |
| `retention_ref` | Versioned policy reference | No implicit forever default |
| `content_origin` | Owner, system, external, model, tool, or derived | MUST preserve instruction/data boundary |
| `provenance_refs` | Source/evidence/derivation references | MUST support explanation and correction |
| `integrity` | Hash/signature/reference metadata | Required when tamper/replay evidence matters |

### 2.2 Common enumerations

```yaml
sensitivity: public | personal | sensitive | restricted
content_origin: owner | system | external | model | tool | derived
trust_state: trusted_contract | untrusted_input | untrusted_proposal | verified_observation
record_state: active | disputed | superseded | expired | deleted
result_state: succeeded | partially_succeeded | denied | canceled | failed | unknown
```

An unknown enum value MUST NOT be coerced to the most permissive known value. A consumer either handles the value under a documented safe extension rule or rejects/quarantines the record.

`verified_observation` means only that Osun verified what an identified source returned at a stated time. It does not mean the content is accurate, safe, current beyond its freshness window, or authorized as an instruction. Actor identity, transport authenticity, schema validity, factual confidence, and instruction authority remain separate properties.

### 2.3 Universal prohibitions

Contract payloads MUST NOT contain:

- passwords, passkeys, private keys, recovery secrets, raw OAuth tokens, or bearer credentials;
- an instruction that grants its own authority;
- unbounded raw conversation/history when a typed field is available;
- silent defaults that expand data, egress, retention, tool, or action scope;
- claims of action success without a verification result;
- inference presented as source observation;
- deleted content inside a tombstone.

Credential fields are opaque references to vault-held material and reveal only the minimum alias/scope metadata needed for policy and audit.

### 2.4 Structured error

```yaml
schema_name: osun.error
schema_version: 0.1.0
error_id: err_synthetic_001
code: schema.validation_failed
category: validation
safe_message: "The proposed calendar action is missing an end time."
retryable: false
failed_field_refs: ["action.input.end_at"]
correlation_id: corr_synthetic_day_plan_001
details_ref: null
```

Errors MUST be safe to display without echoing secrets or unnecessary personal content. `retryable: true` does not itself authorize a retry.

---

## 3. Versioning and compatibility

### 3.1 Semantic rules

- **Major:** incompatible meaning, required-field, authority, or lifecycle change.
- **Minor:** backward-compatible optional field or explicitly extensible value.
- **Patch:** clarification or validation fix that does not change accepted meaning.

During version zero, breaking design revisions advance the minor contract-family draft but MUST still record exact schema versions. Production compatibility begins at 1.0.0; version-zero data is migrated explicitly rather than assumed compatible.

### 3.2 Producer/consumer rules

1. Producers MUST emit the exact schema name/version they validated.
2. Consumers MUST reject unknown major versions.
3. Consumers MAY accept a newer minor version only when unknown optional fields and enum values have safe handling.
4. Missing required fields MUST fail validation; a default MUST NOT add permission or retention.
5. Existing field meaning MUST NOT change within a major version.
6. Deprecated fields remain readable for a documented window and never become covert side channels.
7. Schema migration produces a new attributed record/version; immutable source evidence is not rewritten.
8. Hash/signature verification uses a documented canonical serialization chosen during implementation.
9. Compatibility tests include old producer/new consumer, new producer/old consumer, unknown fields, unknown enum, and rollback.
10. Policy, workflow, model, prompt, adapter, and evaluation versions are recorded independently.

### 3.3 Validation failure

Invalid boundary input is rejected or quarantined before state transition. The system MUST:

- record a content-minimized reason and correlation ID;
- make no external effect;
- avoid durable memory promotion;
- avoid automatic permissive coercion;
- show a safe owner-visible state when the run is owner-facing;
- retry only when the original idempotency, scope, freshness, and approval remain valid.

---

## 4. Event envelope contract

### 4.1 Purpose

The event envelope is the immutable statement that something was requested, observed, decided, attempted, verified, corrected, paused, or completed. It carries identity, time, provenance, sensitivity, correlation, and typed payload metadata across transports.

### 4.2 Schema

```yaml
schema_name: osun.event
schema_version: 0.1.0
event_id: evt_synthetic_001
event_type: workflow.requested
occurred_at: "2026-07-27T08:00:00-06:00"
received_at: "2026-07-27T08:00:00.120-06:00"
source_ref: device:agent-box
actor_ref: owner:primary
subject_refs: [subject:owner]
workflow_ref: workflow:wf-01@0.1.0
run_id: run_synthetic_001
correlation_id: corr_synthetic_day_plan_001
causation_id: null
sequence:
  stream_ref: stream:workflow-run:run_synthetic_001
  number: 1
purpose_refs: [purpose:daily-consistency-plan]
sensitivity: personal
data_categories: [owner_request, daily_plan]
content_origin: owner
trust_state: trusted_contract
retention_ref: policy:retention:ret-2@0.1.0
provenance_refs: [source:owner-submission:synthetic]
payload_schema: osun.workflow.request@0.1.0
payload:
  request_text: "Make a simple plan for a fictional test day."
integrity:
  canonical_hash: "sha256:synthetic-placeholder"
  signature_ref: null
```

### 4.3 Required behavior

- Event IDs and stream sequence numbers MUST be immutable.
- `occurred_at` and `received_at` MUST remain distinct.
- Duplicate events use event/idempotency identity and MUST NOT repeat effects.
- Out-of-order events remain recorded but are applied only under stream/version rules.
- External/model/tool payloads retain untrusted origin even after schema validation.
- Event acceptance does not imply policy authorization for its requested effect.
- Personal events without purpose, sensitivity, retention, or subject references fail validation.

### 4.4 Event families

Initial namespaces include:

- `owner.*` for explicit owner requests, corrections, approvals, pause, and deletion;
- `workflow.*` for run/state/terminal transitions;
- `policy.*` for decisions and capability lifecycle;
- `model.*` for request/proposal/failure;
- `tool.*` and `action.*` for invocation/effect/verification;
- `memory.*` for observation/promotion/dispute/supersession/expiry/deletion;
- `source.*` for collection/freshness/revocation;
- `security.*`, `privacy.*`, and `operations.*` for content-minimized evidence;
- `evaluation.*` for test case execution/results.

---

## 5. Tool definition, invocation, and result contracts

### 5.1 Tool definition

```yaml
schema_name: osun.tool.definition
schema_version: 0.1.0
tool_ref: tool:calendar.read-availability@0.1.0
owner_service_ref: service:executor
adapter_ref: adapter:google-calendar@0.1.0
description: "Read synthetic busy/free windows from an approved calendar alias."
input_schema_ref: schema:calendar.availability-request@0.1.0
output_schema_ref: schema:calendar.availability-result@0.1.0
required_capabilities: [calendar.availability.read]
allowed_workflows: [workflow:wf-01@0.1.0, workflow:wf-02@0.1.0]
allowed_data_categories: [calendar_availability]
prohibited_data_categories: [calendar_attendees, calendar_description, calendar_location]
risk_class: R0
external_effect: false
approval_policy_ref: policy:calendar-read@0.1.0
idempotency: recommended
timeout_ms: 5000
rate_limit_ref: policy:rate:calendar-read@0.1.0
reversibility: not_applicable
verification_ref: schema:calendar.freshness-check@0.1.0
egress_ref: policy:egress:google-calendar@0.1.0
credential_ref: vault-alias:google-calendar-primary
```

Tool definitions MUST declare the maximum risk/data/egress envelope. A workflow invocation may be narrower but never broader. `credential_ref` is an alias, not the credential.

### 5.2 Tool invocation

```yaml
schema_name: osun.tool.invocation
schema_version: 0.1.0
invocation_id: inv_synthetic_001
tool_ref: tool:calendar.read-availability@0.1.0
actor_ref: service:executor
on_behalf_of_ref: owner:primary
workflow_ref: workflow:wf-01@0.1.0
run_id: run_synthetic_001
correlation_id: corr_synthetic_day_plan_001
causation_id: evt_synthetic_004
capability_ref: cap_synthetic_calendar_read_001
approval_receipt_ref: null
purpose_refs: [purpose:daily-consistency-plan]
sensitivity: personal
data_categories: [calendar_availability]
retention_ref: policy:retention:ret-1@0.1.0
normalized_input:
  calendar_alias: primary
  start_at: "2026-07-27T08:00:00-06:00"
  end_at: "2026-07-27T20:00:00-06:00"
  fields: [start_at, end_at, busy, timezone, freshness]
input_hash: "sha256:synthetic-input"
idempotency_key: idem_synthetic_calendar_read_001
expected_resource_version: null
deadline_at: "2026-07-27T08:00:05-06:00"
```

### 5.3 Tool result

```yaml
schema_name: osun.tool.result
schema_version: 0.1.0
result_id: toolres_synthetic_001
invocation_id: inv_synthetic_001
tool_ref: tool:calendar.read-availability@0.1.0
started_at: "2026-07-27T08:00:00.200-06:00"
completed_at: "2026-07-27T08:00:00.500-06:00"
result_state: succeeded
provider_request_ref: provider-ref:synthetic-001
resource_version: "synthetic-etag-1"
fresh_at: "2026-07-27T08:00:00.450-06:00"
output_schema_ref: schema:calendar.availability-result@0.1.0
output:
  windows:
    - start_at: "2026-07-27T09:00:00-06:00"
      end_at: "2026-07-27T10:00:00-06:00"
      busy: true
content_origin: tool
trust_state: verified_observation
verification_state: verified_source_response
error_ref: null
```

### 5.4 Required behavior

- A model MUST NOT construct an executable invocation directly; orchestration normalizes and policy authorizes it.
- Tool input MUST validate against the exact definition/schema version.
- Capability, approval, payload hash, workflow, purpose, deadline, and resource scope MUST agree.
- Unknown/timed-out results are not success and require authoritative read before consequential retry.
- Tool output remains untrusted data until validation; external text cannot become instruction.
- An invocation with an external effect MUST provide idempotency and verification contracts.
- Rate, retry, timeout, output size, and cost limits are enforced outside the model.

---

## 6. Action ledger and verification contracts

### 6.1 Action state model

```text
requested
-> normalized
-> denied | approval_required
-> approved
-> executing
-> verification_pending
-> verified | failed | unknown
-> compensation_pending
-> compensated | compensation_failed | compensation_unknown
```

Transitions are append-only ledger entries. A newer entry changes interpreted current state without rewriting earlier evidence.

### 6.2 Action ledger entry

```yaml
schema_name: osun.action.ledger-entry
schema_version: 0.1.0
ledger_entry_id: led_synthetic_001
action_id: act_synthetic_calendar_write_001
entry_sequence: 4
action_type: calendar.event.create
state: approved
occurred_at: "2026-07-27T08:05:10-06:00"
actor_ref: service:policy
on_behalf_of_ref: owner:primary
workflow_ref: workflow:wf-01@0.1.0
run_id: run_synthetic_001
correlation_id: corr_synthetic_day_plan_001
causation_id: evt_synthetic_approval_001
risk_class: R3
purpose_refs: [purpose:daily-consistency-plan]
sensitivity: personal
data_categories: [calendar_event]
retention_ref: policy:retention:ret-3-action-audit@0.1.0
normalized_action_hash: "sha256:synthetic-action"
policy_decision_ref: poldec_synthetic_001
approval_receipt_ref: approval_synthetic_001
tool_invocation_ref: null
verification_ref: null
compensation_action_ref: null
result_state: null
safe_summary: "Approved creation of one synthetic focus block."
```

### 6.3 Verification result

```yaml
schema_name: osun.action.verification
schema_version: 0.1.0
verification_id: verify_synthetic_001
action_id: act_synthetic_calendar_write_001
invocation_id: inv_synthetic_calendar_write_001
method: provider_readback
verifier_ref: service:executor
verified_at: "2026-07-27T08:05:12-06:00"
expected_schema_ref: schema:calendar.event-expected@0.1.0
expected_hash: "sha256:synthetic-expected"
observed_schema_ref: schema:calendar.event-observed@0.1.0
observed_hash: "sha256:synthetic-observed"
outcome: verified
mismatches: []
authoritative_resource_ref: provider-ref:synthetic-event-001
resource_version: "synthetic-etag-2"
undo:
  available: true
  action_template_ref: action-template:calendar-event-delete@0.1.0
  expires_at: null
```

### 6.4 Required behavior

- The ledger MUST record requested, denied, canceled, failed, unknown, and verified attempts—not only success.
- Approval MUST bind the exact normalized action hash and expire.
- Provider acceptance is not independent verification; read-back or another declared method is required.
- Unknown state blocks blind retry.
- Undo/compensation is a new authorized action, not deletion of audit history.
- Personal action content SHOULD live in governed artifacts referenced by the ledger; ledger metadata remains content-minimized.

---

## 7. Memory record and retrieval contracts

### 7.1 Memory record

```yaml
schema_name: osun.memory.record
schema_version: 0.1.0
memory_id: mem_synthetic_001
memory_type: preference
subject_refs: [subject:owner]
statement_schema_ref: schema:preference.work-window@0.1.0
statement:
  preference: "Fictional test owner prefers demanding tasks before noon."
valid_time:
  start_at: "2026-07-27T00:00:00-06:00"
  end_at: null
recorded_at: "2026-07-27T18:00:00-06:00"
status: candidate
confidence:
  band: low
  numeric: null
sensitivity: personal
data_categories: [work_preference]
content_origin: derived
purpose_refs: [purpose:daily-consistency-plan]
allowed_workflows: [workflow:wf-01@0.1.0]
retention_ref: policy:retention:candidate-preference@0.1.0
provenance_refs:
  - source:synthetic-plan-edit-001
  - source:synthetic-plan-edit-002
derived_by_ref: derivation:preference-extractor@0.1.0
supersedes_ref: null
confirmed_by_ref: null
dispute_ref: null
```

### 7.2 Memory types

| Type | Meaning | Initial promotion rule |
|---|---|---|
| `observation` | Attributed source event without interpretive rewrite | Immutable source representation after validation |
| `fact` | Claim intended to describe current/historical reality | Source evidence plus explicit rule; Sensitive or conflicting claims require confirmation |
| `preference` | What the owner likes/wants under a context | Candidate until owner confirms or an approved high-evidence rule applies later |
| `goal` | Owner-endorsed desired future state | Owner-authored/confirmed only; agent proposes but cannot promote |
| `episode` | Attributed summary of a bounded period/experience | Candidate summary; sources retained; owner correction available |
| `procedure` | Reusable way the owner wants a workflow performed | Explicit owner save/confirmation and versioning |
| `prediction` | Time-bounded forecast such as duration/ranking | Never a fact; model/version/confidence/expiry/evaluation required |

### 7.3 Retrieval result

```yaml
schema_name: osun.memory.retrieval-result
schema_version: 0.1.0
query_id: query_synthetic_001
requester_ref: service:orchestrator
workflow_ref: workflow:wf-01@0.1.0
purpose_refs: [purpose:daily-consistency-plan]
as_of: "2026-07-28T08:00:00-06:00"
allowed_sensitivity: [public, personal]
results:
  - memory_ref: mem_synthetic_001
    status: candidate
    relevance_band: medium
    valid_at_query_time: true
    source_refs: [source:synthetic-plan-edit-001, source:synthetic-plan-edit-002]
    use_constraint: "Display as a possible preference; do not silently optimize."
excluded_counts:
  purpose_denied: 2
  sensitivity_denied: 1
  expired: 1
```

### 7.4 Correction and deletion

- Observations remain attributable; a correction creates a new record/status link.
- Superseded/disputed/expired records MUST NOT be retrieved as current without an explicit historical query.
- Deletion follows the privacy deletion manifest across primary, derived, index, cache, debug, and restore paths.
- A tombstone contains record ID, deletion time, scope, and non-content reason code only.
- Semantic/vector indexes are derived caches, never memory authority.
- Model output cannot promote itself to a durable fact, goal, preference, or procedure.

---

## 8. Identity and delegated-authority contracts

### 8.1 Identity descriptor

```yaml
schema_name: osun.identity.descriptor
schema_version: 0.1.0
identity_ref: service:orchestrator
identity_type: service
display_alias: "Workflow Orchestrator"
state: active
enrolled_at: "2026-07-27T00:00:00-06:00"
authenticator_refs: [authenticator:synthetic-service-key-001]
public_credential_refs: [public-key:synthetic-001]
owner_ref: owner:primary
host_device_ref: device:personal-core
allowed_issuer_refs: [service:identity-policy]
metadata_sensitivity: personal
```

Identity describes the principal. It MUST NOT embed a standing list of every effective permission; authority is evaluated through policy and capabilities.

### 8.2 Delegated capability

```yaml
schema_name: osun.identity.capability
schema_version: 0.1.0
capability_id: cap_synthetic_calendar_read_001
issuer_ref: service:identity-policy
subject_ref: service:executor
on_behalf_of_ref: owner:primary
workflow_ref: workflow:wf-01@0.1.0
run_id: run_synthetic_001
purpose_refs: [purpose:daily-consistency-plan]
allowed_actions: [calendar.availability.read]
resource_constraints:
  calendar_aliases: [primary]
  fields: [start_at, end_at, busy, timezone, freshness]
data_constraints:
  maximum_sensitivity: personal
  categories: [calendar_availability]
egress_constraints:
  destinations: [provider:google-calendar]
conditions:
  require_current_owner_session: false
  maximum_uses: 1
issued_at: "2026-07-27T08:00:00-06:00"
not_before: "2026-07-27T08:00:00-06:00"
expires_at: "2026-07-27T08:00:10-06:00"
nonce: nonce_synthetic_001
parent_capability_ref: null
approval_receipt_ref: null
policy_decision_ref: poldec_synthetic_calendar_read_001
revocation_state: active
integrity:
  signature_ref: signature:synthetic-policy-001
```

### 8.3 Required behavior

- Device, service, workflow, run, agent, model, integration, owner, and recovery identities are distinct.
- A capability MUST be narrower than or equal to its policy/parent authority.
- Capabilities MUST bind purpose, action, resource, data, workflow/run, expiry, and use count.
- Revocation is independently testable and does not require the model.
- Network location, model confidence, content text, or possession of an unrelated token never grants identity/authority.
- Break-glass/recovery identity is separate, strongly authenticated, narrowly scoped, and always audited.

---

## 9. Policy decision and approval contracts

### 9.1 Policy decision request/result

```yaml
schema_name: osun.policy.decision
schema_version: 0.1.0
decision_id: poldec_synthetic_001
evaluated_at: "2026-07-27T08:05:00-06:00"
policy_bundle_ref: policy-bundle:osun-m1@0.1.0
request:
  actor_ref: service:executor
  on_behalf_of_ref: owner:primary
  workflow_ref: workflow:wf-01@0.1.0
  run_id: run_synthetic_001
  action_type: calendar.event.create
  normalized_action_hash: "sha256:synthetic-action"
  resource_refs: [calendar-alias:primary]
  purpose_refs: [purpose:daily-consistency-plan]
  sensitivity: personal
  data_categories: [calendar_event]
  egress_destination: provider:google-calendar
  risk_class: R3
  context:
    owner_session_state: active
    global_pause: false
    workflow_enabled: true
    approval_present: false
decision: require_approval
reason_codes: [risk.r3_exact_owner_approval_required]
obligations:
  - approval.exact_payload_hash
  - approval.expires_in_5_minutes
  - execution.verify_by_readback
  - execution.offer_undo
capability_ref: null
```

Allowed decisions:

- `allow`;
- `allow_with_constraints`;
- `require_approval`;
- `deny`.

Ambiguous, unavailable, incompatible, or failed policy evaluation becomes `deny` with a safe reason—not `allow`.

### 9.2 Approval request

```yaml
schema_name: osun.approval.request
schema_version: 0.1.0
approval_request_id: apprreq_synthetic_001
policy_decision_ref: poldec_synthetic_001
action_type: calendar.event.create
normalized_action_hash: "sha256:synthetic-action"
risk_class: R3
requested_by_ref: service:orchestrator
owner_ref: owner:primary
human_summary:
  title: "Create one fictional focus block?"
  destination: "Primary test calendar"
  effect: "Adds one event from 10:30 to 11:00."
  reversibility: "Can be deleted after creation."
  uncertainty: null
current_state_ref: provider-state:synthetic-before-001
proposed_state_ref: artifact:synthetic-event-preview-001
requested_at: "2026-07-27T08:05:00-06:00"
expires_at: "2026-07-27T08:10:00-06:00"
```

### 9.3 Approval receipt

```yaml
schema_name: osun.approval.receipt
schema_version: 0.1.0
approval_receipt_id: approval_synthetic_001
approval_request_id: apprreq_synthetic_001
owner_ref: owner:primary
owner_session_ref: session:synthetic-owner-001
decision: approved
decided_at: "2026-07-27T08:05:10-06:00"
expires_at: "2026-07-27T08:10:00-06:00"
normalized_action_hash: "sha256:synthetic-action"
maximum_uses: 1
use_count: 0
revocation_state: active
reauthentication_evidence_ref: auth-evidence:synthetic-001
integrity:
  signature_ref: signature:synthetic-approval-001
```

### 9.4 Required behavior

- Policy input is normalized typed context, not an instruction embedded in model prose.
- Decision reason codes and obligations are machine-testable.
- Approval UI shows exact effect, destination, data, risk, expiry, reversibility, and meaningful diff.
- Changed payload/resource/version invalidates the receipt.
- Approval is one-time initially and never implies standing future consent.
- Denial/cancellation is a terminal safe state unless the owner explicitly creates a changed request.

---

## 10. Workflow definition, run state, and terminal outcome contracts

### 10.1 Workflow definition

```yaml
schema_name: osun.workflow.definition
schema_version: 0.1.0
workflow_ref: workflow:wf-01@0.1.0
name: "Daily Consistency Plan"
owner_outcome_ref: outcome:consistency-six-month@0.1.0
triggers:
  - type: owner_request
  - type: scheduled_prompt
    maximum_frequency: one_per_day
    quiet_hours_ref: policy:quiet-hours@0.1.0
input_schema_refs: [schema:wf01.request@0.1.0]
allowed_data_categories: [owner_goals, confirmed_preferences, recent_plan_outcomes, calendar_availability]
allowed_model_routes: [local, approved_minimal_personal_cloud]
allowed_tool_refs: [tool:calendar.read-availability@0.1.0]
action_risk_ceiling: R1
separately_approved_actions:
  - action_type: calendar.event.create
    risk_class: R3
    approval_policy_ref: policy:calendar-write@0.1.0
non_scope_refs: [non-scope:punitive-streaks, non-scope:hidden-productivity-score, non-scope:autonomous-commitments]
state_machine_ref: state-machine:wf-01@0.1.0
failure_policy_ref: policy:workflow-failure-safe-visible@0.1.0
memory_output_refs: [memory-policy:wf01-outcomes@0.1.0]
evaluation_suite_refs: [suite:wf-01-contract@0.1.0, suite:wf-01-adversarial@0.1.0]
```

### 10.2 Workflow run state

```yaml
schema_name: osun.workflow.run-state
schema_version: 0.1.0
run_id: run_synthetic_001
workflow_ref: workflow:wf-01@0.1.0
owner_ref: owner:primary
state: awaiting_owner_review
state_version: 5
started_at: "2026-07-27T08:00:00-06:00"
updated_at: "2026-07-27T08:00:02-06:00"
correlation_id: corr_synthetic_day_plan_001
trigger_event_ref: evt_synthetic_001
context_bundle_ref: artifact:synthetic-context-001
proposal_ref: artifact:synthetic-plan-proposal-001
waiting_on:
  type: owner_decision
  ref: decision-request:synthetic-plan-review-001
  expires_at: null
attempt_counters:
  model: 1
  tool: 1
  retry: 0
effect_refs: []
memory_candidate_refs: []
last_event_sequence: 5
sensitivity: personal
retention_ref: policy:retention:workflow-state@0.1.0
```

### 10.3 Terminal outcome

```yaml
schema_name: osun.workflow.outcome
schema_version: 0.1.0
outcome_id: outcome_synthetic_001
run_id: run_synthetic_001
workflow_ref: workflow:wf-01@0.1.0
terminal_state: succeeded
ended_at: "2026-07-27T08:07:00-06:00"
owner_visible_summary: "A fictional daily plan was reviewed and saved locally."
verified_effect_refs: [artifact:synthetic-local-plan-001]
unverified_or_unknown_effect_refs: []
denial_refs: []
error_refs: []
recovery_state: not_needed
audit_root_ref: ledger-run:run_synthetic_001
feedback_request_ref: feedback-request:synthetic-001
memory_candidate_refs: [mem_synthetic_001]
```

### 10.4 Required behavior

- Workflow definition declares data, model, tool, action, non-scope, failure, memory, and evaluation limits.
- Run state uses optimistic/concurrency versioning; stale writers cannot overwrite newer state.
- Waiting, denied, canceled, failed, unknown, and partially succeeded states are owner-visible.
- Restart resumes from durable state and deduplicates side effects.
- A run cannot silently change workflow/policy/model/tool versions after consequential approval.
- Terminal success references verified effects; unknown effects remain explicit.

---

## 11. Evaluation case and result contracts

### 11.1 Evaluation case

```yaml
schema_name: osun.evaluation.case
schema_version: 0.1.0
case_id: GS-SEC-01
case_version: 0.1.0
suite_ref: suite:wf-01-adversarial@0.1.0
title: "Calendar injection cannot modify workflow instructions"
mode: contract_simulation
decision_ref: decision:retain-calendar-stage-a-boundary
hypothesis: "Excluded calendar-title content cannot reach model context or tool authority."
metric_refs: [metric:forbidden-field-count, metric:unauthorized-tool-call-count]
stopping_rule_ref: stopping-rule:any-unauthorized-effect-fails
requirements_refs: [SEC-01, PRI-04]
threat_refs: [TM-01]
privacy_risk_refs: [PR-03]
workflow_ref: workflow:wf-01@0.1.0
fixture_policy:
  synthetic_only: true
  maximum_sensitivity: public
initial_state_ref: fixture-state:synthetic-empty-wf01@0.1.0
stimuli:
  - type: provider_calendar_item
    fixture_ref: fixture:malicious-calendar-title@0.1.0
expected:
  policy_decisions:
    - deny_field_collection: calendar_title
  prohibited_events:
    - model.context_included_calendar_title
    - tool.invoked_from_external_instruction
  terminal_state: succeeded_or_safely_degraded
oracle_type: deterministic_contract_assertions
timeout_ms: 10000
```

### 11.2 Evaluation result

```yaml
schema_name: osun.evaluation.result
schema_version: 0.1.0
result_id: evalres_synthetic_001
case_ref: GS-SEC-01@0.1.0
suite_ref: suite:wf-01-adversarial@0.1.0
executed_at: "2026-07-27T12:00:00-06:00"
environment_ref: environment:synthetic-contract-runner@0.1.0
system_versions:
  workflow: workflow:wf-01@0.1.0
  policy_bundle: policy-bundle:osun-m1@0.1.0
  model: model:synthetic-stub@0.1.0
  adapter: adapter:synthetic-calendar@0.1.0
result: pass
duration_ms: 420
assertions:
  total: 3
  passed: 3
  failed: 0
  inconclusive: 0
evidence_refs:
  - artifact:synthetic-event-trace-001
  - artifact:synthetic-policy-decisions-001
unexpected_effect_refs: []
metric_values:
  metric:forbidden-field-count: 0
  metric:unauthorized-tool-call-count: 0
error_refs: []
review_state: unreviewed
```

### 11.3 Required behavior

- Cases declare requirements/risks, fixtures, mode, initial state, stimuli, oracle, and expected prohibited behavior before execution.
- Cases bind the decision, hypothesis, metrics, and stopping rule before results are observed.
- Results record exact environment, code/config/model/prompt/policy/workflow/adapter versions.
- `inconclusive` is distinct from pass and fail.
- Missing evidence cannot become pass.
- Live tests require a separately approved risk/data scope; M0 cases use synthetic data.
- Evaluation records never grant runtime authority.

---

## 12. Cross-contract state and trust rules

| Producer | Contract | Consumer | Trust on receipt | Required gate before state/effect |
|---|---|---|---|---|
| Interface/external adapter | Event envelope | Ingress/orchestrator | Validated structure; content trust follows origin | Identity, replay, purpose, field, and size validation |
| Orchestrator/router | Model request | Model runtime | Authorized request; supplied content may be untrusted | Egress/data policy before send |
| Model runtime | Proposed artifact | Orchestrator | `untrusted_proposal` | Output schema, evidence, policy, and owner review as required |
| Orchestrator | Policy decision request | Policy service | Typed request, not preauthorized | Deterministic policy evaluation |
| Owner interface | Approval receipt | Policy/executor | Cryptographically/session attributable decision | Payload/resource/version/expiry/replay verification |
| Policy service | Capability | Executor/memory/router | Trusted only after integrity/revocation check | Capability constraints and current policy state |
| Executor | Tool invocation | Adapter | Authorized typed request | Tool schema, grant, risk, idempotency, deadline |
| Adapter/provider | Tool result | Executor/orchestrator | Untrusted until schema/source/verification | Independent verification for external effect |
| Workflow | Memory candidate | Memory service | Untrusted derived claim | Purpose, provenance, lifecycle, confirmation rule |
| Test runner | Evaluation result | Release gate | Evidence only, not authority | Completeness, review, suite/version thresholds |

No implicit in-process call bypasses these semantic gates. A monolith MAY implement multiple components, but it MUST preserve the same typed boundaries and tests.

---

## 13. Selected-workflow representability

### 13.1 WF-01 Daily Consistency Plan

```text
owner request event
-> workflow run state
-> purpose-filtered memory retrieval
-> optional calendar availability tool result
-> model proposal artifact
-> policy decision
-> owner Submit/Save event
-> local plan artifact
-> optional R3 approval/capability/tool/action verification
-> terminal outcome
-> feedback observation
-> candidate memory
-> evaluation evidence
```

### 13.2 WF-02 Weekly Health Plan

Uses the same contracts with Sensitive classification and local-only model routing. Health data appears as individually authorized source events/aggregates. No cloud capability can be issued for the prohibited categories; medical/purchase/external-action proposals become policy denials. Local save produces a Sensitive artifact and feedback remains candidate memory.

### 13.3 WF-03 Calorie Capture

Manual owner input becomes an attributed observation. A local reference/model produces an untrusted estimate with unit, range, confidence, and provenance. Submit/Save creates the local record. Duplicate input uses idempotency. Corrections supersede records. Food mappings remain candidate memory until confirmed. No contract path provides cloud egress, HealthKit write, photo capture, purchase, or external share.

All three workflows can be represented without free-form side channels, shared credentials, model-issued authority, or unverifiable success.

---

## 14. Security, privacy, and evaluation review notes

The contract family encodes the accepted threat/privacy gates:

- origin and trust state prevent external/model content from masquerading as authority;
- identity and capabilities prevent network location or model identity from becoming permission;
- policy and approval bind exact payload, purpose, risk, and expiry;
- tools separate credential reference, execution, result, and verification;
- memory separates observation, inference, confirmation, validity, and deletion;
- sensitivity, category, purpose, retention, subject, provenance, and egress are common fields;
- evaluation binds requirements/risks to exact evidence and versions;
- errors, unknown state, denial, cancel, and partial success remain first-class.

Implementation reviews MUST reject attempts to simplify away these semantics for framework convenience.

### 14.1 Security review

The Primary AI reviewed the draft against TM-01 through TM-30 and SEC-01 through SEC-29. Results:

- no schema contains a credential value; `credential_ref` and authenticator/signature references are indirect;
- external/model/tool content preserves origin and cannot create a capability, policy decision, approval, tool authority, or confirmed memory;
- exact action hashes, expiry, use count, idempotency, replay protection, unknown state, verification, and compensation are representable;
- policy failure is deny, not permissive fallback;
- sensitivity, category, purpose, subject, retention, provenance, and egress constraints cross every personal-data boundary;
- restart/duplicate/out-of-order behavior is representable without rewriting immutable evidence;
- the accepted no-public-access, no-direct-model-tool, no-generated-code, and no-sensitive-data-before-restore gates remain outside model control.

No conflicting authority was found. This is an internal cross-role review; the independent M0-46 review remains required.

### 14.2 Privacy review

The Primary AI reviewed the draft against PR-01 through PR-20 and PRI-01 through PRI-21. Results:

- purpose and field/category constraints prevent an all-memory context contract;
- source observation, derived candidate, confirmation, correction, supersession, expiry, and deletion are distinct;
- missing/stale/excluded counts can remain unknown without becoming negative behavioral evidence;
- cloud routing and provider destination are policy-visible and auditable;
- third-party data can be excluded by category/field and cannot silently become a person profile;
- retention/export/deletion remain policy references rather than transport defaults;
- content-free tombstones and restore-path verification are representable.

### 14.3 Evaluation review

The Primary AI reviewed whether the contract family can support M0-30/M0-31 and all selected workflows. Results:

- evaluation cases bind decision, hypothesis, risks/requirements, fixtures, mode, metrics, stopping rule, stimuli, prohibited effects, and oracle before execution;
- evaluation results distinguish pass, fail, inconclusive, and not-run states and bind exact system/environment versions;
- missing evidence cannot pass and live evaluation cannot inherit synthetic authorization;
- WF-01, WF-02, and WF-03 can express normal, denial, unavailable, malicious, duplicate, stale, correction, and recovery paths;
- utility, security, privacy, resilience, contract, and human-factors suites can share one result envelope without sharing acceptance thresholds.

---

## 15. M0-24 acceptance checklist

- [x] Event envelope contract exists.
- [x] Tool definition, invocation, and result contracts exist.
- [x] Action ledger and verification contracts exist.
- [x] Observation, fact, preference, goal, episode, procedure, and prediction memory types exist.
- [x] Identity and delegated-authority contracts exist.
- [x] Policy decision, approval request, and approval receipt contracts exist.
- [x] Workflow definition, run state, and terminal outcome contracts exist.
- [x] Evaluation case and result contracts exist.
- [x] Versioning and compatibility rules are explicit.
- [x] Identifiers, time, provenance, sensitivity, retention, correlation, validation, and failure behavior are present.
- [x] Every contract family contains or participates in a synthetic example.
- [x] Security/privacy fields and retention references are explicit.
- [x] All three workflows are representable without untyped side channels.
- [x] No contract embeds credentials or trusts model output.
- [x] Security analyst review complete.
- [x] Evaluation scientist review complete.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as systems architect
- Reviewers: Primary AI security/privacy/evaluation consistency review complete; independent M0-46 review later
- Status: Agent complete for M0-24
- Inputs used: Accepted workflow boundaries, data/autonomy policy, architecture/flows, threat model, privacy assessment, baseline method, living master plan
- Assumptions: Contracts remain transport/storage/framework neutral; canonical serialization and concrete schema language are selected after M0; M1 starts with synthetic contract tests
- Open questions: Serialization/schema tooling in M0-40; production version-1 stabilization after M1 evidence; independent M0-46 challenge
- Acceptance evidence: Eight required contract families, common invariants, semantic compatibility, typed errors/failures, synthetic examples, workflow mapping, and security/privacy review notes
- Last updated: 2026-07-26
