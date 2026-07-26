# Osun Owner Charter

**Task:** M0-10 - Define the owner charter and "better life" outcomes \
**State:** Owner accepted; M0-10 complete \
**Owner:** Primary owner \
**Interview analyst:** Primary AI coordinator \
**Last updated:** 2026-07-25

---

## 1. Purpose

This charter translates the owner's vision into stable outcomes and constraints without allowing observed behavior, agent preferences, or implementation choices to redefine what a better life means.

The owner remains the authority on values, priorities, unacceptable outcomes, and tradeoffs. Agent interpretations in this document remain **UNCONFIRMED** until the owner accepts them.

---

## 2. Owner statements already established

The following statements come directly from the owner's project requests and acceptance of the M0 process:

- Osun is intended to grow over ten or more years.
- Its components should remain cohesive, seamless, and fast as the system expands.
- The initial Agent Box is the owner's Windows PC and will run local AI, skills, workflows, and interactive task processing.
- A Raspberry Pi is intended to provide an always-on server that can coordinate tools and the external world.
- Home Assistant and future servers/devices should integrate into the same system.
- Osun should aggregate authorized life data into a memory of the owner, routines, workflows, timing, and preferences.
- Osun should offer timely help and support the owner in becoming the person they want to be.
- The architecture should eventually support a larger home and family without being rebuilt from scratch.
- The initial planning constraint is one person contributing about ten focused hours each week with extensive AI assistance.
- Personalization should grow first through explicit memory and evaluated learning, with personal-model training later when evidence supports it.
- The owner accepted the M0 scope and operating rules as written and approved AI-assisted coordination on 2026-07-25.

These statements define direction but do not yet rank the first six-month life outcomes.

---

## 3. Draft mission

> Build an owner-controlled personal intelligence system that learns how the owner lives and prefers to work, coordinates authorized tools and environments, and provides timely help that improves daily life while preserving privacy, agency, explainability, and long-term portability.

**Status:** Owner accepted on 2026-07-25.

---

## 4. Proposed outcome domains

The owner should rank these domains and may add, remove, merge, or rename them.

| Domain | Proposed outcome | Six-month signal examples | Status |
|---|---|---|---|
| Time and attention | Spend less time remembering, organizing, and re-entering routine information | Fewer forgotten tasks; less planning time; fewer repeated explanations | Not selected in top five |
| Execution | Turn intentions into completed actions with less friction | Higher completion of owner-selected priorities; fewer abandoned captures | Not selected in top five; productivity remains a desired result |
| Self-knowledge | Understand patterns, routines, energy, and decisions without confusing correlation with value | Useful weekly reflections; corrected rather than hidden false inferences | Selected priority 4 |
| Learning and growth | Retain lessons and make progress on skills and long-term goals | Reused learning notes; sustained progress on chosen goals | Selected priority 2 |
| Health and wellbeing | Support owner-defined healthy routines without diagnosis or coercion | Better adherence to explicitly chosen routines; owner-reported energy | Selected priority 1 |
| Relationships | Remember commitments and create space for important people without surveilling them | Fewer missed commitments; owner-rated relationship support | UNCONFIRMED |
| Home and environment | Reduce household friction through bounded coordination | Successful low-risk automations; fewer manual repeated steps | UNCONFIRMED |
| Responsibilities and administration | Reduce avoidable life-admin burden | Less time on recurring administration; fewer late obligations | Selected priority 5 |
| Creativity and recreation | Protect time and context for meaningful creative or enjoyable activity | More owner-valued sessions; more interest in intended weekly activities | Selected priority 3 |
| System ownership | Maintain a private, portable, understandable system that can evolve for a decade | Successful export/restore; low maintenance; vendor replaceability | UNCONFIRMED |

The final charter should contain five to eight prioritized outcomes rather than treating every domain as equally important.

---

## 5. Proposed principles and conflict order

These are draft owner principles derived from the accepted master plan. The owner should confirm the ordering because it resolves future tradeoffs.

1. Physical safety and legal/ethical boundaries.
2. Owner agency, consent, and ability to stop.
3. Privacy and protection of the owner and other people.
4. Accuracy, evidence, and honest uncertainty.
5. Support for explicitly stated values and current goals.
6. Reliability and reversibility.
7. Usefulness and reduction of cognitive load.
8. Speed and seamlessness.
9. Cost and feature breadth.

**Status:** Owner accepted on 2026-07-25.

---

## 6. Draft non-goals and unacceptable outcomes

The following are inherited from the accepted M0 scope but require owner confirmation as charter-level boundaries:

- Osun does not covertly monitor family, guests, coworkers, neighbors, or the public.
- Osun does not treat frequent behavior as proof that the owner values that behavior.
- Osun does not optimize a hidden score over the owner's stated judgment.
- Osun does not make medical, legal, financial, or safety-critical decisions as an authority.
- Osun does not move money, enter contracts, impersonate the owner, or make irreversible commitments independently.
- Osun does not make the owner's personal intelligence dependent on one model, vendor, or computer.
- Osun does not place credentials or restricted data into general model context.
- Osun does not train on every captured datum automatically.
- Osun does not expand autonomy merely because a model expresses confidence.
- Osun must remain usable, inspectable, exportable, pausable, and recoverable without the model's cooperation.

Unacceptable project outcomes proposed for owner review:

- Osun consumes more attention or maintenance than it saves for a sustained period.
- The owner feels watched, manipulated, shamed, or trapped by the system.
- The system discourages personal change by overfitting to past behavior.
- A family member loses meaningful privacy or agency because they share a home.
- The owner cannot understand why an important suggestion or action occurred.
- The owner becomes unable to perform essential life functions when Osun is unavailable.

**Status:** Owner accepted on 2026-07-25, including safeguards against unintended influence while retaining a strong Osun personality.

---

## 7. Owner interview - Round 1

These questions unblock the first charter draft and workflow catalog. Short, informal answers are acceptable.

### Q1 - Six-month transformation

If Osun were genuinely helping six months from now, what three concrete differences would you notice in an ordinary week?

**Owner response (2026-07-25):** Be more productive in everyday life, have more energy for desired activities, and feel more interested in the things the owner wants to do each week.

### Q2 - Current friction

Which recurring tasks, decisions, or responsibilities currently consume the most avoidable time or mental energy?

**Owner response (2026-07-25):** Calorie tracking, workout planning, applying to jobs, checking email, and meal planning currently consume the most time.

### Q3 - First workflow preference

Of daily planning, universal capture, and daily review, which would help most first? Is there another workflow that clearly matters more?

**Owner response (2026-07-25):** No preferred starting workflow; choose the order that produces visible improvement in everyday life.

### Q4 - Support versus change

Name one behavior or routine Osun should reinforce and one observed behavior it must not treat as a preference because you want to change it.

**Owner response (2026-07-25):** The owner wants to change inconsistency across activities. A specific behavior to reinforce was not yet named.

### Q5 - Intrusion boundary

What would make Osun feel intrusive, manipulative, judgmental, or dependency-forming to you?

**Owner response (2026-07-25):** The owner does not initially consider intrusiveness, judgment, or manipulation a material risk and wants Osun to have its own personality.

**Analyst interpretation:** A distinct, proactive personality is a product requirement. Non-coercion, pause, audit, and attention-burden controls remain engineering safeguards against unintended influence; they are not a request to make Osun bland or passive.

### Q6 - Outcome priorities

Choose and rank five outcome domains from Section 4, or replace them with your own terms.

**Owner response (2026-07-25):** 1. Health and wellbeing; 2. Learning and growth; 3. Creativity and recreation; 4. Self-knowledge; 5. Responsibilities and life administration.

---

## 8. Round 1 synthesis

### 8.1 Six-month outcome statement

The first six-month system should help the owner:

1. act more consistently on intended activities;
2. reduce planning and tracking burden around health, meals, workouts, job applications, and email;
3. experience more usable energy and engagement for chosen weekly activities.

This is not a mandate to maximize task count. Productivity is valuable when it supports health, learning, creativity, self-knowledge, and life administration in that priority order.

### 8.2 Initial workflow implications

The workflow catalog should give special consideration to:

- meal planning plus low-friction calorie capture;
- workout planning and follow-through;
- daily/weekly planning focused on consistency and energy;
- job discovery/application tracking;
- email triage and actionable summaries;
- a weekly reflection that detects obstacles without labeling inconsistent behavior as a preference.

No workflow is selected yet. M0-12 will compare at least ten candidates using value, frequency, privacy, reversibility, feasibility, and maintenance burden.

### 8.3 Personality requirement

Osun should be allowed to develop a recognizable personality and point of view. Personality does not grant authority: action permissions, data boundaries, explanations, pause, and owner correction remain deterministic product controls.

### 8.4 Questions required to complete M0-10

1. **Mission:** Accepted as written on 2026-07-25.
2. **Behavior to reinforce:** Living consistently and continuing to act toward the owner's dreams.
3. **Non-goals and safeguards:** Accepted as written on 2026-07-25.
4. **Principle conflict order:** Accepted as written on 2026-07-25.

The behavior statement is intentionally aspirational. Individual workflows must translate it into small owner-chosen actions rather than a universal streak score.

---

## 9. Later owner interview topics

These will be asked after Round 1 so the owner is not required to answer everything at once:

- A good ordinary weekday and weekend.
- Responsibilities most often forgotten or delayed.
- Personal definitions of health, learning, relationships, creativity, and rest.
- Areas Osun may support but must never optimize autonomously.
- Desired six-month, one-year, and ten-year project outcomes.
- Acceptable monthly cost and maintenance burden.
- Privacy, cloud-processing, memory-retention, and autonomy decisions.

---

## 10. M0-10 acceptance checklist

- [x] Existing owner statements separated from agent interpretations.
- [x] Owner confirms or revises the mission.
- [x] Owner selects five to eight prioritized life outcomes.
- [x] Owner confirms non-goals and unacceptable outcomes.
- [x] Owner confirms principle conflict order.
- [x] Each outcome can connect to observable evidence without becoming a hidden optimization score.
- [x] Owner confirms the charter preserves their meaning.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as owner-interview analyst
- Reviewer: Owner
- Status: Accepted
- Inputs used: Owner's project vision, accepted master plan, accepted M0 operating rules
- Assumptions: Workflow-level definitions of consistency remain to be designed and evaluated
- Open questions: No blocker for M0-10; later interview topics remain in Section 9
- Acceptance evidence: Owner accepted mission, ranked outcomes, non-goals, principle order, and consistency direction on 2026-07-25
- Last updated: 2026-07-25
