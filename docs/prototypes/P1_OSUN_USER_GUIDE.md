# Osun Shell - Local User Guide

**Version:** 0.2.0 \
**Host:** Windows Agent Box \
**Conversation model:** Local `qwen3.5:9b` \
**Available focused agent:** Lighting \
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

Select **New conversation** to clear the in-memory model history, close the active widget, and cancel any pending Lighting proposal. Reloading or quitting also clears visible chat.

---

## 3. Call the Lighting agent

Talk naturally:

- `I want to feel like I am in the ocean.`
- `Make the room warm and cozy.`
- `Set the lights to 35 percent.`
- `Make them purple over four seconds.`
- `Suggest a lighting theme for right now.`

Qwen calls the Lighting agent, and its widget appears in the right dock. The widget contains selected targets, an exact proposal, color swatches, individual light values, Apply, Cancel, Connection, and Emergency pause.

Qwen cannot execute the proposal. Select **Apply exact proposal** only after reviewing it.

---

## 4. Connect the real Home Assistant Pi

As of 2026-07-27, `homeassistant.local` resolves to `10.21.190.62`, but port `8123` is not accepting connections. Before setup:

1. Confirm the Home Assistant Pi is powered and its Ethernet link lights are active.
2. Open `http://homeassistant.local:8123` directly in a browser.
3. If it does not open, inspect the Pi/HA boot state or confirm its new IP in the router.
4. Confirm each real light can already be controlled from the Home Assistant dashboard.

Once Home Assistant opens:

1. Open your Home Assistant owner profile.
2. Create a Long-Lived Access Token for this prototype.
3. Open **Osun → Settings → Lighting agent**.
4. Select **Home Assistant** and enter the local URL.
5. Paste the token into **Access token · write only**.
6. Select **Test & discover lights**.
7. Select only one or two ordinary lamps for the first allowlist.
8. Enable live light execution but keep **Pause execution** checked.
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

If Osun reports partial or failed, do not repeatedly Apply. Pause the Lighting agent and use Home Assistant directly.

---

## 6. Local runtime record

| Component | Current location/state |
|---|---|
| Ollama | `%LOCALAPPDATA%\Programs\Ollama` |
| Qwen model | `qwen3.5:9b`, official Ollama build |
| Model store | `F:\Osun\ollama-models` through the user `OLLAMA_MODELS` setting |
| Osun configuration | `%LOCALAPPDATA%\Osun\lighting\config.json` |
| Protected light token | `%LOCALAPPDATA%\Osun\lighting\secrets\home_assistant_token.bin` |
| Content-minimized light audit | `%LOCALAPPDATA%\Osun\lighting\audit.jsonl` |

No raw chat is stored in these files.

---

## 7. Recovery

- Qwen unavailable: Lighting requests with explicit light language still produce deterministic previews.
- Pi unavailable: Use simulator mode or Home Assistant directly when it returns.
- Immediate action block: Select **Emergency pause** in the Lighting widget.
- Remove local lighting authority: Settings → **Delete light token**.
- Revoke provider authority: Revoke the token in the Home Assistant profile.
- Free GPU memory: Quit Osun from Settings; if necessary, run `ollama stop qwen3.5:9b`.
