# Osun M0 Recovery, Pause, and Incident Concept

**Task:** M0-32 - Define backup, restore, pause, kill, and incident concepts \
**State:** Agent complete; internal systems-architecture review passed \
**Accountable:** Security/operations analyst \
**Reviewer:** Systems architect \
**Concept version:** 0.1.0 \
**Last updated:** 2026-07-26

---

## 1. Purpose and authority

This document defines the recoverability and emergency-control contract that Osun must implement before the owner relies on it. It is technology-neutral until M0-40 through M0-42 select and validate concrete storage, backup, encryption, monitoring, and deployment tools.

The owner is the final authority for pause, containment, recovery, and re-enablement. Models may explain a condition or suggest a response, but they cannot suppress an alert, defeat a pause, declare a restore valid, rotate a secret, or return a contained system to live operation.

The accepted stop gate remains normative:

> Osun may not retain irreplaceable or Sensitive live data until an encrypted backup has succeeded and a clean restore has been verified for the exact schema, configuration, and deployment family in use.

M0 defines the concept. M1 must produce implementation evidence before the gate can pass.

---

## 2. Recovery principles

1. **Restore evidence, not copy success.** A backup is healthy only after its manifest, integrity, decryption, migration, deletion handling, and usable restored state have been tested.
2. **Fail closed for effects.** Missing policy, ledger, identity, approval, time, or authoritative-state evidence blocks consequential execution.
3. **Keep control outside the model.** Pause, action kill, source disconnect, credential revocation, isolation, restore, and re-enablement use deterministic owner/operations paths.
4. **Separate failure domains.** Working data, local backup, offsite backup, and recovery-key custody cannot depend on one Pi, SD card, PC, account, provider, or physical location.
5. **Back up authority; rebuild acceleration.** Authoritative records and control evidence are protected. Indexes, caches, binaries, and derived acceleration structures are normally rebuilt from verified sources.
6. **Preserve owner agency.** Degraded state, uncertainty, data loss, unresolved external effects, and recovery choices are visible. Osun never invents success.
7. **Do not resurrect deleted data.** Deletion manifests and restore-time suppression are recovery-critical artifacts.
8. **Recovery does not broaden permissions.** Restored grants are revalidated against the current narrower policy; expired capabilities and approval receipts never reactivate.
9. **Contain first when compromise is plausible.** Do not collect evidence by executing untrusted components or attaching a clean recovery environment to a suspect writable store.
10. **Rehearse before reliance.** The owner should not discover missing keys, incompatible media, or undocumented steps during an incident.

---

## 3. Recovery classes and targets

Targets are elapsed-clock objectives after the owner detects and declares an incident. They are design objectives, not current guarantees. M0-40/M0-41 must test feasibility on the selected hardware and storage.

| Class | Content | Routine-failure RPO | Site/account-loss RPO | RTO target | Recovery rule |
|---|---|---:|---:|---:|---|
| RC-0 Recovery root | Offline recovery instructions, trusted device/service inventory, root public metadata, encrypted key-recovery package | At every accepted change | At every accepted change | 4 hours | Two separately held recovery copies; never depend on the failed node or model |
| RC-1 Safety/control state | Policy/config, identities and revocation state, active workflow state, idempotency state, action/policy ledger, deletion manifests | 15 minutes; after each consequential transition where feasible | 24 hours | 4 hours | Restore first; effects remain killed until reconciliation and validation pass |
| RC-2 Durable owner data | RET-2/RET-3 source records, confirmed memory, saved plans, corrections, governed evaluation observations | 24 hours | 24 hours | 24 hours | Restore with provenance, retention, derivation, and deletion controls intact |
| RC-3 Releasable system artifacts | Accepted schemas, workflows, prompts, policy bundles, adapter/config manifests, evaluation fixtures/results | At each accepted release/change | 24 hours | 8 hours | Restore or reproduce only from verified versioned artifacts |
| RC-4 Rebuildable/ephemeral | Caches, indexes, embeddings, temporary context, binaries available from verified source | No backup | No backup | 48 hours or explicit feature outage | Rebuild/refetch; never promote a rebuilt cache to source of truth |
| RC-X External authority | Google Calendar and, later, Home Assistant/provider state | Osun does not claim an RPO | Provider-specific | Reconcile before any retry | Provider state is read back; Osun ledger records references and uncertainty |

