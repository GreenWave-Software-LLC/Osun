# Osun Current System Inventory

**Task:** M0-11 - Inventory current systems, devices, services, and data sources \
**State:** Accepted; core inventory and selected-workflow integration validation complete \
**Technology scout:** Primary AI coordinator \
**Last updated:** 2026-07-26

---

## 1. Collection boundary

This inventory records capabilities and integration constraints, not personal content.

Excluded by design:

- passwords, API keys, recovery keys, and tokens;
- usernames, email addresses, IP addresses, MAC addresses, device serial numbers, and account identifiers;
- file listings and personal document contents;
- calendar events, messages, contacts, health records, financial data, or location history;
- data about other people.

Sources used so far:

- read-only Windows system inspection approved under M0;
- command availability and version checks;
- owner statements in the master plan.

---

## 2. Windows Agent Box

### 2.1 Hardware and operating system

| Attribute | Observed value | Confidence/notes |
|---|---|---|
| Intended role | Interactive Agent Box, local AI, skills, workflows, heavy processing | Confirmed by owner vision |
| Operating system | Microsoft Windows 11 Pro, 64-bit | Observed locally |
| OS version/build | 10.0.26200 / build 26200 | Observed locally; servicing channel not assessed |
| CPU | AMD Ryzen 9 5900X | Observed locally |
| CPU topology | 12 physical cores / 24 logical processors | Observed locally |
| System memory | 31.9 GB usable/reported | Observed locally |
| GPU | AMD Radeon RX 7800 XT | Observed locally |
| GPU memory | Not confirmed | WMI value was not treated as authoritative; benchmark later |
| Manufacturer/model | Generic system-board identifiers | No useful OEM model detected; serial identifiers intentionally excluded |

### 2.2 Storage volumes

| Volume | File system | Approx. size | Approx. free | Initial observation |
|---|---|---:|---:|---|
| C: | NTFS | 231.1 GB | 24.6 GB | Limited free space for large models, containers, or datasets |
| E: | NTFS | 931.5 GB | 656.8 GB | Candidate capacity; media type, backup status, and purpose unconfirmed |
| F: | NTFS | 917.4 GB | 871.6 GB | Candidate capacity; media type, backup status, and purpose unconfirmed |

The repository is currently located under a OneDrive-synchronized Desktop path. Whether live runtime databases or high-churn model artifacts should be stored there is an **UNCONFIRMED operational risk** for M0-40/M0-41; the project documents may remain synchronized, but runtime storage needs explicit durability and sync-conflict evaluation.

### 2.3 Development and runtime tools

| Tool/capability | Observed state | Notes |
|---|---|---|
| Git | Installed; version 2.54.0.windows.1 | Repository operational |
| Python | Installed; version 3.14.6 | Ecosystem compatibility must be evaluated; no runtime choice implied |
| pip | Command present | Environment isolation approach unselected |
| Node.js | Installed; version 24.16.0 | Path is part of the Codex tooling environment; persistence outside Codex unconfirmed |
| WSL launcher | Present | WSL subsystem/distribution is not installed |
| Docker | Not detected | No installation authorized during M0 |
| Podman | Not detected | No installation authorized during M0 |
| Ollama | Not detected | No local-model runtime detected |
| llama.cpp commands | Not detected | No local-model runtime detected |
| ROCm tooling | Not detected | AMD acceleration path requires later evidence |
| uv / pipx / Poetry | Not detected | Python project-management choice remains open |
| CMake | Not detected | Native-build needs remain open |
| Rust/Cargo | Not detected | Language choice remains open |
| Go | Not detected | Language choice remains open |

### 2.4 Initial capability assessment

Facts:

- CPU and memory are sufficient for M0 work and ordinary development.
- The discrete AMD GPU makes local inference a meaningful Week 4 benchmark candidate.
- The system has substantial free space outside C:, but media type, performance, encryption, and backup are unknown.
- Container and local-model runtimes are not currently available as commands.
- WSL is not currently installed despite the Windows launcher being present.

Questions, not decisions:

- Which Windows-native local inference runtimes support the GPU reliably on this exact configuration?
- Should model files and runtime data live on E: or F:, and which volume is backed up?
- Does Python 3.14 have sufficient library compatibility, or should Osun use a project-pinned runtime?
- Is a container layer worth its maintenance and resource cost for a one-person Raspberry Pi/Windows system?
- Should the repository remain in OneDrive while runtime state is stored elsewhere?

