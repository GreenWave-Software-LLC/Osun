# Osun M0 Threat Model

**Task:** M0-22 - Complete the initial threat model \
**State:** Accepted for M0-22 \
**Accountable:** Security analyst \
**Reviewers:** Primary AI systems-architecture consistency review; owner for residual-risk dispositions; independent M0-46 review later \
**Scope:** M0 design and the proposed M1 WF-01 vertical slice \
**Last updated:** 2026-07-26

---

## 1. Security objective and scope

Osun must remain useful without becoming a privileged path around the owner's agency, privacy, accounts, devices, or safety. The threat model covers:

- the Windows Agent Box;
- Raspberry Pi Personal Core;
- Home Assistant as a peer system;
- owner interfaces and the local network;
- identity, policy, workflow, model-routing, execution, memory, audit, and operations planes;
- Google Calendar and approved model providers;
- WF-01 Daily Consistency Plan, WF-02 Weekly Health Plan, and WF-03 Calorie Capture;
- code, model, skill, dependency, update, backup, and recovery supply chains.

The model considers malicious attacks, accidental owner or operator error, model/system failures, provider failures, physical loss, and environmental events. It does not assume that a threat must be intentional to cause harm.

This is a design threat model. It authorizes no installation, credential grant, public exposure, Home Assistant control, sensitive-data collection, or production use.

---

## 2. Method and current references

The analysis combines conventional asset/actor/entry-point reasoning with agent-specific threats to goals, identity, tools, memory, and human trust. Its lifecycle follows the NIST AI RMF functions of govern, map, measure, and manage, with the Generative AI Profile used for AI-specific risks and third-party/fallback planning: [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) and [NIST AI 600-1 Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence).