RPO is the maximum intended loss of committed data. RTO is the intended time to a safe usable state, not necessarily full feature restoration. A system that is paused, inspectable, and capable of export/revocation may meet a safety RTO while model-backed workflows remain unavailable.

### 3.1 Assumptions and stop conditions

- The owner is one person and can supply about ten project hours per week; routine operation must be mostly automated, while restores remain deliberate.
- The Pi SD card is never the sole durable store for RC-1 or RC-2.
- Offsite means outside the same physical/device/account failure domain, not merely another folder on the PC or the current OneDrive tree.
- Provider sync is not a backup unless Osun can independently enumerate versions, decrypt data, restore into a clean environment, and prove deletion behavior.
- If the measured RPO/RTO misses its target twice, backup health becomes failed and Sensitive live collection remains or returns paused until the design is corrected.
- Loss of the only usable recovery key is unrecoverable by design; no service/model backdoor is permitted.

---

## 4. Persistent-artifact inventory and policy

Every current persistent class has either a recovery class or an explicit no-backup policy.

| Artifact/data class | Authority and retention | Recovery class | Backup policy | Restore/verification rule |
|---|---|---|---|---|
| Owner charter, goals, confirmed preferences/procedures | Memory/data plane; RET-3 | RC-2 | Encrypted local and offsite | Preserve versions, source, validity, subject, purpose, and current/superseded status |
| Daily plans, outcomes, edits, usefulness | Memory/data plane; RET-2, promoted facts RET-3 | RC-2 | Encrypted local and offsite | Restore current and history without converting missing outcomes to failures |
| Energy/interest self-report | Memory/data plane; Sensitive RET-2 | RC-2 | Encrypted local and offsite only after stop gate | Field-level deletion and purpose isolation must survive restore |
| Meal/workout preferences, constraints, and accepted plans | Memory/data plane; Sensitive RET-2/3 | RC-2 | Encrypted local and offsite only after stop gate | Restore provenance, owner edits, supersession, and wellness non-scope |
| Food entries, estimates, corrections, reusable mappings | Memory/data plane; Sensitive RET-2/candidate lifecycle | RC-2 | Encrypted local and offsite only after stop gate | Recompute summaries; disputed mappings cannot become current |
| Later approved Health aggregates | Memory/data plane; Sensitive RET-2 | RC-2 | Encrypted local and offsite only after a separate source approval and stop gate | Per-type grant, time window, deletion, and unknown-state semantics remain |
| Immutable source events and governed memory facts/candidates | Memory/data plane; source policy | RC-2 | Encrypted local and offsite | Verify schema, hashes, lineage, lifecycle, and purpose-filtered retrieval |
| Workflow run/checkpoint/timer state | Orchestrator; active plus bounded history | RC-1 | Frequent encrypted local; daily encrypted offsite | Expired/paused runs do not resume; incomplete effects reconcile before transition |
| Idempotency keys, nonces, approval use state | Policy/execution plane; bounded by action/audit policy | RC-1 | Frequent encrypted local and offsite | Used/expired receipts remain unusable; duplicate tests pass after restore |
| Policy bundles, owner policy, grants, revocations, pause state | Policy plane; versioned/current history | RC-1/RC-3 | After-change local plus daily offsite | Current narrower policy wins; global/action/egress pause defaults on when uncertain |
| Device/service/integration identity metadata | Identity plane; current plus revocation history | RC-1 | Encrypted local/offsite | Re-enroll private identities if compromise is possible; revoked identity stays revoked |
| Device/service private keys and trust roots | Dedicated identity store | RC-0 | Dedicated encrypted recovery package, separate from general data backups | Rotate/re-enroll after suspected compromise; verify trust chain without printing secrets |
| Action and policy-decision ledger | Append-only ledger; consequential RET-3 | RC-1 | Frequent append replication plus encrypted local/offsite | Verify chain/completeness, correlation IDs, external references, and read-only history |
| Deletion manifests and restore-suppression set | Privacy/operations authority; at least as long as affected backup | RC-1 | Included in every backup generation and recovery root | Apply before indexes/context become available; deleted content must not resurrect |
| Incident case index and content-minimized evidence | Operations plane; incident-specific | RC-1 | Sealed encrypted incident set plus manifest | Hash/integrity check; access log; sensitive payload collected only when necessary |
| Operational telemetry and routine debug evidence | Operations plane; RET-1/2 | No general backup | Expire locally; only promoted incident evidence enters RC-1 | Raw personal content remains prohibited; absence never blocks authoritative restore |
| Calendar Stage A cache and optional later detail cache | Provider-derived RET-1 | RC-4 | Do not back up | Refetch after reconnection; show unavailable/stale until authoritative refresh |
| Semantic/vector/search indexes and computed summaries | Derived cache | RC-4 | Do not back up unless a benchmark proves rebuild infeasible and owner later approves | Rebuild from governed sources; compare counts/derivations; never use as authority |
| Model request context and unsaved output | RET-0; approved debug RET-1 | RC-4 | Do not back up | Discard; owner-saved output is backed up under its destination artifact class |
| Pending UI draft not explicitly submitted | Interface RET-0 | RC-4 | Do not back up | Loss is acceptable and visible; never infer submission after restart |
| Schemas, workflows, prompts, policy-as-code, adapters, migrations | Development/release authority; versioned | RC-3 | Version control plus encrypted release/config backup | Signature/hash, compatibility, migrations, and regression suite pass before activation |
| Dependency/container/OS manifests and SBOM | Release process | RC-3 | Back up manifests, locks, hashes, provenance—not arbitrary installed trees | Rebuild from verified sources; scan before promotion |
| Model binaries and public food/reference datasets | Verified external/release source | RC-4 with RC-3 manifest | Do not back up by default; preserve exact source/version/hash/license metadata | Reacquire, verify, scan, and evaluate; remain unavailable if exact artifact cannot be trusted |
| Future personalized model weights/adapters | Not authorized in M0/M1 | No current data | No collection/training/backup path exists | Requires a separate privacy, threat, deletion, lineage, evaluation, and recovery design |
| OAuth tokens and provider credentials | Restricted vault; RET-X | Dedicated secret recovery | Prefer revoke/re-authorize; if backup is necessary, use a separately encrypted vault recovery set | Never enter general backup, Git, logs, model context, or ordinary export; test revocation |
| Passkeys, Apple/Google account recovery, backup decryption secrets | External/offline owner authority | RC-0/no Osun data backup | Never place plaintext or sole copy inside Osun backup | Owner tests account and offline recovery without exposing secret material to Osun |
| Owner-requested exports | Owner-selected destination | Outside Osun backup scope by default | Do not silently re-ingest or back up | Manifest tells owner destination, categories, time, and that deletion is separately controlled |
| Google Calendar authoritative event state | Google/provider | RC-X | Not duplicated as an Osun backup of Calendar | Use ledger provider IDs, ETag/version where available, and read-back reconciliation |
| Home Assistant configuration/history/device state | Home Assistant | RC-X | Governed by an independent HA backup/recovery plan; not copied into Osun by default | Direct HA operation and recovery remain independent; future integration needs separate tests |
| Git planning repository | Development authority; no live personal data/secrets | RC-3 | Version history plus a separately recoverable repository copy selected later | Clone/checkout exact commit; scan for prohibited data/secrets before trust |
| Host OS/service installation | Deployment, not data authority | RC-4 with RC-3 deployment manifest | Rebuild instead of byte-level machine restore by default | Install clean OS, patch, apply verified manifest, enroll new identity, then restore data |

