# Osun Workflow Catalog

**Tasks:** M0-12 candidate catalog and scoring; M0-13 owner selection; M0-25 narratives \
**State:** M0-12, M0-13, and M0-25 owner accepted \
**Workflow analyst:** Primary AI coordinator \
**Last updated:** 2026-07-26

---

## 1. Selection context

The owner wants visible improvement in everyday life and does not prefer a workflow merely because it comes first. The accepted outcome order is:

1. Health and wellbeing.
2. Learning and growth.
3. Creativity and recreation.
4. Self-knowledge.
5. Responsibilities and life administration.

The six-month transformation is greater consistency, more usable energy, more engagement with intended weekly activities, and less burden from calorie tracking, workout planning, meal planning, job applications, and email.

The catalog deliberately includes more candidates than can be selected. Scores support—not replace—owner judgment.

---

## 2. Scoring method

Each dimension is scored from 1 to 5. Higher is better.

| Code | Dimension | A score of 5 means |
|---|---|---|
| V | Owner value | Directly supports a high-priority outcome or major stated friction |
| F | Frequency | Useful on most days or whenever a frequent event occurs |
| M | Measurability | Outcome and failure can be observed with little ambiguity |
| P | Privacy ease | Requires little sensitive data or is easily minimized/localized |
| R | Reversibility | Suggestions/actions are easy to reject, correct, or undo |
| A | Architectural learning | Exercises contracts/capabilities useful across future Osun workflows |
| I | Implementation feasibility | A useful first version is realistic at 10 owner hours/week |
| O | Operational ease | Low recurring maintenance, integration churn, and support burden |

The unweighted total is out of 40. Owner value already reflects the accepted outcome order. Exact time savings remain unknown until M0-16 establishes a baseline.

---

## 3. Candidate workflows

### WF-01 - Daily Consistency Plan

- **Trigger:** Owner starts the day or requests a reset.
- **Outcome:** Convert dreams, current goals, calendar constraints, energy, and unfinished commitments into a small realistic plan.
- **Inputs:** Owner goals, primary Google Calendar, prior plan outcomes, optional energy/interest check-in.
- **Output/action:** Three to five owner-chosen actions with timing, minimum viable versions, and optional reminders.
- **Initial autonomy:** R1 suggestions; any calendar/reminder write is R2 after preview.
- **Worst plausible failure:** Overloading the day, creating guilt, or optimizing completion instead of a meaningful life.
- **Offline requirement:** Core planning and review should work locally; calendar freshness may degrade offline.
- **Learning signal:** Accepted/edited actions, completion, deferral reason, energy, and owner-rated usefulness.

### WF-02 - Weekly Health Plan

- **Trigger:** Weekly planning session or material schedule change.
- **Outcome:** Reduce meal and workout planning burden while supporting energy and consistency.
- **Inputs:** Owner-defined nutrition preferences, meals, schedule, grocery constraints, workout goals, equipment, and recovery constraints.
- **Output/action:** Proposed meal outline, grocery list, and workout schedule for owner approval.
- **Initial autonomy:** R1 only; no medical advice and no automatic purchases.
- **Worst plausible failure:** Unsuitable nutrition/training suggestions, unrealistic workload, or health planning becoming rigid.
- **Offline requirement:** Saved preferences and plan generation should work locally; nutrition/reference lookup may be optional external context.
- **Learning signal:** Plan edits, meals/workouts completed, substitutions, perceived energy, and planning time saved.

### WF-03 - Low-Friction Calorie Capture and Nutrition Review

- **Trigger:** Owner records a meal or requests a daily nutrition review.
- **Outcome:** Reduce calorie-tracking time while keeping estimates transparent and correctable.
- **Inputs:** Owner-entered meal text initially; optional photos or nutrition sources only after later approval.
- **Output/action:** Estimated food record, confidence/range, daily summary, and correction interface.
- **Initial autonomy:** R0 calculation and R1 suggestions; owner confirms uncertain food matches.
- **Worst plausible failure:** Incorrect estimates, false precision, shame, or unhealthy fixation on the metric.
- **Offline requirement:** Capture must work locally and queue optional lookups.
- **Learning signal:** Owner corrections, recurring foods, portion adjustments, capture time, and whether tracking remains useful.

### WF-04 - Workout Execution Companion

- **Trigger:** Scheduled workout or owner request.
- **Outcome:** Turn an accepted workout plan into a manageable session and record what actually happened.
- **Inputs:** Approved plan, equipment, time available, recent owner-reported completion and constraints.
- **Output/action:** Session checklist, substitutions, rest/timing prompts, and completion record.
- **Initial autonomy:** R1; owner decides exercises and intensity. No diagnosis or injury treatment.
- **Worst plausible failure:** Unsafe progression, ignoring pain/fatigue, or turning missed sessions into pressure.
- **Offline requirement:** Current plan and completion capture should work locally.
- **Learning signal:** Completion, substitutions, duration, perceived exertion/energy, and owner edits.

### WF-05 - Job Application Pipeline

