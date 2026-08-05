"use strict";

const sessionToken = location.pathname.split("/").filter(Boolean)[1];
const apiRoot = `/api/${sessionToken}`;

const state = {
  status: null,
  activeWidget: null,
  widgetExpanded: false,
  runningWidgetId: null,
  selectedEntities: new Set(),
  discoveredLights: [],
  discoveredMediaCenters: [],
  busy: false,
  applyingProposalId: null,
  resultText: "",
  musicResultText: "",
  musicKit: null,
  musicKitScript: null,
};

const ui = {
  messages: document.getElementById("messages"),
  welcome: document.getElementById("welcome"),
  composer: document.getElementById("composer"),
  input: document.getElementById("messageInput"),
  send: document.getElementById("sendButton"),
  hint: document.getElementById("composerHint"),
  workspace: document.getElementById("workspace"),
  widgetDock: document.getElementById("widgetDock"),
  activeWidget: document.getElementById("activeWidget"),
  newChat: document.getElementById("newChatButton"),
  lightingNav: document.getElementById("lightingNav"),
  musicNav: document.getElementById("musicNav"),
  agentBoxDot: document.getElementById("agentBoxDot"),
  agentBoxModel: document.getElementById("agentBoxModel"),
  agentBoxStatus: document.getElementById("agentBoxStatus"),
  settingsButton: document.getElementById("settingsButton"),
  settings: document.getElementById("settingsDialog"),
  settingsModelBadge: document.getElementById("settingsModelBadge"),
  qwenProvider: document.getElementById("qwenProvider"),
  qwenModel: document.getElementById("qwenModel"),
  qwenEndpoint: document.getElementById("qwenEndpoint"),
  qwenHelp: document.getElementById("qwenHelp"),
  lightingModeBadge: document.getElementById("lightingModeBadge"),
  haUrl: document.getElementById("haUrl"),
  haToken: document.getElementById("haToken"),
  discover: document.getElementById("discoverButton"),
  connectionResult: document.getElementById("connectionResult"),
  discoveredLights: document.getElementById("discoveredLights"),
  liveEnabled: document.getElementById("liveEnabled"),
  autonomousExecution: document.getElementById("autonomousExecution"),
  globalPause: document.getElementById("globalPause"),
  musicModeBadge: document.getElementById("musicModeBadge"),
  musicAppTest: document.getElementById("musicAppTestButton"),
  musicAppTestResult: document.getElementById("musicAppTestResult"),
  discoverMediaCenters: document.getElementById("discoverMediaCentersButton"),
  mediaCenterResult: document.getElementById("mediaCenterResult"),
  mediaCenterSelect: document.getElementById("mediaCenterSelect"),
  mediaCenterDeviceName: document.getElementById("mediaCenterDeviceName"),
  mediaCenterDeviceDetail: document.getElementById("mediaCenterDeviceDetail"),
  musicDeveloperToken: document.getElementById("musicDeveloperToken"),
  musicEnabled: document.getElementById("musicEnabled"),
  musicAutonomousExecution: document.getElementById("musicAutonomousExecution"),
  deleteToken: document.getElementById("deleteTokenButton"),
  deleteMusicToken: document.getElementById("deleteMusicTokenButton"),
  quit: document.getElementById("quitButton"),
  saveSettings: document.getElementById("saveSettingsButton"),
  toast: document.getElementById("toast"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function request(path, method = "GET", payload = undefined) {
  const options = { method, headers: {} };
  if (payload !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }
  const response = await fetch(`${apiRoot}${path}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Local request failed (${response.status})`);
  return data;
}

function showToast(message) {
  ui.toast.textContent = message;
  ui.toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => ui.toast.classList.remove("show"), 3400);
}

function updateComposerHint() {
  if (state.status?.lighting?.paused) {
    ui.hint.textContent = "Qwen runs locally. Lighting execution is paused outside the model layer.";
  } else {
    ui.hint.textContent = state.status?.lighting?.autonomous_execution
      ? "Qwen runs locally. Lighting proposals execute under the widget's autonomous policy."
      : "Qwen runs locally. Lighting changes require a visible Apply.";
  }
}

function appendMessage(role, text, agent = "osun") {
  if (ui.welcome) ui.welcome.hidden = true;
  const item = document.createElement("article");
  item.className = `message ${role}`;
  const name = role === "user" ? "You" : agent === "lighting" ? "Lighting agent" : agent === "music" ? "Music agent" : "Osun";
  const avatar = role === "user" ? "Y" : agent === "lighting" ? "L" : agent === "music" ? "M" : "O";
  item.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div>
      <div class="message-meta"><strong>${name}</strong><span>${role === "assistant" ? "Local" : "Now"}</span></div>
      <div class="message-copy">${escapeHtml(text)}</div>
    </div>`;
  ui.messages.appendChild(item);
  ui.messages.scrollTop = ui.messages.scrollHeight;
  return item;
}

function showThinking() {
  const item = appendMessage("assistant", "", "osun");
  item.id = "thinkingMessage";
  item.querySelector(".message-copy").innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  return item;
}

function lightColor(light) {
  if (Array.isArray(light.rgb_color) && light.rgb_color.length >= 3) {
    return `rgb(${light.rgb_color.slice(0, 3).map(Number).join(",")})`;
  }
  return light.state === "on" ? "#f1d9a3" : "#31454a";
}

function paletteFromProposal(proposal) {
  const colors = (proposal?.changes || []).map(change => change.rgb_color).filter(color => Array.isArray(color));
  return colors.map(color => `<span style="background:rgb(${color.map(Number).join(",")})"></span>`).join("");
}

function lightingExecutionGate(widget) {
  const reasons = [];
  const recovery = ["review the allowlist"];
  if (widget.mode === "home_assistant" && !widget.live_enabled) {
    reasons.push("live light execution is disabled");
    recovery.push("enable live execution");
  }
  if (widget.paused) {
    reasons.push("execution is paused");
    recovery.push("clear Pause");
  }
  if (!reasons.length) return null;
  return `${reasons.join(" and ")}. Open Connection, ${recovery.join(", ")}, and save.`;
}

function lightingTargetRow(light) {
  const members = light.member_names || [];
  const memberText = members.length
    ? `<span class="zone-members">Contains ${escapeHtml(members.join(", "))}</span>`
    : light.kind === "zone" ? '<span class="zone-members">Membership unavailable from Home Assistant</span>' : "";
  return `
    <label class="light-row ${light.kind === "zone" ? "zone-row" : ""}">
      <span class="light-identity">
        <input type="checkbox" class="widget-light-select" value="${escapeHtml(light.entity_id)}" ${state.selectedEntities.has(light.entity_id) ? "checked" : ""}>
        <span class="light-dot ${light.state === "on" ? "on" : ""}" style="color:${lightColor(light)};background:${lightColor(light)}"></span>
        <span class="light-label"><span class="light-name">${escapeHtml(light.friendly_name)}</span>${memberText}</span>
      </span>
      <span class="light-state">${escapeHtml(light.state)}</span>
    </label>`;
}

function showAgentWidget(widget) {
  state.activeWidget = widget;
  state.widgetExpanded = false;
  state.runningWidgetId = null;
  if (widget.kind === "lighting") state.resultText = widget.execution?.summary || "";
  if (widget.kind === "music") state.musicResultText = widget.execution?.summary || "";
  renderActiveWidget();
  if (widget.kind === "music" && widget.request?.state === "ready") {
    setTimeout(() => executeMusic(widget.request.request_id), 0);
  }
}

function setWidgetRunning(running) {
  if (!state.activeWidget) return;
  state.runningWidgetId = running ? state.activeWidget.id : null;
  renderActiveWidget();
}

function toggleWidget() {
  if (!state.activeWidget) return;
  state.widgetExpanded = !state.widgetExpanded;
  renderActiveWidget();
}

function renderActiveWidget() {
  if (state.activeWidget?.kind === "lighting") renderLightingWidget();
  if (state.activeWidget?.kind === "music") renderMusicWidget();
}

function renderLightingWidget(widget = state.activeWidget) {
  if (!widget) return;
  state.activeWidget = widget;
  const expanded = state.widgetExpanded;
  const running = state.runningWidgetId === widget.id;
  ui.widgetDock.hidden = false;
  ui.activeWidget.hidden = false;
  ui.workspace.classList.add("has-widget");
  ui.workspace.classList.toggle("widget-expanded", expanded);
  const lights = widget.lights || [];
  if (!state.selectedEntities.size) lights.forEach(light => state.selectedEntities.add(light.entity_id));
  const zones = lights.filter(light => light.kind === "zone");
  const individualLights = lights.filter(light => light.kind !== "zone");
  const zoneRows = zones.map(lightingTargetRow).join("");
  const lightRows = individualLights.map(lightingTargetRow).join("");
  const proposal = widget.proposal;
  const executionGate = lightingExecutionGate(widget);
  const proposalApplying = proposal && state.applyingProposalId === proposal.proposal_id;
  const autonomousExecution = proposal && widget.execution?.proposal_id === proposal.proposal_id
    ? widget.execution
    : null;
  const proposalConsumed = autonomousExecution && autonomousExecution.state !== "denied";
  const autonomousLabel = autonomousExecution?.state === "failed"
    ? "Autonomous attempt"
    : "Executed autonomously";
  const proposalName = proposal?.theme_name || "Lighting controls";
  const proposalChangeCount = proposal?.changes?.length || 0;
  const compactStatus = running
    ? "Running lighting agent…"
    : proposal
      ? `${proposalName} · ${proposalChangeCount} change${proposalChangeCount === 1 ? "" : "s"}`
      : state.resultText || "Ready for another request";
  const changes = (proposal?.changes || []).map(change => `
    <div class="change"><strong>${escapeHtml(change.friendly_name)}</strong><span>${escapeHtml(change.preview)}</span></div>`).join("");
  const proposalHtml = proposal ? `
    <div class="proposal-card">
      <div class="proposal-heading"><h3>${escapeHtml(proposal.theme_name || "Lighting change")}</h3><span>${proposalConsumed ? autonomousLabel : "Review only"}</span></div>
      <p class="proposal-summary">${escapeHtml(proposal.summary)}</p>
      ${paletteFromProposal(proposal) ? `<div class="palette">${paletteFromProposal(proposal)}</div>` : ""}
      <div class="change-list">${changes}</div>
      ${proposalConsumed ? `<div class="autonomous-result">${escapeHtml(autonomousExecution.summary)}</div>` : `<div class="widget-actions">
        <button class="secondary-button" id="cancelLighting" type="button" ${running ? "disabled" : ""}>Cancel</button>
        <button class="primary-button" id="applyLighting" type="button" ${executionGate || proposalApplying ? "disabled" : ""}>${executionGate ? "Execution locked" : proposalApplying ? "Applying…" : "Apply exact proposal"}</button>
      </div>`}
    </div>` : '<p class="muted small">Ask Osun for a lighting change to create an exact preview.</p>';
  ui.activeWidget.innerHTML = `
    <div class="widget-card ${expanded ? "expanded" : "compact"} ${running ? "running" : ""}" aria-busy="${running}">
      <div class="widget-hero">
        <div class="widget-title-row">
          <button id="toggleWidget" class="widget-toggle" type="button" aria-expanded="${expanded}" aria-controls="lightingWidgetBody">
            <span class="widget-agent">
              <span class="widget-glyph" aria-hidden="true"><span class="widget-orbit"></span><span class="widget-glyph-mark">◌</span></span>
              <span class="widget-agent-copy"><span class="widget-title">Lighting</span><span class="widget-subtitle" aria-live="polite">${escapeHtml(compactStatus)}</span></span>
            </span>
            <span class="widget-expand-icon" aria-hidden="true">${expanded ? "−" : "+"}</span>
          </button>
          <button id="closeWidget" class="widget-close" type="button" aria-label="Close lighting widget">×</button>
        </div>
        <div class="widget-mode" ${expanded ? "" : "hidden"}>
          <span class="${widget.mode === "home_assistant" ? "live" : ""}">${escapeHtml(widget.mode === "home_assistant" ? "Home Assistant" : "Simulator")}</span>
          <span class="${widget.autonomous_execution ? "autonomous" : ""}">${widget.autonomous_execution ? "Autonomous" : "Manual Apply"}</span>
          <span>${widget.paused ? "Paused" : "Execution ready"}</span>
          <span>${zones.length} zone${zones.length === 1 ? "" : "s"} · ${individualLights.length} light${individualLights.length === 1 ? "" : "s"}</span>
        </div>
      </div>
      <div id="lightingWidgetBody" class="widget-body" ${expanded ? "" : "hidden"}>
        ${executionGate ? `<p class="execution-gate widget-gate">${escapeHtml(executionGate)}</p>` : ""}
        <section class="widget-section"><p class="section-kicker">Zones</p><div class="light-list">${zoneRows || '<p class="muted small">No zones are allowlisted.</p>'}</div></section>
        <section class="widget-section"><p class="section-kicker">Lights</p><div class="light-list">${lightRows || '<p class="muted small">No individual lights are allowlisted.</p>'}</div></section>
        <section class="widget-section"><p class="section-kicker">Exact proposal</p>${proposalHtml}</section>
        <section class="widget-section">
          <div class="widget-actions"><button id="lightingSettings" class="secondary-button" type="button" ${running ? "disabled" : ""}>Connection</button><button id="pauseLighting" class="danger-button" type="button" ${running ? "disabled" : ""}>Emergency pause</button></div>
          ${widget.warning ? `<p class="widget-warning">${escapeHtml(widget.warning)}</p>` : ""}
          ${state.resultText ? `<div class="widget-result">${escapeHtml(state.resultText)}</div>` : ""}
        </section>
      </div>
    </div>`;
  bindWidgetEvents();
}

function bindWidgetEvents() {
  document.querySelectorAll(".widget-light-select").forEach(input => input.addEventListener("change", () => {
    input.checked ? state.selectedEntities.add(input.value) : state.selectedEntities.delete(input.value);
  }));
  document.getElementById("toggleWidget")?.addEventListener("click", toggleWidget);
  document.getElementById("closeWidget")?.addEventListener("click", closeWidget);
  document.getElementById("lightingSettings")?.addEventListener("click", openSettings);
  document.getElementById("pauseLighting")?.addEventListener("click", pauseLighting);
  document.getElementById("cancelLighting")?.addEventListener("click", cancelLighting);
  document.getElementById("applyLighting")?.addEventListener("click", applyLighting);
}

function musicActionDescription(musicRequest) {
  if (!musicRequest) return "Ready for a music request";
  if (musicRequest.action === "play") return `Play ${musicRequest.query || "music"}`;
  return {
    pause: "Pause music",
    resume: "Resume music",
    next: "Skip to the next song",
    previous: "Go to the previous song",
  }[musicRequest.action] || "Control Apple Music";
}

function musicDeviceDetail(device) {
  if (device.recent && Number.isFinite(device.seconds_since_playback)) {
    const seconds = Math.max(0, Number(device.seconds_since_playback));
    return seconds < 60 ? "Played here just now" : `Played here ${Math.floor(seconds / 60)} min ago`;
  }
  if (device.kind === "windows_headphones") {
    return device.connected ? `${device.detail || "Bluetooth headphones"} · Windows Apple Music app` : "Bluetooth headphones are not connected";
  }
  if (device.kind === "apple_tv") {
    return device.connected ? "Apple Music on Apple TV through Home Assistant" : "Apple TV is unavailable in Home Assistant";
  }
  if (device.kind === "windows_app") return "Windows Apple Music app on this PC";
  return device.kind === "browser" ? "Apple Music in this Osun window" : "Registered playback device";
}

function musicModeLabel(mode) {
  return { windows_app: "Windows app", musickit: "MusicKit", simulator: "Simulator" }[mode] || "Music";
}

function musicRequestStateLabel(musicRequest) {
  return {
    needs_device: "Device needed",
    ready: "Ready",
    running: "Running",
    playing: "Now playing",
    complete: "Complete",
    completed: "Sent",
    failed: "Failed",
  }[musicRequest?.state] || "Ready";
}

function musicSelectionDetail(musicRequest) {
  return {
    recent_playback: "Automatically selected from transport activity in the last five minutes",
    headphones_unavailable_default_tv: "Selected automatically because Bluetooth headphones are not connected",
    default_tv: "Default television destination for this transport command",
    only_available_destination: "The only currently available playback destination",
  }[musicRequest?.selection_reason] || "Selected for this request";
}

function renderMusicWidget(widget = state.activeWidget) {
  if (!widget) return;
  state.activeWidget = widget;
  const expanded = state.widgetExpanded;
  const running = state.runningWidgetId === widget.id;
  const musicRequest = widget.request;
  const devices = (widget.devices || []).filter(device => device.enabled);
  const showingDevices = widget.view === "devices";
  const needsDevice = musicRequest?.state === "needs_device";
  const action = musicActionDescription(musicRequest);
  const selectedDevice = devices.find(device => device.device_id === musicRequest?.device_id);
  const compactStatus = running
    ? "Running Music agent…"
    : showingDevices
      ? `${devices.length} playback device${devices.length === 1 ? "" : "s"} available`
    : needsDevice
      ? `${action} · choose a device`
      : state.musicResultText || `${action}${selectedDevice ? ` · ${selectedDevice.name}` : ""}`;
  const deviceChoices = devices.map(device => `
    <button class="device-choice" type="button" data-music-device="${escapeHtml(device.device_id)}" ${running ? "disabled" : ""}>
      <span class="device-icon" aria-hidden="true">♫</span>
      <span><strong>${escapeHtml(device.name)}</strong><small>${escapeHtml(musicDeviceDetail(device))}</small></span>
      <span class="device-choice-arrow" aria-hidden="true">→</span>
    </button>`).join("");
  const availableDevices = devices.map(device => `
    <div class="device-choice static-device">
      <span class="device-icon" aria-hidden="true">♫</span>
      <span><strong>${escapeHtml(device.name)}</strong><small>${escapeHtml(musicDeviceDetail(device))}</small></span>
      <span class="device-availability">${device.recent ? "Recent" : "Available"}</span>
    </div>`).join("");
  const requestCard = showingDevices ? `
    <div class="music-request-card">
      <div class="proposal-heading"><h3>Available playback devices</h3><span>${devices.length} enabled</span></div>
      <p class="proposal-summary">Osun can route Apple Music only to enabled, registered devices shown here.</p>
      <div class="device-choice-list">${availableDevices || '<p class="muted small">No music devices are enabled.</p>'}</div>
    </div>` : musicRequest ? `
    <div class="music-request-card">
      <div class="proposal-heading"><h3>${escapeHtml(action)}</h3><span>${escapeHtml(musicRequestStateLabel(musicRequest))}</span></div>
      ${needsDevice ? `<p class="proposal-summary">Bluetooth headphones are connected. Choose Headphones for normal PC audio or Living Room Apple TV for television playback.</p>
        <div class="device-choice-list">${deviceChoices || '<p class="muted small">No music devices are enabled.</p>'}</div>` : `
        <div class="music-device-line"><span class="device-icon" aria-hidden="true">♫</span><span><strong>${escapeHtml(selectedDevice?.name || musicRequest.device_name || "Selected device")}</strong><small>${escapeHtml(musicSelectionDetail(musicRequest))}</small></span></div>
        <div class="widget-actions">
          ${widget.mode === "musickit" ? '<button id="connectAppleMusic" class="secondary-button" type="button">Connect Apple Music</button>' : ""}
        </div>`}
    </div>` : '<p class="muted small">Ask Osun to play, pause, resume, skip, or go back.</p>';

  ui.widgetDock.hidden = false;
  ui.activeWidget.hidden = false;
  ui.workspace.classList.add("has-widget");
  ui.workspace.classList.toggle("widget-expanded", expanded);
  ui.activeWidget.innerHTML = `
    <div class="widget-card music-card ${expanded ? "expanded" : "compact"} ${running ? "running" : ""}" aria-busy="${running}">
      <div class="widget-hero">
        <div class="widget-title-row">
          <button id="toggleWidget" class="widget-toggle" type="button" aria-expanded="${expanded}" aria-controls="musicWidgetBody">
            <span class="widget-agent">
              <span class="widget-glyph" aria-hidden="true"><span class="widget-orbit"></span><span class="widget-glyph-mark">♫</span></span>
              <span class="widget-agent-copy"><span class="widget-title">Music</span><span class="widget-subtitle" aria-live="polite">${escapeHtml(compactStatus)}</span></span>
            </span>
            <span class="widget-expand-icon" aria-hidden="true">${expanded ? "−" : "+"}</span>
          </button>
          <button id="closeWidget" class="widget-close" type="button" aria-label="Close music widget">×</button>
        </div>
        <div class="widget-mode" ${expanded ? "" : "hidden"}>
          <span class="${widget.mode !== "simulator" ? "live" : ""}">${escapeHtml(musicModeLabel(widget.mode))}</span>
          <span>${widget.recent_window_seconds || 300}s transport-memory window</span>
          <span class="${widget.autonomous_execution ? "autonomous" : ""}">${widget.autonomous_execution ? "Autonomous" : "Owner requests only"}</span>
        </div>
      </div>
      <div id="musicWidgetBody" class="widget-body" ${expanded ? "" : "hidden"}>
        <section class="widget-section"><p class="section-kicker">${showingDevices ? "Playback devices" : "Playback request"}</p>${requestCard}</section>
        <section class="widget-section">
          <div class="widget-actions"><button id="musicSettings" class="secondary-button" type="button" ${running ? "disabled" : ""}>Music settings</button></div>
          ${state.musicResultText ? `<div class="widget-result music-result">${escapeHtml(state.musicResultText)}</div>` : ""}
        </section>
      </div>
    </div>`;
  document.getElementById("toggleWidget")?.addEventListener("click", toggleWidget);
  document.getElementById("closeWidget")?.addEventListener("click", closeWidget);
  document.getElementById("musicSettings")?.addEventListener("click", openSettings);
  document.getElementById("connectAppleMusic")?.addEventListener("click", connectAppleMusic);
  document.querySelectorAll("[data-music-device]").forEach(button => button.addEventListener("click", () => {
    selectMusicDevice(musicRequest?.request_id, button.dataset.musicDevice);
  }));
}

function closeWidget() {
  state.activeWidget = null;
  state.widgetExpanded = false;
  state.runningWidgetId = null;
  ui.activeWidget.hidden = true;
  ui.activeWidget.innerHTML = "";
  ui.widgetDock.hidden = true;
  ui.workspace.classList.remove("has-widget", "widget-expanded");
}

async function selectMusicDevice(requestId, deviceId) {
  if (
    !requestId ||
    !deviceId ||
    state.runningWidgetId ||
    state.activeWidget?.kind !== "music" ||
    state.activeWidget.request?.request_id !== requestId
  ) return;
  setWidgetRunning(true);
  try {
    state.activeWidget = await request("/agents/music/select-device", "POST", {
      request_id: requestId,
      device_id: deviceId,
    });
    state.musicResultText = `Selected ${state.activeWidget.request.device_name}.`;
  } catch (error) {
    showToast(error.message);
    if (state.activeWidget) setWidgetRunning(false);
    return;
  }
  state.runningWidgetId = null;
  renderActiveWidget();
  await executeMusic(requestId);
}

function loadMusicKitScript(scriptUrl) {
  if (window.MusicKit) return Promise.resolve();
  if (state.musicKitScript) return state.musicKitScript;
  state.musicKitScript = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = scriptUrl;
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error("Apple MusicKit could not be loaded"));
    document.head.appendChild(script);
  });
  return state.musicKitScript;
}

async function getMusicKit() {
  if (state.musicKit) return state.musicKit;
  const config = await request("/agents/music/client-config", "POST", {});
  await loadMusicKitScript(config.script_url);
  if (!window.MusicKit) throw new Error("Apple MusicKit did not initialize");
  state.musicKit = await window.MusicKit.configure({
    developerToken: config.developer_token,
    app: { name: "Osun", build: "0.6.0" },
  });
  return state.musicKit;
}

async function connectAppleMusic() {
  if (state.runningWidgetId) return;
  let pendingRequestId = null;
  setWidgetRunning(true);
  try {
    const music = await getMusicKit();
    await music.authorize();
    if (!musicKitAuthorized(music)) throw new Error("Apple Music authorization was canceled or denied");
    state.musicResultText = "Apple Music is connected for local headphone playback.";
    if (state.activeWidget?.request?.state === "ready") {
      pendingRequestId = state.activeWidget.request.request_id;
    }
    showToast(state.musicResultText);
  } catch (error) {
    state.musicResultText = `Apple Music connection failed: ${error.message}`;
    showToast(state.musicResultText);
  } finally {
    if (state.activeWidget) setWidgetRunning(false);
  }
  if (pendingRequestId) await executeMusic(pendingRequestId);
}

function musicKitAuthorized(music) {
  return music.isAuthorized === true || Boolean(music.musicUserToken);
}

async function waitForMusicKit(predicate, failureMessage, timeoutMs = 8_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (predicate()) return;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(failureMessage);
}

function musicKitItemId(music) {
  return music.nowPlayingItem?.id || music.nowPlayingItem?.playParams?.id || null;
}

function musicKitNowPlaying(music, fallback = "") {
  const item = music.nowPlayingItem;
  const title = item?.title || item?.attributes?.name || fallback;
  const artist = item?.artistName || item?.attributes?.artistName;
  return artist && title ? `${title} by ${artist}` : title;
}

async function performMusicKitCommand(command) {
  const music = await getMusicKit();
  if (!musicKitAuthorized(music)) {
    const error = new Error("Connect Apple Music in the expanded widget, then try the request again.");
    error.authorizationRequired = true;
    throw error;
  }
  if (command.action === "play") {
    const storefront = music.storefrontCountryCode || "us";
    const response = await music.api.music(`/v1/catalog/${storefront}/search`, {
      term: command.query || "music",
      types: "songs",
      limit: 1,
    });
    const songs = response?.data?.results?.songs?.data || response?.results?.songs?.data || [];
    const song = songs[0];
    if (!song?.id) throw new Error(`Apple Music could not find ${command.query || "that music"}.`);
    await music.setQueue({ song: song.id });
    await music.play();
    await waitForMusicKit(() => music.isPlaying === true, "Apple Music did not report that playback started.");
    const fallbackTitle = song.attributes?.name || command.query || "music";
    const fallbackArtist = song.attributes?.artistName;
    const fallback = fallbackArtist ? `${fallbackTitle} by ${fallbackArtist}` : fallbackTitle;
    return musicKitNowPlaying(music, fallback);
  }
  if (command.action === "pause") {
    await music.pause();
    await waitForMusicKit(() => music.isPlaying === false, "Apple Music did not report that playback paused.");
  }
  if (command.action === "resume") {
    await music.play();
    await waitForMusicKit(() => music.isPlaying === true, "Apple Music did not report that playback resumed.");
  }
  if (command.action === "next" || command.action === "previous") {
    const previousItemId = musicKitItemId(music);
    if (command.action === "next") await music.skipToNextItem();
    if (command.action === "previous") await music.skipToPreviousItem();
    await waitForMusicKit(
      () => music.isPlaying === true && (!previousItemId || musicKitItemId(music) !== previousItemId),
      `Apple Music did not report a ${command.action === "next" ? "next" : "previous"} track transition.`,
    );
  }
  return musicKitNowPlaying(music);
}

async function executeMusic(requestId) {
  if (
    !requestId ||
    state.runningWidgetId ||
    state.activeWidget?.kind !== "music" ||
    state.activeWidget.request?.request_id !== requestId
  ) return;
  setWidgetRunning(true);
  try {
    const execution = await request("/agents/music/execute", "POST", { request_id: requestId });
    if (["simulated", "verified", "completed", "failed"].includes(execution.state)) {
      state.activeWidget.request = execution.request;
      state.activeWidget.execution = execution;
      state.musicResultText = execution.summary;
      appendMessage("assistant", execution.summary, "music");
    } else if (execution.state === "client_required") {
      let nowPlaying = "";
      try {
        nowPlaying = await performMusicKitCommand(execution.command);
      } catch (error) {
        if (error.authorizationRequired) {
          state.activeWidget.request = { ...execution.request, state: "ready" };
          state.musicResultText = error.message;
          state.widgetExpanded = true;
          return;
        }
        const failed = await request("/agents/music/result", "POST", {
          request_id: execution.request_id,
          device_id: execution.device_id,
          success: false,
          error: error.message,
        });
        state.activeWidget.request = failed.request;
        state.activeWidget.execution = failed;
        state.musicResultText = failed.summary;
        appendMessage("assistant", failed.summary, "music");
        return;
      }
      const verified = await request("/agents/music/result", "POST", {
        request_id: execution.request_id,
        device_id: execution.device_id,
        success: true,
        now_playing: nowPlaying,
      });
      state.activeWidget.request = verified.request;
      state.activeWidget.execution = verified;
      state.musicResultText = verified.summary;
      appendMessage("assistant", verified.summary, "music");
    }
    await refreshStatus(false);
    state.activeWidget.devices = state.status.music.devices;
  } catch (error) {
    state.musicResultText = error.message;
    showToast(error.message);
  } finally {
    if (state.activeWidget) setWidgetRunning(false);
  }
}

async function sendMessage(text) {
  text = text.trim();
  if (!text || state.busy) return;
  state.busy = true;
  ui.send.disabled = true;
  appendMessage("user", text, "user");
  ui.input.value = "";
  resizeInput();
  const thinking = showThinking();
  ui.hint.textContent = "Qwen is thinking locally. A cold start can take up to two minutes.";
  try {
    const response = await request("/message", "POST", {
      text,
      context: { lighting_selected_entities: [...state.selectedEntities] },
    });
    thinking.remove();
    appendMessage("assistant", response.text, response.agent);
    if (response.widgets?.length) {
      showAgentWidget(response.widgets[0]);
    }
  } catch (error) {
    thinking.remove();
    appendMessage("assistant", `I couldn't complete that safely: ${error.message}`, "osun");
  } finally {
    state.busy = false;
    ui.send.disabled = false;
    updateComposerHint();
    ui.input.focus();
  }
}

