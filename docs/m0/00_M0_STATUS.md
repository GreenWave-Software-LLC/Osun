# Osun M0 Status and Evidence Register

**Milestone:** M0 - Charter, requirements, and evidence plan \
**Milestone state:** In progress \
**Target window:** Four weeks from owner acceptance of M0-00 \
**Human-owner budget:** 40 hours \
**Human hours reported:** 0.0 \
**Human hours remaining:** 40.0 \
**Last updated:** 2026-07-26 \
**Coordinator:** AI-assisted coordination approved \
**Current critical-path task:** M0-23 - Initial privacy impact assessment; M0-16 baseline runs concurrently \
**Primary references:** [M0 Agent Execution Checklist](../M0_AGENT_CHECKLIST.md) and [Living Master Plan](../OSUN_MASTER_PLAN.md)

---

## 1. Executive status

The owner charter, workflows, data/autonomy policies, architecture/flows, and thirty-risk threat model are accepted. The baseline is active, and the privacy assessment now evaluates every selected flow, affected people, twenty privacy risks, deletion/export verification, and ten residual-risk dispositions.

### Current state

- **Completed:** M0-00, M0-01, M0-02, M0-10, M0-11, M0-12, M0-13, M0-14, M0-15, M0-20, M0-21, and M0-22.
- **In progress:** M0-16 baseline measurement and M0-23 privacy impact assessment.
- **Approved ranking:** WF-01 Daily Consistency Plan, WF-02 Weekly Health Plan, WF-03 Calorie Capture and Nutrition Review.
- **Current input dependency:** Owner completes the private baseline and approves or amends the M0-23 residual privacy treatment plan.
- **Production build authorization:** Not granted; M0 remains specification-first.

### Critical path

```text
M0-01 -> M0-00 -> M0-10 -> M0-12 -> M0-13
-> M0-14/M0-15 -> M0-20 -> M0-21 -> M0-22/M0-23 -> M0-24 -> M0-25 -> M0-30
-> M0-40 -> M0-43 -> M0-46 -> M0-47
```

### Next three assignments

1. **Owner:** Complete the private seven-day baseline cards from 2026-07-27 through 2026-08-02.
2. **Owner:** Approve or amend the ten privacy dispositions in Section 13 of `08_PRIVACY_IMPACT_ASSESSMENT.md`.
3. **AI coordinator:** Close M0-23 after review, then open M0-24 while M0-16 remains active.

---

## 2. Task register

Statuses: `Not started`, `In progress`, `Blocked`, `Agent complete`, `Owner accepted`, or `Superseded`.