- **Trigger:** Owner finds a job, starts an application, or requests pipeline review.
- **Outcome:** Reduce repeated application work and make next actions visible.
- **Inputs:** Job posting, owner-approved resume/profile, application stage, deadlines, and notes.
- **Output/action:** Fit summary, checklist, tailored draft material, status, and follow-up reminder proposal.
- **Initial autonomy:** R1 preparation; every submission/message is R3 and always requires approval.
- **Worst plausible failure:** Incorrect claims, missed deadlines, poor-fit prioritization, or accidental external submission.
- **Offline requirement:** Tracking and drafts should work locally; job discovery/submission requires internet.
- **Learning signal:** Applications advanced, draft edits, response outcomes, effort per application, and owner fit rating.

### WF-06 - Gmail Action Digest

- **Trigger:** Scheduled digest or owner request.
- **Outcome:** Reduce inbox-checking time by separating actionable, informational, and low-value messages.
- **Inputs:** Minimum necessary Gmail message metadata/content under a future approved policy.
- **Output/action:** Grounded digest, action list, and optional response drafts with source links.
- **Initial autonomy:** R0 read/summarize and R1 draft; sending/deleting/archiving requires later policy and approval.
- **Worst plausible failure:** Missing an important message, leaking sensitive content, or prompt injection from email influencing tools.
- **Offline requirement:** Previously synchronized digest remains available; current inbox processing requires internet.
- **Learning signal:** Corrections, opened items, action completion, false-important/false-unimportant classifications, and time saved.

### WF-07 - Universal Capture

- **Trigger:** Owner records a thought, intention, idea, commitment, or observation.
- **Outcome:** Provide one low-friction place to capture without requiring a preexisting task app.
- **Inputs:** Owner text first; voice/photo deferred.
- **Output/action:** Local inbox item with proposed type, project, time, sensitivity, and next action.
- **Initial autonomy:** R1 classification and R2 reversible local save after owner intent is clear.
- **Worst plausible failure:** Lost capture, incorrect categorization, duplicate reminders, or sensitive material assigned the wrong policy.
- **Offline requirement:** Full core capture must work locally.
- **Learning signal:** Classification corrections, later use, completion, deletion, and preferred capture patterns.

### WF-08 - Weekly Self-Knowledge Review

- **Trigger:** Weekly review.
- **Outcome:** Help the owner understand consistency, energy, engagement, obstacles, and progress without treating behavior as destiny.
- **Inputs:** Owner-approved plans, outcomes, brief check-ins, and corrections.
- **Output/action:** Evidence-linked reflection, patterns as hypotheses, wins, obstacles, and questions for the next week.
- **Initial autonomy:** R1 only.
- **Worst plausible failure:** False narrative, judgment, overgeneralization, or confusing correlation with causation.
- **Offline requirement:** Should work locally over owner-approved records.
- **Learning signal:** Owner confirmations/disputes, usefulness rating, and which reflections lead to desired adjustments.

### WF-09 - Learning Session Planner

- **Trigger:** Weekly plan or available learning window.
- **Outcome:** Maintain consistent progress on owner-selected skills and subjects.
- **Inputs:** Learning goals, current resources, previous session, available time, and interest/energy.
- **Output/action:** Small session objective, materials, recall prompt, and progress note.
- **Initial autonomy:** R1 only.
- **Worst plausible failure:** Overplanning, selecting shallow activity, or replacing curiosity with obligation.
- **Offline requirement:** Current plan and notes should work locally; external resources are optional.
- **Learning signal:** Session completion, recall, resource usefulness, time, and owner interest.

### WF-10 - Creative Momentum

- **Trigger:** Planned creative window, idea capture, or owner request.
- **Outcome:** Reduce setup friction and help the owner begin meaningful creative activity.
- **Inputs:** Creative projects, captured ideas, available time, current state, and interest.
- **Output/action:** A small starting action, relevant context/materials, and optional session plan.
- **Initial autonomy:** R1 only.
- **Worst plausible failure:** Turning recreation into obligation or favoring measurable output over enjoyment.
- **Offline requirement:** Core project context should work locally.
- **Learning signal:** Sessions started, owner enjoyment, continuation, discarded suggestions, and setup time.

### WF-11 - Energy and Interest Check-in

- **Trigger:** One or two owner-chosen moments each day or an explicit check-in.
- **Outcome:** Create a low-burden signal for plan adaptation and six-month outcome evaluation.
- **Inputs:** Owner self-report using a very small scale plus optional note.
- **Output/action:** Local observation and optional suggestion to reduce, continue, or change the current plan.
- **Initial autonomy:** R0 record and R1 suggestion.
- **Worst plausible failure:** Notification fatigue, overinterpreting a subjective score, or pressuring the owner to report.
- **Offline requirement:** Fully local.
- **Learning signal:** The check-in itself, response burden, skip rate, and relationship to owner-confirmed outcomes.

### WF-12 - Life Administration Radar

