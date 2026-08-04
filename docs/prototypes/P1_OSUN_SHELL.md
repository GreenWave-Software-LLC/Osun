# P1 Osun Shell and Agent Widget Architecture

**State:** Local Qwen Agent Box and extensible shell implemented; real Home Assistant canary pending \
**Prototype:** P1-SHELL-01 \
**Owner authorization:** 2026-07-27 \
**Host:** Windows Agent Box \
**Primary local model:** `qwen3.5:9b` through Ollama \
**Focused agents/widgets:** Lighting and Music \
**Last updated:** 2026-07-27

---

## 1. Product decision

The owner selected the P0 lighting interface as the visual foundation for Osun's main interface, with these changes:

1. Osun—not Lighting—is the application identity and primary conversation.
2. Focused agents appear only when relevant and own task-specific widgets.
3. Lighting becomes the first agent/widget rather than the application shell.
4. Qwen runs locally on the Windows Agent Box as the initial conversational model and agent router.
5. Voice is the expected long-term primary input, but the initial desktop UI must remain a high-quality complete interface.
6. Home Assistant on the Raspberry Pi remains the authority for real lights.

This expands the P0-LIGHT-01 implementation exception to P1-SHELL-01. P2-MUSIC-01 now adds Apple Music playback under its own [agent contract](P2_APPLE_MUSIC_AGENT.md). Each widget retains an independent default-off autonomy switch. Neither prototype authorizes ambient surveillance, unsolicited or background autonomy, arbitrary Home Assistant services, general shell/code execution, or persistent conversation capture.

---

## 2. End-to-end system at P1

```text
Owner text now / owner voice later
  -> local Osun shell on Windows
  -> local Qwen conversation + agent selection
       -> no tool: conversational response
       -> known typed tool: open a focused agent widget
            -> Lighting: exact proposal -> policy -> Home Assistant -> read-back
            -> Music: typed intent -> recent-device policy -> Windows Apple Music app -> media-session read-back
            -> focused compact/expandable widget exposes state and controls
```

Qwen is a proposer and router, not an execution authority. Its exposed tools, `open_lighting_widget()` and `open_music_widget()`, have no command arguments. Osun passes the original owner message—not model-authored device parameters—to the deterministic focused agent. Widget and execution policies remain independent of Qwen.

---

## 3. Agent and widget contract

Every future agent must define the following before activation:

| Contract field | Meaning |
|---|---|
| Agent ID and purpose | Stable identity and one bounded responsibility |
| Invocation schema | The exact model-visible tool with a closed argument schema |
| Proposal schema | Immutable, typed preview produced before any consequential action |
| Widget schema | User-visible state, targets, controls, and result representation |
| Authority source | System that owns truth and actual execution |
| Policy boundary | Allowlist, pause, confirmation, value bounds, and denial behavior |
| Autonomy control | Independent default-off switch; scope, trigger, audit, and precedence rules |
| Credential boundary | Where secrets live and which component may receive them |
| Verification contract | How success is observed instead of inferred |
| Audit contract | Minimum non-sensitive evidence and explicit exclusions |
| Revocation path | Immediate pause, credential removal, and provider-side revocation |

The shell accepts widget objects with stable `id`, `kind`, `title`, `agent`, and agent-owned state. The shell renders only registered widget kinds. Unknown model tool names and unknown widget kinds are ignored or rejected, never executed.

---

## 4. Local Agent Box

### 4.1 Selected runtime

- Ollama `0.32.4` installed as a native Windows runtime.
- Official Ollama `qwen3.5:9b` model, Q4_K_M, approximately 6.6 GB.
- API restricted by Osun to `http://127.0.0.1:11434` or an equivalent loopback hostname.
- Model store moved to `F:\Osun\ollama-models` to preserve the constrained system drive.
- Current hardware: Ryzen 9 5900X, 32 GB RAM, Radeon RX 7800 XT 16 GB.
- Observed local execution: model loaded 100% on GPU; warm tool routing approximately 1.3 seconds and warm short chat approximately 1.0 second during initial setup.
- First cold load was approximately 129 seconds. Osun therefore preloads Qwen in a background thread, reports a warming state, keeps it resident for 30 minutes after use, and unloads it when the app exits cleanly.

Ollama's Windows documentation lists native AMD support and its current hardware table includes the RX 7800 XT. The selected Qwen build advertises vision, tool use, and thinking, but P1 uses text plus one closed tool with thinking disabled for predictable latency.

### 4.2 Qwen authority

Qwen may:

- converse using short in-memory history;
- choose from the model-visible registered tools;
- request that a registered Lighting or Music widget open;
- explain a proposal after deterministic code creates it.

Qwen may not:

- access Home Assistant credentials;
- construct Home Assistant services or payloads;
- execute a proposal;
- access files, shell, network, email, calendar, memory stores, sensors, or other tools not explicitly registered;
- claim unavailable capabilities;
- persist raw conversation in P1.

Only twelve recent user/assistant messages are sent to the local model. Individual history entries and current input are bounded. Chat is cleared on New conversation, reload, or app exit and is not written to the prototype audit.

---

## 5. Shell behavior

The main UI contains:

- neutral Osun branding and a central conversation;
- visible local/ephemeral privacy status;
- Agent Box model readiness, warming, and missing-runtime states;
- an agent navigation area designed to grow without redesigning the conversation;
- no widget column until an agent is called, followed by a compact widget that expands on demand and visibly animates while its operation runs;
- Lighting targets, palette, exact values, manual/autonomous mode, Apply when manual, Connection, and Emergency pause inside the Lighting widget;
- Music request, recent-device reason, registered device choices, connection state, and result inside the Music widget;
- a unified Connection & safety dialog for Agent Box status and Home Assistant setup;
- a visible but disabled voice affordance reserved for the next interface milestone.