async function applyLighting() {
  const proposal = state.activeWidget?.proposal;
  if (!proposal || state.applyingProposalId === proposal.proposal_id) return;
  state.applyingProposalId = proposal.proposal_id;
  setWidgetRunning(true);
  try {
    const report = await request("/agents/lighting/apply", "POST", { proposal_id: proposal.proposal_id });
    state.resultText = report.summary;
    appendMessage("assistant", report.summary, "lighting");
    await refreshStatus(false);
    state.activeWidget.proposal = null;
    state.activeWidget.lights = state.status.lighting.lights;
    state.activeWidget.paused = state.status.lighting.paused;
    state.activeWidget.live_enabled = state.status.lighting.live_enabled;
    state.activeWidget.autonomous_execution = state.status.lighting.autonomous_execution;
    renderLightingWidget();
  } catch (error) {
    showToast(error.message);
  } finally {
    state.applyingProposalId = null;
    if (state.activeWidget) setWidgetRunning(false);
  }
}

async function cancelLighting() {
  setWidgetRunning(true);
  try {
    await request("/agents/lighting/cancel", "POST", {});
    state.activeWidget.proposal = null;
    state.resultText = "Proposal canceled. No light change was sent.";
  } catch (error) { showToast(error.message); }
  finally { if (state.activeWidget) setWidgetRunning(false); }
}

