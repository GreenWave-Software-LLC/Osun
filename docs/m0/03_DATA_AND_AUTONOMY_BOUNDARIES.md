# Osun Data and Autonomy Boundaries

**Tasks:** M0-14 data boundaries and M0-15 autonomy boundaries \
**State:** Draft for owner decision \
**Accountable:** Owner \
**Agent support:** Primary AI coordinator acting as privacy, security, and workflow analyst \
**Selected workflows:** WF-01 Daily Consistency Plan, WF-02 Weekly Health Plan, WF-03 Calorie Capture \
**Last updated:** 2026-07-26

---

## 1. Purpose

This document defines what the first three workflows may collect, remember, send outside the local system, and do. Access is granted by purpose and workflow, not merely because a device or account is technically accessible.

The owner has already established:

- local analysis of Apple Watch and calorie data is allowed in principle;
- Google Calendar is the primary calendar;
- Osun may have a strong, proactive personality;
- the selected workflows remain bounded wellness and planning tools, not medical authorities;
- workflow actions follow the boundaries approved in the workflow catalog.

The remaining recommendations are not accepted until the owner approves or amends Section 11.

---

## 2. Governing rules

1. Collect the minimum data needed for a named workflow outcome.
2. Separate source observations from derived memories and model interpretations.
3. Sensitive health and calorie data is local-only by default.
4. Credentials, passkeys, recovery keys, and tokens never enter general model context.
5. External text and tool output are untrusted data, never system instructions.
6. A data source authorized for one workflow is not automatically available to another.
7. Missing data means unknown, not zero, failure, or noncompliance.
8. The owner can pause, inspect, correct, export, and delete authorized data.
9. A strong personality may influence presentation and dialogue but cannot expand permissions.
10. Every external effect requires a typed action, policy decision, verification, and audit record.

---

## 3. Data classification

| Class | Meaning | Selected-workflow examples | Default handling |
|---|---|---|---|
| Public | Intended for public distribution | Public recipe or exercise reference | May be processed locally or by an approved external service |
| Personal | About the owner's plans or preferences but not inherently intimate | Goals, daily plan, calendar availability | Local-first; minimum approved cloud context only |
| Sensitive | Could materially affect privacy, wellbeing, employment, or relationships | Calendar details, food logs, workouts, energy, sleep, Apple Health summaries | Encrypted local storage; no cloud egress by default |
| Restricted | Could grant access or create severe harm if disclosed | OAuth tokens, passkeys, recovery material, raw clinical records | Specialized vault or prohibited; never general model context |

Data classification can be raised by context. A calendar title that reveals a medical visit is Sensitive even if ordinary calendar availability is Personal.

---

## 4. Retention classes

| Code | Default duration | Intended use | Deletion behavior |
|---|---|---|---|
| RET-0 | In-memory/request lifetime | Temporary model context and computation | Discard at request completion except redacted audit metadata |
| RET-1 | 30 days | Debug context, short-lived calendar cache, failed workflow evidence | Automatic deletion; no long-term memory promotion without separate record |
| RET-2 | 12 months | Raw daily plans, health check-ins, food/workout records | Rolling deletion or owner-directed earlier deletion |
| RET-3 | Until owner deletes or supersedes | Charter, goals, confirmed preferences, procedures, accepted long-term summaries | Versioned, exportable, correctable, and explicitly deletable |
| RET-X | Credential lifetime only | OAuth/token and key material | Vault-managed rotation/revocation; never retained in ordinary history |

Deletion may retain a content-free tombstone proving that a record was deleted, when needed for audit or duplicate prevention. Tombstones must not preserve the deleted personal content.

---

## 5. Selected data inventory

