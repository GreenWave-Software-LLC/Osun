"use strict";

const sessionToken = location.pathname.split("/").filter(Boolean)[1];
const apiRoot = `/api/${sessionToken}`;

const state = {
  status: null,
  activeWidget: null,
  selectedEntities: new Set(),
  discoveredLights: [],
  busy: false,
  resultText: "",
};

const ui = {
  messages: document.getElementById("messages"),
  welcome: document.getElementById("welcome"),
  composer: document.getElementById("composer"),
  input: document.getElementById("messageInput"),
  send: document.getElementById("sendButton"),
  hint: document.getElementById("composerHint"),
  widgetEmpty: document.getElementById("widgetEmpty"),
  activeWidget: document.getElementById("activeWidget"),
  newChat: document.getElementById("newChatButton"),
  lightingNav: document.getElementById("lightingNav"),
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
  globalPause: document.getElementById("globalPause"),
  deleteToken: document.getElementById("deleteTokenButton"),
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

function appendMessage(role, text, agent = "osun") {
  if (ui.welcome) ui.welcome.hidden = true;
  const item = document.createElement("article");
  item.className = `message ${role}`;
  const name = role === "user" ? "You" : agent === "lighting" ? "Lighting agent" : "Osun";
  const avatar = role === "user" ? "Y" : agent === "lighting" ? "L" : "O";
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
  if (widget.mode === "home_assistant" && !widget.live_enabled) reasons.push("live light execution is disabled");
  if (widget.paused) reasons.push("execution is paused");
  if (!reasons.length) return null;
  return `${reasons.join(" and ")}. Open Connection, review the allowlist, enable live execution, clear Pause, and save.`;
}

function renderLightingWidget(widget = state.activeWidget) {
  if (!widget) return;
  state.activeWidget = widget;
  ui.widgetEmpty.hidden = true;
  ui.activeWidget.hidden = false;
  const lights = widget.lights || [];
  if (!state.selectedEntities.size) lights.forEach(light => state.selectedEntities.add(light.entity_id));
  const lightRows = lights.map(light => `
    <label class="light-row">
      <span class="light-identity">
        <input type="checkbox" class="widget-light-select" value="${escapeHtml(light.entity_id)}" ${state.selectedEntities.has(light.entity_id) ? "checked" : ""}>
        <span class="light-dot ${light.state === "on" ? "on" : ""}" style="color:${lightColor(light)};background:${lightColor(light)}"></span>
        <span class="light-name">${escapeHtml(light.friendly_name)}</span>
      </span>
      <span class="light-state">${escapeHtml(light.state)}</span>
    </label>`).join("");
  const proposal = widget.proposal;
  const executionGate = lightingExecutionGate(widget);
  const changes = (proposal?.changes || []).map(change => `
    <div class="change"><strong>${escapeHtml(change.friendly_name)}</strong><span>${escapeHtml(change.preview)}</span></div>`).join("");
  const proposalHtml = proposal ? `
    <div class="proposal-card">
      <div class="proposal-heading"><h3>${escapeHtml(proposal.theme_name || "Lighting change")}</h3><span>Review only</span></div>
      <p class="proposal-summary">${escapeHtml(proposal.summary)}</p>
      ${paletteFromProposal(proposal) ? `<div class="palette">${paletteFromProposal(proposal)}</div>` : ""}
      <div class="change-list">${changes}</div>
      <div class="widget-actions">
        <button class="secondary-button" id="cancelLighting" type="button">Cancel</button>
        <button class="primary-button" id="applyLighting" type="button" ${executionGate ? "disabled" : ""}>${executionGate ? "Execution locked" : "Apply exact proposal"}</button>
      </div>
    </div>` : '<p class="muted small">Ask Osun for a lighting change to create an exact preview.</p>';
  ui.activeWidget.innerHTML = `
    <div class="widget-card">
      <div class="widget-hero">
        <div class="widget-title-row">
          <div class="widget-agent"><div class="widget-glyph">◌</div><div><h2>Lighting</h2><p>Focused agent widget</p></div></div>
          <button id="closeWidget" class="widget-close" type="button" aria-label="Close lighting widget">×</button>
        </div>
        <div class="widget-mode">
          <span class="${widget.mode === "home_assistant" ? "live" : ""}">${escapeHtml(widget.mode === "home_assistant" ? "Home Assistant" : "Simulator")}</span>
          <span>${widget.paused ? "Paused" : "Execution ready"}</span>
          <span>${lights.length} lights</span>
        </div>
      </div>
      <div class="widget-body">
        ${executionGate ? `<p class="execution-gate widget-gate">${escapeHtml(executionGate)}</p>` : ""}
        <section class="widget-section"><p class="section-kicker">Targets</p><div class="light-list">${lightRows || '<p class="muted small">No allowlisted lights are available.</p>'}</div></section>
        <section class="widget-section"><p class="section-kicker">Exact proposal</p>${proposalHtml}</section>
        <section class="widget-section">
          <div class="widget-actions"><button id="lightingSettings" class="secondary-button" type="button">Connection</button><button id="pauseLighting" class="danger-button" type="button">Emergency pause</button></div>
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
  document.getElementById("closeWidget")?.addEventListener("click", closeWidget);
  document.getElementById("lightingSettings")?.addEventListener("click", openSettings);
  document.getElementById("pauseLighting")?.addEventListener("click", pauseLighting);
  document.getElementById("cancelLighting")?.addEventListener("click", cancelLighting);
  document.getElementById("applyLighting")?.addEventListener("click", applyLighting);
}

function closeWidget() {
  state.activeWidget = null;
  ui.activeWidget.hidden = true;
  ui.widgetEmpty.hidden = false;
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
      state.resultText = "";
      renderLightingWidget(response.widgets[0]);
    }
  } catch (error) {
    thinking.remove();
    appendMessage("assistant", `I couldn't complete that safely: ${error.message}`, "osun");
  } finally {
    state.busy = false;
    ui.send.disabled = false;
    ui.hint.textContent = "Qwen runs locally. Device changes always require a visible Apply.";
    ui.input.focus();
  }
}