async function pauseLighting() {
  setWidgetRunning(true);
  try {
    await request("/agents/lighting/pause", "POST", {});
    state.resultText = "Lighting execution is paused. Pending changes were canceled.";
    appendMessage("assistant", state.resultText, "lighting");
    await refreshStatus(false);
    state.activeWidget.proposal = null;
    state.activeWidget.paused = true;
    state.activeWidget.live_enabled = state.status.lighting.live_enabled;
    state.activeWidget.autonomous_execution = state.status.lighting.autonomous_execution;
  } catch (error) { showToast(error.message); }
  finally { if (state.activeWidget) setWidgetRunning(false); }
}

async function refreshStatus(renderWidget = true) {
  state.status = await request("/status");
  updateComposerHint();
  const box = state.status.agent_box;
  ui.agentBoxModel.textContent = box.model;
  ui.agentBoxDot.classList.toggle("online", box.online && box.model_available);
  ui.agentBoxStatus.textContent = box.online
    ? box.model_available ? box.warming || !box.loaded ? "Warming model on GPU…" : "Local model ready" : "Runtime online · model missing"
    : "Local model unavailable";
  if (!state.selectedEntities.size) state.status.lighting.lights.forEach(light => state.selectedEntities.add(light.entity_id));
  if (renderWidget && state.activeWidget) {
    if (state.activeWidget.kind === "lighting") {
      state.activeWidget.lights = state.status.lighting.lights;
      state.activeWidget.paused = state.status.lighting.paused;
      state.activeWidget.mode = state.status.lighting.effective_mode;
      state.activeWidget.live_enabled = state.status.lighting.live_enabled;
      state.activeWidget.autonomous_execution = state.status.lighting.autonomous_execution;
    }
    if (state.activeWidget.kind === "music") {
      state.activeWidget.mode = state.status.music.effective_mode;
      state.activeWidget.developer_token_configured = state.status.music.developer_token_configured;
      state.activeWidget.windows_app_available = state.status.music.windows_app_available;
      state.activeWidget.autonomous_execution = state.status.music.autonomous_execution;
      state.activeWidget.recent_window_seconds = state.status.music.recent_window_seconds;
      state.activeWidget.devices = state.status.music.devices;
    }
    renderActiveWidget();
  }
}