- **Trigger:** Weekly review or detected upcoming obligation.
- **Outcome:** Make important administrative next actions visible without constant checking.
- **Inputs:** Primary calendar, owner-entered commitments, later-approved email signals, and job pipeline.
- **Output/action:** Prioritized upcoming responsibilities with source, due date, and proposed next action.
- **Initial autonomy:** R1; any external change or message requires appropriate approval.
- **Worst plausible failure:** False urgency, missed obligation, duplicate work, or inappropriate blending of sensitive domains.
- **Offline requirement:** Last synchronized commitments remain available; freshness is visible.
- **Learning signal:** Confirmed obligations, completion, missed/false alerts, and time saved.

---

## 4. Provisional scores

| ID | Workflow | V | F | M | P | R | A | I | O | Total / 40 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| WF-01 | Daily Consistency Plan | 5 | 5 | 4 | 4 | 5 | 5 | 5 | 5 | 38 |
| WF-07 | Universal Capture | 4 | 5 | 4 | 4 | 5 | 5 | 5 | 5 | 37 |
| WF-11 | Energy and Interest Check-in | 5 | 5 | 4 | 4 | 5 | 4 | 5 | 5 | 37 |
| WF-08 | Weekly Self-Knowledge Review | 5 | 3 | 3 | 4 | 5 | 5 | 5 | 5 | 35 |
| WF-09 | Learning Session Planner | 4 | 4 | 4 | 4 | 5 | 4 | 5 | 5 | 35 |
| WF-10 | Creative Momentum | 4 | 4 | 3 | 4 | 5 | 4 | 5 | 5 | 34 |
| WF-02 | Weekly Health Plan | 5 | 4 | 4 | 3 | 5 | 4 | 4 | 4 | 33 |
| WF-04 | Workout Execution Companion | 5 | 4 | 4 | 3 | 5 | 4 | 4 | 4 | 33 |
| WF-03 | Calorie Capture and Nutrition Review | 5 | 5 | 5 | 2 | 5 | 4 | 3 | 3 | 32 |
| WF-05 | Job Application Pipeline | 4 | 4 | 5 | 3 | 5 | 4 | 4 | 3 | 32 |
| WF-06 | Gmail Action Digest | 4 | 5 | 4 | 2 | 5 | 5 | 3 | 3 | 31 |
| WF-12 | Life Administration Radar | 4 | 3 | 4 | 3 | 5 | 4 | 4 | 4 | 31 |

### Scoring caveats

- Scores are provisional agent judgments and must be reviewed by the owner.
- Privacy scores are lower for health and email because their content is sensitive, even when processed locally.
- High architectural-learning scores do not justify a workflow with weak owner value.
- WF-11 can be embedded as a tiny input to WF-01 instead of becoming a separate product surface.
- WF-07 is a useful foundation because no task/reminder application currently exists, but foundation value alone does not make it one of the three owner workflows.
- Job/email workflows may save substantial time but add external-service, prompt-injection, and privacy complexity.

---

## 5. Agent recommendation for owner selection

### Recommended first-year trio

1. **WF-01 Daily Consistency Plan** - the direct expression of the owner's stated behavior goal and a cross-domain backbone.
2. **WF-02 Weekly Health Plan** - aligns with the top outcome and directly reduces meal/workout planning burden.
3. **WF-03 Low-Friction Calorie Capture and Nutrition Review** - addresses the most frequent concrete burden and produces measurable corrections/outcomes.

WF-11 should be embedded as an optional, very small signal within WF-01. WF-07 should be treated as a supporting capability unless the owner prefers it as a named workflow.

### Balanced alternative

Replace WF-03 with **WF-05 Job Application Pipeline** if near-term employment progress is more important than reducing calorie-tracking burden. Gmail digest should follow after prompt-injection controls and sensitive-data policy are designed.

### Why not select solely by total score

WF-07 and WF-11 score highly because they are simple, frequent, and architecturally useful. The approved trio instead prioritizes the owner's top health outcome and explicitly named daily friction.

---

## 6. M0-12 acceptance checklist

- [x] At least ten workflows are cataloged; twelve are included.
- [x] Each workflow states trigger, outcome, inputs, output/action, autonomy, worst failure, offline need, and learning signal.
- [x] Every workflow is scored using the same eight-dimension rubric.
- [x] Owner value reflects accepted outcome priorities and stated friction.
- [x] Scores are labeled provisional and do not replace owner judgment.
- [x] A recommendation and balanced alternative are explicit.
- [x] Owner reviews the catalog and either accepts or corrects material scoring assumptions.

---

## 7. M0-13 owner selection record

The owner must select and rank three workflows. For each selected workflow, the owner will confirm:

- measurable six-month outcome;
- explicit non-scope;
- maximum year-one autonomy;
- whether it is eligible to become the M1 vertical-slice candidate.

**Owner selection approved on 2026-07-25:**

1. WF-01 Daily Consistency Plan.
2. WF-02 Weekly Health Plan.
3. WF-03 Low-Friction Calorie Capture and Nutrition Review.

### 7.1 WF-01 selected boundary

**Six-month outcome:** The owner uses a realistic plan on at least four days per week during a 30-day evaluation period, reports that it makes consistency easier on most evaluated weeks, and spends less time deciding what to do than in the M0 baseline.

**Non-scope:** Punitive streaks, moral judgment, maximizing task count, autonomous commitments, hidden productivity scores, and treating incomplete plans as failure.