async function applyLighting() {
  const proposal = state.activeWidget?.proposal;
  if (!proposal) return;
  try {
    const report = await request("/agents/lighting/apply", "POST", { proposal_id: proposal.proposal_id });
    state.resultText = report.summary;
    appendMessage("assistant", report.summary, "lighting");
    await refreshStatus(false);
    state.activeWidget.proposal = null;
    state.activeWidget.lights = state.status.lighting.lights;
    state.activeWidget.paused = state.status.lighting.paused;
    state.activeWidget.live_enabled = state.status.lighting.live_enabled;
    renderLightingWidget();
  } catch (error) { showToast(error.message); }
}

async function cancelLighting() {
  try {
    await request("/agents/lighting/cancel", "POST", {});
    state.activeWidget.proposal = null;
    state.resultText = "Proposal canceled. No light change was sent.";
    renderLightingWidget();
  } catch (error) { showToast(error.message); }
}

async function pauseLighting() {
  try {
    await request("/agents/lighting/pause", "POST", {});
    state.resultText = "Lighting execution is paused. Pending changes were canceled.";
    appendMessage("assistant", state.resultText, "lighting");
    await refreshStatus(false);
    state.activeWidget.proposal = null;
    state.activeWidget.paused = true;
    state.activeWidget.live_enabled = state.status.lighting.live_enabled;
    renderLightingWidget();
  } catch (error) { showToast(error.message); }
}

