# Osun Lighting Assistant - Prototype User Guide

> **Superseded interface:** Lighting now runs as an agent widget inside the main Osun shell. Use the [P1 Osun Shell User Guide](P1_OSUN_USER_GUIDE.md). The Home Assistant safety and canary instructions below remain applicable.

**Version:** 0.1.0 \
**Runs on:** Windows Agent Box \
**Default mode:** Simulator \
**Live authority:** Explicitly allowlisted Home Assistant `light.*` entities only

---

## 1. Start the app

Double-click `Launch Osun.cmd` in the repository root.

For a visible diagnostic console, open PowerShell in the repository and run:

```powershell
.\run_osun.ps1
```

The launcher starts a Python service bound only to a random `127.0.0.1` port and opens Microsoft Edge in app mode. Select **Quit app** in Connection & safety to stop the local service cleanly.

No package installation is required on the current PC. The prototype uses the installed Python runtime, Windows DPAPI, and Microsoft Edge.

---

## 2. Try simulation first

All four simulated lights are selected initially. Useful requests include:

- `I want to feel like I am in the ocean`
- `Make it warm and cozy`
- `Give me a focus theme`
- `Make it feel like a bioluminescent cave`
- `Set the lights to 35 percent`
- `Make them purple at 50%`
- `Turn the lights off over 4 seconds`
- `Suggest something for right now`

The assistant responds and fills the **Exact preview** card. Read the targets and values, then select **Apply**. Nothing changes before Apply. Select **Cancel** to discard the proposal.

Use **Pause simulator** to verify that emergency pause cancels a pending proposal and blocks execution. Resume through Connection & safety by clearing **Pause execution** and saving.

---

## 3. Prepare Home Assistant

Live mode requires actual light entities to exist in Home Assistant first. Add each light using the appropriate Home Assistant hardware integration and confirm it can be controlled from the Home Assistant dashboard before giving Osun access.

The prototype follows Home Assistant's documented REST setup:

1. Open the local Home Assistant frontend.
2. Open the owner profile.
3. Create a Long-Lived Access Token for this prototype as described in the [Home Assistant REST API documentation](https://developers.home-assistant.io/docs/api/rest/).
4. Copy the full token once. Do not paste it into chat, source files, issue trackers, or this document.

A long-lived token is a prototype compromise, not the final least-privilege identity design. Revoke it from the Home Assistant profile when testing ends or if the PC/token may be compromised.

---

## 4. Connect without executing

1. Select the gear button.
2. Select **Home Assistant**.
3. Enter the local URL, normally `http://homeassistant.local:8123` or a private LAN IP.
4. Paste the token into **Access token - write only**.
5. Select **Test & discover lights**.
6. Select only the non-safety-critical lights Osun may control.
7. Select **Enable live light execution** but leave **Pause execution** checked.
8. Select **Save**.

The token is encrypted with Windows DPAPI for the current Windows user. The configuration file contains the URL and allowed entity IDs but never the token. A saved token is not displayed again.

Keep the initial saved state paused so discovery/setup cannot accidentally become execution authority.

---

## 5. Run the first supervised canary

Use one or two ordinary lamps first—not emergency lighting or anything whose unexpected state could cause harm.

1. Confirm direct Home Assistant control still works.
2. Reopen Connection & safety.
3. Confirm the exact allowlist.
4. Clear **Pause execution** and select **Save**.
5. Ask Osun for a simple low-brightness color change.
6. Review the exact preview and physically observe the target area.
7. Select **Apply** once.
8. Confirm Osun reports Home Assistant read-back as verified.
9. Test off, brightness, one color, Ocean, Cancel, and Emergency pause.

If the result is partial or failed, do not repeatedly Apply. Use Home Assistant directly, pause Osun, and inspect the visible result. The adapter deliberately avoids blind retries.

---

## 6. Stop or revoke access

- **Immediate software pause:** Select **Emergency pause**.
- **Return to simulation:** Open Connection & safety, select Simulator, then Save.
- **Delete local token:** Select **Delete token & disable live**.
- **Revoke provider authority:** Delete/revoke the prototype token in the Home Assistant owner profile.
- **Stop the app:** Select **Quit app**. If using the diagnostic console, `Ctrl+C` also stops it.

Home Assistant remains the device authority and fallback interface throughout.

---

## 7. Local files and privacy

The real launcher uses `%LOCALAPPDATA%\Osun\lighting`:

| Item | Purpose | Contains raw chat/token? |
|---|---|---|
| `config.json` | Mode, local URL, allowlisted light IDs, enable/pause state | No raw chat; no token |
| `secrets\home_assistant_token.bin` | Windows DPAPI-protected token ciphertext | Encrypted token only |
| `audit.jsonl` | Proposal/result ID, mode, action, target entity IDs, outcome | No raw chat; no token |

Chat exists only in the current app page. Reloading or quitting clears it. No cloud model is used in version 0.1.0.

---

## 8. Current limitations

- Real lights have not yet been connected or canary-tested in this repository.
- The conversation layer is a deterministic local intent/theme engine, not yet a language model.
- Device-specific effects and unusual RGBW/RGBWW behavior may need later capability tests.
- There is no voice, mobile app, background scheduling, presence sensing, remote access, or non-light device control.
- The prototype has no installer or code signing yet; use the repository launcher.

Record any canary result without placing tokens or private household details in Git.