function renderMediaCenterOptions(selectedEntityId = "", selectedName = "Living Room Apple TV") {
  const discovered = [...state.discoveredMediaCenters];
  if (selectedEntityId && !discovered.some(center => center.entity_id === selectedEntityId)) {
    discovered.push({ entity_id: selectedEntityId, friendly_name: selectedName, state: "saved" });
  }
  const options = [
    '<option value="" data-name="Living Room Apple TV">Auto-detect Living Room Apple TV (legacy)</option>',
    ...discovered.map(center => `<option value="${escapeHtml(center.entity_id)}" data-name="${escapeHtml(center.friendly_name)}">${escapeHtml(center.friendly_name)} · ${escapeHtml(center.entity_id)}</option>`),
  ];
  ui.mediaCenterSelect.innerHTML = options.join("");
  ui.mediaCenterSelect.value = selectedEntityId;
  if (ui.mediaCenterSelect.value !== selectedEntityId) ui.mediaCenterSelect.value = "";
  updateMediaCenterPreview();
}

function updateMediaCenterPreview() {
  const selected = ui.mediaCenterSelect.selectedOptions[0];
  const name = selected?.dataset.name || "Living Room Apple TV";
  const entityId = selected?.value || "";
  ui.mediaCenterDeviceName.textContent = name;
  ui.mediaCenterDeviceDetail.textContent = entityId
    ? `Allowlisted Home Assistant entity · ${entityId}`
    : "Legacy exact-name auto-detection; discover and select an entity for reliable routing";
}