**Year-one autonomy ceiling:** R1 plan suggestions by default. R2 reversible local saves or reminders only in an owner-approved workflow. External calendar writes require preview and approval. No autonomous messages or commitments.

**M1 eligibility:** Provisional M1 vertical-slice candidate because it is ranked first, can begin with low-sensitivity manual inputs, and exercises planning, policy, audit, verification, and feedback.

### 7.2 WF-02 selected boundary

**Six-month outcome:** Weekly meal/workout planning time falls materially from the M0 baseline, most generated plans are accepted with only bounded edits, and the owner reports that the workflow supports energy and consistency rather than rigidity.

**Non-scope:** Medical diagnosis, treatment, injury guidance, automatic purchases, prescriptive body goals, or overriding owner-reported pain, fatigue, schedule, preferences, or professional advice.

**Year-one autonomy ceiling:** R1 meal, grocery, and workout proposals. R2 save to Osun or add approved calendar/reminder items after preview. No purchase, health-record write, or external communication.

**M1 eligibility:** Not the first candidate; introduce after the policy and feedback spine is proven by WF-01.

### 7.3 WF-03 selected boundary

**Six-month outcome:** Average calorie-capture time falls materially from baseline, uncertain estimates are visibly labeled and easy to correct, and the owner continues to rate tracking as helpful rather than burdensome.

**Non-scope:** Diagnosis, treatment, automatic restrictive targets, shame, fabricated precision, sharing data externally by default, or using missed entries as evidence of failure. Photo-based inference is deferred until separately assessed.

**Year-one autonomy ceiling:** R0 local calculation and storage plus R1 estimates/summaries. The owner confirms uncertain matches. No external sharing, health-record writes, purchases, or autonomous goal changes.

**M1 eligibility:** Not the first candidate; initial manual text capture can follow after memory and sensitive-data controls are defined.

### 7.4 Boundary confirmation

The owner approved the outcome, non-scope, autonomy, and M1 eligibility statements in Sections 7.1-7.3 without amendment on 2026-07-26. M0-13 is complete.

---

## 8. M0-25 success and failure narratives

Each story uses the version-zero contracts in `09_CONTRACT_DRAFTS.md`. A safe failure is visible to the owner, makes no unauthorized external effect, preserves enough content-minimized evidence to investigate, and never converts missing data into failure or noncompliance.

### 8.1 WF-01 Daily Consistency Plan

#### WF-01-N01 Normal request to verified outcome

1. **Owner interface:** Captures an authenticated owner request or emits the one allowed daily prompt after checking quiet hours, pause, and frequency; creates an owner-origin `workflow.requested` event.
2. **Ingress service:** Validates identity/session, schema, purpose, size, nonce, and workflow version; rejects any embedded claim of authority.
3. **Workflow orchestrator:** Creates/deduplicates the WF-01 run and requests only confirmed goals/preferences plus recent plan outcomes from the memory API.
4. **Memory/data plane:** Applies WF-01 purpose/sensitivity filters and returns attributed current records; missing or disputed memory remains explicit.
5. **Execution gateway/calendar adapter:** If connected, reads only Stage A busy/free/time/timezone/source/freshness fields using a short-lived read capability; otherwise returns an explicit unavailable state.
6. **Model router:** Builds the minimum context, enforces the cloud/local rule, and sends one schema-bound request to the selected replaceable model.
7. **Model runtime:** Returns an `untrusted_proposal` containing a small editable plan, assumptions, uncertainty, and source references; it has no tool or memory authority.
8. **Orchestrator and policy service:** Validate output schema, feasibility, non-scope, notification budget, action risk, and current policy; unsafe/unsupported items are removed or sent for correction.
9. **Owner interface:** Shows the proposed plan, source freshness, uncertainty, and any proposed external effects; the owner edits, dismisses, or selects Submit/Save.
10. **Memory/data plane:** Stores the exact owner-reviewed plan as a versioned local artifact under RET-2 and writes content-minimized audit evidence.
11. **Policy/execution gateway:** If the owner separately requests a calendar event, presents an exact R3 preview, obtains one-time approval, writes through the restricted adapter, reads back authoritative state, and offers undo.
12. **Orchestrator/memory:** Records the verified terminal outcome and later optional feedback as an observation; any preference inference remains a candidate.

**Safe visible end:** The owner sees the saved plan, whether any external effect was verified, source freshness, and how to edit, delete, disable, or undo it.

#### WF-01-F01 Owner denial, dismissal, or cancellation

1. **Owner interface:** Records dismiss, snooze, reject, or cancel as an explicit owner decision without asking for justification.
2. **Policy service:** Issues no action capability and revokes any unused short-lived proposal capability.
3. **Workflow orchestrator:** Moves the run to `denied` or `canceled`, stops model/tool work, and cancels pending timers/retries.
4. **Execution gateway:** Confirms that no external invocation was issued; if one had already begun, reports its actual verification state rather than assuming cancellation reversed it.
5. **Memory/data plane:** Records content-minimized decision evidence; dismissal is not promoted into a negative preference or consistency failure.
6. **Proactivity controller:** Applies the approved rule that repeated dismissal lowers future prompt frequency.

