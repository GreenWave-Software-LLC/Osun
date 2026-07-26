# Osun M0 Agent Execution Checklist

**Milestone:** M0 - Charter, requirements, and evidence plan  
**Interpretation:** M0 is the first milestone in the Osun roadmap  
**Target duration:** 4 weeks  
**Human-owner budget:** Approximately 40 hours total  
**Document status:** Ready for owner review and agent assignment  
**Parent plan:** [Osun Living Master Plan](OSUN_MASTER_PLAN.md)  
**M0 completion record:** `docs/m0/M0_GATE_REVIEW.md`  

---

## 1. Mission

Complete the decisions and evidence needed to begin M1 safely. M0 produces a build-ready paper design; it does not produce the Osun runtime.

At the end of M0:

- the owner has selected three measurable first-year workflows;
- the data, privacy, and autonomy boundaries are explicit;
- a request can be traced across the proposed system from capture through memory and audit;
- threats, failure behavior, and recovery concepts are documented;
- version-zero contracts and at least 25 evaluation scenarios exist;
- technology choices are supported by evidence from bounded experiments;
- the first M1 vertical slice is small enough to finish in four weeks or less.

This checklist is both an execution dashboard and a dispatch guide for AI agents.

---

## 2. Scope boundary

### 2.1 Authorized M0 work

- Interviewing the owner and structuring answers.
- Research using authoritative sources.
- Drafting specifications, diagrams, inventories, risk analyses, scenarios, and decision records.
- Read-only inspection of the owner's explicitly named devices, services, and project files.
- Small, disposable technology benchmarks in Week 4 after the owner approves the benchmark plan.
- Creating synthetic examples and mock contracts.
- Reviewing artifacts for consistency, feasibility, privacy, security, and testability.

### 2.2 Not authorized during M0

- Building or deploying the production runtime.
- Starting broad personal-data collection.
- Ingesting email, health, finance, location, voice, camera, or home data.
- Exposing the PC, Pi, or Home Assistant to the public internet.
- Installing persistent services on the PC or Pi without explicit owner approval.
- Creating live automations or performing physical-device actions.
- Selecting a vendor merely because an agent prefers it.
- Training or fine-tuning a personal model.
- Adding household members or collecting information about them.
- Making owner-only decisions by inference.

If a task would cross this boundary, the agent must stop, describe the proposed expansion, and request owner authorization.

---

## 3. Responsibility model

### 3.1 Decisions only the owner can make

Agents may clarify options and consequences, but only the owner may approve:

- what “living better” means;
- the first three workflows and their priority;
- data that is prohibited, confirmation-only, or allowed;
- local-versus-cloud processing policy;
- acceptable autonomy and actions that always require approval;
- acceptable financial and time budgets;
- acceptable privacy, safety, and maintenance tradeoffs;
- whether M0 passes and M1 may begin.

An agent must label any assumed owner preference as **UNCONFIRMED**.

### 3.2 Agent roles

One agent may perform several roles, but each artifact has one accountable author and one reviewer.

| Role | Primary responsibility | Prohibited from deciding |
|---|---|---|
| M0 coordinator | Dependencies, status, evidence register, artifact consistency | Owner values or final gate approval |
| Owner-interview analyst | Convert owner answers into requirements without changing meaning | What the owner ought to value |
| Workflow analyst | Catalog, score, and narrate candidate workflows | Final workflow selection |
| Systems architect | Component boundaries, flows, contracts, deployment responsibilities | Privacy/autonomy policy |
| Security analyst | Threat model, controls, abuse and failure cases | Risk acceptance on owner's behalf |
| Privacy analyst | Data inventory, purpose, retention, access, deletion, egress | Consent or prohibited-data choices |
| Evaluation scientist | Baselines, metrics, golden scenarios, exit evidence | Redefining success after seeing results |
| Technology scout | Evidence-based options and bounded benchmarks | Final purchasing or stack commitment |
| Independent reviewer | Find omissions, contradictions, unjustified assumptions, and infeasible scope | Editing owner decisions without approval |

### 3.3 Human review rule

AI output is a draft until the owner accepts it. The coordinator may mark an agent task complete when its artifact passes its acceptance criteria, but only the owner can mark an owner-decision task or the M0 gate complete.

---

## 4. Agent operating contract

Every assigned agent must:

1. Read this checklist and the relevant sections of the master plan before working.
2. Stay within the assigned task and scope boundary.
3. Preserve owner statements separately from agent interpretations.
4. Use synthetic data unless the owner explicitly provides real data for the task.
5. Prefer primary and authoritative sources for technical, security, legal, and standards claims.
6. Record important assumptions, uncertainty, alternatives, and unresolved questions.
7. Produce the named artifact, not only a chat summary.
8. Include acceptance evidence and source links in the artifact.
9. Avoid implementation choices that have not passed the decision process.
10. Never mark owner approval on the owner's behalf.

### 4.1 Stop-and-escalate conditions

An agent must stop and ask the owner or coordinator when:

- the answer depends on an undisclosed owner value or privacy preference;
- a requested action would write to an external system, install software, expose a service, or collect personal data;
- two accepted requirements conflict;
- a safety-critical assumption is unresolved;
- a benchmark requires spending money or changing persistent device state;
- the agent cannot cite evidence for an important factual recommendation;
- the work would expand beyond M0.

### 4.2 Required artifact footer

Each M0 artifact ends with:

```markdown
## Artifact status

- Author/agent:
- Reviewer:
- Status: Draft | Owner review | Accepted | Superseded
- Inputs used:
- Assumptions:
- Open questions:
- Acceptance evidence:
- Last updated:
```