| Task | Description | Accountable | Assigned | Depends on | Status | Evidence/artifact | Review date |
|---|---|---|---|---|---|---|---|
| M0-01 | Create live status and evidence register | Coordinator | AI coordinator | None | Agent complete | This file | 2026-07-25 |
| M0-00 | Accept M0 scope and operating rules | Owner | Owner | M0-01 | Owner accepted | Section 7.1 | 2026-07-25 |
| M0-02 | Establish glossary and naming | Systems architect | Primary AI systems architect | M0-00 | Agent complete | `06_SYSTEM_ARCHITECTURE.md` | 2026-07-26 |
| M0-10 | Define owner charter and life outcomes | Owner | Owner + primary AI interview analyst | M0-00 | Owner accepted | `01_OWNER_CHARTER.md` | 2026-07-25 |
| M0-11 | Inventory systems, devices, services, and sources | Technology scout | Primary AI technology scout | M0-00 | Agent complete | `04_CURRENT_SYSTEM_INVENTORY.md` | 2026-07-25 |
| M0-12 | Create and score ten candidate workflows | Workflow analyst | Primary AI workflow analyst | M0-10 | Owner accepted | `02_WORKFLOW_CATALOG.md` | 2026-07-25 |
| M0-13 | Select first three workflows | Owner | Owner | M0-12 | Owner accepted | `02_WORKFLOW_CATALOG.md` | 2026-07-26 |
| M0-14 | Define data and cloud-egress boundaries | Owner | Owner + primary AI privacy analyst | M0-10, M0-11, M0-13 | Owner accepted | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` | 2026-07-26 |
| M0-15 | Define autonomy and approval boundaries | Owner | Owner + primary AI security/workflow analyst | M0-13 | Owner accepted | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` | 2026-07-26 |
| M0-16 | Define and begin baseline measurement | Evaluation scientist | Primary AI evaluation scientist + owner | M0-13 | In progress; collection authorized | `05_BASELINE_MEASUREMENT.md` | End-of-week review after 2026-08-02 |
| M0-20 | Define component responsibilities | Systems architect | Primary AI systems architect | M0-13, M0-14, M0-15 | Owner accepted | `06_SYSTEM_ARCHITECTURE.md` | 2026-07-26 |
| M0-21 | Map identities, trust zones, and flows | Systems architect | Primary AI systems architect | M0-20 | Owner accepted | `06_SYSTEM_ARCHITECTURE.md` | 2026-07-26 |
| M0-22 | Complete threat model | Security analyst | Primary AI security analyst | M0-21 | Owner accepted | `07_THREAT_MODEL.md` | 2026-07-26 |
| M0-23 | Complete privacy impact assessment | Privacy analyst | Primary AI privacy analyst | M0-14, M0-21 | In progress; agent draft complete | `08_PRIVACY_IMPACT_ASSESSMENT.md` | Pending owner review |
| M0-24 | Draft version-zero contracts | Systems architect | Unassigned | M0-20, M0-21, M0-22, M0-23 | Not started | `09_CONTRACT_DRAFTS.md` | Pending |
| M0-25 | Write success and failure narratives | Workflow analyst | Unassigned | M0-13, M0-20, M0-21, M0-22, M0-23, M0-24 | Not started | `02_WORKFLOW_CATALOG.md` | Pending |
| M0-30 | Write golden and adversarial scenarios | Evaluation scientist | Unassigned | M0-25 | Not started | `11_GOLDEN_SCENARIOS.md` | Pending |
| M0-31 | Define metrics, baselines, and evaluation | Evaluation scientist | Unassigned | M0-16, M0-30 | Not started | `10_EVALUATION_PLAN.md` | Pending |
| M0-32 | Define recovery, pause, and incidents | Security/operations analyst | Unassigned | M0-20, M0-21, M0-22, M0-23, M0-24 | Not started | `12_RECOVERY_PAUSE_AND_INCIDENTS.md` | Pending |
| M0-33 | Define evidence required for autonomy | Evaluation scientist | Unassigned | M0-15, M0-30, M0-31 | Not started | `10_EVALUATION_PLAN.md` | Pending |
| M0-34 | Create requirements traceability | Coordinator | AI coordinator | M0-20 through M0-33 | Not started | `13_REQUIREMENTS_TRACEABILITY.md` | Pending |
| M0-40 | Create technology decision scorecard | Technology scout | Unassigned | M0-20, M0-24, M0-31, M0-32 | Not started | `14_TECHNOLOGY_SCORECARD.md` | Pending |
| M0-41 | Run owner-approved bounded experiments | Technology scout | Unassigned | M0-40, owner approval | Not started | `14_TECHNOLOGY_SCORECARD.md` | Pending |
| M0-42 | Record provisional architecture decisions | Systems architect | Unassigned | M0-40, M0-41 if required | Not started | `14_TECHNOLOGY_SCORECARD.md` | Pending |
| M0-43 | Specify first M1 vertical slice | Systems architect | Unassigned | M0-25, M0-30 through M0-42 | Not started | `15_M1_VERTICAL_SLICE_AND_BACKLOG.md` | Pending |
| M0-44 | Create six-week M1 backlog | Coordinator | AI coordinator | M0-43 | Not started | `15_M1_VERTICAL_SLICE_AND_BACKLOG.md` | Pending |
| M0-45 | Consolidate M0 evidence package | Coordinator | AI coordinator | M0-10 through M0-44 | Not started | This file | Pending |
| M0-46 | Perform independent review | Independent reviewer | Unassigned | M0-45 | Not started | `M0_INDEPENDENT_REVIEW.md` | Pending |
| M0-47 | Hold owner M0 gate review | Owner | Owner | M0-46 | Not started | `M0_GATE_REVIEW.md` | Pending |