function renderSettings() {
  const box = state.status.agent_box;
  const lighting = state.status.lighting;
  const settings = lighting.settings;
  ui.settingsModelBadge.textContent = box.online && box.model_available
    ? box.warming || !box.loaded ? "Warming" : "Ready"
    : "Needs attention";
  ui.qwenProvider.value = box.provider;
  ui.qwenModel.value = box.model;
  ui.qwenEndpoint.value = box.endpoint;
  ui.qwenHelp.textContent = box.online
    ? box.model_available
      ? box.warming || !box.loaded ? "Qwen is loading into GPU memory in the background." : "Qwen is installed locally and loaded on the Agent Box."
      : "Ollama is online, but the configured Qwen model is missing."
    : box.error || "Ollama is not responding on loopback.";
  document.querySelector(`input[name="lightingMode"][value="${settings.mode}"]`).checked = true;
  ui.haUrl.value = settings.home_assistant_url;
  ui.haToken.value = "";
  ui.liveEnabled.checked = settings.live_enabled;
  ui.autonomousExecution.checked = settings.autonomous_execution;
  ui.globalPause.checked = settings.global_pause;
  ui.lightingModeBadge.textContent = lighting.effective_mode === "home_assistant" ? "Home Assistant" : "Simulator";
  state.discoveredLights = lighting.lights;
  renderDiscoveredLights(settings.allowed_entities);
  const music = state.status.music;
  document.querySelector(`input[name="musicMode"][value="${music.mode}"]`).checked = true;
  ui.musicDeveloperToken.value = "";
  ui.musicEnabled.checked = music.enabled;
  ui.musicAutonomousExecution.checked = music.autonomous_execution;
  ui.musicModeBadge.textContent = musicModeLabel(music.effective_mode);
  renderMediaCenterOptions(music.media_center?.entity_id || "", music.media_center?.name || "Living Room Apple TV");
  ui.musicAppTestResult.textContent = music.windows_app_available
    ? "Windows app control is supported; test to inspect the Apple Music installation and live session."
    : "Windows app control is unavailable on this operating system.";
}