---

## 5. Artifact map

Agents should create these artifacts under `docs/m0/`. An artifact can be split later if it becomes unwieldy.

| Artifact | Purpose | Primary task IDs |
|---|---|---|
| `00_M0_STATUS.md` | Live dashboard, dependencies, evidence, blockers | M0-01, M0-45 |
| `01_OWNER_CHARTER.md` | Mission, life outcomes, principles, non-goals | M0-10 |
| `02_WORKFLOW_CATALOG.md` | Ten candidates, scoring, selected three, narratives | M0-12, M0-13, M0-25 |
| `03_DATA_AND_AUTONOMY_BOUNDARIES.md` | Data policy, egress, risk classes, approval rules | M0-14, M0-15 |
| `04_CURRENT_SYSTEM_INVENTORY.md` | Devices, services, data sources, dependencies | M0-11 |
| `05_BASELINE_MEASUREMENT.md` | Current-process baseline and measurement plan | M0-16 |
| `06_SYSTEM_ARCHITECTURE.md` | Components, responsibilities, flows, trust zones | M0-20, M0-21 |
| `07_THREAT_MODEL.md` | Assets, actors, threats, misuse cases, controls | M0-22 |
| `08_PRIVACY_IMPACT_ASSESSMENT.md` | Purpose, minimization, retention, rights, residual risks | M0-23 |
| `09_CONTRACT_DRAFTS.md` | Event, tool, action, memory, identity, policy contracts | M0-24 |
| `10_EVALUATION_PLAN.md` | Metrics, experiment rules, evaluation suites | M0-31, M0-33 |
| `11_GOLDEN_SCENARIOS.md` | At least 25 end-to-end and adversarial cases | M0-30 |
| `12_RECOVERY_PAUSE_AND_INCIDENTS.md` | Backup, restore, pause, incident, safe-failure concepts | M0-32 |
| `13_REQUIREMENTS_TRACEABILITY.md` | Requirement-to-design-to-test-to-risk mapping | M0-34 |
| `14_TECHNOLOGY_SCORECARD.md` | Options, criteria, benchmarks, recommendations | M0-40, M0-41, M0-42 |
| `15_M1_VERTICAL_SLICE_AND_BACKLOG.md` | First M1 slice and six-week backlog | M0-43, M0-44 |
| `M0_INDEPENDENT_REVIEW.md` | Findings from review independent of artifact authors | M0-46 |
| `M0_GATE_REVIEW.md` | Exit-gate evidence and owner decision | M0-47 |

---

## 6. Master status checklist

Status marks:

- `[ ]` Not started
- `[-]` In progress or blocked
- `[x]` Artifact acceptance criteria met
- Owner decisions also require an explicit `Owner accepted: YYYY-MM-DD` entry in the artifact.

### Setup and control

- [x] **M0-01 - Create the live M0 status and evidence register**
- [x] **M0-00 - Owner accepts the M0 scope and operating rules**
- [x] **M0-02 - Establish project glossary and naming consistency**

### Week 1 - Life outcomes and boundaries

- [x] **M0-10 - Define the owner charter and “better life” outcomes**
- [x] **M0-11 - Inventory current systems, devices, services, and data sources**
- [x] **M0-12 - Create and score at least ten candidate workflows**
- [x] **M0-13 - Owner selects the first three workflows**
- [x] **M0-14 - Define data collection, retention, deletion, and cloud-egress boundaries**
- [x] **M0-15 - Define autonomy and approval boundaries**
- [-] **M0-16 - Define and begin baseline measurement**

### Week 2 - Architecture, security, privacy, and contracts

- [x] **M0-20 - Define component responsibilities and non-responsibilities**
- [x] **M0-21 - Map identities, trust zones, and end-to-end data flows**
- [-] **M0-22 - Complete the initial threat model**
- [ ] **M0-23 - Complete the initial privacy impact assessment**
- [ ] **M0-24 - Draft version-zero system contracts**
- [ ] **M0-25 - Write success and failure narratives for the selected workflows**

### Week 3 - Evaluation and failure design

- [ ] **M0-30 - Write at least 25 golden and adversarial scenarios**
- [ ] **M0-31 - Define metrics, baselines, and evaluation methods**
- [ ] **M0-32 - Define backup, restore, pause, kill, and incident concepts**
- [ ] **M0-33 - Define evidence required to earn autonomy**
- [ ] **M0-34 - Create the requirements traceability matrix**

### Week 4 - Technology evidence and M1 readiness

- [ ] **M0-40 - Create the technology decision scorecard**
- [ ] **M0-41 - Run only approved, bounded PC/Pi technology experiments**
- [ ] **M0-42 - Record provisional architecture decisions and reversal triggers**
- [ ] **M0-43 - Specify the first M1 vertical slice**
- [ ] **M0-44 - Create the six-week M1 backlog**
- [ ] **M0-45 - Consolidate the M0 evidence package**
- [ ] **M0-46 - Perform an independent M0 review**
- [ ] **M0-47 - Hold the owner M0 gate review**

---

## 7. Detailed task cards

### M0-00 - Owner accepts the M0 scope and operating rules

**Accountable:** Owner  
**Agent support:** Coordinator  
**Depends on:** M0-01  
**Output:** Acceptance entry in `00_M0_STATUS.md`

Checklist:

- [ ] Owner has reviewed Sections 1-4 of this checklist.
- [ ] Owner confirms M0 is specification-first and not a production build.
- [ ] Owner confirms the 10-hour weekly budget and preferred meeting/review cadence.
- [ ] Owner identifies any additional prohibited actions for agents.
- [ ] Owner names the coordinator or accepts AI-assisted coordination.

