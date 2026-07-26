# Osun M0 Baseline Measurement

**Task:** M0-16 - Define and begin baseline measurement \
**State:** Active; owner authorized the seven-day window \
**Accountable:** Evaluation scientist \
**Reviewer:** Owner \
**Selected workflows:** WF-01 Daily Consistency Plan, WF-02 Weekly Health Plan, WF-03 Calorie Capture \
**Authorized window:** 2026-07-27 through 2026-08-02 \
**Last updated:** 2026-07-26

---

## 1. Purpose

This baseline measures the current effort, friction, and experience of the three selected workflows before Osun changes them. It is not a score of the owner and must not become a streak, compliance grade, health claim, or productivity target.

The baseline will inform:

- which part of each workflow deserves the first intervention;
- what "materially less time" should mean after observing normal variation;
- whether a proposed feature saves attention or merely moves work around;
- which M1 success thresholds are ambitious but realistic.

No causal health conclusions may be drawn from seven days.

---

## 2. Privacy and storage rule

The repository is currently inside OneDrive. It is suitable for specifications but not approved for sensitive health, energy, meal, calorie, or workout observations.

During M0:

1. Keep the completed daily cards on paper or in a private, non-synced local location controlled by the owner.
2. Do not enter completed cards, meal descriptions, health notes, calendar titles, or personal narrative into this repository.
3. Do not send raw observations to a cloud model.
4. At the end of the week, review the cards locally. The repository may record only owner-approved design conclusions or an attestation that the baseline was completed.
5. A future encrypted Osun data root must be approved before digital sensitive measurements become routine.

The blank form and metric definitions are safe to version because they contain no observations.

---

## 3. Current manual processes

These are the processes being measured, not prescriptions for how the owner should behave.

### WF-01 Daily Consistency Plan

Current state:

- no dedicated task or reminder application;
- intentions are held across memory, calendars, notes, and immediate decisions;
- the owner decides what to do and when without a single daily planning workflow;
- inconsistency and repeated deciding are the named friction.

Observed process boundary begins when the owner starts deciding what matters for the day and ends when a usable intention or plan exists. Time spent doing the tasks is excluded.

### WF-02 Weekly Health Plan

Current state:

- meal and workout planning are separate sources of effort;
- Google Calendar is the primary calendar, but there is no Osun planning workflow;
- schedule, energy, preferences, and constraints are reconciled manually.

Observed process boundary begins when meal or workout planning starts and ends when the owner considers the plan usable. Shopping, cooking, commuting, and exercising are excluded. Rework caused by an unrealistic plan is recorded separately.

### WF-03 Low-Friction Calorie Capture

Current state:

- calorie tracking is a named high-friction activity;
- the exact tool and detailed sequence are intentionally not required for this baseline;
- time spent finding, estimating, entering, and correcting food records is included.

Observed process boundary begins when the owner starts recording or estimating a meal and ends when the entry is accepted or abandoned. Eating and meal preparation are excluded.

---

## 4. Metrics and decision use

Only metrics tied to a design or acceptance decision are collected.

| Metric | Workflow | Measurement | Decision informed |
|---|---|---|---|
| Planning/deciding minutes | WF-01 | Total minutes spent creating or revising the day's intention | Whether M1 should focus first on prioritization, scheduling, or capture |
| Intentional-plan presence | WF-01 | Yes, partial, no, or not attempted | Whether the workflow is currently available often enough to improve |
| Day-alignment rating | WF-01 | 1-5 answer to "Did today resemble the day you intended?" | Outcome baseline without treating task count as the goal |
| Energy rating | WF-01/WF-02 | Owner-chosen 1-5 rating at roughly the same evening time | Descriptive context and future guardrail; never a medical inference |
| Interest/engagement rating | WF-01 | Owner-chosen 1-5 rating | Whether later planning helps engagement rather than only output |
| Meal-planning minutes | WF-02 | Minutes spent making the weekly or partial-week meal plan | Time-saving target and workflow-scope choice |
| Workout-planning minutes | WF-02 | Minutes spent making or revising the workout plan | Time-saving target and workflow-scope choice |
| Health-plan rework minutes | WF-02 | Minutes spent replacing an unusable meal/workout plan | Whether constraint capture is more important than generation |
| Meals intended for capture | WF-03 | Count chosen for tracking that day | Denominator for capture availability, not a compliance target |
| Meals captured | WF-03 | Count recorded to the owner's current standard | Current completion baseline |
| Calorie-capture minutes | WF-03 | Total daily tracking time | Latency target for the future workflow |
| Corrections/retries | WF-03 | Count of entries materially redone | Whether matching accuracy or input speed is the main problem |
| Attention burden | All | One daily 1-5 rating for the measurement itself and current workflows | Ensure an intervention does not cost more attention than it saves |
| Confounder flag | All | Ordinary, unusual workload, illness/injury, travel, social event, or other | Interpret variation without inventing explanations |

