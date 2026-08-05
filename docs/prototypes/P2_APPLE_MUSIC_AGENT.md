# P2 Apple Music Agent

**State:** Windows app adapter implemented; Bluetooth/Apple TV destination policy implemented; Windows canary passed \
**Prototype:** P2-MUSIC-01 \
**Owner authorization:** 2026-07-27 \
**Host:** Windows Agent Box \
**Playback destinations:** Connected Bluetooth Headphones; Living Room Apple TV \
**Last updated:** 2026-08-05

---

## 1. Product contract

The Music agent handles explicit requests to play, pause, resume, skip, or go back in Apple Music. Qwen can call only `open_music_widget()` with no model-authored device or playback arguments. Deterministic Music code reparses the owner's original words, selects a registered device under the policy below, and emits a typed playback command.

The Headphones adapter controls the installed Windows Apple Music application on the Agent Box. It uses Apple's public iTunes Search API to resolve an owner query to an Apple-owned catalog result, validates that result, and opens it using the Apple package's registered `/url` command. It starts the visible matching song using Apple's documented Windows interaction, falling back to catalog Search with the resolved title and artist when needed, and reads back only the Apple Music Windows media session. Pause, resume, next, and previous use targeted Windows media-session commands. No Apple developer membership or MusicKit token is required.

The Apple TV adapter reuses the owner's existing DPAPI-protected Home Assistant connection. Settings discovers only valid `media_player` entities and lets the owner persist one exact entity ID and display name. Runtime playback can target only that stored entity, sends a validated Apple Music catalog link through `media_player.play_media`, and reads the selected media-player state back. The former exact `media_player.living_room_apple_tv` or friendly-name lookup remains only as a migration fallback until the owner saves a selection. Apple does not document a Windows AirPlay output control comparable to the one on Mac, so Osun launches native Apple Music content on Apple TV rather than adding an unsupported or paid system-audio mirroring dependency. MusicKit on the Web remains optional. Osun does not control arbitrary iPhones, HomePods, or unselected media players.

## 2. Device-routing policy

For every request, the agent evaluates only enabled, registered Osun music destinations:

1. Windows performs a cached, read-only check for a currently present Bluetooth headphone audio output.
2. If headphones and Living Room Apple TV are available, every new **play** request asks the owner to choose **Headphones** or **Living Room Apple TV**. Recent playback never suppresses this choice.
3. If headphones are absent and Apple TV is available, new play requests route to Apple TV automatically.
4. An explicit `TV` or `Living Room Apple TV` chooses Apple TV. An explicit `headphones`, `my PC`, `my computer`, or `agent box` chooses Headphones when connected and falls back to Apple TV when they are disconnected.
5. Pause, resume, next, and previous reuse successful playback evidence for up to 300 seconds. Without recent evidence, transport controls default to Apple TV.
6. Successful verified playback refreshes only the selected destination's memory-only activity time. Pause does not invent playback evidence.

A destination-only reply such as `headphones`, `my PC`, `TV`, or `on the Living Room Apple TV` resolves the newest unanswered Music choice without asking Qwen or creating a second playback request. A new explicit music command supersedes older unanswered choices.

Exact commands such as `play`, `play Cardi B`, and `play Cardi B on my PC` are parsed deterministically before model routing. When Qwen has explicitly selected the Music agent, short query fragments such as `a Cardi B song` and `anything` may fill the play-query slot; outside that scoped agent call, arbitrary bare chat is not reinterpreted as playback.

Playback-device inventory questions are also deterministic and read-only. Requests such as `what devices are available to play on?`, `where can I play Apple Music?`, and `list my music devices` return enabled registered devices, adapter details, and recent-playback context in a dedicated Music widget view. Listing devices never executes playback and preserves any request that is waiting for a device choice.

Playback activity, requests, and results are memory-only in P2. Restarting Osun intentionally clears recent-destination state. Bluetooth presence is recomputed from Windows and is never written to disk. This minimizes listening-history and presence collection until durable music memory has its own retention and consent contract.

## 3. End-to-end flow

```text
Owner chat request
  -> local Qwen selects open_music_widget()
  -> deterministic Music intent parser
  -> destination router checks live Bluetooth headphone presence
       -> Headphones + TV: compact widget asks the owner
       -> no Headphones: Living Room Apple TV is selected
       -> explicit destination: bounded alias resolution
  -> simulator OR typed destination adapter
       -> Headphones: Windows Apple Music app + media-session read-back
       -> Living Room Apple TV: allowlisted Home Assistant deep link + state read-back
  -> command result returns to deterministic Music controller
  -> destination activity refreshed only after successful playback evidence
  -> compact/expandable widget and chat show the result
```

