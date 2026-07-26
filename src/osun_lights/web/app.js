"use strict";

const pathParts = window.location.pathname.split("/");
const sessionToken = pathParts[2];
const apiBase = `/api/${sessionToken}`;

const ui = {
  chat: document.querySelector("#chat"),
  lightList: document.querySelector("#lightList"),
  modeBadge: document.querySelector("#modeBadge"),
  proposalCard: document.querySelector("#proposalCard"),
  proposalTitle: document.querySelector("#proposalTitle"),
  proposalRationale: document.querySelector("#proposalRationale"),
  proposalChanges: document.querySelector("#proposalChanges"),
  applyButton: document.querySelector("#applyButton"),
  cancelButton: document.querySelector("#cancelButton"),
  pauseButton: document.querySelector("#pauseButton"),
  refreshButton: document.querySelector("#refreshButton"),
  composer: document.querySelector("#composer"),
  messageInput: document.querySelector("#messageInput"),
  sendButton: document.querySelector("#sendButton"),
  settingsButton: document.querySelector("#settingsButton"),
  settingsDialog: document.querySelector("#settingsDialog"),
  closeSettingsButton: document.querySelector("#closeSettingsButton"),
  haUrl: document.querySelector("#haUrl"),
  haToken: document.querySelector("#haToken"),
  connectionResult: document.querySelector("#connectionResult"),
  testConnectionButton: document.querySelector("#testConnectionButton"),
  discoveredLights: document.querySelector("#discoveredLights"),
  liveEnabled: document.querySelector("#liveEnabled"),
  globalPause: document.querySelector("#globalPause"),
  saveSettingsButton: document.querySelector("#saveSettingsButton"),
  deleteTokenButton: document.querySelector("#deleteTokenButton"),
  quitButton: document.querySelector("#quitButton"),
};

let state = null;
let pending = null;
let discovered = [];