**Safe visible end:** The interface says the plan was not saved and no external action occurred, or clearly identifies any already-started effect needing recovery.

#### WF-01-F02 Model unavailable or malformed

1. **Model router:** Detects unavailable endpoint, timeout, resource limit, incompatible version, or malformed output and emits a typed failure.
2. **Policy service:** Forbids sensitive/unapproved cloud fallback; any allowed minimal Personal cloud fallback still requires the accepted routing policy and owner confirmation.
3. **Workflow orchestrator:** Offers a deterministic blank daily-plan template using only owner-visible inputs, or stops; it does not claim personalization.
4. **Owner interface:** Labels the degraded mode and lets the owner fill, save, retry later, or cancel.
5. **Memory/data plane:** Saves only content the owner intentionally submits; no failed-model output becomes memory.
6. **Operations plane:** Records model/version/latency/error metadata without prompt content by default.

**Safe visible end:** The owner either has a clearly labeled manual plan or a visible no-plan outcome; no hidden provider switch or external effect occurs.

#### WF-01-F03 Calendar unavailable or stale

1. **Calendar adapter:** Returns `failed`, `timed_out`, or a response with freshness outside policy; it never fabricates empty availability.
2. **Execution gateway:** Records the typed result and avoids blind retry outside the original time/retry budget.
3. **Workflow orchestrator:** Marks schedule context unknown and chooses only an approved degraded path: ask the owner for constraints or produce an unscheduled priority list.
4. **Model router:** Excludes stale calendar facts unless policy explicitly permits display-only context with age.
5. **Owner interface:** Shows calendar unavailable/stale and the exact freshness of any displayed cache.
6. **Policy service:** Blocks calendar writes if current state cannot be checked and revalidated.

**Safe visible end:** The owner receives a usable unscheduled draft or cancels; Osun never claims the time slots are free.

#### WF-01-F04 Invalid or malicious external content

1. **Calendar adapter/ingress:** Stage A excludes titles/descriptions/attendees/locations. If a later enabled field contains instruction-like text, it remains `content_origin: external`.
2. **Schema/content boundary:** Validates size/type/encoding, strips active markup where needed, and stores source provenance without treating text as workflow instruction.
3. **Model router:** Removes fields not authorized for WF-01 and labels remaining external text as untrusted data.
4. **Model runtime:** May reference the data only within the supplied task; its proposal cannot grant authority.
5. **Policy service:** Denies secret access, purpose expansion, egress, or tool action requested by content/model text.
6. **Operations/security:** Records an injection/validation reason code and correlation ID without echoing malicious personal content.

**Safe visible end:** The owner sees a normal/narrowed plan or an explicit blocked-content notice; no injected instruction changes memory, policy, or tools.

#### WF-01-F05 Restart or duplicate event

1. **Ingress service:** Recognizes duplicate trigger/event IDs and returns the existing run reference.
2. **Workflow orchestrator:** Reloads the latest durable run state/version and resumes only an incomplete idempotent step.
3. **Policy service:** Revalidates current policy and rejects expired approval/capability after restart.
4. **Execution gateway:** Before retrying an ambiguous calendar action, reads authoritative provider state using idempotency/resource references.
5. **Action ledger:** Appends recovery/verification evidence; it never overwrites the earlier attempt.
6. **Owner interface:** Opens one plan/run and explains recovered, pending, unknown, or completed status.

**Safe visible end:** There is one daily plan and at most one external event; ambiguous state is shown rather than retried blindly.

#### WF-01-F06 Incorrect, stale, or conflicting memory

1. **Memory API:** Returns validity, status, provenance, and conflict indicators with each retrieved goal/preference.
2. **Owner interface:** Shows the memory/source that materially shaped the plan when the owner asks or when confidence/conflict requires it.
3. **Owner:** Corrects, disputes, expires, or supersedes the memory.
4. **Memory service:** Creates an attributed correction/version, prevents the old record from current retrieval, and rebuilds affected indexes/summaries.
5. **Workflow orchestrator:** Invalidates the proposal and regenerates only after the corrected context is current.
6. **Evaluation/audit:** Links the bad-memory event to the affected run and future memory-correction scenario without labeling the owner inconsistent.

**Safe visible end:** The corrected memory and regenerated plan are visible; the prior claim remains historical evidence but no longer drives current decisions.

#### WF-01-F07 Audit, correction, undo, and recovery

1. **Owner interface:** Lets the owner inspect the run trace, source categories, model route, policy reasons, saved artifact, and verified effects.
2. **Owner:** Requests a plan edit/delete, memory correction, calendar undo, source disconnect, or workflow pause.
3. **Policy service:** Normalizes each request separately and requires exact approval for consequential external undo/delete.
4. **Execution gateway:** Applies the local change or provider action and independently verifies the resulting state.
5. **Memory/data plane:** Supersedes/deletes governed records and propagates the deletion manifest through indexes/caches while preserving content-free audit evidence.
6. **Operations plane:** Reports verified, scheduled-for-backup-expiry, provider-controlled, owner-exported, or unresolved copies honestly.
7. **Workflow orchestrator:** Ends in `succeeded`, `partially_succeeded`, or `unknown` based on evidence and keeps the affected integration paused if privacy/integrity is uncertain.