The Music widget is absent until called, starts compact, expands when selected, and animates while selecting or executing. Settings includes bounded Home Assistant media-center discovery, an explicit selector, and a live adapter test that reports the Windows app/media session, connected Bluetooth headphones, and selected media-center availability. The per-widget autonomous switch defaults off. Explicit owner chat commands are direct authorization for the requested playback; the switch is reserved for future proactive music actions and does not silently grant them today.

## 4. Credentials and trust boundaries

- Windows app mode requires only the installed Apple Music application, an Apple Music subscription, and a one-time interactive sign-in within Apple's app. Osun never receives or stores the Apple Account password, passkey, cookies, or subscription credential.
- Play searches call only `https://itunes.apple.com/search`, request at most ten song results, cap the response at 1 MB, and accept playback links only from `https://music.apple.com` or `https://itunes.apple.com`.
- The PowerShell bridge exposes a closed action set: probe, play an already validated Apple URL, pause, resume, next, and previous. The Apple URL is passed only to the package-declared `/url` handler; the unsupported `/play` argument is never used. No model-authored shell, process name, URL host, or script is accepted.
- Transport control selects a Windows media session whose source identity matches Apple Music. It never broadcasts global media keys that could control a browser, video call, or unrelated player.
- The bounded UI Automation path is limited to the `AppleMusic.exe` process. It first uses the accessible Search field and only falls back to Apple's documented `Alt`, then `N`, `F` access key after verifying Apple Music owns the foreground window. It sets query text through the accessibility Value pattern, invokes the exact catalog result to reach its album, and double-clicks the exact visible `ListViewItem` track row, as documented by Apple. The click point comes from the row's live accessibility rectangle rather than a hard-coded coordinate. It does not use global media keys.
- Windows prevents cross-privilege UI control. Osun and Apple Music must run under the same signed-in Windows user and privilege level; neither should be run as Administrator. MiniPlayer and full-screen playback should be exited for catalog-search requests.
- A play request is recorded as recent only after media-session playback evidence. A targeted UI command without read-back is shown honestly and does not fabricate playback history.
- Bluetooth discovery is a closed, parameter-free PowerShell probe. It prefers PnP ancestry for currently present `AudioEndpoint` devices and falls back to WinRT's active audio-render endpoint list when the process cannot read PnP ancestry. It returns only a bounded connected flag and up to eight short endpoint names; the result is cached for five seconds and not persisted.
- Media-center discovery may read `GET /api/states`, filters the result to at most 100 syntactically valid `media_player` entities, and exposes only bounded entity ID, friendly name, and state fields. Playback may read only the persisted selected entity and call the fixed `media_player` services needed for play, pause, resume, next, or previous. The owner request and Qwen cannot provide or change the Home Assistant URL, credential, entity ID, service path, or media host.
- Apple TV play accepts only the Apple-owned URL returned by the bounded catalog client. Home Assistant service acceptance without state confirmation is reported as unverified and does not create playback history.
- The optional MusicKit provider retains the existing DPAPI-protected developer-token design. Never place an Apple `.p8` private key in Osun, chat, Git, screenshots, or the Pi.

## 5. Real setup and supervised canary

1. Install or update **Apple Music** from Microsoft Store, open it once, sign in, and confirm a song plays normally through the PC.
2. In Home Assistant, add and pair the official **Apple TV** integration and confirm it exposes a `media_player` entity.
3. Open **Osun -> Settings -> Music agent**, select **Discover media centers**, choose the Apple TV entity, select **Windows app**, keep **Enable Music agent** checked, and save.
4. Select **Test Apple Music app**. Require the result to report the Windows app state, current Bluetooth headphone state, the selected entity name, and `available`.
5. Connect Bluetooth headphones, ask `play Kind of Blue`, and require a choice between **Headphones** and **Living Room Apple TV**.
6. Choose **Headphones**. Confirm the Windows Apple Music app starts an audible result and Osun reports media-session verification.
7. Make a new play request while the headphones remain connected. Require the choice again; recent playback must not suppress it.
8. Choose **Living Room Apple TV**. Confirm the Apple TV launches/plays the matched Apple Music result and Osun reports Home Assistant read-back when available.
9. Disconnect the headphones and ask for another song. Require automatic routing to Living Room Apple TV without a destination question.
10. Test pause, resume, next, and previous on both destinations; each must remain inside its typed adapter.
11. Disable or remove the selected Apple TV entity and confirm Osun fails closed without calling another media player.
12. Sign out or close Windows Apple Music and confirm the Headphones path fails with a recovery instruction rather than controlling another player.

Official references:

- Apple MusicKit overview: <https://developer.apple.com/musickit/>
- MusicKit on the Web documentation: <https://js-cdn.music.apple.com/musickit/v3/docs/index.html>
- MusicKit JavaScript instance reference: <https://js-cdn.music.apple.com/musickit/v3/docs/iframe.html?path=%2Fstory%2Freference-javascript-musickit-instance--page>
- Apple iTunes Search API: <https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/Searching.html>
- Apple Music search on Windows: <https://support.apple.com/guide/music-windows/search-for-music-mus896f20db7/windows>
- Apple Music keyboard shortcuts on Windows: <https://support.apple.com/guide/music-windows/keyboard-shortcuts-mus1019/windows>
- Apple Music playback on Windows: <https://support.apple.com/guide/music-windows/play-songs-mus36265ad9/windows>
- Apple AirPlay audio platforms and controls: <https://support.apple.com/en-us/105068>
- Home Assistant Apple TV integration and deep links: <https://www.home-assistant.io/integrations/apple_tv>
- Microsoft global media-session API: <https://learn.microsoft.com/en-us/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessionmanager>
- Microsoft UI Automation fundamentals: <https://learn.microsoft.com/windows/win32/winauto/entry-uiautocore-overview>

## 6. Acceptance evidence

| ID | Scenario | Success condition |
|---|---|---|
| MUSIC-T01 | Agent not called | No Music widget is shown |
| MUSIC-T02 | Headphones connected | Every new play asks Headphones or Living Room Apple TV and does not execute yet |
| MUSIC-T03 | Owner selects Headphones | One typed Windows app command executes and records only verified activity |
| MUSIC-T04 | Headphones absent | Living Room Apple TV is selected automatically |
| MUSIC-T05 | Owner selects TV | One allowlisted Home Assistant command targets only Living Room Apple TV |
| MUSIC-T06 | Recent transport control | Pause/resume/next/previous reuse a destination for at most 300 seconds |
| MUSIC-T07 | Explicit destination | Named available destination wins; unavailable Headphones fall back to TV |
| MUSIC-T08 | Closed adapter boundary | Only allowed Apple hosts and typed bridge actions can reach the Windows adapter |
| MUSIC-T09 | Unknown model tool | No music execution path opens |
| MUSIC-T10 | Real Headphones canary | Audible playback, Apple Music media-session title, and Osun result agree |
| MUSIC-T11 | Restart | Recent-device activity is cleared and device is requested again |
| MUSIC-T12 | Widget lifecycle | Widget arrives compact, expands on click, and animates during work |
| MUSIC-T13 | Natural PC alias | `play Cardi B on my PC` resolves to Headphones when connected and removes the device phrase from the catalog query |
| MUSIC-T14 | Destination-only follow-up | `play Cardi B` followed by `TV` or `my PC` reuses the pending request and executes once |
| MUSIC-T15 | Scoped query fragment | A model-routed `a Cardi B song` becomes a play request; the same bare phrase outside Music scope does not |
| MUSIC-T16 | Device inventory | A playback-device question bypasses Qwen, lists enabled registered devices, executes nothing, and preserves pending playback |
| MUSIC-T17 | Bluetooth probe | Only active bounded headphone endpoint metadata is returned; nothing is persisted |
| MUSIC-T18 | Apple TV allowlist | Discovery exposes bounded media-player metadata; playback targets only the persisted owner-selected entity and a missing entity fails closed |
| MUSIC-T19 | Apple TV canary | Audible Apple TV playback and Home Assistant read-back agree on the requested song |

Automated evidence covers MUSIC-T01 through MUSIC-T09 and MUSIC-T11 through MUSIC-T18, including configured media-center discovery, persistence, exact targeting, and rejection of non-media-player selections. MUSIC-T10 passed under direct owner-session observation on 2026-08-04: the adapter changed playback from `Blue In Green` to `So What`, and the targeted Windows media session returned `So What by Miles Davis — Kind of Blue` with active, verified playback. A second exact conversational canary routed `play cardi b on my pc` to the local Windows path, preserved `cardi b` as the catalog query, played `Up by Cardi B — Up - Single`, and verified the result through the targeted Windows media session. Both canaries used the installed Windows app and required no developer credentials. MUSIC-T19 remains the supervised real-device check after the owner selects the correct Home Assistant Apple TV entity.

## 7. Next device adapters

Each new adapter must add a stable device identity, authenticated command channel, playback-activity heartbeat, result verification, timeout behavior, and revocation path. Recommended order:

1. Bluetooth Headphones via the Windows Apple Music app (current).
2. Living Room Apple TV through the exact Home Assistant media-player adapter (current; supervised canary pending).
3. iPhone companion using native MusicKit, when an iOS client exists.
4. HomePod or room speakers through a separately accepted Home Assistant/Music Assistant integration.
5. Household devices only after multi-user identity, preference separation, and guest/privacy rules exist.

No adapter may claim a device is recent merely because it is online; it needs observed successful playback evidence.