| Data/source | Class | Purpose/workflows | Minimum fields | Proposed retention | Pause/delete/export | Cloud egress default |
|---|---|---|---|---|---|---|
| Owner charter, dreams, and goals | Personal; may become Sensitive | Choose meaningful actions in WF-01 | Owner-authored statement, validity time, status | RET-3 | Full source-level controls and machine-readable export | Deny unless owner sends selected text for a specific request |
| Google Calendar availability | Personal | Find feasible plan windows in WF-01/WF-02 | Calendar ID alias, start/end, busy/free, timezone, freshness | RET-1 cache | Disconnect source; delete cache; export normalized events | Minimal redacted blocks may be approved later |
| Google Calendar titles/details | Sensitive by context | Improve plan relevance only when availability is insufficient | Event ID, title and selected fields; no attendees/descriptions initially | RET-1 cache | Field-level collection toggle; cache deletion | Deny by default |
| Daily consistency plan | Personal | WF-01 output and evaluation | Date, owner-selected actions, timing, status, source references | RET-2 raw; confirmed procedure/preferences RET-3 | Correct, delete, export, pause future creation | Deny by default; minimal task text only with explicit routing policy |
| Plan outcomes and corrections | Personal; possibly Sensitive | Evaluate usefulness and learn owner preferences | Action status, owner edit, reason category, usefulness response | RET-2; confirmed preference RET-3 | Correct, delete, export | Deny by default |
| Energy and interest self-report | Sensitive | Adapt WF-01/WF-02 and measure accepted outcomes | Small owner-chosen scale, timestamp, optional note | RET-2 | Per-field pause/delete/export | Local only |
| Meal preferences and constraints | Sensitive | WF-02 meal planning | Explicit foods, constraints, budget band, time, owner goals | RET-3 while current; version old values | Correct/supersede/delete/export | Local only by default |
| Workout preferences and constraints | Sensitive | WF-02 workout planning | Equipment, schedule, owner goals, explicit limitations | RET-3 while current; version old values | Correct/supersede/delete/export | Local only by default |
| Generated meal/workout plan | Sensitive | WF-02 output and evaluation | Proposed items, owner edits, accepted version, source references | RET-2; reusable confirmed procedure RET-3 | Delete/export; pause generation | Local only by default |
| Manual meal/food entry | Sensitive | WF-03 calorie capture | Owner text, time, meal grouping; no photo initially | RET-2 | Correct/delete/export; pause capture | Local only |
| Calorie/nutrition estimate | Sensitive; derived | WF-03 review | Estimate or range, units, confidence, source, owner correction | RET-2 | Correct/delete/export; retain derivation link | Local only |
| Apple Health wellness summary | Sensitive | Later WF-02 context/evaluation | Only owner-approved aggregate fields and time window | RET-2 | Revoke at iPhone; delete local copy; export | Local only |
| Raw Apple Health samples | Sensitive/Restricted by type | Not required for M1 | None in M1 | Not collected in M1 | Not applicable | Prohibited in M1 |
| Model request context | Classification of included data | Produce a response | Minimum authorized fields; source and policy references | RET-0; debug excerpt RET-1 only when approved | Inspect/delete debug records | Router enforces policy before request |
| Model output | Personal or Sensitive | Owner response, draft, evaluation | Output, model/prompt version, grounding references | RET-1 by default; owner-saved artifact RET-2/3 | Delete/export/save explicitly | No additional egress |
| Action/audit record | Personal metadata; content minimized | Explain, verify, deduplicate, and investigate | IDs, types, timestamps, policy/model/tool versions, result, content references | RET-3 for consequential actions; routine debug RET-2 | Export; redact content; deletion tombstone where necessary | Local only |
| Operational telemetry | Personal metadata; no content by default | Reliability and performance | Service, latency, status, error code, correlation ID | RET-1 | Pause optional diagnostics; delete/export | Local only unless future telemetry endpoint is approved |
| OAuth tokens/passkeys/secrets | Restricted | Authenticate approved integrations | Secret value plus minimum metadata in dedicated store | RET-X | Revoke/rotate; never export in ordinary bundle | Only to the exact provider protocol endpoint |