### Task-register verification

- Expected task count: 29.
- Registered task count: 29.
- Duplicate task IDs: 0.
- Tasks without an accountable role: 0.
- Owner-decision tasks: M0-00, M0-10, M0-13, M0-14, M0-15, M0-22/M0-23 residual-risk dispositions, M0-33 approval, M0-41 authorization, M0-42 approval, and M0-47.

---

## 3. Artifact register

| Artifact | Responsible role | Status | Required by | Evidence notes |
|---|---|---|---|---|
| `00_M0_STATUS.md` | Coordinator | Agent complete | M0-01, M0-45 | Created 2026-07-25 |
| `01_OWNER_CHARTER.md` | Owner + interview analyst | Accepted | M0-10 | Accepted 2026-07-25 |
| `02_WORKFLOW_CATALOG.md` | Workflow analyst | Accepted for M0-12/M0-13 | M0-12, M0-13, M0-25 | Ranked trio and detailed boundaries approved; M0-25 remains |
| `03_DATA_AND_AUTONOMY_BOUNDARIES.md` | Owner + privacy/security analysts | Accepted | M0-14, M0-15 | All recommendations accepted 2026-07-26 |
| `04_CURRENT_SYSTEM_INVENTORY.md` | Technology scout | Agent complete | M0-11 | Selected integration paths validated at M0 precision |
| `05_BASELINE_MEASUREMENT.md` | Evaluation scientist | Active | M0-16 | Private seven-day window authorized; no sensitive observations in Git/OneDrive |
| `06_SYSTEM_ARCHITECTURE.md` | Systems architect | Accepted through M0-21 | M0-02, M0-20, M0-21 | Component, identity, trust-zone, and flow model accepted |
| `07_THREAT_MODEL.md` | Security analyst | Accepted | M0-22 | All eight dispositions accepted 2026-07-26 |
| `08_PRIVACY_IMPACT_ASSESSMENT.md` | Privacy analyst | Owner review | M0-23 | Complete agent draft; Section 13 disposition approval required |
| `09_CONTRACT_DRAFTS.md` | Systems architect | Not started | M0-24 | Version-zero conceptual contracts |
| `10_EVALUATION_PLAN.md` | Evaluation scientist | Not started | M0-31, M0-33 | Metrics fixed before results |
| `11_GOLDEN_SCENARIOS.md` | Evaluation scientist | Not started | M0-30 | Minimum 25 precise scenarios |
| `12_RECOVERY_PAUSE_AND_INCIDENTS.md` | Security/operations analyst | Not started | M0-32 | Pause must not depend on model |
| `13_REQUIREMENTS_TRACEABILITY.md` | Coordinator | Not started | M0-34 | No hidden high-risk orphans |
| `14_TECHNOLOGY_SCORECARD.md` | Technology scout | Not started | M0-40, M0-41, M0-42 | Evidence before final recommendation |
| `15_M1_VERTICAL_SLICE_AND_BACKLOG.md` | Systems architect + coordinator | Not started | M0-43, M0-44 | Slice must fit within 40 owner hours |
| `M0_INDEPENDENT_REVIEW.md` | Independent reviewer | Not started | M0-46 | Reviewer independent of majority authorship |
| `M0_GATE_REVIEW.md` | Owner + coordinator | Not started | M0-47 | Final owner decision |

---

## 4. Exit-gate evidence register

Each row must link to exact evidence before M0-47.

