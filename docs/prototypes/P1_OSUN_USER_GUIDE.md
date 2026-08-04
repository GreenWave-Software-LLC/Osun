# Osun Shell - Local User Guide

**Version:** 0.4.0 \
**Host:** Windows Agent Box \
**Conversation model:** Local `qwen3.5:9b` \
**Available focused agents:** Lighting and Music \
**Chat storage:** Memory-only for the current app session

---

## 1. Start Osun

Double-click `Launch Osun.cmd` in the repository root.

The launcher:

1. checks the loopback Ollama service;
2. starts it in the background if necessary;
3. starts the local Osun service on a random `127.0.0.1` port;
4. opens Osun in Microsoft Edge app mode;
5. begins preloading Qwen into GPU memory.

For a visible diagnostic console, run:

```powershell
.\run_osun.ps1
```

The first model load after a restart may take around two minutes on the current system. The Agent Box card reports **Warming model on GPU** while this happens. Warm requests were approximately one second in the initial setup test.

Use **Settings → Quit Osun** to stop the shell cleanly and request that Ollama unload Qwen from GPU memory.

---

## 2. Use the main conversation

General prompts go to local Qwen. Examples:

- `Help me think through my priorities for today.`
- `Turn this vague goal into three small next steps.`
- `Ask me questions to understand why I keep avoiding this task.`

P1 Qwen does not yet have calendar, email, web, file, memory, or task-manager access. It should say so instead of pretending.

Select **New conversation** to clear the in-memory model history, close the active widget, and cancel pending agent work. Reloading or quitting also clears visible chat.

---

## 3. Call the Lighting agent

Talk naturally:

- `I want to feel like I am in the ocean.`
- `Make the room warm and cozy.`
- `Set the lights to 35 percent.`
- `Make them purple over four seconds.`
- `Suggest a lighting theme for right now.`

Qwen calls the Lighting agent, and only then does a compact widget appear in the right dock. Select the compact card to expand it; select its minus control to collapse it again. While a widget operation is in progress, its icon and top edge animate and its status reads **Running**. The expanded widget separates Home Assistant grouped-light targets under **Zones** from physical entities under **Lights**. A zone shows the member-light names Home Assistant provides. The widget also contains an exact proposal, color swatches, individual target values, its manual/autonomous mode, Connection, and Emergency pause.

For a theme, a selected zone expands into its physical member lights. Osun assigns a coordinated palette across those members and the exact proposal shows one row per physical light. Selecting both a zone and one of its members does not duplicate the member. If you name one selected light—for example, **“make the desk lamp blue”**—only that individual light enters the proposal, even while its zone is also selected.

Qwen never executes a light command directly. With the default manual policy, select **Apply exact proposal** only after reviewing it. If you explicitly enable the Lighting widget's autonomous policy, deterministic code applies each new exact proposal from your request immediately and shows the proposal and execution result afterward.

---

## 4. Connect the real Home Assistant Pi

On 2026-07-27, `homeassistant.local` resolved to `10.21.190.62` and Home Assistant API reachability was verified. If it becomes unavailable later:

1. Confirm the Home Assistant Pi is powered and its Ethernet link lights are active.
2. Open `http://homeassistant.local:8123` directly in a browser.
3. If it does not open, inspect the Pi/HA boot state or confirm its new IP in the router.
4. Confirm each real light can already be controlled from the Home Assistant dashboard.

To configure or reconnect Home Assistant:

1. Open your Home Assistant owner profile.
2. Create a Long-Lived Access Token for this prototype.
3. Open **Osun → Settings → Lighting agent**.
4. Select **Home Assistant** and enter the local URL.
5. Paste the token into **Access token · write only**.
6. Select **Test & discover lights**.
7. Select only one or two ordinary lamps for the first allowlist.
8. Enable live light execution, leave **Autonomous execution** off, and keep **Pause execution** checked.
9. Save settings.

Never paste the token into chat, Git, documentation, screenshots, or messages. Osun encrypts it for the current Windows user with DPAPI and never displays it after save.

---

## 5. Supervised real-light canary

After successful discovery:

1. Confirm direct Home Assistant control still works.
2. Reopen Settings and confirm the exact one- or two-light allowlist.
3. Clear **Pause execution** and save.
4. Ask Osun for `Set the selected lights to blue at 25 percent.`
5. Review every target and value in the widget.
6. Observe the room and select **Apply exact proposal** once.
7. Require a verified Home Assistant read-back result.
8. Test Cancel, off, brightness, Ocean, and Emergency pause.

If Osun reports **targets changed; attribute read-back review needed** for a zone, confirm the visible result and Home Assistant state without applying again. This means on/off actuation was observed but the zone's aggregate color or brightness did not exactly match. If Osun reports **failed**, pause the Lighting agent and use Home Assistant directly.