**Safe visible end:** The owner sees what changed, what was verified, what remains, and what is paused; recovery never silently rewrites history.

### 8.2 WF-02 Weekly Health Plan

#### WF-02-N01 Normal request to verified outcome

1. **Owner interface:** Captures an authenticated weekly request or one permitted weekly prompt after quiet-hour/frequency checks.
2. **Ingress/orchestrator:** Creates one WF-02 run and requests only explicit current meal/workout constraints, schedule availability, and any individually authorized local wellness aggregates.
3. **Memory/data plane:** Returns Sensitive purpose-filtered records with provenance/validity; missing HealthKit data remains unknown.
4. **Calendar adapter:** Reads Stage A availability only and labels freshness.
5. **Model router:** Forces Sensitive context to an approved local model and provides no cloud fallback.
6. **Local model:** Produces an editable meal/workout proposal with assumptions and uncertainty as an untrusted artifact.
7. **Policy/orchestrator:** Reject diagnosis, treatment, injury direction, restrictive automatic targets, purchases, health-record writes, and conflict with owner-reported pain/fatigue/schedule.
8. **Owner interface:** Shows the proposal, assumptions, freshness, and sources; owner edits, saves, dismisses, or cancels.
9. **Memory/data plane:** Stores the exact accepted plan locally under RET-2; any reusable procedure/preference remains candidate until confirmed.
10. **Policy/execution gateway:** Optional calendar items each receive exact preview/approval, restricted execution, provider read-back, and undo.
11. **Orchestrator:** Records verified outcome and optional usefulness/rework feedback without moralizing adherence.

**Safe visible end:** The owner has a local wellness plan reflecting stated constraints and sees that it is not medical advice or an autonomous commitment.

#### WF-02-F01 Owner denial, dismissal, or cancellation

1. **Owner interface:** Records dismissal, edit rejection, snooze, or cancellation.
2. **Workflow orchestrator:** Stops generation/execution and moves the run to a visible terminal state.
3. **Policy service:** Issues no calendar/purchase/health capability and revokes unused grants.
4. **Memory service:** Does not interpret dismissal or lack of adherence as health failure, motivation, or diagnosis.
5. **Proactivity controller:** Lowers frequency after repeated dismissals and preserves manual access.

**Safe visible end:** No plan or external action is saved unless the owner intentionally saved an exact reviewed version.

#### WF-02-F02 Local model unavailable or malformed

1. **Model router:** Emits an unavailable/malformed result and blocks cloud fallback because context is Sensitive.
2. **Workflow orchestrator:** Offers a blank structured meal/workout planner populated only with owner-visible schedule fields if allowed.
3. **Policy service:** Prevents old cached model output from being relabeled current.
4. **Owner interface:** Shows degraded/manual mode and lets the owner save, retry later, or cancel.
5. **Memory/data plane:** Stores only owner-submitted content and no failed proposal.

**Safe visible end:** The owner retains a usable manual template or clear failure; sensitive context never leaves locally as a fallback.

#### WF-02-F03 Calendar or HealthKit unavailable/stale/denied

1. **Calendar/Health source adapter:** Returns unavailable, stale, limited-window, or no-data state without guessing whether HealthKit permission was denied.
2. **Memory/data plane:** Preserves source authorization/freshness metadata and treats absent samples as unknown.
3. **Workflow orchestrator:** Omits unavailable inputs and asks only for the minimum explicit constraint needed, if any.
4. **Local model:** Receives no fabricated zeros/history and states assumptions.
5. **Policy service:** Blocks any output that claims medical/behavioral meaning from missing data.
6. **Owner interface:** Shows which sources were unavailable and permits plan creation without them.

**Safe visible end:** A constrained plan may proceed with explicit unknowns, or the owner cancels; missing health/calendar data never becomes a negative judgment.

#### WF-02-F04 Invalid or malicious reference/content

1. **Reference/source adapter:** Labels recipes, workout references, calendar content, and tool output as external data with provenance.
2. **Validation boundary:** Rejects malformed units, impossible values, active markup, oversized payloads, and instruction-like attempts to change policy/tools.
3. **Model router/local model:** Receives only authorized fields and returns a proposal without authority.
4. **Policy service:** Rejects diagnosis, unsafe constraint override, data egress, purchase, or external action regardless of content/model wording.
5. **Security/evaluation:** Records the blocked class/reason and links the case to injection/unsafe-advice tests.

**Safe visible end:** The suspicious item is omitted or the plan is blocked with a clear explanation; no memory promotion or sensitive egress occurs.

#### WF-02-F05 Restart or duplicate event

1. **Ingress/orchestrator:** Uses owner/week/workflow idempotency identity to reopen the existing weekly run.
2. **Memory service:** Returns the current accepted plan version and refuses stale state overwrite.
3. **Policy service:** Expires previous one-time approvals and rechecks constraints after restart.
4. **Execution gateway:** Reconciles any ambiguous calendar action before retry and avoids duplicate events.
5. **Owner interface:** Shows one active/accepted weekly plan and recovered state.

