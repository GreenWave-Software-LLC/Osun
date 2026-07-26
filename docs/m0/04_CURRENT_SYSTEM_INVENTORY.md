# Osun Current System Inventory

**Task:** M0-11 - Inventory current systems, devices, services, and data sources \
**State:** In progress; Windows Agent Box inspected, remaining systems require owner input \
**Technology scout:** Primary AI coordinator \
**Last updated:** 2026-07-25

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
| Pi model | At least one Raspberry Pi 4 Model B; exact model per unit UNCONFIRMED |
| RAM | UNCONFIRMED |
| Storage type/capacity | UNCONFIRMED |
| Operating system/version | One unit runs Raspberry Pi OS; one runs Home Assistant OS; versions UNCONFIRMED |
| Current use | Home Assistant server is running but not configured; third unit is unconfigured |
| Network connection | UNCONFIRMED |
| Power supply/UPS | UNCONFIRMED |
| Cooling/case | A cooling fan/block was reported; unit mapping UNCONFIRMED |
| Backup method | No backups currently exist |
| Remote administration method | UNCONFIRMED |
| Availability for Osun experiments | All units may be reconfigured; timing and preservation requirements need confirmation |

Owner questions:

1. Are all three units Raspberry Pi 4 Model B, and how much RAM does each have?
2. What storage does each use: microSD, USB SSD, NVMe, or something else, and what capacity?
3. Which physical unit has the cooling fan/block?
4. Is each unit connected by Ethernet or Wi-Fi?
5. What power supplies are used, and is any UPS present?
6. Should the current Raspberry Pi OS and Home Assistant OS installations be preserved before later reconfiguration?

---

## 4. Home Assistant

**Status:** Server running on one Raspberry Pi using Home Assistant OS; no integrations or automations configured. No Home Assistant access attempted.

| Attribute | Current value |
|---|---|
| Currently deployed | Yes |
| Deployment type | Home Assistant OS |
| Host hardware | One of the Raspberry Pi units; exact model/RAM/storage UNCONFIRMED |
| Version/update channel | UNCONFIRMED |
| Existing integrations | None configured |
| Existing automations | None configured |
| Backup method | None currently exists |
| External access | UNCONFIRMED |
| Osun integration timing | Planned for M4, unless requirements change |

Owner questions:

1. Which Raspberry Pi unit hosts Home Assistant OS?
2. Is Home Assistant reachable only on the home network, or is external access enabled?
3. Confirm that it controls no safety- or security-relevant devices because nothing is configured.

---

## 5. Personal devices and external services

No accounts were inspected. The owner should name products and broad usage only; credentials and content are not needed.

| Category | Product/system | Needed for selected workflow | Data sensitivity | API/export known | Status |
|---|---|---|---|---|---|
| Phone ecosystem | Apple iPhone | TBD | Potentially sensitive | TBD | Owner confirmed |
| Calendar | Apple Calendar and Google Calendar | Likely daily planning | Personal/sensitive | TBD | Owner confirmed products |
| Tasks/reminders | UNCONFIRMED | Likely all initial workflows | Personal | TBD | Owner input |
| Notes/knowledge | Apple Notes | Likely capture/review | Personal/sensitive | TBD | Owner confirmed product |
| Email | Gmail | Candidate inbox/job workflow | Sensitive | TBD | Owner confirmed product |
| Wearables/health | Apple Watch | Candidate health workflows; data use not approved | Sensitive | TBD | Owner confirmed product |
| Cloud storage | iCloud, Google cloud storage, and OneDrive for project path | Project documents and future integrations TBD | Personal/sensitive | TBD | Google product name needs confirmation |
| Cloud AI subscriptions/APIs | ChatGPT Plus, Kimi API, Claude reactivation available, other APIs acceptable if needed | Optional model routing later | Depends on payload | TBD | ChatGPT subscription is not assumed to include API access |
| Smart-home platforms | Home Assistant intended | M4 | Personal/sensitive | TBD | Owner input |
| Password/secrets manager | Apple passkeys used; dedicated password/secrets manager UNCONFIRMED | M1 security design | Restricted | TBD | Passkeys do not by themselves define server secret storage |
| Backup destinations | None currently exists | M1 recovery design | Sensitive/restricted | TBD | Early project risk |

Owner questions:

1. Which task/reminder application do you use, if any (for example Apple Reminders)?
2. By Google storage, do you mean Google Drive?
3. Do you use Apple Passwords/iCloud Keychain as a password manager, or only passkeys?
4. Which calendar is the primary source when Apple and Google contain overlapping events?
5. Are Apple Watch health/fitness data and calorie data allowed for future local analysis, or should that decision wait for M0-14?

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
- [ ] Raspberry Pi facts confirmed; unit mapping, RAM, storage, network, and power remain open.
- [ ] Home Assistant facts confirmed; host mapping and external access remain open.
- [ ] Calendar, task, note, phone, AI, secrets, and backup systems named.
- [ ] Each system required by a selected workflow is present or marked missing.
- [ ] Authentication method, API/export availability, sensitivity, expected rate, and offline behavior recorded for selected systems.
- [ ] Unknowns remain explicitly unconfirmed rather than guessed.
- [ ] Owner reviews the inventory for accuracy.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as technology scout
- Reviewer: Owner and future privacy analyst
- Status: Owner review
- Inputs used: Read-only Windows inspection, command/version checks, owner project statements
- Assumptions: Exact Pi unit mapping, RAM/storage/network/power, task app, password manager, storage purpose/media, and local-AI support remain unconfirmed
- Open questions: Sections 3-5
- Acceptance evidence: Windows facts recorded without credentials, identifiers, or personal content; remaining acceptance items are explicit
- Last updated: 2026-07-25