| Gate ID | Exit criterion | Planned evidence | State |
|---|---|---|---|
| G-MIS-01 | Owner accepted mission, non-goals, principles, and scope | `01_OWNER_CHARTER.md` | Evidence present |
| G-WFL-01 | Ten workflows considered consistently | `02_WORKFLOW_CATALOG.md` | Evidence present; owner accepted |
| G-WFL-02 | Three workflows selected and measurable | `02_WORKFLOW_CATALOG.md` | Evidence present; owner accepted |
| G-BAS-01 | Baseline completed or valid alternative recorded | `05_BASELINE_MEASUREMENT.md` | Collection authorized; completion pending |
| G-DAT-01 | Every source has purpose, sensitivity, retention, pause/delete/export/egress | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` | Evidence present; owner accepted |
| G-AUT-01 | Every external action has risk and approval rule | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` | Evidence present; owner accepted |
| G-ARC-01 | Owner can explain architecture and authority boundaries | `06_SYSTEM_ARCHITECTURE.md`, owner gate record | Component map present; owner accepted |
| G-FLW-01 | All three workflows trace end to end | `06_SYSTEM_ARCHITECTURE.md`, `02_WORKFLOW_CATALOG.md` | Evidence present; owner accepted |
| G-CON-01 | Version-zero contracts exist | `09_CONTRACT_DRAFTS.md` | Missing |
| G-SEC-01 | Threat model and privacy assessment reviewed | `07_THREAT_MODEL.md`, `08_PRIVACY_IMPACT_ASSESSMENT.md` | Threat model accepted; privacy assessment in review |
| G-RES-01 | Backup, restore, pause, kill, and incident concepts exist | `12_RECOVERY_PAUSE_AND_INCIDENTS.md` | Missing |
| G-EVL-01 | At least 25 precise scenarios exist | `11_GOLDEN_SCENARIOS.md` | Missing |
| G-MET-01 | Useful and feasible metrics are defined | `10_EVALUATION_PLAN.md` | Missing |
| G-TRC-01 | Requirements, risks, design, and tests are traceable | `13_REQUIREMENTS_TRACEABILITY.md` | Missing |
| G-TEC-01 | Technology recommendations have evidence and reversal triggers | `14_TECHNOLOGY_SCORECARD.md` | Missing |
| G-M1-01 | M1 vertical slice fits within 40 owner hours | `15_M1_VERTICAL_SLICE_AND_BACKLOG.md` | Missing |
| G-REV-01 | Blocking independent-review findings resolved or accepted | `M0_INDEPENDENT_REVIEW.md` | Missing |
| G-GAT-01 | Owner records final M0 decision | `M0_GATE_REVIEW.md` | Missing |

---

## 5. Human-effort register

Human time is the governing capacity constraint. AI generation time or token use may be recorded for cost analysis but does not reduce the need for human review.

| Date | Person | Task | Activity | Hours | Evidence/notes |
|---|---|---|---|---:|---|
| 2026-07-25 | Owner | Pre-M0 | Requested master plan, checklist, commit, and M0 start | 0.0 reported | Owner may replace with actual focused time |

### Budget allocation target

| Category | Planned hours | Used | Remaining |
|---|---:|---:|---:|
| Product and requirements | 12.0 | 0.0 | 12.0 |
| Architecture, security, and privacy | 10.0 | 0.0 | 10.0 |
| Evaluation and failure design | 8.0 | 0.0 | 8.0 |
| Technology evidence and M1 planning | 7.0 | 0.0 | 7.0 |
| Reviews, decisions, and consolidation | 3.0 | 0.0 | 3.0 |
| **Total** | **40.0** | **0.0** | **40.0** |

The coordinator updates this table from owner-reported focused time; it must not infer time from message timestamps.

---

## 6. Queues

### 6.1 Blockers

| ID | Blocking condition | Affected tasks | Owner | State | Resolution |
|---|---|---|---|---|---|
| B-001 | M0 operating rules not yet owner-accepted | M0-00 and all downstream work | Owner | Resolved 2026-07-25 | Accepted as written; AI coordination approved |

### 6.2 Owner decisions