**Safe visible end:** Restart cannot produce competing plans, duplicated events, or a broader permission scope.

#### WF-02-F06 Incorrect health preference, constraint, or memory

1. **Owner interface:** Exposes source/validity when a constraint affects the proposal and lets the owner report it wrong or outdated.
2. **Memory service:** Marks the record disputed/superseded, preserves provenance, and blocks current retrieval.
3. **Policy service:** Quarantines affected plans when the bad memory relates to pain, fatigue, allergy-like constraints, or other safety-relevant owner statements.
4. **Workflow orchestrator/local model:** Rebuilds a proposal only from corrected explicit information.
5. **Evaluation/audit:** Records the correction path and checks that no diagnosis or hidden health inference was created.

**Safe visible end:** The incorrect constraint no longer influences plans; the owner sees the corrected plan and evidence trail.

#### WF-02-F07 Audit, correction, deletion, and recovery

1. **Owner interface:** Shows which preference, calendar fields, optional health types, local model, and policy rules influenced the plan.
2. **Owner:** May revoke a HealthKit type on iPhone, disconnect Calendar, delete a plan, correct a preference, undo a calendar item, or disable WF-02.
3. **Source adapters/policy:** Stop future collection and revoke/expire related capabilities without affecting unrelated local functions.
4. **Memory/data plane:** Applies correction/deletion manifests across raw, derived, index, cache, and debug records; no health content remains in ordinary audit.
5. **Execution gateway:** Verifies external calendar undo when requested.
6. **Operations plane:** Reports restore/backup/provider limitations honestly and keeps the workflow paused on unresolved privacy state.

**Safe visible end:** The owner sees verified source revocation, local deletion/correction, external effect state, and any remaining copy/expiry limitation.

### 8.3 WF-03 Low-Friction Calorie Capture

#### WF-03-N01 Normal request to verified outcome

1. **Owner interface:** Accepts one manual meal/food text entry; no unsolicited calorie reminder or photo/audio capture occurs.
2. **Ingress/orchestrator:** Validates schema, time/group, size, origin, and Sensitive/local-only purpose; creates one idempotent WF-03 run.
3. **Local reference adapter:** Searches only approved local nutrition references and returns attributed candidate matches/units.
4. **Model router/local calculator/model:** Uses local-only processing to produce an estimate/range, units, confidence, sources, and alternatives as an untrusted proposal.
5. **Policy/orchestrator:** Rejects fabricated precision, impossible units, hidden restrictive target, diagnosis/treatment, external sharing, or health-record write.
6. **Owner interface:** Shows the estimate, uncertainty, source, alternatives, and easy correction; owner edits, confirms, saves unresolved, or cancels.
7. **Memory/data plane:** Saves the exact intentional local record under RET-2 with derivation links; no cloud egress occurs.
8. **Local review service:** Aggregates only saved records and labels summaries incomplete when entries are missing.
9. **Memory service:** Treats corrected food mappings as candidates until owner confirmation.

**Safe visible end:** The owner sees a local, correctable record with uncertainty and no implication that missing entries are failures.

#### WF-03-F01 Owner denial or cancellation

1. **Owner interface:** Records cancel/discard without saving the draft unless the owner explicitly chooses a raw unresolved save.
2. **Workflow orchestrator:** Terminates the run and cancels local estimation work.
3. **Policy service:** Issues no external capability because none exists for the initial workflow.
4. **Memory/data plane:** Persists no meal/calorie record from a discarded draft; content-minimized run metadata follows short retention if needed.
5. **Evaluation service:** Does not count cancellation as dietary noncompliance or motivation evidence.

**Safe visible end:** The interface confirms nothing was saved and provides no shame, streak loss, or repeated unsolicited prompt.

#### WF-03-F02 Local model/calculator unavailable or malformed

1. **Model router/local computation service:** Returns typed unavailable, timeout, or invalid-unit/output failure and forbids cloud fallback.
2. **Workflow orchestrator:** Offers manual raw entry without estimate, a clarification field, or retry later.
3. **Policy service:** Blocks stale/cached estimates from being presented as current and prevents fabricated default values.
4. **Owner interface:** Labels the entry unresolved and lets the owner intentionally save only known text/amount or cancel.
5. **Memory service:** Does not promote an unresolved match into a food mapping.

**Safe visible end:** The owner has either an explicitly unresolved local entry or no saved record; Osun never invents precision.

#### WF-03-F03 Reference source unavailable or stale

1. **Local reference adapter:** Returns unavailable/stale database version rather than an empty confident match.
2. **Workflow orchestrator:** Does not add an external/cloud lookup because the approved workflow has no such route.
3. **Local calculator/model:** Uses only still-valid local evidence or abstains.
4. **Owner interface:** Shows reference unavailability/version age and provides manual entry/cancel.
5. **Operations plane:** Records source health/version without food content.

**Safe visible end:** Tracking can continue as a raw/manual local record, or stop, without hidden egress or fabricated estimate.

#### WF-03-F04 Invalid or malicious reference/input