---

## 5. Backup architecture concept

### 5.1 Copy and trust layout

```text
authoritative transactional stores
  -> application-consistent snapshot/export
  -> encrypt before leaving the protected data boundary
  -> local backup on a physically separate medium
  -> offsite backup in a separate device/account/location failure domain

offline recovery root
  -> recovery procedure + trusted manifests + encrypted key package
  -> never stored only beside, or encrypted only by, the data it must recover
```

The concrete implementation must:

- use an allowlisted dataset manifest rather than broad filesystem copying;
- capture schema, application, policy, workflow, and migration versions;
- use application-consistent database snapshots or exports, never assume a live file copy is coherent;
- encrypt before data leaves Z4 and authenticate both the archive and manifest;
- use separate backup credentials that cannot run workflows or browse plaintext;
- prevent the Personal Core from silently deleting or rewriting every recovery generation;
- retain multiple generations so corruption or deletion is not immediately replicated over the last good copy;
- enforce source-aligned retention and record unavoidable delayed backup expiry honestly;
- monitor last successful snapshot, last successful offsite copy, age, size anomaly, integrity, and last verified restore;
- fail the backup-health gate if any required dataset, manifest, key, or restore check is missing.

### 5.2 Encryption and recovery-key custody

Use separate roles for data encryption, backup writing, and recovery. The working node may hold the minimum key needed to create encrypted backups, but it must not hold the only recovery secret or a credential that can erase all recovery generations.

