# Osun M0 Privacy Impact Assessment

**Task:** M0-23 - Complete the initial privacy impact assessment \
**State:** Accepted for M0-23 \
**Accountable:** Privacy analyst \
**Reviewer:** Owner \
**Scope:** Selected WF-01/WF-02/WF-03 data flows and proposed M1 WF-01 slice \
**Last updated:** 2026-07-26

---

## 1. Purpose and limitation

Osun is intended to learn from one person's life over many years. That creates privacy risks even when every device is locally owned and no attacker is present. Continuous collection can alter behavior, freeze old patterns into identity, expose other people, create pressure to comply with the system, or make deletion practically incomplete.

This assessment asks:

- Is each data flow necessary for a named owner outcome?
- Is the minimum useful field set used?
- Can the owner understand, pause, correct, export, and delete it?
- Could data or inference harm the owner or another person outside its intended purpose?
- Could Osun become psychologically intrusive or difficult to live without?
- Can implementation and tests demonstrate the promised privacy behavior?

This is a product/design privacy assessment, not legal advice or a claim of compliance with any jurisdiction. Legal review becomes necessary before commercialization, public service, multi-person use, employer-controlled processing, clinical/medical functionality, or materially different data sources.

---

## 2. Method and reference profile

The assessment uses the accepted data/autonomy policy and architecture as normative inputs. It uses the NIST Privacy Framework as a voluntary risk-management reference. NIST's current site identifies Privacy Framework 1.0 as the stable published framework and Privacy Framework 1.1 as an Initial Public Draft, so Osun records the reference version rather than claiming adoption of an unfinished standard: [NIST Privacy Framework](https://www.nist.gov/privacy-framework).