function renderDiscoveredLights(allowed = []) {
  const allowedSet = new Set(allowed);
  const renderChoice = light => {
    const members = (light.member_names || []).join(", ");
    return `<label><input class="allowed-light" type="checkbox" value="${escapeHtml(light.entity_id)}" ${allowedSet.has(light.entity_id) ? "checked" : ""}><span><strong>${escapeHtml(light.friendly_name)}</strong>${members ? `<small>Contains ${escapeHtml(members)}</small>` : ""}</span></label>`;
  };
  const zones = state.discoveredLights.filter(light => light.kind === "zone").map(renderChoice).join("");
  const lights = state.discoveredLights.filter(light => light.kind !== "zone").map(renderChoice).join("");
  ui.discoveredLights.innerHTML = `
    <div class="discovery-group"><p class="section-kicker">Zones</p>${zones || '<p class="muted small">No zones discovered.</p>'}</div>
    <div class="discovery-group"><p class="section-kicker">Lights</p>${lights || '<p class="muted small">No individual lights discovered.</p>'}</div>`;
}

async function openSettings() {
  try {
    await refreshStatus(false);
    renderSettings();
    ui.settings.showModal();
  } catch (error) { showToast(error.message); }
}

async function discoverLights() {
  ui.discover.disabled = true;
  ui.connectionResult.textContent = "Connecting locally…";
  try {
    const result = await request("/agents/lighting/settings/test", "POST", {
      home_assistant_url: ui.haUrl.value,
      token: ui.haToken.value,
    });
    state.discoveredLights = result.lights;
    renderDiscoveredLights(state.status.lighting.settings.allowed_entities);
    ui.connectionResult.textContent = `Connected · ${result.lights.length} light entities found`;
  } catch (error) {
    ui.connectionResult.textContent = error.message;
  } finally { ui.discover.disabled = false; }
}