The single-owner version-zero custody plan is:

1. Generate a recovery package through an approved, auditable setup path.
2. Keep two sealed/offline recovery copies in separate physical failure domains.
3. Keep only non-secret fingerprints, instructions, media labels, and test dates in the repository.
4. Test recovery with a disposable encrypted fixture before any Sensitive data and at the scheduled cadence.
5. Replace/reseal recovery material after exposure, loss, custodian change, or cryptographic migration.

Key risks are loss of all copies, theft of a copy plus ciphertext, forgotten recovery steps, dependence on one cloud account/passkey, damaged media, and a backup containing its own sole decryption key. There is deliberately no model-operated recovery bypass. A future trusted-person or professional-custody design is an owner decision, not an M0 assumption.

### 5.3 Backup cadence and retention concept

| Activity | Initial target | Health condition |
|---|---|---|
| RC-1 local protection | Within 15 minutes and after consequential transitions where feasible | Snapshot/replication plus manifest succeeds without integrity anomaly |
| RC-2 local snapshot | Daily | Application-consistent, encrypted, complete allowlist |
| Offsite transfer | Daily after local protection | Ciphertext and authenticated manifest arrive in separate failure domain |
| Integrity/decryption sampling | Weekly | Selected generations authenticate and decrypt in an isolated test path |
| Partial clean restore | Monthly and after schema/storage changes | Restored fixture/query/action-ledger/deletion checks pass |
| Full clean recovery exercise | Before Sensitive live data; quarterly after reliance; after major migration or serious incident | Replacement environment reaches safe reduced mode and all applicable acceptance tests pass |
| Recovery-key/media check | Quarterly and after custody change | Both expected copies located; one approved non-destructive recovery exercise succeeds |

Retention generations must cover operational mistakes and delayed detection while respecting RET-1/2/3. Exact generation counts and media/provider costs are M0-40 scorecard decisions. Immutable history does not justify retaining personal content forever.

---

## 6. Restore and verification protocol

A restore is performed into a clean, isolated environment. It must not overwrite the only remaining source or attach writable suspect media.

### 6.1 Ordered restore procedure

1. **Declare scope and safety state.** Record incident/cause, chosen recovery point, affected data/classes, and set global/action/egress pause before services can start.
2. **Establish clean trust.** Use known-good OS/release media, verify hashes/provenance, patch, and create fresh device/service identities when compromise is plausible.
3. **Recover RC-0.** Validate the offline instructions, expected manifest fingerprints, recovery authorization, and key material without exposing secrets to logs or model context.
4. **Verify archive before import.** Authenticate manifest/archive, compare dataset allowlist, versions, timestamps, sizes, and checksums, and reject partial/unexpected content.
5. **Restore RC-1 first.** Recover policy, revocation/pause state, ledger, workflow/idempotency state, and deletion manifests. Default to the most restrictive compatible policy.
6. **Apply deletion and retention rules.** Purge expired data and suppression-manifest records before rebuilding indexes or permitting retrieval.
7. **Restore RC-2 and RC-3.** Run explicit schema migrations in a copy, preserve source/provenance/version history, and reject incompatible silent coercion.
8. **Rebuild RC-4.** Reacquire verified binaries/data, rebuild indexes/summaries from authoritative records, and refetch external caches only after source reauthorization.
9. **Reconcile external state.** Read Calendar/provider authoritative state for any `unknown`, `attempted`, or interrupted action. Never blind-retry.
10. **Run verification suites.** Validate counts, referential integrity, policy denials, secret absence, purpose isolation, duplicate/replay behavior, pause, deletion non-resurrection, ledger chain, workflow samples, export, and evidence completeness.
11. **Enter safe reduced mode.** Permit authenticated inspect/export/correct/delete/revoke functions; keep models, collection, scheduling, egress, and effects off until their specific gates pass.
12. **Owner re-enables deliberately.** Present recovery point, measured data loss, unresolved copies/effects, versions, tests, and remaining risk. Re-enable one workflow/source/route at a time.

### 6.2 Restore pass criteria