If Osun reports **denied**, the request was stopped locally before Home Assistant. Open Connection and verify all three canary gates: only the intended lamp is selected in the allowlist, **Enable live light execution** is checked, and **Pause execution** is cleared. Save, create a fresh proposal, and review it again before Apply.

If a Hue room or zone cannot expose resolvable member identities, Osun may fall back to the grouped entity and request attribute review because Home Assistant reports aggregate brightness or color. When member identities are available, Osun controls and verifies each physical light instead. Osun does not repeat the Home Assistant service call when the same Apply request is received twice; it returns the original report.

Natural wording such as **“Change the lights to a bright morning”** resolves directly to the built-in **Bright Morning** theme; a follow-up “yes” is not required.

---

## 6. Use autonomous Lighting execution

Each consequential agent widget has its own execution policy. Lighting is the first implementation, and its switch is off by default. Enabling Lighting does not enable any future agent.

To stop approving every Lighting proposal:

1. Open **Settings → Lighting agent**.
2. Confirm the Home Assistant allowlist contains only lights and zones you want Osun to control.
3. Check **Enable live light execution**.
4. Check **Autonomous execution**.
5. Clear **Pause execution** and save.
6. Make a new lighting request in chat.

Osun will still construct the same exact proposal, enforce the light-only allowlist and value limits, execute it once, read the result back, and display both the settings and the result in the Lighting widget. The audit records the policy change, autonomous dispatch, targets, actions, and verification result without storing raw chat or credentials.

Autonomy does not mean background control: Lighting acts only after a new owner request routes to it. **Emergency pause** always wins, even while autonomy remains enabled. Turn off **Autonomous execution** to restore Apply for future proposals. Delete the light token or revoke it in Home Assistant to remove the authority entirely.

---

## 7. Use the Music agent

Ask naturally: `play Kind of Blue`, `pause the music`, `resume the music`, `next song`, or `previous song`. If no registered device has successfully played music in the last five minutes, Osun asks where to play and the compact Music widget offers **This PC**. After successful playback, another request within 300 seconds routes to that device automatically. At 301 seconds, Osun asks again. You can always name a device explicitly: `play Discovery on This PC`.

For real playback, first open the full Windows **Apple Music** app, sign in, and play one song normally. Then open **Settings -> Music agent**, choose **Windows app**, save, and select **Test Apple Music app**. No Apple Developer Program membership or developer token is required. Osun searches Apple's public catalog, searches for the validated result inside the installed app, starts the visible matching song, and verifies playback through Apple Music's Windows media session. Keep Osun and Apple Music under the same Windows user and privilege level; do not run either as Administrator. If Apple Music is in MiniPlayer/full-screen mode, has never been opened, or is signed out, Osun stops with a specific recovery instruction.

The initial adapter controls only the Apple Music app on this PC. It does not broadcast global media keys and cannot remotely take over an arbitrary iPhone or HomePod. Those require future registered companion or Home Assistant/Music Assistant adapters. Recent-device evidence is memory-only and resets when Osun restarts. MusicKit remains an optional future provider; never paste an Apple private `.p8` signing key into Osun. See the [P2 Music contract](P2_APPLE_MUSIC_AGENT.md) for setup, limitations, and canary steps.

## 8. Local runtime record

| Component | Current location/state |
|---|---|
| Ollama | `%LOCALAPPDATA%\Programs\Ollama` |
| Qwen model | `qwen3.5:9b`, official Ollama build |
| Model store | `F:\Osun\ollama-models` through the user `OLLAMA_MODELS` setting |
| Osun configuration | `%LOCALAPPDATA%\Osun\lighting\config.json` |
| Protected light token | `%LOCALAPPDATA%\Osun\lighting\secrets\home_assistant_token.bin` |
| Content-minimized light audit | `%LOCALAPPDATA%\Osun\lighting\audit.jsonl` |
| Music configuration | `%LOCALAPPDATA%\Osun\music\config.json` |
| Optional protected MusicKit developer token | `%LOCALAPPDATA%\Osun\music\developer-token.bin` |

No raw chat is stored in these files.

---

## 9. Recovery

- Qwen unavailable: Lighting requests with explicit light language still produce deterministic previews.
- Pi unavailable: Use simulator mode or Home Assistant directly when it returns.
- Immediate action block: Select **Emergency pause** in the Lighting widget.
- Remove local lighting authority: Settings → **Delete light token**.
- Remove optional MusicKit authority: Settings -> **Delete music token**. Windows app mode stores no Apple credential in Osun; sign out in Apple's app to revoke that session.
- Revoke provider authority: Revoke the token in the Home Assistant profile.
- Free GPU memory: Quit Osun from Settings; if necessary, run `ollama stop qwen3.5:9b`.