async function discoverMediaCenters() {
  ui.discoverMediaCenters.disabled = true;
  ui.mediaCenterResult.textContent = "Reading Home Assistant media players…";
  const currentSelection = ui.mediaCenterSelect.value;
  const currentName = ui.mediaCenterSelect.selectedOptions[0]?.dataset.name || "Living Room Apple TV";
  try {
    const result = await request("/agents/music/settings/discover-media-centers", "POST", {});
    state.discoveredMediaCenters = Array.isArray(result.media_centers) ? result.media_centers : [];
    renderMediaCenterOptions(currentSelection || result.selected_entity_id || "", currentName);
    ui.mediaCenterResult.textContent = state.discoveredMediaCenters.length
      ? `${state.discoveredMediaCenters.length} media center${state.discoveredMediaCenters.length === 1 ? "" : "s"} found. Select your Apple TV, then save settings.`
      : "No Home Assistant media_player entities were found.";
  } catch (error) {
    ui.mediaCenterResult.textContent = error.message;
  } finally { ui.discoverMediaCenters.disabled = false; }
}

async function testAppleMusicApp() {
  ui.musicAppTest.disabled = true;
  ui.musicAppTestResult.textContent = "Checking the targeted Apple Music session…";
  try {
    const result = await request("/agents/music/settings/test-windows-app", "POST", {});
    const destinationSummary = [
      result.bluetooth_headphones_connected ? `Headphones: ${result.headphone_names?.[0] || "connected"}` : "Headphones: not connected",
      result.apple_tv_available
        ? `${result.apple_tv_name || "Media center"}: available`
        : `Media center: unavailable${result.apple_tv_error ? ` (${result.apple_tv_error})` : ""}`,
    ].join(" · ");
    if (!result.success) {
      ui.musicAppTestResult.textContent = result.error || "Apple Music is unavailable.";
    } else if (result.session_available) {
      ui.musicAppTestResult.textContent = result.now_playing
        ? `Connected · ${result.now_playing}`
        : "Connected · Apple Music media controls are available";
    } else if (result.automation_available) {
      ui.musicAppTestResult.textContent = "Apple Music is open; UI fallback is available. Start a song once to expose media verification.";
    } else if (result.running) {
      ui.musicAppTestResult.textContent = "Apple Music is running, but Windows is hiding its controls from Osun. Keep both apps at the same privilege level, reopen the full Apple Music window, and test again.";
    } else {
      ui.musicAppTestResult.textContent = "Apple Music is installed. Open it and sign in once, then test again.";
    }
    ui.musicAppTestResult.textContent += ` · ${destinationSummary}`;
  } catch (error) {
    ui.musicAppTestResult.textContent = error.message;
  } finally { ui.musicAppTest.disabled = false; }
}