Scale anchors:

- **1:** very low;
- **3:** ordinary/mixed;
- **5:** very high.

Ratings are ordinal descriptions, not precise quantities.

---

## 5. Daily collection method

### Start-of-day action

No separate form is required. If the owner intentionally makes a plan, start a timer and record the total planning/deciding minutes that evening.

### During-day action

Use a timer or rough clock reading for calorie capture and any meal/workout planning. Accuracy to the nearest minute is sufficient. Do not reconstruct forgotten durations in detail.

### Evening card

Complete one card in no more than five minutes:

```text
OSUN BASELINE - DAY __ OF 7       DATE: __________

Day context: ordinary / unusual workload / illness-injury / travel /
             social event / other: __________

WF-01
Planning/deciding minutes: ___
Intentional plan: yes / partial / no / not attempted
Today resembled what I intended (1-5): ___
Energy (1-5): ___        Interest/engagement (1-5): ___

WF-02
Meal-planning minutes today: ___
Workout-planning minutes today: ___
Plan rework minutes today: ___

WF-03
Meals intended for capture: ___    Meals captured: ___
Total calorie-capture minutes: ___  Corrections/retries: ___

Attention burden today (1-5): ___
Optional short confounder label only: ____________________
```

Do not write meal descriptions, medical information, calendar content, or an explanation of personal events on the card.

---

## 6. Seven-day protocol

| Day | Date | Required action |
|---|---|---|
| 1 | Monday, 2026-07-27 | Begin ordinary measurement; do not change behavior for the project |
| 2 | Tuesday, 2026-07-28 | Continue; leave forgotten values blank |
| 3 | Wednesday, 2026-07-29 | Continue; check that logging remains under five minutes |
| 4 | Thursday, 2026-07-30 | Continue; do not compensate for earlier missing entries |
| 5 | Friday, 2026-07-31 | Continue; mark unusual context without personal detail |
| 6 | Saturday, 2026-08-01 | Continue; include weekend variation |
| 7 | Sunday, 2026-08-02 | Complete final card and the local review in Section 7 |

If meal/workout planning normally occurs on another day, record it when it naturally occurs. Do not create extra planning solely to make the dataset look complete.

Missing data remains missing. A blank is different from zero. Estimates must be visibly marked with `~`.

---

## 7. End-of-week local review

The owner reviews the seven cards without sending them to a cloud service. A calculator is sufficient.

For each workflow, determine:

1. median time and observed minimum/maximum time;
2. number of usable observation days;
3. obvious rework or retry burden;
4. whether measurement itself stayed acceptable;
5. one design implication supported by the observations;
6. one uncertainty or confounder that prevents overclaiming.

Suggested local worksheet:

| Workflow | Usable days/events | Median time | Range | Main friction | Design implication | Important uncertainty |
|---|---:|---:|---:|---|---|---|
| WF-01 |  |  |  |  |  |  |
| WF-02 |  |  |  |  |  |  |
| WF-03 |  |  |  |  |  |  |

The owner may later approve specific aggregates for entry into an encrypted Osun evaluation store. Until that store exists, the completed worksheet remains private and uncommitted.

---

## 8. Validity and stopping rules

The baseline is usable when:

- at least five daily cards are present;
- at least one normal meal/workout planning event is observed, or the absence of one is explicitly recorded;
- logging took no more than five minutes on most days;
- unusual days are labeled without private narrative;
- missing observations were not reconstructed as facts.

The baseline should be repeated or extended when:

- fewer than five days are usable;
- the week is dominated by travel, illness, injury, or a clearly abnormal schedule;
- measurement changes behavior enough that it no longer represents the current process;
- the owner finds the collection burdensome or destabilizing.

The owner may stop at any time. Stopping is not failure; it is evidence that the method needs revision.

---

## 9. Acceptance checklist

- [x] Current manual process is defined for all three selected workflows.
- [x] Every metric maps to a design or success decision.
- [x] Time, completion, rework, attention burden, and owner experience are represented.
- [x] The collection method takes no more than five minutes per day.
- [x] Proposed start and end dates are recorded.
- [x] Confounders and missing-data rules are explicit.
- [x] Unrelated personal content is excluded.
- [x] Storage respects the approved local-only policy.
- [x] Owner confirms the window and begins Day 1.
- [ ] Owner completes or records a valid alternative to the seven-day baseline.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as evaluation scientist
- Reviewer: Owner
- Status: Active; collection authorized for 2026-07-27 through 2026-08-02
- Inputs used: Accepted owner charter, selected workflow catalog, accepted data/autonomy policy
- Assumptions: The authorized week is reasonably representative; paper or another private non-synced medium is available
- Open questions: Whether the week becomes atypical; end-of-week local review
- Acceptance evidence: Manual-process definitions, decision-linked metrics, sub-five-minute card, dates, privacy controls, missing-data rules, validity criteria, and owner authorization on 2026-07-26
- Last updated: 2026-07-26