async function refreshStatus(renderWidget = true) {
  state.status = await request("/status");
  const box = state.status.agent_box;
  ui.agentBoxModel.textContent = box.model;
  ui.agentBoxDot.classList.toggle("online", box.online && box.model_available);
  ui.agentBoxStatus.textContent = box.online
    ? box.model_available ? box.warming || !box.loaded ? "Warming model on GPU…" : "Local model ready" : "Runtime online · model missing"
    : "Local model unavailable";
  if (!state.selectedEntities.size) state.status.lighting.lights.forEach(light => state.selectedEntities.add(light.entity_id));
  if (renderWidget && state.activeWidget) {
    state.activeWidget.lights = state.status.lighting.lights;
    state.activeWidget.paused = state.status.lighting.paused;
    state.activeWidget.mode = state.status.lighting.effective_mode;
    state.activeWidget.live_enabled = state.status.lighting.live_enabled;
    renderLightingWidget();
  }
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
  ui.globalPause.checked = settings.global_pause;
  ui.lightingModeBadge.textContent = lighting.effective_mode === "home_assistant" ? "Home Assistant" : "Simulator";
  state.discoveredLights = lighting.lights;
  renderDiscoveredLights(settings.allowed_entities);
}

function renderDiscoveredLights(allowed = []) {
  const allowedSet = new Set(allowed);
  ui.discoveredLights.innerHTML = state.discoveredLights.map(light => `
    <label><input class="allowed-light" type="checkbox" value="${escapeHtml(light.entity_id)}" ${allowedSet.has(light.entity_id) ? "checked" : ""}><span>${escapeHtml(light.friendly_name)}</span></label>`).join("");
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

async function saveSettings() {
  const mode = document.querySelector('input[name="lightingMode"]:checked').value;
  const allowed = [...document.querySelectorAll(".allowed-light:checked")].map(input => input.value);
  try {
    const lighting = await request("/agents/lighting/settings/save", "POST", {
      mode,
      home_assistant_url: ui.haUrl.value,
      token: ui.haToken.value,
      allowed_entities: allowed,
      live_enabled: ui.liveEnabled.checked,
      global_pause: ui.globalPause.checked,
    });
    ui.haToken.value = "";
    await refreshStatus(false);
    ui.settings.close();
    showToast(`Lighting saved in ${lighting.effective_mode === "home_assistant" ? "Home Assistant" : "simulator"} mode.`);
    if (state.activeWidget) {
      state.activeWidget = {
        ...state.activeWidget,
        proposal: lighting.pending,
        mode: lighting.effective_mode,
        paused: lighting.paused,
        live_enabled: lighting.live_enabled,
        lights: lighting.lights,
        warning: lighting.warning,
      };
      renderLightingWidget();
    }
  } catch (error) { showToast(error.message); }
}

async function deleteToken() {
  if (!window.confirm("Delete the protected Home Assistant token and return lighting to simulation?")) return;
  try {
    await request("/agents/lighting/settings/delete-token", "POST", {});
    await refreshStatus(false);
    renderSettings();
    showToast("The protected lighting token was deleted.");
  } catch (error) { showToast(error.message); }
}

async function newChat() {
  try { await request("/new-chat", "POST", {}); } catch (error) { showToast(error.message); return; }
  [...ui.messages.querySelectorAll(".message")].forEach(item => item.remove());
  ui.welcome.hidden = false;
  state.activeWidget = null;
  state.resultText = "";
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
  const lighting = state.status?.lighting;
  if (!lighting) return;
  renderLightingWidget({ id: "lighting", kind: "lighting", title: "Lighting", agent: "lighting", proposal: lighting.pending, mode: lighting.effective_mode, paused: lighting.paused, live_enabled: lighting.live_enabled, lights: lighting.lights, warning: lighting.warning });
});
ui.settingsButton.addEventListener("click", openSettings);
ui.discover.addEventListener("click", discoverLights);
ui.saveSettings.addEventListener("click", saveSettings);
ui.deleteToken.addEventListener("click", deleteToken);
ui.quit.addEventListener("click", async () => {
  try { await request("/shutdown", "POST", {}); } catch (_) { /* service is intentionally stopping */ }
  window.close();
});

refreshStatus().catch(error => showToast(error.message));
ui.input.focus();
