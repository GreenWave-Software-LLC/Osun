# P0 Windows Lighting Assistant

**State:** P0-A and P0-B code complete; promoted into the P1 Osun shell; owner Home Assistant setup and P0-C canary pending \
**Owner authorization:** 2026-07-26 \
**Prototype:** P0-LIGHT-01 \
**Initial host:** Windows Agent Box \
**Device authority:** Home Assistant \
**Last updated:** 2026-07-26

> **Interface update (2026-07-27):** Lighting is no longer the primary application brand. This bounded implementation is preserved as the first agent and widget inside the general [P1 Osun Shell](P1_OSUN_SHELL.md). Its light-only authority, proposal, Apply, pause, credential, and read-back constraints remain in force.

---

## 1. Owner decision and scope amendment

The owner authorized a parallel product prototype while the private M0 baseline continues:

> Build a Windows app assistant that controls the owner's lights through chat, supports normal light functions, creates lighting themes from moods or imagined settings, and can offer its own theme suggestions. For example, “I want to feel like I'm in the ocean” should propose deep-blue lighting across the selected lights.

This decision creates a narrow exception to the earlier M0 no-build and no-Home-Assistant-control rules. It does **not** authorize a general Osun runtime, public/remote access, unrestricted Home Assistant administration, non-light devices, household-member data, ambient sensing, or direct model-to-tool execution.

The prototype runs in simulation by default. Live operation becomes available only after the owner supplies a local Home Assistant URL, stores a token through Windows-protected local storage, selects an explicit light-entity allowlist, enables live mode, clears emergency pause, reviews an exact proposal, and selects **Apply**.

---

## 2. Product outcome

The owner can open a Windows application and chat naturally:

- “Turn the lights off.”
- “Set these lights to 40 percent.”
- “Make the room warm and cozy.”
- “I want to feel like I'm in the ocean.”
- “Suggest something for tonight.”

Osun responds conversationally, creates a typed lighting proposal, shows target lights and exact brightness/color/transition values, and waits for Apply. After execution it reads current Home Assistant state and reports verified, partial, or failed status honestly.

Success for P0 means:

1. the simulator is pleasant and immediately runnable on the current Windows PC in a local Edge app-mode window;
2. the ocean request consistently produces a layered deep-blue theme;
3. on/off/toggle, brightness, named color, warm/cool white, transitions, mood themes, generated themes, and suggestions work;
4. no proposal executes before Apply;
5. only allowlisted `light.*` entities can execute;
6. emergency pause blocks execution without consulting a model;
7. the Home Assistant token never enters source control, chat history, ordinary logs, or theme generation;
8. live results are read back instead of inferred from a successful HTTP call.

---

## 3. Version-zero architecture

```text
Windows Edge app-mode UI on a random loopback session path
  -> deterministic intent/theme engine
  -> typed LightingProposal
  -> exact preview + owner Apply
  -> execution policy (mode, pause, allowlist, light-only schema)
      -> simulator adapter, or
      -> Home Assistant light adapter
           -> Home Assistant remains device authority
           -> state read-back and visible result
```

The initial theme engine is deterministic and local. It has curated themes plus a constrained palette generator for unfamiliar mood/place descriptions. A later local or cloud language model may improve conversation and creativity, but it may return only the same typed proposal schema. It will not receive the Home Assistant token or direct network/tool access.

### 3.1 Stable boundaries

| Component | Responsible for | Must not do |
|---|---|---|
| Windows loopback UI | Chat, light selection, exact preview, Apply/Cancel, settings, pause | Treat prose as execution authority or display a stored token |
| Intent/theme engine | Interpret supported light requests and produce bounded colors/brightness/transitions | Call Home Assistant, read credentials, or create arbitrary service names/payload fields |
| Execution policy | Enforce pause, live enablement, exact proposal, entity allowlist, value bounds | Accept model claims of permission |
| Simulator | Provide safe virtual lights and immediate feedback | Make network calls |
| Home Assistant adapter | Use the documented REST API for allowlisted light actions and read-back | Call non-`light` domains or use state-update endpoints as device control |
| Windows credential store | Protect the Home Assistant token for the current Windows user | Put token plaintext in configuration, repository, audit, or UI after save |
| Home Assistant | Own actual light integrations, entity capabilities, and physical state | Grant Osun general administrative authority merely because it is local |

---

## 4. Home Assistant contract

The adapter follows current official Home Assistant documentation:

- The REST API uses the same frontend port, normally `8123`, accepts JSON, and requires `Authorization: Bearer TOKEN`: [REST API](https://developers.home-assistant.io/docs/api/rest/).
- `GET /api/states` returns entity state objects used for discovery and read-back.
- Device control uses `POST /api/services/<domain>/<service>`; `POST /api/states/<entity_id>` is explicitly not a physical-device command path.
- The allowed services are only `light.turn_on`, `light.turn_off`, and `light.toggle`.
- Supported light inputs include `brightness_pct`, `rgb_color`, `color_temp_kelvin`, and `transition`: [Turn on a light](https://www.home-assistant.io/actions/light.turn_on/).
- Device color capabilities are determined from `supported_color_modes`: [Light entity](https://developers.home-assistant.io/docs/core/entity/light/).

The first token may be a Home Assistant long-lived access token because that is the documented REST setup path. It is treated as a prototype credential with broader risk than the desired future narrowly scoped integration identity. Revocation instructions and migration to least privilege remain required before broader reliance.

---

## 5. Functional requirements

| ID | Requirement |
|---|---|
| LGT-01 | Chat accepts normal on, off, toggle, brightness, named color, white temperature, and transition requests. |
| LGT-02 | Chat recognizes curated moods/settings including ocean, calm, cozy, focus, energize, sunset, forest, aurora, moonlight, and romantic. |
| LGT-03 | Unknown mood/place requests generate a deterministic bounded palette and are labeled as generated suggestions. |
| LGT-04 | “Suggest” and “surprise me” produce a time-aware but non-personal curated suggestion. |
| LGT-05 | Multi-light themes distribute palette colors across color-capable selected lights and safely degrade for dim-only/on-off lights. |
| LGT-06 | Every actionable request creates an immutable typed preview before execution. |
| LGT-07 | Apply executes the exact preview once; editing the chat creates a new proposal. |
| LGT-08 | Simulator is the default and requires no credentials or network. |
| LGT-09 | Live mode requires URL, protected token, nonempty light allowlist, explicit enablement, and pause off. |
| LGT-10 | Live execution calls only documented Home Assistant light services and performs state read-back. |
| LGT-11 | Emergency pause cancels the pending proposal and blocks new executions deterministically. |
| LGT-12 | Audit records contain proposal/result IDs, mode, action type, target IDs, and outcome—not raw chat or credentials. |

---

## 6. Security and privacy properties

- The presentation server binds only to `127.0.0.1` on a random port, uses a high-entropy per-launch session path, rejects cross-origin writes, applies a restrictive Content Security Policy, and creates no LAN/public listener.
- URL schemes are restricted to HTTP/HTTPS; HTTPS certificate verification remains enabled by default.
- Entity IDs must begin with `light.` and be present in the saved allowlist at execution time.
- Service names and payload keys are code allowlists, never model/user-selected strings.
- Brightness is clamped to 1-100 for on actions, RGB channels to 0-255, color temperature to 2000-6500 K, and transition to 0-30 seconds.
- A proposal ID can execute at most once in one app session.
- Live mode starts paused after first configuration or any uncertain configuration state.
- Token display is write-only: a saved token is not put back into a UI text field.
- Connection and execution errors redact authorization headers and token values.
- Raw chat is not persisted in the prototype audit log.
- Real light names/entity IDs remain local application configuration and are not committed.
- The owner uses Home Assistant directly if Osun is unavailable; Osun does not replace device safety or authority.

---

## 7. P0 acceptance scenarios

| ID | Scenario | Expected result |
|---|---|---|
| LGT-T01 | “I want to feel like I'm in the ocean” with four simulated lights | Preview uses Ocean, layered blue palette, bounded brightness/transition, zero execution until Apply |
| LGT-T02 | “Turn all lights off” | Exact off preview; Apply turns each selected/allowed light off |
| LGT-T03 | “Set lights to 35%” | Turn-on preview at 35%; dim-capable lights report verified state |
| LGT-T04 | “Make it purple” | Color-capable lights use purple; dim-only lights receive brightness only |
| LGT-T05 | “Suggest something” | One curated theme is proposed with a short rationale; no action before Apply |
| LGT-T06 | Unknown “bioluminescent cave” request | Deterministic bounded generated palette with visible label |
| LGT-T07 | Apply while paused | Denied locally; zero adapter invocation |
| LGT-T08 | Proposal contains non-allowlisted or non-light entity | Denied before network; zero Home Assistant call |
| LGT-T09 | Home Assistant returns 401/timeout | Failed result with safe message and no token leakage/retry storm |
| LGT-T10 | Service acknowledges but read-back disagrees | Partial/unverified result; never claim success |
| LGT-T11 | Apply same proposal twice | Second attempt denied; zero duplicate service call |
| LGT-T12 | Simulator smoke sequence | Ocean -> brightness -> off operates without dependencies or network |

---

## 8. Deliberate non-scope

- Voice, mobile, tray/background agents, startup tasks, and remote access.
- Automatic themes based on inferred mood, camera, microphone, presence, health, calendar, or behavior.
- Schedules, geofencing, household/guest support, or proactive actions without a visible request.
- Switches, locks, doors, climate, media, security, appliances, or arbitrary Home Assistant services.
- Direct model access to Home Assistant, credentials, network, filesystem, or execution.
- Training/fine-tuning on conversations or light behavior.
- Production installer, auto-update, code signing, or completed backup/recovery deployment.

---

## 9. Implementation stages

1. **P0-A runnable simulator - complete:** Windows app-mode chat UI, themes, normal functions, selection, exact preview, Apply/Cancel, pause, and tests.
2. **P0-B local Home Assistant setup code - complete:** Protected token, connection test, light discovery, explicit allowlist, live enable/pause, light-only calls, read-back.
3. **P0-C owner canary:** One or two non-safety-critical lights, supervised commands, no background automation, rollback by disabling live mode/revoking token.
4. **Later:** Package as a signed Windows executable, replace prototype token with a narrower integration identity if feasible, add a local conversational model behind the typed proposal boundary, and evaluate richer per-device capability handling.

The current implementation may complete P0-A and the P0-B code path without claiming P0-C evidence. Real canary execution requires the owner's Home Assistant URL, token, selected entity IDs, and direct observation.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as product engineer and security reviewer
- Reviewer: Owner for scope; independent implementation review pending
- Status: P0-A and P0-B code complete; P0-C real-device canary not started
- Assumptions: Home Assistant is local and reachable from Windows; actual light integrations/entities may not yet be configured; Python standard library plus Microsoft Edge app mode is acceptable for the first reversible slice
- Open questions: Actual light brands/capabilities, Home Assistant URL/entity inventory, first canary allowlist, packaging preference, future model choice, narrower credential approach
- Acceptance evidence: Owner request, narrow scope amendment, typed architecture, official API contract, twelve requirements/scenarios, 23 automated tests, JavaScript syntax validation, visual browser QA, readable Ocean preview, verified simulator Apply, and deterministic pause
- Last updated: 2026-07-26