Acceptance evidence:

- A dated owner statement accepting or amending the rules.

---

### M0-01 - Create the live M0 status and evidence register

**Accountable:** Coordinator  
**Depends on:** None  
**Output:** `docs/m0/00_M0_STATUS.md`

Checklist:

- [ ] Copy every task ID into a status table.
- [ ] Track accountable party, assigned agent, state, dependency, artifact, and review date.
- [ ] Add an evidence register linking each deliverable and gate criterion.
- [ ] Add blocker, assumption, and decision queues.
- [ ] Add human hours used and remaining; agent token usage may be recorded separately but does not replace human-effort tracking.

Acceptance evidence:

- Every task in Section 6 appears once and has an owner.
- The coordinator can identify the critical path and current blocker in under one minute.

---

### M0-02 - Establish project glossary and naming consistency

**Accountable:** Systems architect  
**Reviewer:** Coordinator  
**Depends on:** M0-00  
**Output:** Glossary section in `00_M0_STATUS.md` or `06_SYSTEM_ARCHITECTURE.md`

Checklist:

- [x] Define Agent Box, Personal Core, owner, agent, model, skill, workflow, tool, event, memory, artifact, policy, action, verification, and autonomy.
- [x] Distinguish M0 from M1 and “first milestone” from “Milestone 1.”
- [x] Identify overloaded terms and choose one canonical meaning.

Acceptance evidence:

- Terms are used consistently across the M0 package.

---

### M0-10 - Define the owner charter and “better life” outcomes

**Accountable:** Owner  
**Agent support:** Owner-interview analyst  
**Depends on:** M0-00  
**Output:** `docs/m0/01_OWNER_CHARTER.md`

Agent interview topics:

- [ ] What does a good ordinary weekday look like?
- [ ] What currently consumes avoidable time or attention?
- [ ] Which responsibilities are most often forgotten or delayed?
- [ ] Which parts of life should Osun support but never optimize autonomously?
- [ ] Which habits should be supported, and which observed habits should not be reinforced?
- [ ] What would make Osun feel intrusive, manipulative, or dependency-forming?
- [ ] What would make the project worthwhile after 6 months, 1 year, and 10 years?

Required charter content:

- [ ] Mission in the owner's language.
- [ ] Five to eight prioritized life outcomes.
- [ ] Non-goals and unacceptable outcomes.
- [ ] Initial product principles and conflict-resolution order.
- [ ] Qualitative definition of net benefit.

Acceptance evidence:

- Owner confirms the charter preserves their meaning.
- Each outcome can later be connected to an observable indicator without reducing it to a single optimization score.

---

### M0-11 - Inventory current systems, devices, services, and data sources

**Accountable:** Technology scout  
**Reviewers:** Owner, privacy analyst  
**Depends on:** M0-00  
**Output:** `docs/m0/04_CURRENT_SYSTEM_INVENTORY.md`

Checklist:

- [ ] Record Windows PC hardware, OS, storage, networking, and AI-relevant compute.
- [ ] Record Raspberry Pi model, memory, storage, OS status, networking, and power protection.
- [ ] Record Home Assistant deployment and integrations, if already present.
- [ ] List calendar, tasks, notes, email, phone ecosystem, wearables, and other candidate services.
- [ ] For each service, record ownership, authentication method, API/export availability, data sensitivity, expected rate, and offline behavior.
- [ ] Identify third-party data about other people.
- [ ] Do not collect credentials or data contents in the inventory.

Acceptance evidence:

- Every system needed by a selected workflow is present or clearly marked missing.
- Unknowns are recorded rather than guessed.

---

### M0-12 - Create and score at least ten candidate workflows

**Accountable:** Workflow analyst  
**Reviewer:** Owner-interview analyst  
**Depends on:** M0-10; M0-11 may proceed in parallel  
**Output:** Candidate section of `docs/m0/02_WORKFLOW_CATALOG.md`

For every workflow, record:

- [ ] Trigger and intended owner outcome.
- [ ] Current manual process and estimated burden.
- [ ] Required inputs and their sensitivity.
- [ ] Proposed output or external action.
- [ ] Maximum autonomy and risk class.
- [ ] Worst plausible failure.
- [ ] Offline requirement.
- [ ] Expected frequency and time saved.
- [ ] Implementation and maintenance complexity.
- [ ] Whether it generates useful learning signals.

Score each workflow from 1-5 on:

- owner value;
- frequency;
- measurability;
- low data/privacy burden;
- reversibility;
- architectural learning value;
- implementation feasibility at 10 hours/week;
- ongoing maintenance burden, reverse-scored.

Acceptance evidence:

- At least ten workflows are comparable using the same rubric.
- Scores are recommendations, not a substitute for owner judgment.

---

### M0-13 - Owner selects the first three workflows

**Accountable:** Owner  
**Agent support:** Workflow analyst  
**Depends on:** M0-12  
**Output:** Selected-workflow section of `docs/m0/02_WORKFLOW_CATALOG.md`

Checklist:

- [ ] Review scores, tradeoffs, and worst-case failures.
- [ ] Select three first-year workflows and rank them.
- [ ] Name a measurable six-month outcome for each.
- [ ] Name explicit non-scope for each.
- [ ] Select one workflow as the M1 vertical-slice candidate.

Recommended initial trio unless the owner chooses otherwise:

1. Daily planning.
2. Universal capture.
3. Daily review.