---

## 3. Raspberry Pi Personal Core

**Status:** Partial owner inventory received; no network probing or remote access attempted.

| Attribute | Current value |
|---|---|
| Pi units | Three units described by owner |
| Pi model | Three Raspberry Pi 4 Model B units, owner-reported |
| RAM | 4 GB per unit, owner-reported with mild uncertainty |
| Storage type/capacity | 128 GB SD card per unit, owner-reported |
| Operating system/version | One unit runs Raspberry Pi OS; one runs Home Assistant OS; versions UNCONFIRMED |
| Current use | Home Assistant server is running but not configured; third unit is unconfigured |
| Network connection | Home Assistant unit uses Ethernet; Raspberry Pi OS and unconfigured units use Wi-Fi |
| Power supply/UPS | UNCONFIRMED |
| Cooling/case | A cooling fan/block was reported; unit mapping UNCONFIRMED |
| Backup method | No backups currently exist |
| Remote administration method | UNCONFIRMED |
| Availability for Osun experiments | Units may eventually be reconfigured, but existing Raspberry Pi OS and Home Assistant OS installations must be preserved |

Owner questions:

Remaining non-blocking questions:

1. Which physical unit has the cooling fan/block?
2. What power supplies are used, and is any UPS present?
3. Confirm installed OS versions during a later authorized device inspection.

---

## 4. Home Assistant

**Status:** Server running on one Raspberry Pi using Home Assistant OS; no integrations or automations configured. No Home Assistant access attempted.

| Attribute | Current value |
|---|---|
| Currently deployed | Yes |
| Deployment type | Home Assistant OS |
| Host hardware | Raspberry Pi 4 Model B, approximately 4 GB RAM, 128 GB SD card, Ethernet |
| Version/update channel | UNCONFIRMED |
| Existing integrations | None configured |
| Existing automations | None configured |
| Backup method | None currently exists |
| External access | UNCONFIRMED; no external access should be assumed |
| Osun integration timing | Planned for M4, unless requirements change |

Owner questions:

Remaining non-blocking questions:

1. Is Home Assistant reachable only on the home network, or is external access enabled?
2. Confirm installed version during a later authorized device inspection.

Because no integrations or automations are configured, it currently controls no safety- or security-relevant devices.

---

## 5. Personal devices and external services

No accounts were inspected. The owner should name products and broad usage only; credentials and content are not needed.

| Category | Product/system | Needed for selected workflow | Data sensitivity | API/export known | Status |
|---|---|---|---|---|---|
| Phone ecosystem | Apple iPhone | TBD | Potentially sensitive | TBD | Owner confirmed |
| Calendar | Apple Calendar and Google Calendar | Likely daily planning | Personal/sensitive | TBD | Owner confirmed products |
| Tasks/reminders | None currently used | Candidate local Osun capability | Personal | Not applicable yet | Owner confirmed |
| Notes/knowledge | Apple Notes | Likely capture/review | Personal/sensitive | TBD | Owner confirmed product |
| Email | Gmail | Candidate inbox/job workflow | Sensitive | TBD | Owner confirmed product |
| Wearables/health | Apple Watch | Candidate health workflows; data use not approved | Sensitive | TBD | Owner confirmed product |
| Cloud storage | iCloud, Google Drive, and OneDrive for project path | Project documents and future integrations TBD | Personal/sensitive | TBD | Owner confirmed products |
| Cloud AI subscriptions/APIs | ChatGPT Plus, Kimi API, Claude reactivation available, other APIs acceptable if needed | Optional model routing later | Depends on payload | TBD | ChatGPT subscription is not assumed to include API access |
| Smart-home platforms | Home Assistant intended | M4 | Personal/sensitive | TBD | Owner input |
| Password/secrets manager | Apple Passwords/iCloud Keychain and passkeys | M1 security design | Restricted | TBD | Server secret storage remains a separate M1 decision |
| Backup destinations | None currently exists | M1 recovery design | Sensitive/restricted | TBD | Early project risk |

Owner questions:

Confirmed owner choices:

- No task or reminder application is currently used.
- Google storage means Google Drive.
- Apple Passwords/iCloud Keychain and passkeys are used.
- Google Calendar is the primary calendar.
- Future local analysis of Apple Watch and calorie data is allowed in principle; exact fields, retention, purpose, and consent controls remain for M0-14.