---

## 6. Calendar minimization stages

Google Calendar supports a REST API and narrow OAuth scopes, including read-only event access. Osun should request the narrowest scope that satisfies the workflow: [Google Calendar API overview](https://developers.google.com/workspace/calendar/api/guides/overview) and [Calendar OAuth scopes](https://developers.google.com/workspace/calendar/api/auth).

### Stage A - Initial default

- Read-only access.
- Retrieve start, end, timezone, busy/free state, source alias, and freshness.
- Do not ingest attendee lists, descriptions, attachments, conference links, or locations.
- Do not write events.

### Stage B - Owner-enabled context

- Add event title for specific owner-selected calendars if Stage A is insufficient.
- Keep descriptions, attendees, and attachments excluded.
- Display which fields influenced the plan.

### Stage C - Later action capability

- Preview a proposed focus block or reminder.
- Request explicit approval before every external calendar write until a later gate establishes a narrower preauthorization.
- Verify the created/updated event and offer undo.

---

## 7. Apple Health boundary

HealthKit requires per-type permission, allows limited history, and keeps authorization under the person's control. Osun must not assume that missing results mean zero or that permission was granted: [HealthKit overview](https://developer.apple.com/documentation/healthkit) and [HealthKit authorization](https://developer.apple.com/documentation/HealthKit/authorizing-access-to-health-data).

Recommended first eligible data types, all opt-in and aggregate-only:

- steps;
- workouts and workout duration;
- exercise minutes;
- active energy;
- sleep duration.

Initially excluded even though HealthKit may support them:

- clinical records;
- medications;
- diagnoses or symptoms;
- reproductive/sexual-health data;
- mental-health/state-of-mind records;
- ECG, blood pressure, blood glucose, oxygen saturation, and detailed cardiac signals;
- precise route/location data;
- raw continuous streams.

An iPhone companion is the long-term permission boundary. A manual Apple Health XML export is technically available for controlled research, but broad exports should not become routine ingestion without a separate minimization review: [Apple Health export](https://support.apple.com/en-euro/guide/iphone/iph5ede58c3d/ios).

---

## 8. Collection policy

### 8.1 Allowed by default within the selected workflow

- Owner text intentionally submitted to that workflow.
- Local saving of the submitted record when the interface clearly communicates that Save/Submit creates a record.
- Minimal local operational telemetry without personal content.
- Use of already authorized, non-expired local workflow records.

### 8.2 Confirmation required

- Connecting Google Calendar and granting OAuth scope.
- Enabling calendar titles beyond busy/free windows.
- Enabling any Apple Health type.
- Promoting a derived observation into a confirmed long-term preference or procedure.
- Sending Personal data to a cloud model under a preapproved routing policy.
- Extending raw-data retention beyond its class.
- Adding photos, voice, location, email, contacts, or a new data source.
- Using a datum for a different workflow or research purpose.

### 8.3 Prohibited in M0/M1

- Credentials or passkeys in prompts, memory, source control, or ordinary logs.
- Clinical records and the initially excluded HealthKit categories in Section 7.
- Email, contacts, precise location, microphone, camera, and ambient recording.
- Data about family, guests, coworkers, or other people beyond incidental minimized calendar context.
- Training/fine-tuning datasets built from personal records.
- Sale, advertising, data brokerage, or unrelated behavioral profiling.
- Unreviewed cloud egress of Sensitive or Restricted data.
- Collection performed merely because an API makes it available.

---

## 9. Cloud and model routing

| Data/request type | Local model | Approved cloud model | Required control |
|---|---|---|---|
| Public references and synthetic test data | Allowed | Allowed | Normal source and license checks |
| Generic planning instructions with no personal details | Allowed | Allowed | No credentials or hidden context |
| Personal goals or task text | Preferred | Confirmation or explicit workflow routing policy | Minimum excerpt, provider recorded, no provider-wide assumption |
| Calendar availability without titles | Preferred | Possible after owner policy approval | Redact calendar/account identifiers and unnecessary exact details |
| Calendar titles/details | Allowed locally | Denied by default | Per-request exception only after M0 decision |
| Meal, workout, calorie, energy, sleep, or Apple Health data | Allowed locally | Denied by default | No cloud route in initial workflows |
| Restricted secrets or excluded health types | Never sent to general model | Prohibited | Dedicated protocol/vault only where applicable |

Cloud providers are interchangeable processors, not memory authorities. Provider subscription status does not grant Osun permission to send data.

---

## 10. Autonomy and approvals

### 10.1 Risk and approval levels

| Level | Meaning | Approval behavior |
|---|---|---|
| R0 | Read-only/local computation with approved data | May run inside an approved workflow; result remains inspectable |
| R1 | Suggestion, estimate, or draft | May present proactively under notification policy; no external effect |
| R2 | Reversible local state change | Clear interface intent or preview/confirmation; undo required |
| R3 | External or consequential action | Just-in-time preview and explicit approval; verify result |
| R4 | Prohibited/specialized high risk | Cannot run under current policy |

### 10.2 Action matrix

| Action | Workflow | Risk | Proposed initial rule | Verification/undo |
|---|---|---:|---|---|
| Read accepted owner goals | WF-01 | R0 | Automatic within WF-01 | Show source/version |
| Read calendar busy/free windows | WF-01/WF-02 | R0 | Automatic after source connection approval | Show freshness and source alias |
| Read calendar title | WF-01/WF-02 | R0 Sensitive | Only after Stage B owner enablement | Display title use and allow field disable |
| Generate daily plan | WF-01 | R1 | On request or approved daily trigger | Owner rates/edits plan |
| Proactively suggest a daily reset | WF-01 | R1 | At most one default prompt/day initially; owner can silence | Dismiss/snooze/disable |
| Save an explicitly submitted local plan | WF-01 | R2 | Submit/Save is sufficient confirmation | Local delete/version rollback |
| Create or modify Google Calendar event | WF-01/WF-02 | R3 | Preview and explicit approval every time initially | Read back event and offer undo |
| Generate meal/workout proposal | WF-02 | R1 | On request or approved weekly trigger | Owner edit/accept/reject |
| Save accepted meal/workout plan locally | WF-02 | R2 | Explicit accept/save | Delete/version rollback |
| Generate grocery list | WF-02 | R1 | Included in approved plan flow | Owner edit/delete |
| Purchase groceries/supplements/equipment | WF-02 | R4 | Prohibited | Not applicable |
| Diagnose, prescribe, or override health constraints | WF-02/WF-03 | R4 | Prohibited | Not applicable |
| Save owner-submitted meal entry | WF-03 | R2 | Submit is sufficient confirmation | Correct/delete |
| Calculate calorie estimate/range | WF-03 | R0/R1 | Automatic locally; uncertainty visible | Recalculate after correction |
| Confirm uncertain food match | WF-03 | R2 | Owner confirmation required | Correct/delete |
| Share or publish health/calorie data | WF-02/WF-03 | R4 | Prohibited initially | Not applicable |
| Promote inferred preference to long-term memory | All | R2 Sensitive | Owner confirmation initially | Dispute/supersede/delete |
| Change owner goal or policy | All | R4 for agent | Agent may propose only; owner edits explicitly | Version history and rollback |

### 10.3 Personality envelope

Osun may:

- express opinions, humor, warmth, curiosity, encouragement, disagreement, and a recognizable voice;
- point out inconsistency between stated dreams and current plans;
- challenge an unrealistic plan and propose a smaller action;
- celebrate progress and invite reflection;
- remember owner-confirmed communication preferences.

Osun may not:

- fabricate urgency, consequences, emotions, or social pressure;
- shame, threaten, punish, or imply moral failure;
- hide uncertainty or selectively present evidence to force agreement;
- claim relationship authority, exclusivity, consciousness, or dependence as leverage;
- make the owner complete a streak to regain features;
- use sensitive data outside its authorized purpose to increase compliance;
- override pause, quiet, correction, or deletion controls.

Personality is expressive freedom, not permission escalation.

### 10.4 Proactivity envelope

Initial defaults:

- one daily consistency prompt at an owner-selected time;
- one weekly health-planning prompt;
- no unsolicited calorie reminders until the owner opts in;
- quiet hours and global/per-workflow pause;
- every notification supports dismiss, snooze, disable, and feedback;
- repeated dismissal lowers frequency rather than increasing persuasion;
- urgent language is reserved for objectively time-bounded owner commitments, not model judgment.

### 10.5 Approval receipt

Every R3 approval records:

- actor and approving owner;
- exact action and target;
- previewed fields;
- policy/workflow/tool version;
- approval time and expiration;
- execution and verification result;
- undo/compensating action where available.

An approval for one action does not authorize future similar actions unless a later explicit standing policy says so.

---

## 11. Owner decisions required

### M0-14 data decisions

1. Approve Sensitive health, meal, calorie, workout, energy, and sleep data as local-only by default.
2. Approve calendar Stage A as busy/free, time, timezone, source alias, and freshness; calendar titles require later enablement.
3. Approve the proposed retention defaults: 30-day cache/debug, 12-month raw behavioral/health records, and long-term confirmed goals/preferences/procedures.
4. Approve the initial eligible Apple Health types: steps, workouts/duration, exercise minutes, active energy, and sleep duration; keep Section 7 exclusions prohibited.
5. Approve the allowed, confirmation-required, and prohibited collection lists in Section 8.
6. Approve cloud routing in Section 9, especially no health/calorie data and no calendar titles by default.

### M0-15 autonomy decisions

1. Approve the action matrix in Section 10.2.
2. Approve Submit/Save as sufficient confirmation for intentionally entered local plans and meals.
3. Require preview and explicit approval for every Google Calendar write initially.
4. Approve one daily consistency prompt and one weekly health-planning prompt as starting proactivity defaults.
5. Approve the personality envelope in Section 10.3.
6. Confirm WF-01 as the provisional M1 vertical-slice candidate.

The owner may approve all recommendations together or amend individual items.

---

## 12. M0-14 acceptance checklist

- [x] Every currently proposed source has purpose, sensitivity, minimum fields, retention, pause/delete/export, and egress proposal.
- [x] Raw source, derived memory, and model context are separated.
- [x] Data about other people and excluded categories are addressed.
- [x] Cloud-model policy is explicit by data type.
- [x] Apple Health and Google Calendar use least-privilege pathways.
- [ ] Owner approves prohibited, confirmation-only, retention, and cloud-egress policy.
- [ ] Residual privacy risks are accepted or the workflow is narrowed.

---

## 13. M0-15 acceptance checklist

- [x] Every selected action has a risk level and proposed approval rule.
- [x] Preview, approval, expiration, verification, and undo are defined where applicable.
- [x] Always-approve and prohibited actions are explicit.
- [x] Global pause and per-workflow disable are required.
- [x] Personality is separated from action authority.
- [ ] Owner accepts the action, personality, and proactivity boundaries.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as privacy, security, and workflow analyst
- Reviewer: Owner
- Status: Owner review
- Inputs used: Accepted owner charter, selected workflow catalog, current-system inventory, Google Calendar and Apple Health official documentation
- Assumptions: Retention periods, calendar minimization stage, Apple Health types, cloud egress, and proactivity defaults are recommendations until owner approval
- Open questions: Section 11 and non-blocking Pi power/external-access facts
- Acceptance evidence: Complete selected-source matrix, retention/classes, collection policy, cloud routing, action matrix, personality envelope, proactivity defaults, and owner decision list
- Last updated: 2026-07-26