| ID | Decision | Needed by | Options/status | Evidence required |
|---|---|---|---|---|
| OD-001 | Accept or amend M0 operating rules | Now | Accepted as written 2026-07-25 | Section 7.1 response |
| OD-002 | Confirm AI-assisted coordinator | M0-00 | Approved 2026-07-25 | Owner statement |
| OD-003 | Define “better life” and prioritized outcomes | M0-10 | Accepted 2026-07-25 | `01_OWNER_CHARTER.md` |
| OD-004 | Select first three workflows | M0-13 | Ranked WF-01/WF-02/WF-03 and detailed boundaries approved 2026-07-26 | `02_WORKFLOW_CATALOG.md` |
| OD-005 | Set prohibited, confirmation-only, and allowed data | M0-14 | Approved as written 2026-07-26 | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` Sections 3-8 and 11 |
| OD-006 | Set local/cloud processing rule | M0-14 | Local-first routing approved as written 2026-07-26 | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` Sections 8 and 11 |
| OD-007 | Set autonomy and always-approve actions | M0-15 | Action matrix approved as written 2026-07-26 | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` Sections 9-11 |
| OD-008 | Set initial monthly operating budget | M0-40 | Pending | Technology options and costs |
| OD-009 | Authorize any Week 4 benchmark writes/installs | M0-41 | Pending | Written experiment plan |
| OD-010 | Approve provisional M1 stack choices | M0-42 | Pending | Scorecard and benchmarks |
| OD-011 | Make final M0 gate decision | M0-47 | Pending | Complete evidence package and review |
| OD-012 | Confirm baseline window and private collection method | M0-16 | Approved 2026-07-26 | `05_BASELINE_MEASUREMENT.md` |
| OD-013 | Confirm component authority map matches owner intent | M0-20 | Approved 2026-07-26 | `06_SYSTEM_ARCHITECTURE.md` Sections 1-9 |
| OD-014 | Approve identity, trust-zone, and workflow-flow model | M0-21 | Approved 2026-07-26 | `06_SYSTEM_ARCHITECTURE.md` Sections 10-18 |
| OD-015 | Approve threat-model residual-risk dispositions and gates | M0-22 | Approved 2026-07-26 | `07_THREAT_MODEL.md` Section 12 |
| OD-016 | Approve privacy residual-risk dispositions and gates | M0-23 | Pending owner review | `08_PRIVACY_IMPACT_ASSESSMENT.md` Section 13 |

### 6.3 Assumptions

| ID | Assumption | Confidence | Validation owner | Revisit/validation point |
|---|---|---|---|---|
| AS-001 | One adult owner is the only M0 subject | Confirmed for M0 | Owner | Revisit if scope changes |
| AS-002 | Owner can provide approximately 10 focused hours/week | Confirmed planning constraint | Owner | Review weekly |
| AS-003 | Windows PC will be Agent Box | High from master plan | Technology scout | M0-11 and M0-41 |
| AS-004 | Raspberry Pi will be Personal Core | High from master plan | Technology scout | M0-11 and M0-41 |
| AS-005 | Home Assistant remains device authority | High from master plan | Owner/architect | M0-20 |
| AS-006 | M0 uses synthetic data except owner interview answers | High | Privacy analyst | Continuous |
| AS-007 | No production implementation is authorized during M0 | High | Owner | M0-00 |

### 6.4 Risks requiring early attention

| ID | Risk | Likelihood | Impact | Immediate response |
|---|---|---|---|---|
| ER-001 | Agents overproduce artifacts beyond owner review capacity | High | High | WIP limit two; coordinator summarizes decisions only |
| ER-002 | Workflow selection occurs before life outcomes are clear | Medium | High | Enforce M0-10 -> M0-12 -> M0-13 sequence |
| ER-003 | Technology preferences bias architecture prematurely | High | Medium | No scorecard until requirements/contracts exist |
| ER-004 | Real personal data enters planning artifacts unnecessarily | Medium | High | Synthetic examples and data minimization |
| ER-005 | “Start M0” is mistaken for production-build authority | Medium | High | Maintain explicit M0 scope and build-authorization status |
| ER-006 | No backup currently exists for project or target systems | High | Critical | Preserve repository history; design and test backup/restore before M1 production data |

---

## 7. Required owner actions

### 7.1 M0-00 acceptance record

The owner should respond with either:

```text
I accept the M0 scope and operating rules as written. AI-assisted coordination is approved.
```

or:

```text
I accept M0 with these changes:
- [change]
- [change]