### 5.1 Selected-workflow integration validation

| Source/capability | Selected workflows | Access/authentication path | Expected M0/M1 rate | Offline behavior | M0 readiness |
|---|---|---|---|---|---|
| Owner goals and dreams | WF-01 | Explicit local owner entry; no external authentication | Updated on owner request; reviewed weekly | Fully local | Ready for design |
| Google Calendar | WF-01, WF-02 | Google Calendar REST API with OAuth 2.0; begin with the narrowest read-only event scope that satisfies planning | Read on owner request and limited scheduled refresh; exact quota/rate set after prototype | Use an encrypted local cache with visible freshness; never claim current state while offline | Research validated; credentials not created during M0 |
| Health/energy check-in | WF-01, WF-02 | Explicit local self-report initially | Optional one or two small entries per day | Fully local | Ready for design |
| Meal/workout preferences | WF-02 | Explicit local owner entry | Weekly and on owner correction | Fully local | Ready for design |
| Apple Watch/Health data | WF-02 and later evaluation | Future iPhone companion using HealthKit fine-grained, per-type permission; manual XML export is a possible research fallback | At most daily summary for initial use; exact fields/rate wait for M0-14 | Last authorized local summary with visible freshness; no silent inference from missing permissions | Deferred from M1; pathway validated |
| Meal/calorie record | WF-03 | Manual local text entry first; no nutrition API selected | Owner-triggered per meal and daily review | Core capture/calculation remains local | Ready for design; reference data undecided |

Google documents its Calendar interface as a REST API and provides narrow OAuth scopes including read-only event access; Osun should request only the minimum scope needed: [Google Calendar API overview](https://developers.google.com/workspace/calendar/api/guides/overview) and [Calendar OAuth scopes](https://developers.google.com/workspace/calendar/api/auth).

Apple HealthKit stores health/fitness data on Apple platforms and requires fine-grained permission for each data type. Permission may be limited to a recent time window and can be changed by the owner. Therefore, Windows and Pi services should not be designed as if they can read Apple Watch data directly: [HealthKit overview](https://developer.apple.com/documentation/healthkit), [HealthKit authorization](https://developer.apple.com/documentation/HealthKit/authorizing-access-to-health-data), and [Apple Health XML export](https://support.apple.com/en-euro/guide/iphone/iph5ede58c3d/ios).

These sources validate possible access paths, not authorization to implement or collect data during M0.

---

## 6. Integration readiness categories

Systems will later be labeled:

- **Ready:** supported interface/export, owner authorization, and necessary security controls exist.
- **Research needed:** likely usable, but interface, terms, or constraints are unknown.
- **Manual first:** no safe integration is required for the initial workflow.
- **Deferred:** outside the current milestone or privacy/risk boundary.
- **Prohibited:** owner or policy disallows integration.

No system is marked Ready during this initial inventory.

---

## 7. M0-11 acceptance checklist

- [x] Windows Agent Box hardware, OS, storage, and relevant command availability recorded.
- [x] Serial numbers, network identifiers, credentials, and personal contents excluded.
- [x] Core Raspberry Pi facts confirmed; power/cooling mapping and OS versions remain explicit unknowns.
- [x] Core Home Assistant facts confirmed; external access and version remain explicit unknowns.
- [x] Calendar, task, note, phone, AI, secrets, and backup systems named.
- [x] Each system required by a selected workflow is present or marked missing.
- [x] Authentication method, API/export availability, sensitivity, expected rate, and offline behavior recorded for selected systems at M0 precision.
- [x] Unknowns remain explicitly unconfirmed rather than guessed.
- [x] Owner reviews the inventory for accuracy.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as technology scout
- Reviewer: Owner and future privacy analyst
- Status: Accepted; M0-11 complete
- Inputs used: Read-only Windows inspection, command/version checks, owner project statements
- Assumptions: Owner-reported Pi RAM is mildly uncertain; power/cooling, OS versions, Home Assistant external access, storage purpose/media, and local-AI support remain unconfirmed
- Open questions: Non-blocking hardware questions in Sections 3-4 and implementation details deferred to later decisions
- Acceptance evidence: Windows and core Pi/service facts recorded without credentials, identifiers, or personal content; owner reviewed the inventory; selected sources have access, rate, sensitivity, and offline expectations
- Last updated: 2026-07-26
