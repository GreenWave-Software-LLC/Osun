# Osun Workflow Catalog

**Tasks:** M0-12 candidate catalog and scoring; M0-13 owner selection; M0-25 narratives later \
**State:** M0-12 and M0-13 accepted; selected workflow boundaries approved \
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

## 8. M0-25 narrative status

Detailed success, denial, outage, injection, duplicate-event, bad-memory, and recovery narratives will be added after M0-13, M0-20, and M0-24 stabilize the selected workflows and component contracts.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as workflow analyst
- Reviewer: Owner
- Status: M0-12 and M0-13 accepted; M0-25 narratives remain future work
- Inputs used: Accepted owner charter, current-system inventory, M0 scoring rubric
- Assumptions: Time savings lack baseline; workflow complexity and privacy scores are provisional; health workflows are wellness support, not diagnosis or treatment
- Open questions: Detailed M0-25 success and failure narratives after architecture and contracts stabilize
- Acceptance evidence: Twelve comparable workflow cards, consistent scoring table, owner-approved ranked trio, owner-approved workflow boundaries, recommendation, caveats, and selection criteria
- Last updated: 2026-07-26