The restore result is `pass`, `fail`, or `inconclusive`; missing evidence is `inconclusive`, never pass. A pass requires:

- the selected recovery point and achieved RPO/RTO are recorded;
- every manifest entry is accounted for and no unallowlisted data appears;
- authentication/decryption/integrity and schema migration pass;
- action/policy ledger chain and authoritative external reconciliation pass;
- global pause and all restrictive revocations survive restore;
- expired capabilities/approvals remain invalid;
- deletion manifests prevent source, derived, index, cache, and context resurrection;
- purpose-filtered retrieval and local/cloud egress rules still deny prohibited access;
- rebuildable artifacts are derived only from verified authoritative sources;
- sampled workflow, duplicate, failure, export, and owner-control tests pass;
- the report identifies actual loss, uncertainty, unresolved provider/export copies, and exceptions.

Backup-job success, mountability, or a checksum alone cannot satisfy this definition.

---

## 7. Pause, kill, isolation, and safe reduced mode

### 7.1 Deterministic controls

| Control | Effect | Still allowed | Must not depend on |
|---|---|---|---|
| Global pause | Blocks new collection, triggers, runs, model routing, capability issuance, tool execution, and pending effects | Authenticated status, audit, export, correction/deletion, credential revocation, restore, recovery guidance | Model, Agent Box, cloud, or active workflow |
| Per-workflow disable | Blocks triggers/new runs for one workflow; cancels or safely checkpoints in-flight work; revokes its unused capabilities | Other approved workflows and inspection | Workflow model or prompt |
| Source disconnect | Stops refresh, revokes/invalidates adapter grant, marks cached data stale, offers governed cache deletion | Historical owner-controlled records if their purpose/retention still permits | Source availability |
| Egress kill | Denies every cloud-model/telemetry/export route except an exact owner-controlled recovery export | Local deterministic recovery and approved local inspection | Router/model compliance |
| External-action kill | Denies new R3 capabilities and adapter invocations; expires queued approvals | Provider read-only reconciliation if separately safe and authorized | Orchestrator/model |
| Identity/credential revoke | Invalidates a device/session/service/integration and rotates or reauthorizes affected credentials | Separate recovery identity | The suspect identity/node |
| Node isolation | Removes suspect node network/service access and quarantines its identity | Recovery from a clean node/environment | Software running on suspect node |
| Infrastructure stop | Stops Osun services/network path when policy plane cannot be trusted | Direct Home Assistant interface, offline recovery material, provider-side revocation | Personal Core availability |

Pause state is durable RC-1 state, versioned, auditable, and monotonic toward restriction during uncertainty. If a component cannot read current pause/policy state, it denies collection, egress, and effects. Pending jobs, approvals, and capabilities are revalidated after every pause transition or restart; none execute merely because the system returned.

At least two owner-accessible pause paths are required before reliance:

- a primary authenticated local control served by the Personal Core/operations plane; and
- a recovery path that does not require the Agent Box, model, workflow, or ordinary owner session, with infrastructure/network isolation and provider-side credential revocation instructions.

The exact physical/network implementation is selected and tested later. Public remote administration is not implied.

### 7.2 Safe reduced mode

| Function | Reduced mode |
|---|---|
| View health, pause, versions, incident state | Allowed through authenticated deterministic UI |
| Inspect/export owner data and audit references | Allowed if store integrity and identity are verified |
| Correct/delete data | Allowed through governed deterministic plan; affected collection remains paused |
| Revoke/rotate identities and integrations | Allowed through recovery authority |
| Model inference and proactive prompts | Off by default |
| Source collection and background scheduling | Off |
| Cloud egress | Off |
| Calendar or other external writes | Off |
| Home Assistant operation | Only through its independent direct interface; Osun control remains off |

No security incident returns automatically from contained/recovery mode to live operation. Routine transient outages may recover automatically only for non-consequential local functions; queued external effects still require current policy, freshness, approval, and reconciliation.

---

## 8. Incident model

### 8.1 Severity and response objectives

