# P2 Apple Music Agent

**State:** Implemented with simulator evidence; owner MusicKit credential and real playback canary pending \
**Prototype:** P2-MUSIC-01 \
**Owner authorization:** 2026-07-27 \
**Host:** Windows Agent Box \
**Initial playback device:** This PC \
**Last updated:** 2026-07-27

---

## 1. Product contract

The Music agent handles explicit requests to play, pause, resume, skip, or go back in Apple Music. Qwen can call only `open_music_widget()` with no model-authored device or playback arguments. Deterministic Music code reparses the owner's original words, selects a registered device under the policy below, and emits a typed playback command.

The first real adapter is MusicKit on the Web inside the local Osun window. Apple's official web integration plays directly in that browser. It does not remotely control an arbitrary iPhone, HomePod, or separate Apple Music application. Those devices can join later only through an installed Osun companion or a separately reviewed Home Assistant/Music Assistant adapter that can report playback activity and verify commands.

## 2. Device-routing policy

For every request, the agent evaluates only enabled, registered Osun music devices:

1. An explicit device in the request, such as `play Kind of Blue on This PC`, wins if it is available.
2. Otherwise, choose the device with the most recent successful playback evidence at or before 300 seconds ago.
3. If no device has such evidence, ask the owner which device to use and do not execute yet.
4. A successful play, resume, next, or previous command refreshes that device's activity time. Pause does not invent new evidence that a device was playing.
5. At 301 seconds the evidence is expired and Osun asks again.

Playback activity, requests, and results are memory-only in P2. Restarting Osun intentionally clears recent-device state, so the first request after restart asks again. This minimizes listening-history collection until durable music memory has its own retention and consent contract.

## 3. End-to-end flow

```text
Owner chat request
  -> local Qwen selects open_music_widget()
  -> deterministic Music intent parser
  -> registered-device router
       -> no playback evidence <= 300 seconds: compact widget asks for device
       -> explicit/recent device: request becomes ready
  -> simulator OR typed MusicKit browser command
  -> Apple account authorization remains in Apple's MusicKit UI
  -> command result returns to deterministic Music controller
  -> device activity refreshed only after successful playback evidence
  -> compact/expandable widget and chat show the result
```

The Music widget is absent until called, starts compact, expands when selected, and animates while selecting, connecting, or executing. The per-widget autonomous switch defaults off. Explicit owner chat commands are already direct authorization for the requested playback; the switch is reserved for future proactive music actions and does not silently grant them today.

## 4. Credentials and trust boundaries

- Real browser playback requires an Apple Music subscription, a MusicKit-enabled Apple developer configuration, a signed developer-token JWT, and Apple account authorization. The current random loopback origin may require authorization again after an Osun restart.
- Store only the signed developer token in Osun. Never place the Apple `.p8` private signing key in Osun, chat, Git, screenshots, or the Pi.
- Osun encrypts the JWT with Windows DPAPI for the current Windows user. The config file contains no token field.
- The developer token is returned only to the session-protected local browser endpoint, over loopback, with `Cache-Control: no-store`.
- MusicKit manages the Music User Token and Apple sign-in state in the browser. Osun does not persist that token itself.
- Delete music token removes the protected JWT and returns the adapter to simulator mode. Provider-side revocation remains the final revocation path.

Apple developer tokens expire and must be renewed. Apple documents a maximum six-month token lifetime and recommends an origin claim for web applications. Because Osun currently uses a random loopback port, the token's origin policy must match the actual local origin or omit that optional claim during this prototype; a stable signed local origin is a packaging milestone.

## 5. Real setup and supervised canary

1. In the Apple Developer portal, create the required Media ID and MusicKit key, then generate a signed developer-token JWT following Apple's instructions.
2. Open **Osun -> Settings -> Music agent**.
3. Select **Apple Music**, paste the signed JWT into **MusicKit developer token**, keep **Enable Music agent** checked, and save.
4. Ask `play Kind of Blue`.
5. Since no registered device is recent, expand the Music widget and choose **This PC**.
6. Select **Connect Apple Music** and complete Apple's authorization. Osun resumes the pending request; if the browser blocks playback, issue the request again as a fresh user gesture.
7. Confirm audible playback and the verified result.
8. Within five minutes, ask `play Blue in Green`; require automatic routing to **This PC**.
9. After more than five minutes without successful playback evidence, make another request and require a new device question.
10. Test pause, resume, next, previous, token deletion, disabled-agent denial, and simulator recovery.

Official references:

- Apple MusicKit overview: <https://developer.apple.com/musickit/>
- MusicKit on the Web documentation: <https://js-cdn.music.apple.com/musickit/v3/docs/index.html>
- MusicKit JavaScript instance reference: <https://js-cdn.music.apple.com/musickit/v3/docs/iframe.html?path=%2Fstory%2Freference-javascript-musickit-instance--page>

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
| MUSIC-T08 | Token storage | Config contains no JWT; protected store is DPAPI-bound |
| MUSIC-T09 | Unknown model tool | No music execution path opens |
| MUSIC-T10 | Real MusicKit canary | Audible playback and typed result agree on This PC |
| MUSIC-T11 | Restart | Recent-device activity is cleared and device is requested again |
| MUSIC-T12 | Widget lifecycle | Widget arrives compact, expands on click, and animates during work |

Automated evidence covers MUSIC-T01 through MUSIC-T09, MUSIC-T11, and the UI contract of MUSIC-T12. MUSIC-T10 needs the owner's Apple developer token, Apple Music authorization, and direct listening observation.

## 7. Next device adapters

Each new adapter must add a stable device identity, authenticated command channel, playback-activity heartbeat, result verification, timeout behavior, and revocation path. Recommended order:

1. This PC via MusicKit web (current).
2. iPhone companion using native MusicKit, when an iOS client exists.
3. HomePod or room speakers through a separately accepted Home Assistant/Music Assistant integration.
4. Household devices only after multi-user identity, preference separation, and guest/privacy rules exist.

No adapter may claim a device is recent merely because it is online; it needs observed successful playback evidence.