The shell is responsive down to a single-column layout. It uses no cloud assets, remote fonts, analytics, third-party JavaScript, or browser storage.

---

## 6. P1 safety and privacy invariants

1. The shell and model endpoints bind to loopback only.
2. Browser writes require the high-entropy session path and reject foreign origins.
3. Raw chat remains memory-only.
4. Qwen sees no Home Assistant token and receives no general execution tool.
5. Lighting remains `light.*` only, explicitly allowlisted, paused by default for live setup, exact-Apply by default, and state-read-back verified. Physical members derived from an allowlisted zone are authorized only while Home Assistant still reports them as members at execution time.
6. Unknown model tool calls are discarded.
7. Qwen unavailability cannot disable deterministic pause or lighting policy.
8. General requests never fabricate calendar, email, memory, sensor, or internet access.
9. Closing Osun through Quit unloads Qwen from GPU memory and stops the loopback shell.
10. Simulator remains a first-class fallback if the Pi, Qwen, or Home Assistant is unavailable.
11. Home Assistant grouped lights are modeled as zones with member-light metadata, separated from individual lights in the widget and connection allowlist.
12. Apply is idempotent per proposal ID: a duplicate local request returns the original report without a second Home Assistant service call.
13. A selected zone expands recursively to unique physical member lights before proposal construction, so themes coordinate a palette across bulbs and read-back verifies each bulb rather than an aggregate group value.
14. An explicitly named selected light takes precedence over broader selected zones; overlapping zone/member selections are deduplicated by entity ID.
15. Every consequential widget owns an independent autonomous-execution switch that defaults off; enabling one widget never grants another agent authority.
16. Lighting autonomy is request-triggered only. It executes the deterministic proposal, not model-authored Home Assistant parameters, and records the policy change, autonomous dispatch, and result locally.
17. Emergency Pause overrides both manual and autonomous execution. Home Assistant autonomy cannot be enabled unless live execution is enabled.

---

## 7. Acceptance evidence

| ID | Scenario | P1 success condition |
|---|---|---|
| SHELL-T01 | Open Osun | Neutral shell, Qwen state, no widget column, no Lighting application branding |
| SHELL-T02 | General planning question | Local Qwen response; no widget or fabricated tool access |
| SHELL-T03 | Ocean atmosphere request | Qwen calls only `open_lighting_widget`; Lighting produces Deep Ocean from original owner text |
| SHELL-T04 | Unknown model tool call | Unknown name ignored; no execution path |
| SHELL-T05 | Qwen offline, explicit light request | Deterministic Lighting preview still available |
| SHELL-T06 | Qwen offline, general request | Honest unavailable message; no invented answer |
| SHELL-T07 | Cold model | UI shows warming/thinking; background preload completes; later request is warm |
| SHELL-T08 | Manual Apply preview | With autonomy off, exact immutable proposal waits and executes once only after Apply |
| SHELL-T09 | New conversation | Chat/pending proposal cleared; widget dock reset |
| SHELL-T10 | Quit | Shell stops and Qwen model unload is requested |
| SHELL-T11 | Real light canary | One or two allowlisted lamps change and read back under direct observation |
| SHELL-T12 | Per-widget autonomy | Lighting switch on causes a new exact proposal to execute immediately and exposes its result without an Apply button |
| SHELL-T14 | Widget lifecycle | Agent widget is absent before a call, arrives compact, expands or collapses on click, and animates during a live widget operation |
| SHELL-T13 | Autonomous pause override | Emergency Pause denies autonomous dispatch and leaves real/simulated light state unchanged |

SHELL-T11 remains partially complete. Later on 2026-07-27, `homeassistant.local:8123` became reachable, local authentication/entity discovery succeeded, and real Hue grouped lights changed under owner observation. The grouped entities returned partial item verification, but the result aggregator incorrectly labeled an all-partial set as failed; an earlier duplicate Apply also replaced a useful result with a denial. Correct partial aggregation, proposal-level idempotency, and clearer grouped-light read-back reporting now prevent both misleading sequences, but a final supervised confirmation remains.

---

## 8. Next interface milestones

1. Restore or confirm the Home Assistant Pi endpoint and complete the supervised light canary.
2. Add push-to-talk voice input with a visible transcript and the same proposal boundary.
3. Keep the passed P2 Windows Apple Music real-playback canary in regression coverage; keep MusicKit optional.
4. Add durable owner-approved memory as a separate service; do not treat raw chat history as memory by default.
5. Package and sign the Windows application after the shell and local model lifecycle stabilize.

---

## Artifact status

- Author/agent: Primary AI coordinator acting as product engineer and security reviewer
- Owner decision: Main Osun chat shell, pluggable widgets, Lighting as first agent, local Qwen Agent Box
- Status: Shell and Qwen implemented; simulator verified; Home Assistant connected and actuating real lights; final supervised per-bulb zone verification remains
- Automated evidence: 92 tests passing with ResourceWarnings treated as errors; JavaScript syntax validation in the merge gate
- Runtime music evidence: Windows adapter changed `Blue In Green` to `So What`, then routed `play cardi b on my pc` to `Up by Cardi B`; both exact active Apple Music media-session titles were verified on 2026-08-04
- Runtime evidence: official Qwen model downloaded, 100% GPU placement observed, warm chat and tool-call smoke tests passed
- Visual evidence: neutral shell, agent dock, real-Qwen Lighting widget, exact Deep Ocean preview, separate Zones/Lights layouts with group membership, and default-off autonomous control/result states; visual QA found and corrected simultaneous empty/widget rendering
- Sensitive-data status: No token, real entity inventory, raw chat, or baseline data committed
- Last updated: 2026-08-04