| Severity | Examples | Owner notification | Containment objective | Re-enable authority |
|---|---|---|---:|---|
| SEV-1 Critical | Confirmed/suspected secret or Sensitive-data disclosure; unauthorized external action; policy/ledger compromise; inability to pause; destructive compromise of multiple copies | Immediate through available local/recovery channel; distinguish confirmed, suspected, unknown | Begin immediately; target 15 minutes after owner awareness | Owner only after clean rebuild/restore, credential rotation, evidence, and blocking findings resolved |
| SEV-2 High | Suspected node compromise; corrupt authoritative store; restore failure; repeated unknown provider effects; RC-1 backup beyond target | Prompt, target within 1 hour of detection | Target 4 hours | Owner after scoped recovery and verification |
| SEV-3 Moderate | One workflow/source/model unavailable; local backup delay; bounded data-quality or duplicate issue with no confirmed harm | Same day, target within 24 hours; no repeated noisy alerts | Target 24 hours or keep affected feature disabled | Deterministic auto-recovery for non-effectful outage, otherwise owner/operator |
| SEV-4 Low | Cosmetic defect, optional metric gap, non-urgent maintenance | Weekly digest or visible status | Next planned maintenance | Normal release process |

If severity is uncertain, choose the higher credible level until evidence narrows it. Notification contains incident ID, time detected, affected scope, confirmed/suspected/unknown facts, automatic containment already taken, owner action if any, and next update target. It excludes raw personal content and secrets.

### 8.2 Incident lifecycle and ownership

```text
detect -> classify -> contain/pause -> preserve minimal evidence
-> eradicate/rebuild -> restore/reconcile -> verify in reduced mode
-> owner re-enable -> monitor -> retrospective and control update
```

| Activity | Accountable authority | Required evidence |
|---|---|---|
| Detection and automatic fail-closed response | Operations/policy plane | Health/security event, affected identity/version/run, reason code |
| Severity and containment decision | Owner using deterministic guidance; safest automatic containment may precede acknowledgment | Incident record, scope, pause/revocation/isolation receipts |
| External provider reconciliation/revocation | Owner/recovery operator through restricted adapter or provider UI | Provider authoritative state, grant/revocation result, timestamps |
| Evidence preservation | Operations/recovery process | Hashed manifest, source, access record, time, minimal necessary contents |
| Eradication/rebuild/restore | Recovery operator on clean environment | Verified artifact versions, identity rotation, restore report |
| Functional/security/privacy verification | Evaluation plus deterministic policy/ops tools | Applicable GS-SEC/GS-PRI and restore cases with exact versions |
| Risk acceptance and re-enablement | Owner | Explicit scope, residual risk, enabled workflow/source/route, date |
| Retrospective and specification update | Coordinator with security/operations review | Cause, contributing controls, data/effect impact, lessons, assigned changes |

### 8.3 Evidence preservation rules

- Preserve correlation/causation IDs, actor/service/device identities, time sources, policy/workflow/model/tool/config versions, decision/result states, provider resource IDs, relevant hashes, and backup/recovery-point manifests.
- Acquire evidence read-only where possible. Hash before analysis and record each access/copy.
- Do not collect whole personal databases, raw prompts, secrets, or unrelated content when identifiers/metadata suffice.
- Never paste suspected secrets or Sensitive evidence into a cloud model or ordinary project file.
- Treat evidence from a compromised node as untrusted but preserve it; corroborate using ledger, backup, network, and provider authority.
- Keep remediation actions separate from original evidence and preserve content-free audit history after governed content deletion.

---

## 9. Failure and compromise playbooks