async function request(path, method = "GET", payload = null) {
  const options = { method, headers: { "Accept": "application/json" } };
  if (payload !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }
  const response = await fetch(`${apiBase}${path}`, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function appendMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  const name = document.createElement("div");
  name.className = "message-role";
  name.textContent = role === "owner" ? "YOU" : role === "system" ? "SYSTEM" : "OSUN";
  const body = document.createElement("div");
  body.className = "message-body";
  body.textContent = text;
  wrapper.append(name, body);
  ui.chat.append(wrapper);
  ui.chat.scrollTop = ui.chat.scrollHeight;
}

function selectedEntities() {
  return [...ui.lightList.querySelectorAll("input[type=checkbox]:checked")].map((input) => input.value);
}

function renderLights(lights, selectAll = false) {
  const previous = new Set(selectedEntities());
  ui.lightList.replaceChildren();
  if (!lights.length) {
    const empty = document.createElement("p");
    empty.className = "muted small";
    empty.textContent = "No allowed lights are available.";
    ui.lightList.append(empty);
    return;
  }
  for (const light of lights) {
    const row = document.createElement("label");
    row.className = "light-row";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = light.entity_id;
    checkbox.checked = selectAll || previous.has(light.entity_id) || previous.size === 0;
    const name = document.createElement("span");
    name.className = "light-name";
    name.textContent = light.friendly_name;
    const lightState = document.createElement("span");
    lightState.className = "light-state";
    lightState.textContent = light.state;
    row.append(checkbox, name, lightState);
    ui.lightList.append(row);
  }
}

function renderStatus(nextState, selectAll = false) {
  state = nextState;
  const mode = state.effective_mode === "home_assistant" ? "HOME ASSISTANT" : "SIMULATOR";
  const suffix = state.paused ? "PAUSED" : state.effective_mode === "home_assistant" && state.live_enabled ? "LIVE" : "SAFE";
  ui.modeBadge.textContent = `${mode} · ${suffix}`;
  ui.pauseButton.textContent = state.paused ? "Paused · settings to resume" : state.effective_mode === "simulator" ? "Pause simulator" : "Emergency pause";
  renderLights(state.lights || [], selectAll);
  renderProposal(state.pending || null);
  if (state.warning) appendMessage("system", `Connection status: ${state.warning}`);
}

function renderProposal(proposal) {
  pending = proposal;
  ui.proposalChanges.replaceChildren();
  if (!proposal) {
    ui.proposalCard.classList.add("empty");
    ui.proposalTitle.textContent = "No pending lighting change";
    ui.proposalRationale.textContent = "Describe a mood or ask for a normal adjustment.";
    ui.applyButton.disabled = true;
    ui.cancelButton.disabled = true;
    return;
  }
  ui.proposalCard.classList.remove("empty");
  ui.proposalTitle.textContent = proposal.summary;
  ui.proposalRationale.textContent = proposal.rationale || "Review every target and value before applying.";
  for (const change of proposal.changes) {
    const row = document.createElement("div");
    row.className = "change";
    const swatch = document.createElement("span");
    swatch.className = "swatch";
    if (change.rgb_color) swatch.style.background = `rgb(${change.rgb_color.join(",")})`;
    const text = document.createElement("span");
    text.className = "change-text";
    text.textContent = change.preview;
    row.append(swatch, text);
    ui.proposalChanges.append(row);
  }
  ui.applyButton.disabled = false;
  ui.cancelButton.disabled = false;
}

async function refresh(selectAll = false) {
  ui.refreshButton.disabled = true;
  try {
    renderStatus(await request("/status"), selectAll);
  } catch (error) {
    appendMessage("system", `Refresh failed safely: ${error.message}`);
  } finally {
    ui.refreshButton.disabled = false;
  }
}

async function sendMessage(text) {
  const clean = text.trim();
  if (!clean) return;
  appendMessage("owner", clean);
  ui.sendButton.disabled = true;
  ui.messageInput.disabled = true;
  try {
    const reply = await request("/message", "POST", { text: clean, selected_entities: selectedEntities() });
    appendMessage("osun", reply.text);
    renderProposal(reply.proposal);
  } catch (error) {
    appendMessage("system", `I couldn't prepare that proposal: ${error.message}`);
  } finally {
    ui.sendButton.disabled = false;
    ui.messageInput.disabled = false;
    ui.messageInput.focus();
  }
}

ui.composer.addEventListener("submit", (event) => {
  event.preventDefault();
  const value = ui.messageInput.value;
  ui.messageInput.value = "";
  sendMessage(value);
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});

ui.applyButton.addEventListener("click", async () => {
  if (!pending) return;
  ui.applyButton.disabled = true;
  ui.applyButton.textContent = "Applying…";
  try {
    const report = await request("/apply", "POST", { proposal_id: pending.proposal_id });
    if (report.state === "verified") {
      appendMessage("osun", `Done—${report.summary}`);
    } else if (report.state === "denied") {
      appendMessage("osun", `I didn't change the lights: ${report.items[0]?.detail?.replaceAll("_", " ") || "policy denied"}.`);
    } else {
      const unresolved = report.items.filter((item) => item.state !== "verified").map((item) => `${item.entity_id}: ${item.detail}`).join("; ");
      appendMessage("system", `The result is ${report.state}, not confirmed success. ${unresolved}`);
    }
    renderProposal(null);
    await refresh();
  } catch (error) {
    appendMessage("system", `Execution failed safely: ${error.message}`);
  } finally {
    ui.applyButton.textContent = "Apply";
  }
});

ui.cancelButton.addEventListener("click", async () => {
  try { await request("/cancel", "POST", {}); } catch (_) { /* visible local state is still canceled */ }
  renderProposal(null);
  appendMessage("osun", "Canceled. No light change was executed.");
});

ui.pauseButton.addEventListener("click", async () => {
  try {
    await request("/pause", "POST", {});
    renderProposal(null);
    appendMessage("system", "Execution is paused. Pending proposals were canceled; no model is involved in this control.");
    await refresh();
  } catch (error) {
    appendMessage("system", `Pause failed: ${error.message}. Close the app and use Home Assistant directly if needed.`);
  }
});

ui.refreshButton.addEventListener("click", () => refresh());

function renderDiscovered(lights, selectedIds) {
  const selected = new Set(selectedIds || []);
  discovered = lights;
  ui.discoveredLights.replaceChildren();
  if (!lights.length) {
    const empty = document.createElement("p");
    empty.className = "muted small";
    empty.style.padding = "10px";
    empty.textContent = "Test the connection to discover light entities.";
    ui.discoveredLights.append(empty);
    return;
  }
  for (const light of lights) {
    const row = document.createElement("label");
    row.className = "entity-option";
    const box = document.createElement("input");
    box.type = "checkbox";
    box.value = light.entity_id;
    box.checked = selected.has(light.entity_id);
    const name = document.createElement("span");
    name.textContent = light.friendly_name;
    const id = document.createElement("span");
    id.className = "entity-id";
    id.textContent = light.entity_id;
    row.append(box, name, id);
    ui.discoveredLights.append(row);
  }
}

ui.settingsButton.addEventListener("click", () => {
  if (!state) return;
  const settings = state.settings;
  document.querySelector(`input[name=mode][value=${settings.mode}]`).checked = true;
  ui.haUrl.value = settings.home_assistant_url;
  ui.haToken.value = "";
  ui.liveEnabled.checked = settings.live_enabled;
  ui.globalPause.checked = settings.global_pause;
  ui.connectionResult.textContent = settings.credential_saved
    ? "A protected token is saved. Leave the field blank to keep it."
    : "No protected Home Assistant token is saved.";
  const existing = (state.lights || []).filter((light) => settings.allowed_entities.includes(light.entity_id));
  const placeholders = settings.allowed_entities.map((entity) => existing.find((light) => light.entity_id === entity) || {
    entity_id: entity,
    friendly_name: entity.replace("light.", "").replaceAll("_", " "),
  });
  renderDiscovered(placeholders, settings.allowed_entities);
  ui.settingsDialog.showModal();
});

ui.testConnectionButton.addEventListener("click", async () => {
  ui.testConnectionButton.disabled = true;
  ui.testConnectionButton.textContent = "Testing…";
  ui.connectionResult.textContent = "Connecting locally…";
  try {
    const result = await request("/settings/test", "POST", {
      home_assistant_url: ui.haUrl.value,
      token: ui.haToken.value,
    });
    renderDiscovered(result.lights, state?.settings?.allowed_entities || []);
    ui.connectionResult.textContent = `Connected. Found ${result.lights.length} light entities. Select only the lights Osun may control.`;
  } catch (error) {
    ui.connectionResult.textContent = `Connection failed safely: ${error.message}`;
  } finally {
    ui.testConnectionButton.disabled = false;
    ui.testConnectionButton.textContent = "Test & discover lights";
  }
});

ui.saveSettingsButton.addEventListener("click", async () => {
  const mode = document.querySelector("input[name=mode]:checked").value;
  const allowed = [...ui.discoveredLights.querySelectorAll("input:checked")].map((input) => input.value);
  ui.saveSettingsButton.disabled = true;
  ui.connectionResult.textContent = "Validating and saving…";
  try {
    const next = await request("/settings/save", "POST", {
      mode,
      home_assistant_url: ui.haUrl.value,
      token: ui.haToken.value,
      allowed_entities: allowed,
      live_enabled: ui.liveEnabled.checked,
      global_pause: ui.globalPause.checked,
    });
    ui.haToken.value = "";
    ui.settingsDialog.close();
    renderStatus(next, true);
    appendMessage("system", "Connection and safety settings were validated and reloaded.");
  } catch (error) {
    ui.connectionResult.textContent = `Settings not saved: ${error.message}`;
  } finally {
    ui.saveSettingsButton.disabled = false;
  }
});

ui.deleteTokenButton.addEventListener("click", async () => {
  if (!window.confirm("Delete the protected token and disable live light control?")) return;
  try {
    const next = await request("/settings/delete-token", "POST", {});
    ui.settingsDialog.close();
    renderStatus(next, true);
    appendMessage("system", "The protected token was deleted. Osun is back in simulation.");
  } catch (error) {
    ui.connectionResult.textContent = `Credential deletion failed: ${error.message}`;
  }
});

ui.quitButton.addEventListener("click", async () => {
  if (!window.confirm("Quit the Osun Lighting Assistant?")) return;
  try { await request("/shutdown", "POST", {}); } catch (_) { /* process may close before response */ }
  document.body.replaceChildren();
  const message = document.createElement("main");
  message.style.cssText = "display:grid;place-items:center;height:100vh;color:#edf4ff;font:18px Segoe UI;background:#07101f";
  message.textContent = "Osun Lighting Assistant has closed. You can close this window.";
  document.body.append(message);
  window.close();
});

appendMessage("osun", "I'm ready. Try “I want to feel like I'm in the ocean” or ask for a normal light change.");
refresh(true).then(() => ui.messageInput.focus());