The agentic categories are cross-checked against the [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), including goal hijacking, tool misuse, identity/privilege abuse, agentic supply-chain compromise, unexpected code execution, memory/context poisoning, cascading failures, human-agent trust exploitation, and rogue behavior. Secure defaults and avoiding public/default-password exposure follow [CISA Secure by Design](https://www.cisa.gov/securebydesign).

These are reference profiles, not certification claims. The threat model is versioned and must be revisited after technology selection, before each autonomy increase, after any incident, and at least annually.

---

## 3. Risk scoring

### 3.1 Likelihood

| Score | Meaning | M0 interpretation |
|---:|---|---|
| 1 | Rare | Requires multiple unusual failures or unavailable capability |
| 2 | Unlikely | Plausible but needs special access or conditions |
| 3 | Possible | Credible during normal use over the system lifetime |
| 4 | Likely | Common failure mode or attractive attack path |
| 5 | Expected | Will occur repeatedly without deliberate controls |

### 3.2 Impact

Impact is the highest credible harm across confidentiality, integrity, availability, safety, agency, reputation, and recovery burden.

| Score | Meaning | Example |
|---:|---|---|
| 1 | Negligible | Minor inconvenience with immediate recovery |
| 2 | Limited | Small private/local error with easy correction |
| 3 | Material | Lost time, repeated wrong guidance, or limited personal-data exposure |
| 4 | Major | Unauthorized external action, serious privacy/agency harm, or multi-day loss |
| 5 | Severe | Credential takeover, broad sensitive exposure, physical/medical harm, or unrecoverable data loss |

### 3.3 Rating

`Likelihood × impact` determines the planning band:

| Score | Band | Required treatment |
|---:|---|---|
| 1-4 | Low | Track and test proportionately |
| 5-9 | Moderate | Planned control and verification required |
| 10-15 | High | Must have an implementation gate, scope prohibition, or dated owner acceptance |
| 16-25 | Critical | Prohibit exposure until controls and recovery evidence reduce the risk |

The target residual score is a design estimate after every listed control works. It is not evidence that the current system is secure.

---

## 4. Assets

| ID | Asset | Security property most important |
|---|---|---|
| A-01 | Owner agency, consent, goals, and ability to pause | Integrity and availability |
| A-02 | Health, energy, sleep, meal, calorie, and workout information | Confidentiality and integrity |
| A-03 | Calendar, notes, plans, job/life context, and future communications | Confidentiality and integrity |
| A-04 | Credentials, OAuth tokens, passkeys, recovery material, and device keys | Confidentiality and controlled use |
| A-05 | Policy definitions, approval receipts, capability grants, and workflow versions | Integrity and authenticity |
| A-06 | Memory, provenance, source events, preferences, and evaluation data | Integrity, confidentiality, and lifecycle control |
| A-07 | External account state such as Google Calendar events | Integrity, authorization, and recoverability |
| A-08 | Home Assistant state, device controls, and physical safety boundaries | Integrity, availability, and safety |
| A-09 | Models, prompts, skills, adapters, dependencies, and release artifacts | Integrity and provenance |
| A-10 | Audit ledger, security telemetry, and incident evidence | Integrity, completeness, and availability |
| A-11 | Personal Core, Agent Box, network, storage, and backup availability | Availability and recoverability |
| A-12 | Owner attention, trust calibration, emotional wellbeing, and reputation | Agency, safety, and integrity |

---

## 5. Threat actors and failure sources

| ID | Actor/source | Capability and motivation |
|---|---|---|
| TA-01 | Malicious content author | Places instructions or deceptive data in calendar items, webpages, documents, recipes, device names, or tool output |
| TA-02 | Internet attacker | Probes exposed services, steals credentials, abuses dependencies, or denies service |
| TA-03 | Compromised provider/integration | Returns malicious data, leaks submitted context, abuses tokens, or changes behavior |
| TA-04 | Malicious or compromised dependency/model/skill | Executes code, alters model behavior, exfiltrates data, or weakens controls |
| TA-05 | Malware or unauthorized local user | Reads files/secrets, tampers with services, impersonates the owner, or moves laterally |
| TA-06 | Compromised IoT/Home Assistant node | Attacks the local network or supplies false device state |
| TA-07 | Model or workflow failure | Hallucinates, goal-drifts, misuses a tool, loops, or produces persuasive misinformation without malicious intent |
| TA-08 | Owner/operator error | Approves the wrong payload, misconfigures access, deletes data, or ignores a warning under fatigue |
| TA-09 | Future household member or visitor | Gains unintended visibility or uses an interface under ambiguous identity/consent |
| TA-10 | Physical thief or disaster | Steals a device, destroys storage, interrupts power, or prevents recovery |
| TA-11 | Time and distributed-system failure | Causes stale, duplicated, out-of-order, replayed, or partially committed state |

---

## 6. Entry points and trust boundaries

| Entry point | Trust boundary | Representative risk |
|---|---|---|
| Owner text, pasted content, uploaded artifact | Z0/Z1 -> Z3 | Direct injection, malicious embedded instructions, oversized/malformed input |
| Scheduled/proactive trigger | Z3 internal | Duplicate runs, quiet-hour violation, notification flooding, stale state |
| Agent Box local model endpoint | Z3/Z6 -> Z2 | Model endpoint spoofing, context leakage, malformed output, resource exhaustion |
| Google Calendar read/write adapter | Z3/Z4 -> Z7 | Indirect injection, excessive OAuth scope, replay, unauthorized event write |
| Future Apple Health/iPhone path | Mobile/external -> Z4 | Excessive collection, false data, health inference, token/device compromise |
| Home Assistant adapter | Z3/Z6 -> Z5 | Lateral movement, unsafe device action, stale/false state |
| Memory/data API | Z3 -> Z4 | Unauthorized retrieval, poisoning, deletion failure, inference promoted as fact |
| Credential vault | Z3/Z4 | Token theft, confused deputy, recovery lockout |
| Local network and administration | Z6 -> Z2/Z3/Z5 | Spoofing, interception, exposed admin interface, default credentials |
| Dependency/model/skill/update path | Development -> Z2/Z3 | Supply-chain compromise, unsigned artifact, rollback to vulnerable version |
| Logs, traces, crash dumps, exports | Z2/Z3/Z4 -> operator/storage | Secret or sensitive-content disclosure, tampering, excessive retention |
| Backup and restore path | Z4 -> Z8 -> Z4 | Missing backup, plaintext copy, poisoned restore, untested recovery |

---

## 7. Security control catalog

### 7.1 Preventive controls

| ID | Control |
|---|---|
| P-01 | Default-deny network exposure; no public Osun administrative or workflow endpoint in M0/M1 |
| P-02 | Unique device/service/workflow identities and short-lived purpose-bound capabilities |
| P-03 | Deterministic policy and approval plane between models, data, and execution |
| P-04 | Typed/versioned schemas, strict argument validation, allowlists, limits, and safe parsers |
| P-05 | Content-origin labels and instruction/data separation for all external or pasted content |
| P-06 | Minimum-context retrieval and explicit local/cloud egress enforcement by data type |
| P-07 | Dedicated secret vault; no secrets in code, prompts, ordinary logs, memory, or exports |
| P-08 | Sandboxing and prohibition of arbitrary generated code/commands in selected workflows |
| P-09 | Version pinning, dependency inventory/SBOM, artifact verification, controlled updates, and rollback |
| P-10 | Memory provenance, candidate-before-confirmed promotion, conflict handling, retention, and correction |
| P-11 | Idempotency, nonce/replay protection, approval expiry, provider version checks, read-back verification, and undo |
| P-12 | Network/service segmentation, host firewalling, least-privilege OS accounts, and node quarantine |
| P-13 | Authenticated encrypted transport and encrypted sensitive storage/backup with separate key handling |
| P-14 | Exact owner preview/approval for R3 actions; no blanket approval in initial workflows |
| P-15 | Wellness-only health scope; no diagnosis/treatment, restrictive auto-goals, or override of pain/fatigue |
| P-16 | Request, token, time, retry, concurrency, storage, and cost budgets with circuit breakers |
| P-17 | Secure setup: no default credentials, explicit enrollment, no silent integration enablement |

### 7.2 Detective controls

| ID | Control |
|---|---|
| D-01 | Append-only/tamper-evident action and policy-decision ledger with correlation IDs |
| D-02 | Content-minimized structured security events, health checks, and owner-visible alerts |
| D-03 | Freshness, integrity, signature/hash, schema, sequence, and drift monitoring |
| D-04 | Dependency, secret, vulnerability, configuration, model, prompt, and artifact scanning |
| D-05 | Golden/adversarial evaluation for injection, privilege escalation, tool misuse, memory poisoning, and unsafe advice |
| D-06 | Periodic review of identities, grants, provider scopes, egress, retained data, and disabled workflows |
| D-07 | Backup success monitoring plus scheduled restore verification; copied bytes alone do not count |

### 7.3 Response controls

| ID | Control |
|---|---|
| R-01 | Owner-accessible global pause/kill path independent of model inference |
| R-02 | Revoke/rotate credentials and quarantine a device, service, model, skill, or integration independently |
| R-03 | Disable one workflow, adapter, data source, or egress route without disabling inspection/recovery |
| R-04 | Severity-based incident process with SEV-1 through SEV-4 response objectives |
| R-05 | Preserve minimal evidence, affected versions, correlation IDs, and authoritative external state |
| R-06 | Clear owner notification that distinguishes confirmed harm, suspected harm, and unknown state |

### 7.4 Recovery controls

| ID | Control |
|---|---|
| C-01 | Restore from a verified encrypted backup to replacement hardware using a documented procedure |
| C-02 | Rebuild a compromised node from known-good artifacts and re-enroll with new identity/keys |
| C-03 | Roll back code, configuration, workflow, prompt, model, policy, schema, and adapter versions |
| C-04 | Reconcile calendar/HA/external state before retry; reverse or compensate verified effects |
| C-05 | Quarantine poisoned memory, restore source truth, recompute indexes/summaries, and preserve correction history |

---

## 8. Threat and risk register

Notation: `L×I=score band`. The target residual assumes the named controls are implemented and pass their tests.

| ID | Threat scenario | Assets/entry | Inherent | Required disposition and controls | Target residual | Requirement / future scenario |
|---|---|---|---:|---|---:|---|
| TM-01 | Indirect prompt injection hijacks an agent through calendar, web, document, recipe, device name, or tool output | A-01, A-03, A-05, A-07; external content | 5×4=20 Critical | Stage A calendar excludes titles; P-03, P-04, P-05, P-14; injected text cannot issue capabilities | 3×3=9 Moderate | SEC-01; GS-SEC-01/02 |
| TM-02 | Direct owner/pasted prompt requests policy bypass, hidden mode, secret access, or unsafe tool use | A-01, A-04, A-05; UI | 4×4=16 Critical | P-03 through P-08; policy ignores model claims of authority; D-05 | 2×4=8 Moderate | SEC-01/02; GS-SEC-03 |
| TM-03 | Model invents or mutates tool arguments and causes unauthorized or incorrect external state | A-05, A-07, A-08; model/tool boundary | 4×4=16 Critical | P-03, P-04, P-11, P-14; executor accepts normalized typed action only; verify/undo | 2×4=8 Moderate | SEC-03; GS-SEC-04/05 |
| TM-04 | Individually allowed steps chain into a harmful outcome or exceed workflow purpose | A-01, A-05, A-07, A-12; orchestrator | 4×5=20 Critical | Per-run purpose/cost/action budgets; P-02, P-03, P-14, P-16; chain-level evaluation | 2×5=10 High | SEC-04; GS-SEC-06 |
| TM-05 | Confused deputy or privilege escalation lets a model/workflow use another identity, integration, or owner grant | A-04, A-05, A-07; identity/policy | 3×5=15 High | P-02, P-03, payload-bound grants, separate adapter identity; D-01/D-06 | 2×4=8 Moderate | SEC-05; GS-SEC-07/08 |
| TM-06 | Secret appears in prompt, log, trace, memory, crash dump, Git, OneDrive, or export | A-02-A-04, A-09; storage/diagnostics | 4×5=20 Critical | P-06, P-07, P-13; secret scanning and redaction D-04; rotation R-02 | 2×5=10 High | SEC-06; GS-SEC-09/10 |
| TM-07 | Malicious, wrong, or model-inferred content becomes durable trusted memory and affects later decisions | A-01, A-06, A-12; memory API | 4×4=16 Critical | P-05, P-10; provenance and candidate state; D-03/D-05; quarantine/rebuild C-05 | 2×4=8 Moderate | SEC-07; GS-SEC-11/12 |
| TM-08 | Sensitive or excessive context is sent to an unapproved cloud/provider or retained beyond purpose | A-02, A-03, A-12; router/egress | 3×5=15 High | Health/calorie local-only; P-06/P-07/P-13; egress audit/review D-01/D-06 | 1×5=5 Moderate | SEC-08; GS-SEC-13/14 |
| TM-09 | Agent Box malware or local account compromise steals context, tampers with models, or impersonates owner | A-01-A-06, A-09-A-11; Windows host | 3×5=15 High | M1 host-hardening gate; P-02, P-07, P-09, P-12/P-13; quarantine/rebuild R-02/C-02 | 2×5=10 High | SEC-09; GS-SEC-15 |
| TM-10 | Personal Core compromise changes policy, executes actions, exposes memory, or destroys audit | A-01-A-11; Pi host | 3×5=15 High | No public exposure; least-privilege services, protected keys/ledger, P-01/P-02/P-03/P-12/P-13; rebuild C-02 | 2×5=10 High | SEC-09/10; GS-SEC-16 |
| TM-11 | Compromised Home Assistant/IoT device moves laterally or supplies unsafe/false state | A-08, A-11; Z5/Z6 | 3×5=15 High | HA control excluded from M1; future P-02/P-04/P-11/P-12 and HA-side allowlist/safety | 1×5=5 Moderate | SEC-11; GS-SEC-17 |
| TM-12 | Malicious/vulnerable dependency, model, skill, container, or update compromises Osun | A-04, A-09-A-11; supply chain | 4×5=20 Critical | No unreviewed skill/model execution; P-08/P-09; D-04; staged update and rollback C-03 | 2×5=10 High | SEC-12; GS-SEC-18/19 |
| TM-13 | Generated code, shell, plugin, or tool output reaches unexpected code execution | A-04, A-09-A-11; execution/development | 3×5=15 High | Arbitrary generated execution prohibited in selected workflows; P-04/P-08/P-09/P-16 | 1×5=5 Moderate | SEC-13; GS-SEC-20 |
| TM-14 | Replay or duplicate trigger/approval/tool call repeats an external action or double-counts a record | A-05-A-07; distributed flow | 4×4=16 Critical | P-11 with nonce, idempotency, expiry, exact payload hash, provider read-back; D-01/D-03 | 1×4=4 Low | SEC-14; GS-SEC-21/22 |
| TM-15 | Race, stale cache, clock drift, or out-of-order event causes an invalid plan/action/memory state | A-05-A-07, A-10; events/cache | 4×3=12 High | Valid/received time, freshness, version/ETag, drift gate, P-04/P-11; C-04/C-05 | 2×3=6 Moderate | SEC-15; GS-SEC-23/24 |
| TM-16 | Compromised, changed, or low-quality model/provider produces malicious-looking or systematically unsafe output | A-01, A-05, A-09, A-12; inference | 3×4=12 High | Replaceable model boundary; P-03/P-04/P-09/P-15; D-05; rollback C-03 | 2×4=8 Moderate | SEC-16; GS-SEC-25 |
| TM-17 | Audit/telemetry is missing, poisoned, altered, or leaks personal content | A-02-A-04, A-10; operations | 3×4=12 High | Content-minimized schema, protected append-only ledger P-07/P-13; D-01/D-02/D-03 | 2×3=6 Moderate | SEC-17; GS-SEC-26/27 |
| TM-18 | No usable backup, storage corruption, deletion, theft, or disaster causes unrecoverable loss | A-05, A-06, A-09-A-11; storage/recovery | 4×5=20 Critical | **Current stop gate:** no irreplaceable or sensitive durable data until encrypted backup and restore test; P-13, D-07, C-01 | 2×4=8 Moderate | SEC-18; GS-SEC-28/29 |
| TM-19 | Pi SD wear, disk exhaustion, corrupt database, or power loss creates silent partial state | A-06, A-10, A-11; Personal Core/storage | 4×4=16 Critical | SD not sole store; disk/DB health, atomic writes, quotas, UPS assessment, D-02/D-03/D-07, C-01 | 2×4=8 Moderate | SEC-19; GS-SEC-30/31 |
| TM-20 | Infinite loop, retry storm, huge prompt, or provider misuse exhausts compute, storage, attention, or money | A-11, A-12; ingress/model/orchestrator | 4×3=12 High | P-04/P-16; per-run budgets/circuit breakers; D-02; R-03 | 2×2=4 Low | SEC-20; GS-SEC-32 |
| TM-21 | Persuasive personality, false confidence, or repeated prompts manipulate trust or create dependency | A-01, A-12; interface/model | 4×4=16 Critical | Approved personality envelope; evidence/uncertainty, dismissal budget, no shame/coercion, P-03/P-14; human-factors evaluation | 2×4=8 Moderate | SEC-21; GS-SEC-33/34 |
| TM-22 | Sensitive content leaks through lock-screen notification, shared display, screenshot, export, or backup | A-02, A-03, A-12; interface/export | 3×4=12 High | Generic notification text, authenticated reveal, export confirmation, P-06/P-13; D-06 | 2×3=6 Moderate | SEC-22; GS-SEC-35 |
| TM-23 | Future household support causes cross-person memory, notification, model, or device leakage | A-01-A-03, A-06, A-12; identity/UI/memory | 3×5=15 High | Multi-person support prohibited until independent identities, spaces, consent, policy, and tests exist | 1×5=5 Moderate | SEC-23; GS-SEC-36 |
| TM-24 | Public/remote exposure or default/misconfigured service permits unauthorized administration | A-01-A-11; network/admin | 3×5=15 High | P-01/P-02/P-12/P-17; remote access prohibited pending separate design; D-04/D-06 | 1×5=5 Moderate | SEC-24; GS-SEC-37 |
| TM-25 | Owner approves wrong or deceptively presented R3 action due to fatigue, ambiguity, or stale preview | A-01, A-05, A-07, A-12; approval UI | 4×4=16 Critical | Exact human-readable diff, destination/consequence, expiry, no dark patterns/batching; P-11/P-14/P-16 | 2×4=8 Moderate | SEC-25; GS-SEC-38/39 |
| TM-26 | Policy/config rollback or silent drift restores broader permissions or incompatible behavior | A-05, A-09, A-10; release/recovery | 3×4=12 High | Signed/versioned policy, migration checks, least-privilege revalidation, P-09; D-01/D-03/D-06; C-03 | 2×3=6 Moderate | SEC-26; GS-SEC-40 |
| TM-27 | Wellness workflow generates unsafe medical, injury, or restrictive nutrition guidance | A-01, A-02, A-12; WF-02/WF-03 | 3×5=15 High | P-15, explicit non-scope, owner constraints, abstention/referral language, D-05; no health-record write | 1×5=5 Moderate | SEC-27; GS-SEC-41/42 |
| TM-28 | External provider call succeeds ambiguously; blind retry creates duplicate or conflicting state | A-07, A-10; provider adapter | 3×4=12 High | P-11, authoritative read-before-retry, bounded retry, C-04; visible unknown state | 1×4=4 Low | SEC-14/15; GS-SEC-43 |
| TM-29 | Stolen PC/Pi/backup exposes data or permits offline credential attack | A-02-A-06, A-10-A-11; physical | 2×5=10 High | P-07/P-13, platform lock/encryption, separate recovery keys, credential revocation R-02, rebuild C-02 | 1×5=5 Moderate | SEC-28; GS-SEC-44 |
| TM-30 | Security control itself locks out owner, corrupts state, or prevents emergency pause/recovery | A-01, A-05, A-11; policy/recovery | 2×5=10 High | Separate tested pause/recovery identities, fail-safe inspection, break-glass logging, C-01/C-02; recovery exercises | 1×5=5 Moderate | SEC-29; GS-SEC-45 |

### 8.1 High-residual interpretation

TM-04, TM-06, TM-09, TM-10, and TM-12 retain a High target residual because a long-lived agent, privileged endpoints, credentials, and changing supply chains cannot be made risk-free by paper controls. They are governed by narrow scope and implementation gates:

- no model-to-tool direct path or autonomous multi-step external action in M1;
- no secrets in model context and no sensitive data in ordinary logs;
- no production use on an unhardened or unverified Agent Box/Personal Core;
- no unreviewed model, dependency, skill, or update promotion;
- no broad token or integration scope;
- immediate per-component revocation and owner pause.

These risks require continuing review; M0 approval does not permanently accept them for later autonomy.

---

## 9. Selected-workflow abuse cases

### AB-01 - WF-01 calendar injection to unauthorized action

**Attacker goal:** Use a calendar event or invite to make Osun reveal private context or create another event.

```text
attacker-controlled event title/description
-> calendar adapter retrieves content
-> malicious text says to ignore policy and use a tool
-> model treats text as instruction
-> model proposes data disclosure or event write
-> system executes without a correctly bound approval
```

Required breaks:

- Stage A excludes titles/descriptions entirely;
- later titles carry external-content provenance and cannot change workflow instructions;
- router removes unauthorized context and policy blocks egress;
- executor requires a typed, exact, unexpired approval capability;
- read-back and audit expose the attempted effect.

Tests: GS-SEC-01, GS-SEC-04, GS-SEC-13, and GS-SEC-38.

### AB-02 - WF-02 poisoned wellness input and unsafe plan

**Attacker/failure goal:** A compromised model/reference, malformed owner input, or poisoned memory causes medically unsafe or excessively restrictive advice and leaks health context to cloud fallback.

```text
untrusted wellness/reference content or poisoned preference
-> local model produces confident unsafe recommendation
-> local model is unavailable and router silently falls back to cloud
-> sensitive context leaves the system
-> owner follows persuasive plan
```

Required breaks:

- health context forces local-only routing and no cloud fallback;
- source provenance and candidate-memory status prevent silent trusted promotion;
- policy rejects diagnosis, treatment, restrictive auto-goals, and conflict with pain/fatigue;
- uncertainty and editable assumptions are visible;
- unavailable local inference degrades to a blank structured planner.

Tests: GS-SEC-12, GS-SEC-14, GS-SEC-25, GS-SEC-33, and GS-SEC-41.

### AB-03 - WF-03 unit manipulation, double count, and persistent poisoning

**Attacker/failure goal:** A malicious reference or malformed unit creates a fabricated calorie estimate, duplicate submit, and durable wrong food mapping.

```text
malicious or wrong local reference
-> unit/portion ambiguity is coerced into false precision
-> retry saves the same meal twice
-> wrong match is promoted as a permanent preference
-> later summaries compound the error
```

Required breaks:

- strict unit/schema validation and visible estimate ranges;
- abstention when evidence is insufficient;
- idempotency prevents duplicate save;
- source and derivation remain attached to the record;
- correction supersedes rather than hides the earlier version;
- mappings remain candidates until confirmed.

Tests: GS-SEC-11, GS-SEC-21, GS-SEC-23, GS-SEC-27, and GS-SEC-42.

---

## 10. M0 design controls versus M1 evidence

| Area | M0 design evidence | Required before M1 live exposure |
|---|---|---|
| Identity/authority | Distinct identity and capability model | Enrolled unique identities; negative permission tests; revocation test |
| Network | Trust zones and no-public-exposure rule | Bound interfaces, host firewall, authenticated transport, exposure scan |
| Secrets | Vault boundary and prohibited locations | Selected vault, no hard-coded secrets, secret scan, rotation/revocation rehearsal |
| Model isolation | Model proposal-only contract | Model endpoint isolation; malformed/injected output tests; no direct tool path |
| Tool execution | Typed gateway, approval, verification design | Schema/allowlist/idempotency/replay tests and exact approval receipt tests |
| Memory | Provenance and candidate promotion lifecycle | Access-control, poisoning, conflict, correction, deletion, and rebuild tests |
| Cloud egress | Per-data-type routing policy | Denial tests for health/calorie/calendar-title data and auditable route selection |
| Supply chain | Version/verification/rollback rules | Locked dependencies, inventory/SBOM, artifact source checks, staged rollback test |
| Storage/recovery | No-SD-only and backup/restore requirement | Encrypted durable target plus successful restore to a clean location |
| Operations | Ledger, telemetry, pause, severity concepts | Model-independent pause, tamper/gap detection, resource limits, incident rehearsal |
| Human factors | Personality and approval envelopes | Deceptive-preview, fatigue, dismissal, shame/coercion, and uncertainty tests |

M1 may use synthetic test data before these controls pass. It may not reinterpret synthetic success as authorization for personal production data.

---

## 11. Security requirements and reserved verification scenarios

These identifiers are stable inputs to M0-24 contracts, M0-30 golden scenarios, M0-34 traceability, and the M1 backlog.

| Requirement | Normative statement | Primary threats | Reserved scenarios |
|---|---|---|---|
| SEC-01 | Untrusted content cannot modify system/workflow instructions or mint authority | TM-01, TM-02 | GS-SEC-01 to 03 |
| SEC-02 | Policy decisions are deterministic, versioned, deny-by-default, and independent of model claims | TM-02, TM-04 | GS-SEC-03, 06 |
| SEC-03 | Models cannot directly execute tools; tool inputs are typed, validated, authorized, and verified | TM-03 | GS-SEC-04, 05 |
| SEC-04 | Whole-run budgets and consequence checks prevent unsafe chaining | TM-04, TM-20 | GS-SEC-06, 32 |
| SEC-05 | Each actor uses a distinct revocable identity and purpose-bound capability | TM-05 | GS-SEC-07, 08 |
| SEC-06 | Secrets never enter model context, ordinary logs/memory, source control, or normal exports | TM-06, TM-29 | GS-SEC-09, 10, 44 |
| SEC-07 | Durable memory preserves provenance and separates observation, inference, and confirmation | TM-07 | GS-SEC-11, 12 |
| SEC-08 | Router enforces approved data-class/provider egress before inference | TM-08 | GS-SEC-13, 14 |
| SEC-09 | Agent Box and Personal Core meet a documented hardening baseline before live use | TM-09, TM-10 | GS-SEC-15, 16 |
| SEC-10 | Policy, audit, memory, and secret stores use separated least-privilege access | TM-10, TM-17 | GS-SEC-16, 26 |
| SEC-11 | Home Assistant remains device authority and Osun access is narrowly allowlisted | TM-11 | GS-SEC-17 |
| SEC-12 | Dependencies/models/skills/artifacts are inventoried, verified, staged, and reversible | TM-12 | GS-SEC-18, 19 |
| SEC-13 | Selected workflows cannot execute arbitrary generated code or shell commands | TM-13 | GS-SEC-20 |
| SEC-14 | Consequential operations are idempotent, replay-resistant, expiring, and independently verified | TM-14, TM-28 | GS-SEC-21, 22, 43 |
| SEC-15 | Freshness, event order, versions, and clock drift are explicit and safely handled | TM-15, TM-28 | GS-SEC-23, 24, 43 |
| SEC-16 | Model/prompt/provider changes require evaluation, version evidence, staged release, and rollback | TM-16 | GS-SEC-25 |
| SEC-17 | Audit is content-minimized, complete enough to investigate, and protected from ordinary modification | TM-17 | GS-SEC-26, 27 |
| SEC-18 | No irreplaceable/sensitive durable data exists without encrypted backup and verified restore | TM-18 | GS-SEC-28, 29 |
| SEC-19 | Storage and power failure cannot silently produce accepted partial state | TM-19 | GS-SEC-30, 31 |
| SEC-20 | Every run has bounded time, retries, compute, storage, notifications, and cost | TM-20 | GS-SEC-32 |
| SEC-21 | Personality and proactivity cannot manipulate, shame, fabricate urgency, or expand permissions | TM-21 | GS-SEC-33, 34 |
| SEC-22 | Sensitive content is hidden from unauthenticated/shared notifications, views, exports, and backups | TM-22 | GS-SEC-35 |
| SEC-23 | Multi-person data/actions are prohibited until identity, consent, isolation, and leakage tests pass | TM-23 | GS-SEC-36 |
| SEC-24 | Osun has no public/remote administration until a separately approved design and tests exist | TM-24 | GS-SEC-37 |
| SEC-25 | R3 approval shows the exact action, destination, consequence, expiry, and change from current state | TM-25 | GS-SEC-38, 39 |
| SEC-26 | Rollback/migration cannot silently restore broader authority or incompatible policy | TM-26 | GS-SEC-40 |
| SEC-27 | Health workflows stay within approved wellness non-scope and abstain safely | TM-27 | GS-SEC-41, 42 |
| SEC-28 | Sensitive devices/storage use encryption and support rapid credential revocation after loss | TM-29 | GS-SEC-44 |
| SEC-29 | Pause, recovery, and owner access survive model failure and are exercised before reliance | TM-30 | GS-SEC-45 |

---

## 12. Residual risks and owner decision

The owner is not being asked to accept a Critical or High risk for production. The proposed M0-22 decision is to accept these dispositions and gates:

1. **Backup gate:** No sensitive or irreplaceable durable Osun data until an encrypted backup succeeds and a restore is verified.
2. **Endpoint gate:** No live personal workflow on an unhardened or unverified Agent Box/Personal Core; synthetic data may be used for implementation tests.
3. **Exposure gate:** No public/remote Osun service during M0/M1 without a separate threat model and owner decision.
4. **Execution gate:** No arbitrary generated code/shell execution, no direct model-to-tool path, and no autonomous multi-step external action in the selected workflows.
5. **Home gate:** No Osun control of Home Assistant devices in the initial M1 slice.
6. **Supply-chain gate:** No model, skill, dependency, plugin, container, or update is promoted without source/version inventory, bounded evaluation, and rollback.
7. **Residual prompt/model risk:** Model output remains untrusted and suggestion-only unless deterministic policy, exact approval, restricted execution, and verification all succeed.
8. **Human-trust risk:** The strong personality remains bounded by the accepted non-coercion envelope, evidence/uncertainty display, notification budget, and owner pause.

Approval applies only to the M0 threat-model treatment plan. Later gates must decide whether implementation evidence actually reduces each risk enough for its exact data and autonomy scope.

**Owner decision:** All eight M0-22 residual-risk dispositions and gates accepted as written on 2026-07-26.

---

## 13. M0-22 acceptance checklist

- [x] Assets, threat actors/failure sources, entry points, trust boundaries, and high-impact outcomes are identified.
- [x] Prompt injection, tool abuse, credential exposure, memory poisoning, compromised nodes, replay/duplication, lateral movement, unsafe chaining, supply chain, and data loss are covered.
- [x] At least one detailed abuse case exists for each selected workflow.
- [x] Preventive, detective, response, and recovery controls are mapped.
- [x] Likelihood and impact use a documented scale.
- [x] Every High/Critical risk has controls and a gate or scope prohibition.
- [x] M0 design controls are separated from M1 implementation evidence.
- [x] Stable security requirement and future scenario identifiers provide traceability.
- [x] Systems architect confirms controls fit the accepted architecture.
- [x] Owner approves or amends the residual-risk dispositions in Section 12.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as security analyst
- Reviewers: Primary AI systems-architecture consistency review and owner review complete; independent M0-46 review later
- Status: Owner accepted; M0-22 complete
- Inputs used: Accepted charter, data/autonomy boundaries, system inventory, accepted architecture/trust flows, NIST AI RMF/GAI Profile, OWASP Agentic Top 10 2026, CISA Secure by Design
- Assumptions: M1 remains WF-01-first, no public exposure is required, Home Assistant control is deferred, and synthetic data can support early implementation tests
- Open questions: Exact technology controls after M0-24/M0-40; privacy analysis in M0-23; independent challenge in M0-46
- Acceptance evidence: Thirty scored threats, three workflow abuse cases, full control catalog, High/Critical dispositions, 29 stable security requirements, and 45 reserved adversarial scenarios
- Last updated: 2026-07-26