| Condition | Immediate safe state | Diagnosis/evidence | Recovery | Re-enable gate |
|---|---|---|---|---|
| Power loss during write | External-action kill; affected run `unknown`/recovering | Transaction journal, ledger tail, filesystem/DB health, last verified backup | Atomic rollback/roll-forward; restore if integrity fails; reconcile provider state | Complete state/ledger match; GS-SEC-30 passes |
| Disk full, SD wear, or disk failure | Pause affected writes/workflows; no effect dependent on unsaved state | Capacity, I/O/media health, failed-write IDs, backup age | Replace clean storage; restore RC-1/2; rebuild RC-4 | Integrity, quotas/alerts, GS-SEC-31, restore suite pass |
| Corrupt or poisoned data | Quarantine affected source/memory; disable derived retrieval | Hash/schema/provenance/conflict/deletion checks and affected derivation graph | Restore source truth or correct/supersede; rebuild indexes/summaries | Purpose queries and GS-SEC-11/12 plus GS-PRI-07/09 pass |
| Internet unavailable | Keep local policy/pause; mark external freshness unknown; deny Calendar writes | Connectivity and provider-independent local health | Resume reads after fresh sync; reconcile before any write/retry | Freshness/clock/policy valid; queued approvals re-reviewed |
| Cloud or local model unavailable | No cloud fallback for Sensitive workflows; suggestion unavailable or deterministic fallback | Route/model health, versions, request IDs without content | Restart/rollback/reacquire verified model; offline evaluation | Applicable P0 suite and model-version evidence pass |
| Agent Box unavailable | Personal Core policy/pause remains; model-dependent functions degrade | Device heartbeat/identity; no assumption of compromise | Repair or rebuild/re-enroll Agent Box; restore no unique authority from it | Host gate and GS-SEC-15 pass |
| Personal Core unavailable | Osun effects fail closed; use independent recovery pause/isolation; HA stays independent | External reachability, power/storage, last backup/ledger, provider state | Repair or clean replacement Core, RC-0/1/2 restore, fresh identities as needed | Full restore, pause, policy, ledger, and external reconciliation pass |
| Suspected Agent Box/Core compromise | SEV-1/2: isolate node, revoke identity/credentials, global/action/egress pause | Preserve minimal read-only evidence; inspect from clean environment | Rebuild from known-good artifacts; rotate; restore data from pre-compromise point | GS-SEC-15/16/37/40/44/45 and incident-specific tests pass; owner approval |
| Credential/token disclosure | Disconnect/revoke provider grant; action/egress kill for affected integration | Vault metadata, use/audit/provider history; never copy secret into case | Rotate/re-authorize with narrower scope; invalidate sessions/capabilities | Provider confirms revocation/new scope; secret scan passes |
| Bad update/model/skill/dependency | Quarantine candidate and rollback; retain restrictive current policy | Release manifest, signature/hash, SBOM, failed case/version | Restore prior known-good release or rebuild; correct migration | P0 suite, rollback-scope check, GS-SEC-18/19/25/40 pass |
| Ambiguous external action | Mark `unknown`; no blind retry | Invocation/idempotency/approval evidence and provider read-back | Reconcile, verify one effect, or offer exact compensation | GS-SEC-43 passes; owner sees true state |
| Backup overdue, corrupt, or restore fails | Backup health failed; prohibit new Sensitive/irreplaceable data and autonomy promotion | Job logs without content, manifest/integrity/key/restore report | Repair target/key/process and complete clean restore | GS-SEC-28/29 and full restore criteria pass |

---

## 10. Required exercises and evidence

| Exercise | Minimum mode/cadence | Pass evidence |
|---|---|---|
| Global pause while model is unavailable | Before any M1 live use; each relevant release | New collection/scheduling/model/tool effects denied; inspection/recovery available; GS-SEC-45 |
| Per-workflow disable with in-flight run | Before enabling each workflow | Trigger stops, unused capability revoked, no delayed effect, terminal state visible |
| Source disconnect and credential revocation | Before first integration; quarterly after reliance | Refresh stops, provider grant revoked, cache policy applied, other local functions remain |
| Action and egress kill | Before first cloud route or Calendar write | Zero adapter/cloud calls; deterministic recovery path remains |
| Power-loss and storage-failure injection | Before durable M1 data; after storage changes | GS-SEC-30/31 and no accepted partial state |
| Clean encrypted restore to replacement environment | Before Sensitive data; quarterly after reliance | Section 6 pass criteria plus measured RPO/RTO |
| Deletion followed by restore | Before owner deletion is claimed complete; after backup changes | GS-PRI-09 and GS-SEC-29; no resurrection |
| Compromised-node tabletop/rebuild | Before live data; annually and after identity/host design changes | Isolation, revoke, clean rebuild, fresh identity, restore, evidence, owner re-enable |
| Provider ambiguous-effect reconciliation | Before Calendar write | At most one effect, correct `unknown` handling, GS-SEC-43 |
| Recovery-key loss/damage tabletop | Before Sensitive data; quarterly custody check | Alternate approved copy can recover fixture; missing copy triggers replacement |

Exercise fixtures are synthetic until live-data gates pass. Real restore exercises must use an approved isolated destination and must never overwrite the only working or backup copy.

---

## 11. Stable requirements and scenario traceability