Apple documents HealthKit as a fine-grained, per-data-type authorization system. A person may limit history or deny a type, and applications may be unable to distinguish denial from absence. Osun therefore treats missing HealthKit results as unknown and requests access only at the moment a named feature needs a specific type: [Apple HealthKit privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy) and [HealthKit authorization](https://developer.apple.com/documentation/HealthKit/authorizing-access-to-health-data).

Google Calendar access is likewise scoped through explicit OAuth permissions. Osun begins with the narrowest read-only access that can supply availability and separates read permission from every later write approval: [Google Calendar OAuth scopes](https://developers.google.com/workspace/calendar/api/auth).

Assessment sequence:

```text
purpose and people
-> source and flow necessity
-> minimization and lifecycle
-> privacy harms and affected people
-> controls and rights
-> implementation requirements and tests
-> residual-risk owner decision
```

---

## 3. Privacy posture inherited from accepted decisions

1. The first system has one adult owner and one data subject by default.
2. Sensitive health, meal, calorie, workout, energy, and sleep data is local-only.
3. Google Calendar begins with Stage A busy/free availability; titles are separately enabled later.
4. Apple Health data is deferred from M1 and, later, individually authorized by type.
5. Credentials and recovery material never enter general model context, ordinary logs, or exports.
6. The owner explicitly confirms new sources, memory promotion, sensitive cloud egress, and purpose expansion.
7. Passive microphone, camera, precise location, email, contacts, ambient sensing, clinical data, and data about other people are prohibited in M0/M1.
8. Strong personality is allowed; coercion, shame, hidden scoring, fabricated urgency, and permission expansion are not.
9. Missing data means unknown, not zero, failure, or noncompliance.
10. Multi-person and household support remain prohibited until independent identity, isolation, consent, and leakage controls pass.

---

## 4. People affected

| Person/group | How they may be affected | M0/M1 treatment |
|---|---|---|
| Owner | Direct subject of goals, schedule, plans, behavior, health, meals, energy, model inferences, and actions | Full purpose, access, correction, export, pause, deletion, and approval controls |
| Calendar organizers/attendees | Names, relationships, event meaning, and timing may be embedded in calendar records | Stage A excludes names/titles/descriptions/attendees; later title access needs separate review |
| People mentioned by owner | May appear in free text, goals, preferences, or notes without their knowledge | Minimize/redact; do not create a person profile or durable memory merely from mention |
| Household members/guests | Could be observed indirectly through routines, device state, shared displays, or future sensors | Not in scope; no shared identity or blanket household access |
| Prospective employers/recruiters | Future job/email workflows could expose communications, evaluations, or inferred status | Email/job workflows are not selected and require a later PIA |
| Health professionals or contacts | Could be revealed through calendar titles or clinical/health data | Clinical data excluded; calendar titles disabled initially |
| External service personnel/processors | Providers may process submitted payloads and metadata | Only approved provider/minimum context; sensitive selected-workflow data denied by default |
| Future family members, including children | May have reduced ability to consent and heightened consequences from long-term records | Entirely deferred; separate identities, guardianship/assent analysis, private/shared spaces, and deletion rules required |

The owner cannot consent on behalf of every person incidentally represented in their data. Osun must minimize third-party fields and avoid durable person-level inference unless a later legitimate purpose and consent model exists.

---

## 5. Data-source necessity register

| Data/source | Named purpose | Necessary now? | Minimum useful representation | Privacy decision |
|---|---|---|---|---|
| Owner goals/dreams | Select meaningful WF-01 actions | Yes, manually selected | Current owner-authored statement, validity/status, provenance | Personal; local-first; owner controls promotion and cloud use |
| Calendar busy/free | Avoid plans that conflict with commitments | Useful for later WF-01 integration, not required for first manual prototype | Source alias, start/end, timezone, busy/free, freshness | Stage A only; short cache; explicit OAuth connection |
| Calendar titles/details | Add context beyond availability | No initial necessity | None initially | Disabled; separate purpose demonstration and owner enablement required |
| Calendar attendees/descriptions/location | Potential contextual enrichment | No selected-workflow necessity | None | Prohibited in initial flows |
| Daily plan and owner edits | Deliver WF-01 and measure usability | Yes | Date, selected actions/timing, version, status, source references | Local; RET-2 unless owner promotes a reusable procedure |
| Plan outcome/usefulness | Evaluate WF-01 and learn corrections | Optional but useful | Status/edit/reason category/usefulness; no unrelated narrative | Missing remains unknown; raw RET-2; confirmed preference RET-3 |
| Energy/interest self-report | Adapt wellness planning and evaluate owner outcome | Not needed for M1 plan generation | Small owner-chosen scale and time; note optional | Sensitive and local-only; never passively inferred in M1 |
| Meal/workout preferences | Produce WF-02 plans | Needed only when WF-02 begins | Explicit current constraints/preferences and validity | Sensitive, local-only by default, correctable/supersedable |
| Apple Health aggregates | Optional later WF-02 context/evaluation | Not needed for M1 | Approved type, aggregate window/value, source/freshness | Deferred; per-type consent; local-only; no raw M1 samples |
| Food text and calorie estimates | Deliver WF-03 | Needed only when WF-03 begins | Owner text, time/group, estimate/range, units, confidence, source | Sensitive, manual, local-only, RET-2 |
| Photo/audio of meals | Possible future capture convenience | No current necessity | None | Prohibited until separate necessity, bystander, retention, and model review |
| Model input/output | Produce owner response | Only minimum context for each run | Authorized fields, model/prompt versions, source/policy references | Context RET-0; debug content RET-1 only when explicitly approved |
| Memory inference | Reduce repeat work | Not automatically necessary | Structured claim, confidence, validity, source, purpose, status | Candidate first; owner confirmation for durable personal interpretation |
| Audit/telemetry | Explain effects, investigate incidents, measure reliability | Yes, content-minimized | IDs, types, versions, time, result, reason code, content references | Local; no personal content by default; purpose-specific retention |
| Credentials/tokens | Authenticate an approved integration | Only after connection approval | Secret plus minimum provider/resource/scope/expiry metadata | Restricted vault only; exact protocol endpoint use |
| Email, contacts, Apple Notes, precise location | Possible future workflows | No selected-workflow necessity | None | Not collected in M0/M1 |

No source is justified because it is available, interesting, or potentially useful someday.

---

## 6. Data-flow privacy assessment

| Flow | Purpose/necessity | Data and people | Access/minimization | Egress/retention | Owner control and residual issue |
|---|---|---|---|---|---|
| PF-01 Owner -> interface/ingress | Capture a request, correction, approval, save, pause, or delete instruction | Owner text; Personal/Sensitive depending on content | Authenticated owner session; typed purpose; discourage unrelated content | Local transport; request context RET-0 unless saved | Inspect/edit before submit; free text may still contain third-party data |
| PF-02 Memory -> WF-01 context | Select meaningful and feasible daily actions | Confirmed owner goals/preferences and recent outcomes | Workflow/purpose filter; source and validity required; no broad history dump | Local; source retention applies | Owner can inspect/correct/delete; risk of stale goal or over-personalization |
| PF-03 Google Calendar -> local cache | Obtain feasible time windows | Owner schedule plus indirect facts about others; Personal | Stage A busy/free/time/timezone/source/freshness only | Provider -> local; RET-1 cache | Connect/disconnect/delete cache; timing patterns remain revealing |
| PF-04 Calendar titles/details -> context | Optional later context when Stage A proves insufficient | Sensitive context; organizers/attendees may be implicated | Disabled initially; per-calendar/field enablement; exclude attendee/description/location | Local by default; RET-1 if later enabled | Separate decision required; injection and third-party leakage remain |
| PF-05 Orchestrator -> local model | Generate plan/estimate from authorized context | Owner Personal/Sensitive fields | Router builds field allowlist; model receives no arbitrary memory/secrets | Local request RET-0; output RET-1 unless saved | Show relevant sources; local model process can still expose data if host compromised |
| PF-06 Router -> cloud model | Obtain non-sensitive reasoning when approved | Selected Personal text only; no health/calorie/calendar titles | Per-request minimum-context and provider allowlist; redact identifiers where useful | External processing; RET-0 locally; provider handling evaluated later | Confirmation required; provider metadata/retention cannot be fully controlled by Osun |
| PF-07 Interface -> plan/local save | Preserve exact owner-reviewed plan | Owner plan and edits; Personal/Sensitive by workflow | Submit/Save binds exact artifact; no hidden memory promotion | Local RET-2; reusable confirmed procedure RET-3 | Edit/delete/export/pause; deleted plan may have content-free audit tombstone |
| PF-08 Executor -> Google Calendar write | Create an owner-approved plan event | Event time/title plus possible inferred goal; owner and potential viewers | Exact R3 preview/approval every time; only approved calendar/fields | External provider retention plus local audit | Undo/delete through provider; provider copies/history may not be fully erasable by local deletion |
| PF-09 WF-02 local context | Produce meal/workout proposal | Sensitive preferences, constraints, energy, schedule | Retrieve current explicitly provided fields only | Local-only; RET-2/3 by record type | Field-level correction/pause; risk of intimate inference from combinations |
| PF-10 iPhone HealthKit -> local summary | Optional later wellness context/evaluation | Sensitive owner health/fitness data | Per-type, just-in-time authorization; approved aggregates/time window only | Local-only RET-2; no M1 raw samples | Revoke in iPhone, delete/export local copy; denied/absent indistinguishable and must remain unknown |
| PF-11 WF-03 capture/estimate/save | Reduce calorie-tracking effort | Sensitive meal text, amount, estimate, correction | Manual initial input; local reference/model; no photo/audio | Local-only RET-2 | Correct/delete/export/pause; risk of self-surveillance and restrictive interpretation |
| PF-12 Workflow/model output -> interface | Present suggestion, uncertainty, sources, and possible action | Same classification as included context plus new inference | Display minimum necessary; avoid lock-screen sensitive detail | No new egress; RET-1 unless intentionally saved | Dismiss/snooze/edit; persuasive output may affect behavior despite no stored data |
| PF-13 Outcome -> candidate/confirmed memory | Learn recurring preference or procedure | Owner behavior/correction and derived inference | Candidate status, confidence, validity, provenance, allowed purpose; confirmation before durable interpretation | Local; candidate expiry; confirmed RET-3 | Inspect/confirm/dispute/supersede/delete; risk of fossilizing a transient pattern |
| PF-14 Services -> audit/telemetry | Verify effects, investigate incidents, monitor reliability | Metadata and content references; may reveal behavior timing | Per-service write only; redaction; no payload/content by default | Local RET-1/2/3 by purpose | Export and inspect; security audit may retain content-free evidence after content deletion |
| PF-15 Vault -> exact adapter/provider | Authenticate approved integration | Restricted token/credential and minimum metadata | Adapter cannot export/read secret value beyond protocol use where technology permits | Only exact provider endpoint; credential lifetime | Revoke/rotate/disconnect; provider may retain authorization history |
| PF-16 Data -> encrypted backup | Recover approved data after failure | Copy of all included classifications | Dataset allowlist, encryption before transfer, separate keys, no ordinary model access | Z8 only; retention aligned to source/policy | Restore test and deletion policy required; backup can extend effective retention |
| PF-17 Data -> owner export | Exercise portability/inspection rights | Owner-selected records; may include third-party facts | Strong reauthentication, preview categories/time range, exclude secrets | Owner-chosen destination; Osun control ends after export | Warn about destination; export manifest/checksum; deletion of export is owner-managed |
| PF-18 Owner delete -> all stores | Remove source and governed derivations | Selected source, subject, purpose, or time range | Authorized deletion plan enumerates copies/indexes/derivations | Primary/index/cache purge; backup treatment declared | Verification report; tombstone cannot preserve deleted content |
| PF-19 Osun -> Home Assistant | Future device request | Owner/home routine plus device state and possible bystander effects | Not in M1; later entity/service allowlist and household consent | Local peer; HA retains authoritative state/history | Independent HA UI/pause; privacy impact requires separate update |

Every selected flow is represented in the architecture and this assessment. Deferred flows are included to preserve prohibitions and prevent accidental implementation by omission.

---

## 7. Access and purpose matrix

| Actor/component | May access | Must not access |
|---|---|---|
| Owner | All owner-authorized records, source use, audit explanation, policies, exports, deletion state | Other people's future private spaces without their authorization |
| Owner interface | Exact fields needed to display/capture the active task | Vault secrets, arbitrary database tables, unrelated workflow context |
| Ingress/orchestrator | Normalized request and purpose-authorized workflow state | Raw provider credentials or unrestricted all-memory query |
| Identity/policy service | Identity, scope, sensitivity, purpose, risk, approval, and reason metadata | Meal/health narrative unless essential to a typed policy attribute |
| Model router | Minimum allowed context and provider policy | Unfiltered memory, secrets, prohibited categories |
| Local model | One request envelope | Direct memory, vault, network, tools, or durable write access |
| Cloud model | Explicitly approved minimal Personal/Public context | Health, calorie, energy, sleep, calendar titles, secrets, or other-person data by default |
| Execution adapter | Exact normalized action plus indirect credential capability | Conversation history, broad memory, unrelated provider resources |
| Memory service | Governed source/derived records needed to enforce lifecycle | External network or ability to decide its own purposes |
| Operations service | Content-minimized health/security/audit metadata | Routine prompt, meal, health, goal, or calendar content |
| Backup service | Approved encrypted dataset and manifest | Plaintext secret/data browsing or live workflow execution |

Access is granted by purpose, field, time, and workflow—not merely by role name.

---

## 8. Privacy risk scoring

The likelihood/impact scale and Low/Moderate/High/Critical bands are inherited from the threat model. Privacy impact includes loss of agency, embarrassment, discrimination, relationship harm, chilling effects, manipulation, inaccurate representation, and inability to escape past data.

| ID | Privacy risk/harm | Inherent | Treatment | Target residual | Verification target |
|---|---|---:|---|---:|---|
| PR-01 | Longitudinal aggregation becomes a detailed surveillance record beyond any single workflow's need | 5×5=25 Critical | Purpose-scoped stores/APIs, field minimization, retention classes, access review, no collect-because-available | 2×5=10 High | PRI-01/02; PT-01/02/11/25 |
| PR-02 | Health, meal, calorie, energy, or sleep data is disclosed or repurposed | 4×5=20 Critical | Local-only, per-type consent, no M1 HealthKit/raw health, encryption/backup gate, no cloud fallback | 2×5=10 High | PRI-03; PT-03/05/21 |
| PR-03 | Busy/free timing or calendar titles reveal medical, relationship, religious, employment, or routine facts | 4×4=16 Critical | Stage A only, short cache, source alias, field toggles, no attendees/descriptions/locations | 2×4=8 Moderate | PRI-04; PT-07/14/27 |
| PR-04 | Data about organizers, contacts, household members, or people mentioned by owner is profiled without consent | 3×5=15 High | Exclude third-party fields, redact mentions, no person profile/promotion, multi-person prohibition | 1×5=5 Moderate | PRI-05; PT-08/23 |
| PR-05 | Permission/source creep expands collection after a feature proves useful | 4×4=16 Critical | Source/field/purpose confirmation, no transitive authorization, periodic grant review, deny new source by default | 2×4=8 Moderate | PRI-06; PT-01/24/25 |
| PR-06 | Cloud provider processing, metadata, retention, or secondary use exceeds owner expectation | 3×5=15 High | Provider allowlist/review, per-request minimum context/confirmation, sensitive classes blocked, route audit | 2×4=8 Moderate | PRI-07; PT-05/06/22/28 |
| PR-07 | Wrong, stale, or transient inference becomes a durable identity and shapes later opportunities | 4×4=16 Critical | Candidate-first memory, validity time, provenance, confirmation, conflict display, correction/supersession/expiry | 2×4=8 Moderate | PRI-08; PT-09/10/26/27 |
| PR-08 | Missing or revoked data is interpreted as zero, failure, or noncompliance | 4×4=16 Critical | Unknown state is explicit in contracts/UI/evaluation; no punitive streaks; HealthKit denial-aware behavior | 1×4=4 Low | PRI-09; PT-04/26 |
| PR-09 | Delete appears successful but content persists in cache, index, derivation, model debug, or restore | 4×5=20 Critical | Deletion plan/manifest, derived-link graph, purge/rebuild, restore-time suppression/key retirement, verification report | 2×5=10 High | PRI-10; PT-12/16/17/18/30 |
| PR-10 | Backup/export creates uncontrolled duplicate copies and extends retention | 3×5=15 High | Encrypted allowlisted backup, source-aligned retention, destination warning, export manifest, no secrets | 2×4=8 Moderate | PRI-11; PT-15/17/21 |
| PR-11 | Shared display, notification, screenshot, or diagnostic log reveals sensitive context | 3×4=12 High | Generic notifications, authenticated reveal, no content logs, redaction, debug opt-in/expiry | 2×3=6 Moderate | PRI-12; PT-19/20 |
| PR-12 | Proactive personality causes chilling, shame, dependence, or perceived inability to opt out | 4×4=16 Critical | Non-coercion envelope, quiet hours, low prompt budget, dismissal lowers frequency, pause/disable, human-factors tests | 2×4=8 Moderate | PRI-13; PT-13/29/31 |
| PR-13 | Data collected for planning is reused for health, employment, persuasion, or model training | 4×5=20 Critical | Purpose binding, cross-purpose confirmation, training prohibited, field-level access, audit/review | 1×5=5 Moderate | PRI-14; PT-11/24/25/32 |
| PR-14 | Future household/family use leaks one person's data or lets another person act as them | 3×5=15 High | Multi-person prohibition until separate identity/private/shared-space/consent design and tests | 1×5=5 Moderate | PRI-15; PT-23 |
| PR-15 | Endpoint/provider compromise becomes a privacy breach across aggregated longitudinal data | 3×5=15 High | Threat-model gates, least privilege, encryption, segmented services, no sensitive data before restore/hardening | 2×5=10 High | PRI-16; security scenarios GS-SEC-09/15/16/44 |
| PR-16 | Long retention increases exposure and makes old behavior appear current | 4×4=16 Critical | RET-1/2 rolling deletion, validity/expiry, summary promotion only after confirmation, periodic review | 2×4=8 Moderate | PRI-17; PT-12/27 |
| PR-17 | Osun infers mental state, diagnosis, relationship status, or motivation from behavior without consent/evidence | 4×5=20 Critical | Prohibit diagnosis/state-of-mind collection, no hidden psychographic score, narrow explicit self-report only, no promotion | 1×5=5 Moderate | PRI-18; PT-24/26/33 |
| PR-18 | Owner interactions are silently used to train models or become difficult-to-remove training data | 3×5=15 High | No training in M0/M1; future versioned opt-in dataset, deletion lineage, offline evaluation and separate gate | 1×5=5 Moderate | PRI-19; PT-32 |
| PR-19 | Sensitive observations enter Git/OneDrive through baseline logs, fixtures, screenshots, or debugging | 4×5=20 Critical | Specs/synthetic data only in repo; private paper baseline; secret/privacy scan; safe fixture rules | 1×5=5 Moderate | PRI-20; PT-20/34 |
| PR-20 | Privacy controls create cognitive overload or dark patterns that make broad consent easier than selective consent | 3×4=12 High | Just-in-time plain-language controls, safe default first, separate scopes, no bundled consent, reversible settings | 2×3=6 Moderate | PRI-21; PT-01/03/29/35 |

High target residuals PR-01, PR-02, PR-09, PR-15 reflect the irreversible potential of longitudinal aggregation, intimate data, imperfect deletion, and endpoint compromise. Osun manages them through narrow scope and evidence gates rather than claiming elimination.

---

## 9. Workflow-specific privacy findings

### 9.1 WF-01 Daily Consistency Plan

Primary benefit comes from owner goals, manual plan input, and a small amount of schedule availability. It does not initially require calendar titles, emails, notes, passive behavior, health data, or other-person profiles.

Key privacy risks:

- the system gradually treats productivity history as identity or worth;
- calendar timing reveals sensitive routine even without titles;
- a daily prompt feels like surveillance or pressure;
- owner edits become hidden preference inference;
- cloud planning receives more context than the request needs.

Required treatment:

- Stage A availability only;
- owner-editable plan with no hidden score or punitive streak;
- one daily prompt maximum, quiet hours, dismissal adaptation, and global pause;
- candidate-first memory and visible source influence;
- local model preferred; minimum Personal cloud context only with confirmation.

### 9.2 WF-02 Weekly Health Plan

Health benefit does not justify diagnosis, broad health ingestion, raw streams, detailed clinical/reproductive/cardiac data, or cloud processing. Initial value should be proven with explicit preferences and schedule constraints before Apple Health is connected.

Key privacy risks:

- intimate inference from combining sleep, energy, schedule, meals, and workouts;
- plan rigidity or persuasive advice changes behavior;
- absence of HealthKit data is misread;
- health context leaks through model fallback, logs, or calendar titles;
- plan history becomes a body/health compliance record.

Required treatment:

- defer from M1 and request each HealthKit type just in time;
- approved aggregate types only and local-only processing;
- wellness/non-medical scope and no restrictive automatic targets;
- unknown state for denied/missing data;
- local blank-planner fallback when inference is unavailable.

### 9.3 WF-03 Low-Friction Calorie Capture

Calorie capture can save time while also increasing self-monitoring pressure. Speed must not become a reason to collect photos, audio, location, restaurant history, or body/clinical data.

Key privacy risks:

- meal history reveals health, religion, finances, routine, and location indirectly;
- wrong estimates shape behavior despite uncertainty;
- missed entries become a hidden compliance signal;
- photo capture includes bystanders or environmental details;
- food mappings become persistent without confirmation.

Required treatment:

- manual local text first; photo/audio deferred;
- ranges, confidence, source, and correction;
- missed entries remain missing and are not moralized;
- local-only records and summaries;
- candidate food mappings until owner confirmation.

---

## 10. Owner privacy controls and expected behavior

| Control | Required owner-visible behavior |
|---|---|
| Source connection | Show source, fields, purpose, read/write scope, retention, egress, and how to disconnect before authorization |
| Collection dashboard | Show active workflows, sources, last collection, field categories, freshness, and pause state |
| Data-use explanation | For an output, show which source categories and model route influenced it without exposing unnecessary content |
| Correction/dispute | Preserve source evidence, mark prior claim disputed/superseded, and prevent retrieval as current fact |
| Memory promotion | Show candidate claim, source, confidence/uncertainty, purpose, retention, and accept/edit/reject controls |
| Pause | Global and per-workflow/source pause works without model inference and blocks new collection/action |
| Delete | Preview scope and consequences, enumerate affected copies/derivations, execute, then provide verification status |
| Export | Select source/type/time/purpose, preview sensitive categories, exclude secrets, produce manifest and documented format |
| Cloud routing | Identify provider and categories before first/changed sensitive route; health/calorie data has no initial route |
| Notification | Generic lock-screen content by default; sensitive detail only after authenticated reveal |
| Retention | Display default and current expiry; allow shorter owner choice; no silent extension during feature updates |
| Disable personality/proactivity | Separate tone from action authority; allow prompts/personality to be reduced without losing access to data or core functions |

Privacy settings must not require the owner to trade away functionality that can reasonably work with less data.

---

## 11. Deletion and export verification

### 11.1 Deletion procedure

1. Authenticate the owner and capture exact deletion scope: source, record type, purpose, workflow, time range, or all subject data.
2. Produce a deletion plan listing primary records, artifacts, derived memories, semantic/vector indexes, caches, model-debug records, telemetry content references, exports still controlled by Osun, and backup treatment.
3. Pause new ingestion for the affected source/scope while deletion runs.
4. Delete primary content and sever derivation links; retain only a content-free tombstone when necessary for audit or duplicate prevention.
5. Delete or rebuild indexes and summaries so deleted content cannot be retrieved indirectly.
6. Mark backup copies for expiry, cryptographic erasure, or restore-time suppression according to the approved backup design. Do not promise immediate physical erasure from an immutable backup if the implementation cannot prove it.
7. Query every live store and index for the deleted record IDs, content hashes, and derivation references.
8. Run a controlled restore test and confirm the deletion manifest prevents resurrection.
9. Provide a report distinguishing verified deletion, scheduled backup expiry, owner-controlled exports, provider-controlled copies, and unresolved failures.
10. Retry bounded failures, alert the owner, and keep the affected workflow/source paused if privacy would otherwise be misrepresented.

### 11.2 Export procedure

1. Authenticate/reauthenticate the owner.
2. Show included sources, people, classifications, retention, and estimated size.
3. Exclude secrets and minimize third-party fields.
4. Export documented machine-readable records plus provenance, schemas, policy references, and a manifest/checksum.
5. Encrypt sensitive exports or require an owner-approved protected destination.
6. Record only content-minimized export evidence.
7. State clearly that Osun cannot control copies after the owner moves them elsewhere.

---

## 12. Privacy requirements and tests

These identifiers feed M0-24 contracts, M0-30 scenarios, M0-31 evaluation, M0-34 traceability, and the M1 backlog.

| Requirement | Normative statement | Verification tests |
|---|---|---|
| PRI-01 | Every collection and access has an owner-visible purpose, workflow, source, and field set | PT-01, PT-11, PT-25 |
| PRI-02 | Longitudinal aggregation is accessible only through purpose-filtered APIs and retention policy | PT-02, PT-11, PT-12 |
| PRI-03 | Health/meal/calorie/energy/sleep/workout data is local-only and individually authorized where applicable | PT-03, PT-05, PT-21 |
| PRI-04 | Initial calendar collection is Stage A only and excludes title, attendee, description, location, attachment, and conference fields | PT-07 |
| PRI-05 | Data about other people is minimized and cannot silently become a durable person profile | PT-08, PT-23 |
| PRI-06 | A source, field, workflow, or purpose expansion requires separate confirmation | PT-01, PT-24, PT-25 |
| PRI-07 | Cloud routing is provider-allowlisted, minimum-context, category-audited, and confirmation-gated | PT-05, PT-06, PT-22, PT-28 |
| PRI-08 | Derived memories preserve provenance, confidence, validity, purpose, and candidate/confirmed state | PT-09, PT-10, PT-27 |
| PRI-09 | Missing, denied, stale, or revoked data remains unknown and cannot become a negative behavior signal | PT-04, PT-26, PT-27 |
| PRI-10 | Deletion covers primary, derived, index, cache, debug, and restore paths and reports unresolved copies honestly | PT-12, PT-16, PT-17, PT-18, PT-30 |
| PRI-11 | Backup/export does not expose plaintext sensitive data, secrets, or undocumented third-party fields | PT-15, PT-17, PT-21 |
| PRI-12 | Notifications, displays, telemetry, fixtures, and diagnostics hide sensitive content by default | PT-19, PT-20, PT-34 |
| PRI-13 | Proactivity/personality is optional, bounded, non-coercive, and independently pausable | PT-13, PT-29, PT-31 |
| PRI-14 | Cross-purpose use and training are denied until a separate owner decision and dataset lineage exist | PT-24, PT-25, PT-32 |
| PRI-15 | Multi-person collection/access is denied until a separate privacy/identity/consent design passes | PT-23 |
| PRI-16 | Sensitive live data is prohibited until endpoint hardening and encrypted restore evidence exist | PT-17, PT-20 plus GS-SEC-15/16 |
| PRI-17 | Retention expiry is automated, visible, testable, and cannot silently extend | PT-12, PT-27 |
| PRI-18 | Osun does not infer diagnosis, mental state, motivation, or moral worth from behavior/missing data | PT-26, PT-33 |
| PRI-19 | Personal interactions are not training data in M0/M1 | PT-32 |
| PRI-20 | Git/OneDrive contains specifications, code, and synthetic fixtures only—not secrets or sensitive observations | PT-20, PT-34 |
| PRI-21 | Consent choices are granular, just in time, reversible, and free from bundled/dark-pattern presentation | PT-01, PT-03, PT-29, PT-35 |

### 12.1 Test definitions

| Test | Expected evidence |
|---|---|
| PT-01 Granular authorization | Owner can enable one source/field/purpose without enabling another; denied option remains functional where feasible |
| PT-02 Minimum-field capture | Store/API inspection proves only declared fields exist for each source |
| PT-03 HealthKit per-type consent | Each eligible type is requested separately at feature use; no all-health default |
| PT-04 HealthKit/missing ambiguity | Denied, absent, revoked, and empty states all produce unknown—not zero/failure |
| PT-05 Sensitive cloud denial | Router rejects every health/calorie/energy/sleep/calendar-title route to cloud, including fallback |
| PT-06 Minimum cloud payload | Audit and fixture compare requested purpose with exact transmitted categories/fields |
| PT-07 Calendar Stage A | Contract/adapter tests prove excluded Calendar fields never enter cache/context/logs |
| PT-08 Third-party minimization | Names/attendees/mentions are absent, redacted, or purpose-blocked; no person memory is created |
| PT-09 Candidate memory | Inference cannot be retrieved as confirmed fact before owner confirmation |
| PT-10 Correction/supersession | Corrected fact becomes current; prior version stays attributable but is not used as current |
| PT-11 Purpose isolation | WF-01 identity cannot access WF-02/WF-03 data without a separately authorized purpose |
| PT-12 Retention expiry | Synthetic records disappear from primary/index/cache at policy expiry with verification evidence |
| PT-13 Pause | Global and per-source/workflow pause blocks new collection/action without a model |
| PT-14 Source disconnect | Token revokes, refresh stops, cache deletion option works, and UI shows disconnected state |
| PT-15 Export completeness/safety | Manifest matches selected records/provenance; secrets and unauthorized third-party fields are absent |
| PT-16 Delete propagation | Primary, derived, index, cache, debug, and controlled export locations are checked |
| PT-17 Backup deletion/restore | Restored environment does not resurrect deletion-manifest content and reports delayed expiry honestly |
| PT-18 Tombstone minimization | Tombstone proves deletion/deduplication without original content or reconstructable sensitive detail |
| PT-19 Notification privacy | Locked/shared display reveals no sensitive goal, calendar, meal, health, or action content |
| PT-20 Repository/log scan | Git history, fixtures, logs, traces, and crash artifacts contain no secret/sensitive test observations |
| PT-21 Secret isolation | Credentials never enter model context/export/log/memory and are used only by exact adapter endpoint |
| PT-22 Provider allowlist | Unapproved provider/model route is denied and cannot silently substitute on failure |
| PT-23 Multi-person denial | Another identity/subject cannot be created or queried through initial workflow paths |
| PT-24 Prohibited-source/use denial | Email, notes, contacts, location, ambient sensors, clinical data, cross-purpose use, and photos are blocked |
| PT-25 Function-creep change | Version update requesting new field/purpose pauses and requires explicit owner decision |
| PT-26 Non-inference from absence | Missed plans/meals/data never generate failure, diagnosis, motivation, or compliance claims |
| PT-27 Validity/freshness | Expired/stale preference or source is not presented as current without a warning/confirmation |
| PT-28 Use/egress transparency | Owner can see which source categories, model/provider, and purpose influenced a result |
| PT-29 Consent revocation | Revocation stops future use promptly and preserves access to unrelated local functionality |
| PT-30 Deletion-proof integrity | Deletion report is tamper-evident and cannot claim success when a controlled copy remains unresolved |
| PT-31 Non-coercion/personality | Adversarial prompts fail to produce shame, threat, fabricated urgency, or relationship authority |
| PT-32 Training prohibition | No M0/M1 code/config/path can add owner records to a training dataset |
| PT-33 Sensitive-inference prohibition | Behavior cannot create mental-state, diagnosis, moral-worth, or hidden psychographic records |
| PT-34 Safe fixtures | Tests use synthetic/non-identifying data and reject accidental personal fixture commits |
| PT-35 Consent usability | Owner understands scope/consequence, can select narrowly, and can reverse without deceptive friction |

---

## 13. Residual privacy risks and owner decision

The proposed decision is to accept the following M0 treatment plan—not to accept unrestricted future collection:

1. **Longitudinal aggregation:** Osun may build memory only through purpose-scoped records, candidate-first inference, retention, and owner correction/deletion; no universal all-data model context.
2. **M1 data limit:** M1 begins with synthetic and minimal manually submitted WF-01 Personal data. Sensitive durable data waits for encrypted local storage, endpoint hardening, backup, and restore evidence.
3. **Calendar limit:** Stage A busy/free availability is the only initially eligible calendar context. Titles/details and every write require later separate enablement/approval.
4. **Health/calorie limit:** WF-02/WF-03 sensitive data remains local-only and deferred from the M1 vertical slice; future HealthKit access is per-type and just in time.
5. **Cloud limit:** Only minimum Personal/Public context may use an approved cloud model after confirmation; health/calorie/calendar-title/secrets/other-person data has no default route.
6. **Passive/third-party limit:** No email, contacts, notes, location, microphone, camera, ambient monitoring, clinical data, or person profiles in M0/M1.
7. **Memory/inference limit:** Inferences are attributable candidates, not facts; no mental-state, diagnosis, motivation, compliance, or moral-worth inference from behavior or missing data.
8. **Human-factors limit:** Personality and proactivity remain separately pausable, non-coercive, and subject to notification/attention budgets and testing.
9. **Deletion honesty:** Osun may not claim deletion is complete until primary, derived, index, cache, debug, and restore paths are verified; remaining provider/export/backup copies are disclosed.
10. **Household limit:** No multi-person/family support until a separate privacy assessment, identities, private/shared-space rules, consent/assent model, and leakage tests are approved.

Residual High risks PR-01, PR-02, PR-09, and PR-15 require continuing gates and review. This decision cannot be used to justify broader future data or autonomy.

**Owner decision:** All ten M0-23 privacy dispositions accepted as written on 2026-07-26.

---

## 14. M0-23 acceptance checklist

- [x] Purpose and necessity are stated for every proposed source and selected data flow.
- [x] Minimization, sensitivity, retention, access, egress, correction, deletion, export, and pause are checked.
- [x] Owner, non-users, service providers, and future household members are considered.
- [x] Inference, aggregation, function creep, chilling, dependency, and household leakage risks are analyzed.
- [x] All selected data flows appear in both architecture and this assessment.
- [x] Privacy requirements and 35 verification tests are defined.
- [x] Deletion and export verification behavior is explicit.
- [x] Owner accepts or amends the residual privacy treatment plan in Section 13.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as privacy analyst
- Reviewer: Owner; independent M0-46 review later
- Status: Owner accepted; M0-23 complete
- Inputs used: Accepted charter, workflow catalog, data/autonomy boundaries, baseline method, system inventory, accepted architecture/flows, accepted threat model, NIST Privacy Framework, Apple HealthKit privacy/authorization guidance, Google Calendar OAuth scope guidance
- Assumptions: M1 remains WF-01-first; no public access or multi-person use; HealthKit and WF-02/WF-03 are deferred from M1; privacy promises require implementation evidence
- Open questions: Concrete storage/backup/provider choices after M0-24/M0-40; independent challenge in M0-46
- Acceptance evidence: Complete necessity and flow registers, affected-person analysis, twenty scored privacy risks, workflow findings, privacy controls, deletion/export procedure, 21 requirements, 35 tests, and ten owner dispositions
- Last updated: 2026-07-26