Acceptance evidence:

- Dated owner approval.
- All three workflows have measurable owner outcomes and bounded data requirements.

---

### M0-14 - Define data collection, retention, deletion, and cloud-egress boundaries

**Accountable:** Owner  
**Agent support:** Privacy analyst  
**Depends on:** M0-10, M0-11, M0-13  
**Output:** Data section of `docs/m0/03_DATA_AND_AUTONOMY_BOUNDARIES.md`

Checklist:

- [x] Create `never collect`, `confirmation required`, and `allowed for stated purpose` categories.
- [x] Classify each proposed source as public, personal, sensitive, or restricted.
- [x] Record purpose, subject, collection mode, minimum fields, retention, deletion, export, pause, and allowed uses.
- [x] Define whether each class may be sent to a cloud model.
- [x] Define redaction and minimum-context rules.
- [x] Define handling of data concerning other people.
- [x] Define whether raw source, derived memory, or both may persist.
- [x] Record unresolved legal or ethical questions without making legal claims.

Acceptance evidence:

- Every selected-workflow data source has a complete policy row.
- No data source is authorized merely because it is technically accessible.
- Dated owner approval of prohibited and cloud-egress categories.

---

### M0-15 - Define autonomy and approval boundaries

**Accountable:** Owner  
**Agent support:** Security analyst, workflow analyst  
**Depends on:** M0-13  
**Output:** Autonomy section of `docs/m0/03_DATA_AND_AUTONOMY_BOUNDARIES.md`

Checklist:

- [x] Confirm risk classes R0 through R4.
- [x] Classify every action in the selected workflows.
- [x] Define preview, approval, expiration, verification, and undo requirements.
- [x] Identify actions that always require approval.
- [x] Identify actions prohibited during year one.
- [x] Define global pause and per-workflow disable behavior.
- [x] State that autonomy is earned independently by workflow/domain.

Acceptance evidence:

- Every external action maps to a risk class and approval rule.
- Dated owner acceptance of the initial autonomy policy.

---

### M0-16 - Define and begin baseline measurement

**Accountable:** Evaluation scientist  
**Reviewer:** Owner  
**Depends on:** M0-13  
**Output:** `docs/m0/05_BASELINE_MEASUREMENT.md`

Checklist:

- [x] Define the current manual process for each selected workflow.
- [x] Select only metrics that will inform a design or success decision.
- [x] Include time, completion, error/rework, attention burden, and owner-rated usefulness where appropriate.
- [x] Define a low-burden seven-day baseline collection method.
- [x] Record confounders such as unusual travel or workload.
- [x] Avoid collecting unrelated personal content.

Acceptance evidence:

- Baseline method takes no more than five minutes per day unless the owner approves more.
- Start and end dates are recorded.
- Missing days remain missing; agents do not invent measurements.

---

### M0-20 - Define component responsibilities and non-responsibilities

**Accountable:** Systems architect  
**Reviewer:** Independent architect or coordinator  
**Depends on:** M0-13 through M0-15  
**Output:** Component section of `docs/m0/06_SYSTEM_ARCHITECTURE.md`

Checklist:

- [x] Define owner interfaces, Agent Box, Personal Core, identity/policy plane, execution plane, memory/data plane, and operations plane.
- [x] Define Home Assistant and external services as peer systems.
- [x] Assign one responsibility owner for every capability.
- [x] Document what each component must not own.
- [x] Show replaceable model, store, transport, and hardware boundaries.
- [x] State which functions must work offline.

Acceptance evidence:

- No responsibility has two conflicting authorities.
- No model component has direct unrestricted access to secrets, tools, or all memory.
- The owner can explain the component map in plain language.

---

### M0-21 - Map identities, trust zones, and end-to-end data flows

**Accountable:** Systems architect  
**Reviewers:** Security and privacy analysts  
**Depends on:** M0-20  
**Output:** Trust and flow sections of `docs/m0/06_SYSTEM_ARCHITECTURE.md`

Checklist:

- [x] Identify owner, service, agent, workflow, device, and integration identities.
- [x] Draw trust boundaries across PC, Pi, Home Assistant, local network, and external services.
- [x] Trace all three workflows from trigger to verified outcome and possible learning.
- [x] Label every boundary crossing with authentication, authorization, encryption, validation, and audit expectations.
- [x] Label data sensitivity and egress.
- [x] Identify stale, duplicated, missing, malicious, and out-of-order input behavior.

Acceptance evidence:

- Every selected workflow has a complete request-to-memory trace.
- Every boundary crossing has a named control or an explicit unresolved risk.

---

### M0-22 - Complete the initial threat model

**Accountable:** Security analyst  
**Reviewer:** Systems architect  
**Depends on:** M0-21  
**Output:** `docs/m0/07_THREAT_MODEL.md`

Checklist:

- [x] Identify assets, threat actors, entry points, trust boundaries, and high-impact outcomes.
- [x] Cover prompt injection, tool abuse, credential exposure, memory poisoning, compromised nodes, replay/duplication, lateral movement, unsafe chaining, supply-chain compromise, and data loss.
- [x] Write at least one abuse case for each selected workflow.
- [x] Map preventive, detective, responsive, and recovery controls.
- [x] Score likelihood and impact using a simple documented scale.
- [x] Record residual risks requiring owner acceptance.
- [x] Distinguish M0 design controls from M1 implementation controls.

Acceptance evidence:

- Every high or critical risk has a planned control, explicit acceptance request, or scope prohibition.
- Threats link to golden scenarios and requirements.

---

### M0-23 - Complete the initial privacy impact assessment

