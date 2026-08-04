# P2 Apple Music Agent

**State:** Windows app adapter implemented; supervised audible-playback canary passed \
**Prototype:** P2-MUSIC-01 \
**Owner authorization:** 2026-07-27 \
**Host:** Windows Agent Box \
**Initial playback device:** This PC \
**Last updated:** 2026-08-04

---

## 1. Product contract

The Music agent handles explicit requests to play, pause, resume, skip, or go back in Apple Music. Qwen can call only `open_music_widget()` with no model-authored device or playback arguments. Deterministic Music code reparses the owner's original words, selects a registered device under the policy below, and emits a typed playback command.

The default real adapter controls the installed Windows Apple Music application on the Agent Box. It uses Apple's public iTunes Search API to resolve an owner query to an Apple-owned catalog result, validates that result, and opens it using the Apple package's registered `/url` command. It starts the visible matching song using Apple's documented Windows interaction, falling back to catalog Search with the resolved title and artist when needed, and reads back only the Apple Music Windows media session. Pause, resume, next, and previous use targeted Windows media-session commands. No Apple developer membership or MusicKit token is required.

MusicKit on the Web remains an optional future-compatible provider. Neither local provider remotely controls an arbitrary iPhone or HomePod. Those devices can join later only through an installed Osun companion or a separately reviewed Home Assistant/Music Assistant adapter that reports playback activity and verifies commands.

## 2. Device-routing policy

For every request, the agent evaluates only enabled, registered Osun music devices:

1. An explicit device in the request, such as `play Kind of Blue on This PC`, wins if it is available.
2. Otherwise, choose the device with the most recent successful playback evidence at or before 300 seconds ago.
3. If no device has such evidence, ask the owner which device to use and do not execute yet.
4. A successful play, resume, next, or previous command refreshes that device's activity time. Pause does not invent new evidence that a device was playing.
5. At 301 seconds the evidence is expired and Osun asks again.

For the Windows Agent Box, natural aliases including `my PC`, `my computer`, `this computer`, and `agent box` resolve to the registered **This PC** device. A device-only reply such as `my PC` or `on my PC` resolves the newest unanswered Music device question without asking Qwen or creating a second playback request. A new explicit music command supersedes older unanswered device questions.

Exact commands such as `play`, `play Cardi B`, and `play Cardi B on my PC` are parsed deterministically before model routing. When Qwen has explicitly selected the Music agent, short query fragments such as `a Cardi B song` and `anything` may fill the play-query slot; outside that scoped agent call, arbitrary bare chat is not reinterpreted as playback.

Playback activity, requests, and results are memory-only in P2. Restarting Osun intentionally clears recent-device state, so the first request after restart asks again. This minimizes listening-history collection until durable music memory has its own retention and consent contract.

## 3. End-to-end flow

```text
Owner chat request
  -> local Qwen selects open_music_widget()
  -> deterministic Music intent parser
  -> registered-device router
       -> no playback evidence <= 300 seconds: compact widget asks for device
       -> explicit/recent device: request becomes ready
  -> simulator OR Windows Apple Music adapter
       -> bounded public-catalog lookup for play requests
       -> validated Apple-owned catalog result or typed transport command
       -> Apple Music media-session read-back
       -> targeted UI Automation fallback only when needed
  -> command result returns to deterministic Music controller
  -> device activity refreshed only after successful playback evidence
  -> compact/expandable widget and chat show the result
```

The Music widget is absent until called, starts compact, expands when selected, and animates while selecting or executing. Settings includes a live adapter test that reports whether the app, media session, or bounded UI fallback is available. The per-widget autonomous switch defaults off. Explicit owner chat commands are already direct authorization for the requested playback; the switch is reserved for future proactive music actions and does not silently grant them today.

## 4. Credentials and trust boundaries

- Windows app mode requires only the installed Apple Music application, an Apple Music subscription, and a one-time interactive sign-in within Apple's app. Osun never receives or stores the Apple Account password, passkey, cookies, or subscription credential.
- Play searches call only `https://itunes.apple.com/search`, request at most ten song results, cap the response at 1 MB, and accept playback links only from `https://music.apple.com` or `https://itunes.apple.com`.
- The PowerShell bridge exposes a closed action set: probe, play an already validated Apple URL, pause, resume, next, and previous. The Apple URL is passed only to the package-declared `/url` handler; the unsupported `/play` argument is never used. No model-authored shell, process name, URL host, or script is accepted.
- Transport control selects a Windows media session whose source identity matches Apple Music. It never broadcasts global media keys that could control a browser, video call, or unrelated player.
- The bounded UI Automation path is limited to the `AppleMusic.exe` process. It first uses the accessible Search field and only falls back to Apple's documented `Alt`, then `N`, `F` access key after verifying Apple Music owns the foreground window. It sets query text through the accessibility Value pattern, invokes the exact catalog result to reach its album, and double-clicks the exact visible `ListViewItem` track row, as documented by Apple. The click point comes from the row's live accessibility rectangle rather than a hard-coded coordinate. It does not use global media keys.
- Windows prevents cross-privilege UI control. Osun and Apple Music must run under the same signed-in Windows user and privilege level; neither should be run as Administrator. MiniPlayer and full-screen playback should be exited for catalog-search requests.
- A play request is recorded as recent only after media-session playback evidence. A targeted UI command without read-back is shown honestly and does not fabricate playback history.
- The optional MusicKit provider retains the existing DPAPI-protected developer-token design. Never place an Apple `.p8` private key in Osun, chat, Git, screenshots, or the Pi.