AI-assisted coordination is approved/not approved.
```

After the response, the coordinator will:

- record the exact decision and date here;
- mark M0-00 owner-accepted in the task register and checklist;
- resolve B-001 and OD-001/OD-002;
- dispatch M0-02, M0-10, and M0-11 within the WIP limit.

### 7.2 Owner acceptance status

**Decision:** Accepted as written \
**Date:** 2026-07-25 \
**Amendments:** None \
**AI-assisted coordination:** Approved

---

## 8. Status history

| Date | Change | Evidence |
|---|---|---|
| 2026-07-25 | Master plan and M0 checklist committed as the first Osun planning commit | Git commit `c95cd08` |
| 2026-07-25 | M0-01 started and status/evidence register created | This file |
| 2026-07-25 | Owner accepted M0 scope/rules as written and approved AI-assisted coordination | Section 7.2 |
| 2026-07-25 | M0-10 and M0-11 opened; Windows Agent Box inventory completed | `01_OWNER_CHARTER.md`, `04_CURRENT_SYSTEM_INVENTORY.md` |
| 2026-07-25 | Owner Interview Round 1 and initial Pi/service inventory captured | `01_OWNER_CHARTER.md`, `04_CURRENT_SYSTEM_INVENTORY.md` |
| 2026-07-25 | Owner accepted charter mission, principles, non-goals, and consistency direction | `01_OWNER_CHARTER.md` |
| 2026-07-25 | Twelve candidate workflows cataloged and scored; M0-13 opened | `02_WORKFLOW_CATALOG.md` |
| 2026-07-25 | Owner approved ranked trio; M0-11 integration validation completed | `02_WORKFLOW_CATALOG.md`, `04_CURRENT_SYSTEM_INVENTORY.md` |
| 2026-07-26 | Owner approved selected-workflow boundaries; M0-13 completed | `02_WORKFLOW_CATALOG.md` |
| 2026-07-26 | M0-14 and M0-15 opened; data, cloud-egress, autonomy, and approval defaults drafted | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` |
| 2026-07-26 | Owner approved all M0-14/M0-15 recommendations as written | `03_DATA_AND_AUTONOMY_BOUNDARIES.md` |
| 2026-07-26 | M0-02 completed; M0-16 and M0-20 opened with baseline and component-map drafts | `05_BASELINE_MEASUREMENT.md`, `06_SYSTEM_ARCHITECTURE.md` |
| 2026-07-26 | Owner authorized the baseline window and accepted the M0-20 component map | `05_BASELINE_MEASUREMENT.md`, `06_SYSTEM_ARCHITECTURE.md` |
| 2026-07-26 | M0-20 completed and M0-21 identity/trust/flow draft opened | `06_SYSTEM_ARCHITECTURE.md` Sections 10-18 |
| 2026-07-26 | Owner accepted M0-21 identity, trust-zone, and workflow-flow model | `06_SYSTEM_ARCHITECTURE.md` |
| 2026-07-26 | M0-22 opened; initial threat model and risk-treatment gates drafted | `07_THREAT_MODEL.md` |
| 2026-07-26 | Owner accepted all M0-22 threat-model dispositions and gates | `07_THREAT_MODEL.md` |
| 2026-07-26 | M0-23 opened; privacy impact assessment and verification tests drafted | `08_PRIVACY_IMPACT_ASSESSMENT.md` |

---

## Artifact status

- Author/agent: Primary AI coordinator
- Reviewer: Owner
- Status: Accepted for M0-01; living register remains active
- Inputs used: `docs/OSUN_MASTER_PLAN.md`, `docs/M0_AGENT_CHECKLIST.md`, repository history
- Assumptions: Listed in Section 6.3
- Open questions: Baseline completion, M0-23 privacy-disposition approval, non-blocking device details, and decision queue in Section 6.2
- Acceptance evidence: All 29 tasks registered once; accountable roles, dependencies, artifact paths, critical path, evidence gates, blockers, assumptions, decisions, and human budget are present
- Last updated: 2026-07-26