**Accountable:** Privacy analyst  
**Reviewer:** Owner  
**Depends on:** M0-14, M0-21  
**Output:** `docs/m0/08_PRIVACY_IMPACT_ASSESSMENT.md`

Checklist:

- [ ] State purpose and necessity for every data flow.
- [ ] Check minimization, sensitivity, retention, access, egress, correction, deletion, export, and pause.
- [ ] Identify affected people, including non-users.
- [ ] Analyze inference risks, function creep, chilling effects, dependency, and future household leakage.
- [ ] Define privacy tests and deletion verification expectations.
- [ ] Record residual risks and required owner decisions.

Acceptance evidence:

- Every selected data flow appears in both architecture and privacy assessment.
- Owner accepts residual privacy risks or narrows the workflow.

---

### M0-24 - Draft version-zero system contracts

**Accountable:** Systems architect  
**Reviewers:** Security analyst, evaluation scientist  
**Depends on:** M0-20 through M0-23  
**Output:** `docs/m0/09_CONTRACT_DRAFTS.md`

Draft conceptual contracts for:

- [ ] Event envelope.
- [ ] Tool definition and invocation.
- [ ] Action ledger and verification result.
- [ ] Memory observation, fact, preference, goal, procedure, and prediction.
- [ ] Identity and delegated authority.
- [ ] Policy decision and approval receipt.
- [ ] Workflow state and terminal outcome.
- [ ] Evaluation case and result.

Each contract includes:

- [ ] Versioning and compatibility rule.
- [ ] Required identifiers, times, provenance, sensitivity, and correlation.
- [ ] Validation and failure behavior.
- [ ] Example using synthetic data.
- [ ] Security/privacy fields and data-retention reference.

Acceptance evidence:

- The three workflow narratives can be represented without inventing untyped side channels.
- No contract embeds credentials or assumes model output is trusted.

---

### M0-25 - Write success and failure narratives for the selected workflows

**Accountable:** Workflow analyst  
**Reviewers:** Owner, systems architect, security analyst  
**Depends on:** M0-13, M0-20 through M0-24  
**Output:** Narrative section of `docs/m0/02_WORKFLOW_CATALOG.md`

For each workflow, write:

- [ ] Normal request-to-outcome story.
- [ ] Owner denial/cancellation story.
- [ ] Model unavailable story.
- [ ] External service unavailable or stale story.
- [ ] Invalid/malicious external content story.
- [ ] Restart/duplicate-event story.
- [ ] Incorrect-memory story.
- [ ] Audit, correction, and recovery story.

Acceptance evidence:

- Each narrative names the responsible component at every step.
- Failure stories end in a safe, visible state.

---

### M0-30 - Write at least 25 golden and adversarial scenarios

**Accountable:** Evaluation scientist  
**Reviewers:** Security analyst, workflow analyst  
**Depends on:** M0-25  
**Output:** `docs/m0/11_GOLDEN_SCENARIOS.md`

Minimum coverage:

- [ ] Three normal cases per selected workflow (9).
- [ ] Owner edits, denies, cancels, expires, and undoes actions (5).
- [ ] Prompt injection or malicious content (2).
- [ ] Duplicate/replayed or out-of-order events (2).
- [ ] Internet, model, Pi, or external-service failure (4).
- [ ] Stale or conflicting source data (2).
- [ ] Incorrect, missing, or prohibited memory with correct abstention (3).
- [ ] Unauthorized actor or insufficient scope (2).
- [ ] Backup/restore or pause scenario (1).

More than 25 scenarios are expected if the listed categories produce 30 or more useful cases.

Each scenario contains:

- [ ] ID, purpose, preconditions, input, expected trace, expected policy, expected outcome, prohibited outcome, and evidence.

Acceptance evidence:

- All M0 gate risks and all selected-workflow actions appear in at least one scenario.
- Expected outcomes do not depend on vague wording such as “works correctly.”

---

### M0-31 - Define metrics, baselines, and evaluation methods

**Accountable:** Evaluation scientist  
**Reviewers:** Owner, coordinator  
**Depends on:** M0-16, M0-30  
**Output:** `docs/m0/10_EVALUATION_PLAN.md`

Checklist:

- [ ] Define utility, quality, safety, trust, attention, reliability, privacy, maintainability, and cost measures.
- [ ] Link every metric to a decision.
- [ ] Define collection method, denominator, frequency, and interpretation.
- [ ] Separate offline replay, shadow, canary, and live evidence.
- [ ] Define fixed golden suites and evolving personal evaluation sets.
- [ ] Define how uncertainty and missing data are reported.
- [ ] Prohibit changing success metrics after results without a recorded decision.

Acceptance evidence:

- Each selected workflow has one primary outcome metric and guardrail metrics.
- Metrics are feasible for one owner and do not create more burden than the workflow saves.

---

### M0-32 - Define backup, restore, pause, kill, and incident concepts

**Accountable:** Security/operations analyst  
**Reviewer:** Systems architect  
**Depends on:** M0-20 through M0-24  
**Output:** `docs/m0/12_RECOVERY_PAUSE_AND_INCIDENTS.md`

Checklist:

- [ ] Identify data/configuration/model artifacts requiring backup.
- [ ] Define initial RPO and RTO targets and their assumptions.
- [ ] Define encrypted local and offsite backup concept and key-recovery risk.
- [ ] Define restore verification rather than backup-job success alone.
- [ ] Define global pause, per-workflow disable, credential revocation, and safe reduced mode.
- [ ] Define severity levels, owner notification, evidence preservation, and recovery ownership.
- [ ] Cover power loss, disk failure, corrupt data, unavailable network, and compromised node.