async function saveSettings() {
  const mode = document.querySelector('input[name="lightingMode"]:checked').value;
  const musicMode = document.querySelector('input[name="musicMode"]:checked').value;
  const mediaCenterOption = ui.mediaCenterSelect.selectedOptions[0];
  const allowed = [...document.querySelectorAll(".allowed-light:checked")].map(input => input.value);
  try {
    const lighting = await request("/agents/lighting/settings/save", "POST", {
      mode,
      home_assistant_url: ui.haUrl.value,
      token: ui.haToken.value,
      allowed_entities: allowed,
      live_enabled: ui.liveEnabled.checked,
      autonomous_execution: ui.autonomousExecution.checked,
      global_pause: ui.globalPause.checked,
    });
    const music = await request("/agents/music/settings/save", "POST", {
      mode: musicMode,
      developer_token: ui.musicDeveloperToken.value,
      enabled: ui.musicEnabled.checked,
      autonomous_execution: ui.musicAutonomousExecution.checked,
      media_center_entity_id: ui.mediaCenterSelect.value,
      media_center_name: mediaCenterOption?.dataset.name || "Living Room Apple TV",
    });
    ui.haToken.value = "";
    ui.musicDeveloperToken.value = "";
    if (music.effective_mode === "simulator") state.musicKit = null;
    await refreshStatus(false);
    ui.settings.close();
    showToast(`Lighting and Music settings saved. Music is in ${musicModeLabel(music.effective_mode)} mode.`);
    if (state.activeWidget?.kind === "lighting") {
      state.activeWidget = {
        ...state.activeWidget,
        proposal: lighting.pending,
        mode: lighting.effective_mode,
        paused: lighting.paused,
        live_enabled: lighting.live_enabled,
        autonomous_execution: lighting.autonomous_execution,
        lights: lighting.lights,
        warning: lighting.warning,
      };
      renderActiveWidget();
    }
    if (state.activeWidget?.kind === "music") {
      state.activeWidget = {
        ...state.activeWidget,
        mode: music.effective_mode,
        developer_token_configured: music.developer_token_configured,
        windows_app_available: music.windows_app_available,
        autonomous_execution: music.autonomous_execution,
        devices: music.devices,
      };
      renderActiveWidget();
    }
  } catch (error) { showToast(error.message); }
}

async function deleteToken() {
  if (!window.confirm("Delete the protected Home Assistant token? This disables live lighting and Living Room Apple TV playback.")) return;
  try {
    await request("/agents/lighting/settings/delete-token", "POST", {});
    await refreshStatus(false);
    renderSettings();
    showToast("The protected lighting token was deleted.");
  } catch (error) { showToast(error.message); }
}

async function deleteMusicToken() {
  if (!window.confirm("Delete the optional protected MusicKit developer token? Windows app mode will keep working.")) return;
  try {
    await request("/agents/music/settings/delete-token", "POST", {});
    state.musicKit = null;
    await refreshStatus(false);
    renderSettings();
    showToast("The protected MusicKit developer token was deleted.");
  } catch (error) { showToast(error.message); }
}

async function newChat() {
  try { await request("/new-chat", "POST", {}); } catch (error) { showToast(error.message); return; }
  [...ui.messages.querySelectorAll(".message")].forEach(item => item.remove());
  ui.welcome.hidden = false;
  state.activeWidget = null;
  state.resultText = "";
  state.musicResultText = "";
  closeWidget();
  ui.input.focus();
}

function resizeInput() {
  ui.input.style.height = "auto";
  ui.input.style.height = `${Math.min(ui.input.scrollHeight, 130)}px`;
}

ui.composer.addEventListener("submit", event => { event.preventDefault(); sendMessage(ui.input.value); });
ui.input.addEventListener("input", resizeInput);
ui.input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); ui.composer.requestSubmit(); }
});
document.querySelectorAll("[data-prompt]").forEach(button => button.addEventListener("click", () => sendMessage(button.dataset.prompt)));
ui.newChat.addEventListener("click", newChat);
ui.lightingNav.addEventListener("click", () => {
  if (state.activeWidget?.kind !== "lighting") return;
  state.widgetExpanded = true;
  renderActiveWidget();
});
ui.musicNav.addEventListener("click", () => {
  if (state.activeWidget?.kind !== "music") return;
  state.widgetExpanded = true;
  renderActiveWidget();
});
ui.settingsButton.addEventListener("click", openSettings);
ui.discover.addEventListener("click", discoverLights);
ui.discoverMediaCenters.addEventListener("click", discoverMediaCenters);
ui.mediaCenterSelect.addEventListener("change", updateMediaCenterPreview);
ui.musicAppTest.addEventListener("click", testAppleMusicApp);
ui.saveSettings.addEventListener("click", saveSettings);
ui.deleteToken.addEventListener("click", deleteToken);
ui.deleteMusicToken.addEventListener("click", deleteMusicToken);
ui.quit.addEventListener("click", async () => {
  try { await request("/shutdown", "POST", {}); } catch (_) { /* service is intentionally stopping */ }
  window.close();
});

refreshStatus().catch(error => showToast(error.message));
ui.input.focus();