## 5. Real setup and supervised canary

1. Install or update **Apple Music** from Microsoft Store, open it once, sign in, and confirm a song plays normally.
2. Open **Osun -> Settings -> Music agent**, select **Windows app**, keep **Enable Music agent** checked, and save.
3. Select **Test Apple Music app**. With a song active, require `Connected` and the current title. Without a song, UI-fallback status is acceptable. If the test says Windows is hiding controls, reopen the full Apple Music window and make sure neither app is running as Administrator.
4. Ask `play Kind of Blue`.
5. Since no registered device is recent, expand the Music widget and choose **This PC**.
6. Confirm Apple Music starts an audible catalog result and Osun reports media-session verification rather than assuming success.
7. Within five minutes, ask `play Blue in Green`; require automatic routing to **This PC**.
8. Test pause, resume, next, and previous; each must target Apple Music even if another media app is open.
9. After more than five minutes without successful playback evidence, make another request and require a new device question.
10. Sign out or close Apple Music and confirm Osun fails with a recovery instruction rather than controlling another player.

Official references:

- Apple MusicKit overview: <https://developer.apple.com/musickit/>
- MusicKit on the Web documentation: <https://js-cdn.music.apple.com/musickit/v3/docs/index.html>
- MusicKit JavaScript instance reference: <https://js-cdn.music.apple.com/musickit/v3/docs/iframe.html?path=%2Fstory%2Freference-javascript-musickit-instance--page>
- Apple iTunes Search API: <https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/Searching.html>
- Apple Music search on Windows: <https://support.apple.com/guide/music-windows/search-for-music-mus896f20db7/windows>
- Apple Music keyboard shortcuts on Windows: <https://support.apple.com/guide/music-windows/keyboard-shortcuts-mus1019/windows>
- Apple Music playback on Windows: <https://support.apple.com/guide/music-windows/play-songs-mus36265ad9/windows>
- Microsoft global media-session API: <https://learn.microsoft.com/en-us/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessionmanager>
- Microsoft UI Automation fundamentals: <https://learn.microsoft.com/windows/win32/winauto/entry-uiautocore-overview>

## 6. Acceptance evidence

| ID | Scenario | Success condition |
|---|---|---|
| MUSIC-T01 | Agent not called | No Music widget is shown |
| MUSIC-T02 | First request/no activity | Agent asks for a device and does not execute |
| MUSIC-T03 | Owner selects This PC | One typed command executes and records successful activity |
| MUSIC-T04 | Follow-up at 300 seconds | This PC is selected automatically |
| MUSIC-T05 | Follow-up at 301 seconds | Agent asks for a device again |
| MUSIC-T06 | Multiple recent devices | Most recently active enabled device wins |
| MUSIC-T07 | Explicit device | Named available device wins regardless of recency |
| MUSIC-T08 | Closed adapter boundary | Only allowed Apple hosts and typed bridge actions can reach the Windows adapter |
| MUSIC-T09 | Unknown model tool | No music execution path opens |
| MUSIC-T10 | Real Windows app canary | Audible playback, Apple Music media-session title, and Osun result agree on This PC |
| MUSIC-T11 | Restart | Recent-device activity is cleared and device is requested again |
| MUSIC-T12 | Widget lifecycle | Widget arrives compact, expands on click, and animates during work |
| MUSIC-T13 | Natural PC alias | `play Cardi B on my PC` resolves to This PC and removes the device phrase from the catalog query |
| MUSIC-T14 | Device-only follow-up | `play Cardi B` followed by `my PC` reuses the pending request and executes once |
| MUSIC-T15 | Scoped query fragment | A model-routed `a Cardi B song` becomes a play request; the same bare phrase outside Music scope does not |

Automated evidence covers MUSIC-T01 through MUSIC-T09 and MUSIC-T11 through MUSIC-T15. MUSIC-T10 passed under direct owner-session observation on 2026-08-04: the adapter changed playback from `Blue In Green` to `So What`, and the targeted Windows media session returned `So What by Miles Davis — Kind of Blue` with active, verified playback. A second exact conversational canary routed `play cardi b on my pc` to This PC, preserved `cardi b` as the catalog query, played `Up by Cardi B — Up - Single`, and verified the result through the targeted Windows media session. Both canaries used the installed Windows app and required no developer credentials.

## 7. Next device adapters

Each new adapter must add a stable device identity, authenticated command channel, playback-activity heartbeat, result verification, timeout behavior, and revocation path. Recommended order:

1. This PC via the Windows Apple Music app (current).
2. iPhone companion using native MusicKit, when an iOS client exists.
3. HomePod or room speakers through a separately accepted Home Assistant/Music Assistant integration.
4. Household devices only after multi-user identity, preference separation, and guest/privacy rules exist.

No adapter may claim a device is recent merely because it is online; it needs observed successful playback evidence.