Acceptance evidence:

- Every persistent data class has an intended backup or explicit no-backup policy.
- Pause/kill does not rely on the model functioning correctly.

---

### M0-33 - Define evidence required to earn autonomy

**Accountable:** Evaluation scientist  
**Reviewers:** Owner, security analyst  
**Depends on:** M0-15, M0-30, M0-31  
**Output:** Autonomy section of `docs/m0/10_EVALUATION_PLAN.md`

Checklist:

- [ ] Define eligibility to move from observe to suggest, prepare, reversible action, and consequential action.
- [ ] Require minimum scenario coverage, shadow duration, error limits, verification, undo, and owner approval.
- [ ] Define regression conditions that automatically reduce autonomy.
- [ ] Keep autonomy separate by workflow, context, and action.
- [ ] State actions that cannot earn autonomy under the current roadmap.

Acceptance evidence:

- No autonomy increase can occur solely because a model reports high confidence.
- Owner gives dated acceptance of the autonomy-evidence policy.

---

### M0-34 - Create the requirements traceability matrix

**Accountable:** Coordinator  
**Reviewers:** Systems architect, evaluation scientist  
**Depends on:** M0-20 through M0-33  
**Output:** `docs/m0/13_REQUIREMENTS_TRACEABILITY.md`

Minimum columns:

- [ ] Requirement ID and statement.
- [ ] Source/owner decision.
- [ ] Priority and milestone.
- [ ] Architecture component/contract.
- [ ] Threat/privacy risk.
- [ ] Verification scenario and metric.
- [ ] Status and evidence.

Acceptance evidence:

- Every M0 deliverable and exit criterion maps to evidence.
- Every high/critical threat and privacy risk maps to a requirement and scenario.
- Orphan requirements, designs, and tests are listed for resolution.

---

### M0-40 - Create the technology decision scorecard

**Accountable:** Technology scout  
**Reviewers:** Systems architect, operations analyst  
**Depends on:** M0-20, M0-24, M0-31, M0-32  
**Output:** Scorecard section of `docs/m0/14_TECHNOLOGY_SCORECARD.md`

Decision categories:

- [ ] Primary language/runtime.
- [ ] Initial durable event/relational store.
- [ ] Event transport: in-process/database first versus broker.
- [ ] Durable workflow approach.
- [ ] API and contract validation.
- [ ] Identity and secrets approach.
- [ ] Deployment/package method for Windows and Pi.
- [ ] Testing, observability, backup, and migration tooling.

Score each candidate on:

- functional fit;
- one-person operating burden;
- Windows and Raspberry Pi support;
- measured performance/resource use;
- offline operation;
- security/update record;
- typing, testing, and observability;
- data portability and migration;
- project health and licensing;
- replacement cost.

Acceptance evidence:

- Criteria weights are approved before benchmark results are used.
- Recommendations include runner-up, risks, and reversal triggers.

---

### M0-41 - Run only approved, bounded PC/Pi technology experiments

**Accountable:** Technology scout  
**Reviewers:** Owner, systems architect  
**Depends on:** M0-40 and explicit owner approval  
**Output:** Benchmark section of `docs/m0/14_TECHNOLOGY_SCORECARD.md`

Checklist:

- [ ] Write hypotheses, commands, resource limits, expected writes, cleanup, and stop conditions before running.
- [ ] Use synthetic data.
- [ ] Benchmark only decisions that cannot be made from documentation.
- [ ] Record actual PC/Pi hardware and software environment.
- [ ] Measure startup, idle resources, latency, durability/restart behavior, and operational complexity where relevant.
- [ ] Do not install persistent services or expose ports without separate approval.
- [ ] Record raw results, failures, and uncertainty.

Acceptance evidence:

- Experiments are reproducible and remain inside the approved scope.
- Results answer a named decision question.
- Temporary state is accounted for; destructive cleanup requires owner authorization.

---

### M0-42 - Record provisional architecture decisions and reversal triggers

**Accountable:** Systems architect  
**Approver:** Owner  
**Depends on:** M0-40, M0-41 where needed  
**Output:** Decision section of `docs/m0/14_TECHNOLOGY_SCORECARD.md` and updates to the master-plan decision log

For each decision:

- [ ] Context and decision question.
- [ ] Options and evidence.
- [ ] Accepted choice and why.
- [ ] Consequences and known risks.
- [ ] Reversal trigger and migration path.
- [ ] Status: proposed until owner-approved.

Acceptance evidence:

- All technology needed for the M1 slice is decided or explicitly deferred.
- Decisions are replaceable and do not silently become ten-year commitments.

---

### M0-43 - Specify the first M1 vertical slice

**Accountable:** Systems architect  
**Reviewers:** Owner, coordinator, evaluation scientist  
**Depends on:** M0-25, M0-30 through M0-42  
**Output:** Vertical-slice section of `docs/m0/15_M1_VERTICAL_SLICE_AND_BACKLOG.md`

The slice must include:

- [ ] One owner-visible request.
- [ ] Authentication or a clearly bounded initial identity mechanism.
- [ ] Typed event and correlation ID.
- [ ] One simple planning/routing decision.
- [ ] Policy evaluation.
- [ ] One R0 tool and one mock or safe R2 path.
- [ ] Verification and terminal outcome.
- [ ] Audit visibility.
- [ ] Restart/idempotency behavior.
- [ ] Automated end-to-end test using synthetic data.

Also define:

- [ ] In-scope and non-scope.
- [ ] Acceptance scenarios and metrics.
- [ ] Data and threat controls.
- [ ] Rollback/recovery.
- [ ] Human-hour estimate with uncertainty.

Acceptance evidence:

- Estimated implementation fits within four weeks at 10 owner hours/week.
- No selected feature is required only for a distant milestone.
- The slice exercises the architectural backbone rather than creating a disposable demo.

---

### M0-44 - Create the six-week M1 backlog

**Accountable:** Coordinator  
**Reviewers:** Owner, systems architect  
**Depends on:** M0-43  
**Output:** Backlog section of `docs/m0/15_M1_VERTICAL_SLICE_AND_BACKLOG.md`

Checklist:

- [ ] Break the vertical slice into work items no larger than 5-10 owner hours.
- [ ] Give each item an outcome, dependencies, definition of ready, definition of done, tests, risks, and rollback.
- [ ] Separate owner review time from AI generation time.
- [ ] Reserve at least 25% of the six weeks for testing, documentation, security, and consolidation.
- [ ] Keep work-in-progress limit at two.
- [ ] Identify the critical path and optional stretch work.

Acceptance evidence:

- The first two tasks are ready to assign.
- Removing all stretch work still produces a valid M1 vertical slice.

---

### M0-45 - Consolidate the M0 evidence package

**Accountable:** Coordinator  
**Depends on:** M0-10 through M0-44  
**Output:** Updated `docs/m0/00_M0_STATUS.md`

Checklist:

- [ ] Verify every artifact exists and includes its footer.
- [ ] Resolve or cross-link duplicate definitions.
- [ ] Ensure owner decisions are dated and not inferred.
- [ ] Update the traceability matrix and evidence register.
- [ ] List unresolved decisions, accepted residual risks, and deferred work.
- [ ] Confirm no artifact contains secrets or unnecessary personal data.
- [ ] Record total owner hours and maintenance implications.

Acceptance evidence:

- All links resolve locally.
- No high/critical blocker is hidden in prose.
- The package can be handed to a new agent without relying on chat history.

---

### M0-46 - Perform an independent M0 review

**Accountable:** Independent reviewer who did not author the majority of the package  
**Depends on:** M0-45  
**Output:** `docs/m0/M0_INDEPENDENT_REVIEW.md`

Review lenses:

- [ ] Mission and scope consistency.
- [ ] Feasibility at 10 owner hours/week.
- [ ] Missing trust boundaries or confused authority.
- [ ] Security and prompt-injection exposure.
- [ ] Privacy minimization and third-person impact.
- [ ] Contract completeness and replaceability.
- [ ] Testability and measurable success.
- [ ] Backup, restore, pause, and incident viability.
- [ ] Hidden vendor/hardware lock-in.
- [ ] Premature complexity or distant-milestone leakage.

Each finding includes severity, evidence, consequence, and recommended resolution.

Acceptance evidence:

- All blocking findings are resolved or explicitly accepted by the owner.
- Reviewer states whether M0 is ready for gate review.

---

### M0-47 - Hold the owner M0 gate review

**Accountable and approver:** Owner  
**Facilitator:** Coordinator  
**Depends on:** M0-46  
**Output:** `docs/m0/M0_GATE_REVIEW.md`

The owner chooses one outcome:

- **PASS:** M0 is verified and M1 may begin.
- **CONDITIONAL PASS:** Only named low-risk conditions remain, each with owner and deadline.
- **REWORK:** M0 remains active; blocking evidence is missing.
- **STOP/PIVOT:** The project or selected workflows should change before implementation.

Acceptance evidence:

- Every gate in Section 9 is answered with a link, not only “yes.”
- Residual risks and conditions are explicit.
- Owner decision and date are recorded.
- The master plan current-status and decision-log sections are updated.

---

## 8. Recommended dispatch waves

Agents may work in parallel only when inputs are stable enough to avoid rework.

### Wave A - Owner discovery and inventory

Start immediately:

- M0-01 status/evidence register.

After M0-00 owner acceptance:

- M0-02 glossary.
- M0-10 owner charter.
- M0-11 current-system inventory.

Then complete M0-12 through M0-16. M0-13, M0-14, and M0-15 require owner decisions and are the first critical-path gate.

### Wave B - Architecture and risk

Start after the selected workflows and boundaries are stable:

- Systems architect: M0-20, M0-21, then M0-24.
- Security analyst: begin M0-22 after the first data-flow draft.
- Privacy analyst: begin M0-23 after the first data-flow draft.
- Workflow analyst: M0-25 after component boundaries are stable.

Security, privacy, and architecture agents should exchange findings but retain separate artifacts and reviewers.

### Wave C - Evaluation and resilience

Start after workflow narratives exist:

- Evaluation scientist: M0-30, M0-31, M0-33.
- Security/operations analyst: M0-32.
- Coordinator: M0-34 after requirements, risks, and scenarios stabilize.

### Wave D - Technology and M1 readiness

Start only when required contracts and evaluation needs are known:

- Technology scout: M0-40, then owner-approved M0-41.
- Systems architect and owner: M0-42.
- Systems architect/evaluation scientist: M0-43.
- Coordinator: M0-44 and M0-45.
- Independent reviewer: M0-46.
- Owner: M0-47.

---

## 9. M0 completion gate

M0 cannot pass until every item below has linked evidence.

### Mission and workflow gate