| Requirement | Normative statement | Primary verification |
|---|---|---|
| REC-01 | Every persistent class has an explicit backup or no-backup/rebuild policy | Section 4 inventory audit |
| REC-02 | Sensitive/irreplaceable durable data is blocked until encrypted clean-restore evidence exists | GS-SEC-28, GS-PRI-15 |
| REC-03 | RC-0/1/2 copies span separate device and offsite failure domains | Backup topology inspection and disaster exercise |
| REC-04 | Backup encryption keys and erasure authority are separated; no sole recovery secret is in the backup | Key-custody review and fixture recovery |
| REC-05 | Backup health requires restore verification, not job success alone | Section 6 report and GS-SEC-29 |
| REC-06 | Restore applies current restrictive policy, revocation, retention, and deletion suppression before retrieval/effects | GS-SEC-29/40, GS-PRI-09/16 |
| REC-07 | Global pause and action/egress kill are deterministic and independent of models | GS-SEC-45, GS-PRI-12 |
| REC-08 | A failed/unreachable policy or pause state denies collection, egress, and effects | Fault injection and GS-SEC-45 |
| REC-09 | Per-workflow/source disable and credential revocation do not disable owner inspection/recovery | GS-SEC-44/45, GS-PRI-20 |
| REC-10 | Pending actions/capabilities are revalidated after pause, restart, restore, or clock/freshness change | GS-OWN-04, GS-SEC-22/24/39/43 |
| REC-11 | Severity, notification, containment, evidence, recovery, and re-enable ownership are explicit | Incident tabletop and case record review |
| REC-12 | Power loss and storage failure cannot silently create accepted partial state | GS-SEC-30/31 |
| REC-13 | Compromised nodes are isolated/rebuilt with new trust rather than blindly restored as trusted machines | GS-SEC-15/16/44 |
| REC-14 | External provider state is reconciled before retry or compensation | GS-OWN-05, GS-SEC-43 |
| REC-15 | Recovery reports measured loss, timing, uncertainty, unresolved copies/effects, versions, and evidence | Restore-report schema/test |
| REC-16 | Re-enablement after a security incident is explicit, scoped, owner-controlled, and gradual | Incident tabletop and owner decision record |

---

## 12. M0-32 acceptance checklist

- [x] Data, configuration, identity, secret, model, release, ledger, cache, external-state, and recovery artifacts have backup or explicit no-backup policies.
- [x] Initial RPO/RTO classes and assumptions are defined.
- [x] Encrypted local/offsite backup and separate recovery-key custody are defined conceptually.
- [x] Restore verification is stronger than backup-job success.
- [x] Global pause, action/egress kill, per-workflow disable, source disconnect, credential revocation, node isolation, and safe reduced mode are defined.
- [x] Pause and kill do not depend on model correctness or availability.
- [x] SEV-1 through SEV-4, owner notification, evidence preservation, recovery ownership, and re-enablement are defined.
- [x] Power loss, disk failure/full state, corrupt/poisoned data, unavailable network/model/Core, compromised node, leaked credential, bad update, ambiguous action, and backup failure are covered.
- [x] Recovery requirements have stable identifiers and scenario mappings.
- [x] Systems-architecture consistency review is complete.

### 12.1 Internal architecture review record

Passed 2026-07-26. The concept preserves the accepted single-authority component map, Z0/Z3/Z4/Z8 trust boundaries, replaceable hardware/storage/model boundaries, deterministic policy and operations controls, Home Assistant independence, Calendar provider authority, local-only health/calorie policy, no-public-access rule, and M0 no-build boundary. Technology choices and measured feasibility remain intentionally deferred to M0-40/M0-41. Independent challenge remains required at M0-46.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as security/operations analyst
- Reviewer: Primary AI coordinator acting as systems architect; independent M0-46 review later
- Status: Agent complete; internal systems-architecture review passed
- Inputs used: Accepted data/autonomy boundaries, system architecture and trust flows, threat model, privacy impact assessment, version-zero contracts, and golden scenarios
- Assumptions: One owner; no public access; Home Assistant remains independent; exact storage/encryption/backup products are undecided; no Sensitive live data exists yet
- Open questions: Concrete backup media/provider/tool and costs; tested RPO/RTO feasibility; physical recovery-copy custody; exact infrastructure pause/isolation mechanism; retention-generation counts
- Acceptance evidence: Complete persistent-class disposition, recovery classes/targets, encrypted local/offsite/key concept, clean restore protocol, deterministic pause/kill controls, safe reduced mode, severity/incident ownership, twelve playbooks, ten exercises, and sixteen stable requirements
- Last updated: 2026-07-26