1. **Ingress/reference adapter:** Treats owner-pasted/external reference text as untrusted, validates encoding/size/unit/value bounds, and strips active behavior.
2. **Orchestrator:** Keeps instructions separate from food data and rejects attempts to request secrets, tools, cloud calls, or policy changes.
3. **Local model:** Returns a structured proposal only; confidence cannot override validation.
4. **Policy service:** Denies fabricated precision, unsafe target, cross-purpose memory, external sharing, or generated code.
5. **Memory service:** Quarantines the bad mapping/reference from promotion and retrieval.

**Safe visible end:** The owner sees an invalid/ambiguous input explanation or alternatives; no poisoned mapping, execution, or egress occurs.

#### WF-03-F05 Restart or duplicate submit

1. **Ingress/orchestrator:** Uses run and owner-submit idempotency keys to locate the existing draft/record.
2. **Memory/data plane:** Returns the existing record/version instead of inserting a second meal.
3. **Workflow orchestrator:** Resumes only incomplete local estimation/correction work and rejects stale state writes.
4. **Owner interface:** Shows one saved entry and whether any calculation remains unresolved.
5. **Local review service:** Recomputes summaries from authoritative saved record IDs, preventing double count.

**Safe visible end:** Restart/retry cannot duplicate the meal or calories; the one authoritative record is editable.

#### WF-03-F06 Incorrect food mapping or memory

1. **Owner interface:** Shows match/source/unit/confidence and lets the owner select another match, change amount, or mark unknown.
2. **Memory service:** Marks the old mapping disputed/superseded and prevents it from silently matching later entries.
3. **Memory/data plane:** Creates a new version of the meal/estimate with derivation to the correction; prior value remains historical evidence.
4. **Local review service:** Recomputes affected summaries and labels version/time.
5. **Memory service:** Creates a candidate corrected mapping and requests confirmation before reusable promotion.

**Safe visible end:** Current records/summaries reflect the correction, and the wrong mapping cannot continue as a hidden fact.

#### WF-03-F07 Audit, correction, deletion, and recovery

1. **Owner interface:** Shows saved food text, estimate/range, units, source, confidence, corrections, local model/version, and summary derivation.
2. **Owner:** Requests edit, supersession, delete by record/time range, export, or WF-03 pause.
3. **Policy/memory service:** Builds the exact correction/deletion/export plan and blocks new affected ingestion while it runs.
4. **Memory/data plane:** Updates/deletes raw records, estimates, candidate mappings, indexes, caches, and summaries; tombstones contain no meal content.
5. **Backup/recovery service:** Applies restore-time deletion handling and reports any delayed backup expiry rather than claiming immediate erasure.
6. **Local review service:** Recomputes summaries from remaining authoritative records and keeps missing periods missing.
7. **Operations plane:** Records content-minimized verification and unresolved state.

**Safe visible end:** The owner sees corrected/deleted/exported state, rebuilt summaries, and honest remaining-copy status; no external party receives the data.

---

## 9. M0-25 narrative coverage

| Workflow | Normal | Denial/cancel | Model unavailable | Source unavailable/stale | Invalid/malicious | Restart/duplicate | Incorrect memory | Audit/recovery |
|---|---|---|---|---|---|---|---|---|
| WF-01 | WF-01-N01 | WF-01-F01 | WF-01-F02 | WF-01-F03 | WF-01-F04 | WF-01-F05 | WF-01-F06 | WF-01-F07 |
| WF-02 | WF-02-N01 | WF-02-F01 | WF-02-F02 | WF-02-F03 | WF-02-F04 | WF-02-F05 | WF-02-F06 | WF-02-F07 |
| WF-03 | WF-03-N01 | WF-03-F01 | WF-03-F02 | WF-03-F03 | WF-03-F04 | WF-03-F05 | WF-03-F06 | WF-03-F07 |

Acceptance checks:

- [x] Every selected workflow has a normal request-to-verified-outcome story.
- [x] Every selected workflow has owner denial/cancellation, model unavailable, and source unavailable/stale stories.
- [x] Every selected workflow has invalid/malicious input, restart/duplicate, incorrect-memory, and audit/recovery stories.
- [x] Every step names the responsible component.
- [x] Every failure ends in a safe, owner-visible state.
- [x] Narratives use typed version-zero contracts and preserve accepted data/autonomy boundaries.
- [x] Owner accepts or amends the narratives.

**Owner decision:** Accepted all 24 narratives as written on 2026-07-26; no amendments.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as workflow analyst
- Reviewer: Owner
- Status: M0-12, M0-13, and M0-25 accepted
- Inputs used: Accepted owner charter, current-system inventory, M0 scoring rubric, accepted workflow/data/autonomy/architecture/security/privacy specifications, version-zero contracts
- Assumptions: Time savings lack baseline; workflow complexity and privacy scores are provisional; health workflows are wellness support, not diagnosis or treatment
- Open questions: Success thresholds after private baseline completion
- Acceptance evidence: Twelve comparable workflow cards, consistent scoring table, owner-approved ranked trio/boundaries, and 24 component-named success/failure/recovery narratives
- Last updated: 2026-07-26