- [ ] The owner has accepted the mission, non-goals, principles, and first-year scope.
- [ ] At least ten candidate workflows were considered using a consistent rubric.
- [ ] Three workflows were selected and ranked by the owner.
- [ ] Each selected workflow has a measurable owner outcome, data boundary, risk class, and non-scope.
- [ ] A seven-day baseline was completed or a documented reason and replacement baseline exists.

### Data, privacy, and autonomy gate

- [ ] Every proposed data source has purpose, sensitivity, minimum fields, retention, pause, deletion, export, and egress policy.
- [ ] Prohibited and confirmation-only data categories are owner-approved.
- [ ] Data concerning other people is identified and minimized.
- [ ] Every external action maps to a risk class, approval rule, verification method, and undo/compensation rule where applicable.
- [ ] High and critical residual privacy risks are resolved, prohibited, or owner-accepted.

### Architecture and contract gate

- [ ] The owner can explain the PC, Pi, Home Assistant, policy, execution, memory, and operations boundaries in plain language.
- [ ] Every selected workflow has a complete request-to-verified-outcome-to-memory flow.
- [ ] Every trust-boundary crossing has a named control or explicit unresolved risk.
- [ ] Version-zero event, tool, action, memory, identity, policy, workflow, and evaluation contracts exist.
- [ ] Components have one authority and documented non-responsibilities.

### Security and resilience gate

- [ ] Initial threat model and privacy impact assessment are reviewed.
- [ ] Every high/critical threat has a control, prohibition, or explicit owner risk decision.
- [ ] Prompt injection, replay, memory poisoning, credential exposure, compromised node, and unsafe tool chaining are covered.
- [ ] Backup, restore, pause, kill, incident, and safe-reduced-mode concepts exist.
- [ ] M0 artifacts contain no credentials or unnecessary sensitive data.

### Evaluation gate

- [ ] At least 25 precise end-to-end scenarios exist.
- [ ] Scenarios cover normal operation, refusals, edits, failures, malicious content, duplicated events, bad memory, unauthorized actors, and recovery.
- [ ] Utility, quality, safety, trust, attention, reliability, privacy, maintainability, and cost metrics are defined where relevant.
- [ ] Each metric informs a named decision and has a feasible collection method.
- [ ] Requirements, risks, design elements, and scenarios are traceable.

### M1 readiness gate

- [ ] Technology scorecard criteria were approved before final recommendation.
- [ ] Any benchmark is reproducible, bounded, and based on actual target hardware.
- [ ] Required provisional technology decisions include reversal triggers.
- [ ] The M1 vertical slice exercises the full backbone and fits within 40 owner hours.
- [ ] The six-week backlog reserves at least 25% for testing, documentation, security, and consolidation.
- [ ] All blocking independent-review findings are resolved or owner-accepted.
- [ ] All unresolved decisions are visible and none hides a safety-critical assumption.

### Final owner decision

- [ ] `M0_GATE_REVIEW.md` records PASS, CONDITIONAL PASS, REWORK, or STOP/PIVOT.
- [ ] The master plan is updated to reflect the decision.
- [ ] M1 work does not begin before the owner authorizes it.

---

## 10. Copy-ready agent task packet

Use this template when assigning any task. Fill every bracketed field.

```markdown
# Osun M0 Agent Assignment: [TASK ID and title]

You are acting as the [ROLE] for Osun milestone M0.

## Required context

Read completely before working:

1. `docs/OSUN_MASTER_PLAN.md`
2. `docs/M0_AGENT_CHECKLIST.md`
3. [LIST SPECIFIC UPSTREAM ARTIFACTS]

## Objective

[ONE CONCRETE OUTCOME]

## Scope

You may:

- [AUTHORIZED ACTION]

You may not:

- Build or deploy the production runtime.
- Collect real personal data unless explicitly supplied and authorized.
- Make owner-only values, privacy, autonomy, budget, or gate decisions.
- Expand beyond this task without approval.

## Deliverable

Create or update: `[EXACT PATH]`

The deliverable must contain:

- [REQUIRED CONTENT]
- Assumptions, alternatives, uncertainty, and open questions.
- Primary/authoritative source links for material external claims.
- The required M0 artifact-status footer.

## Acceptance criteria

- [TESTABLE CRITERION]
- [TESTABLE CRITERION]

## Dependencies

- [TASK OR ARTIFACT]

## Stop and escalate when

- An undisclosed owner preference is required.
- Two accepted requirements conflict.
- Work would collect data, install software, create external state, spend money, or exceed M0.
- A high-impact claim cannot be supported.

## Completion response

Return:

1. Artifact path.
2. Concise summary of conclusions.
3. Acceptance evidence.
4. Open decisions requiring the owner.
5. Risks or downstream tasks discovered.
```

---

## 11. Coordinator handoff format

At each owner review, the coordinator should provide only:

```markdown
## M0 status - [DATE]

- Gate progress: [X/Y complete]
- Human hours: [used / 40]
- Current critical-path task:
- Completed since last review:
- Decisions needed from owner:
- Blocking risks:
- Next three assignments:
- Scope or schedule change proposed:
```

Unchanged background detail remains in the status artifact rather than consuming owner attention.

---

## 12. Current checklist status

**Milestone state:** In progress; baseline active, M0-21 accepted, M0-22 threat model in review \
**Current critical path:** M0-22 -> M0-23 -> M0-24 -> M0-25 -> M0-30 -> M0-40 -> M0-43 -> M0-46 -> M0-47; M0-16 runs alongside \
**Next owner action:** Complete private baseline cards and approve or amend Section 12 of `m0/07_THREAT_MODEL.md`. \
**Next agent action:** Close M0-22 after review, then open M0-23 within the WIP limit.
