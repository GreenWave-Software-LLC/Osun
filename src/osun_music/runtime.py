from __future__ import annotations

import secrets
import time
from copy import deepcopy
from threading import RLock
from typing import Any, Callable

from osun_lights.credential_store import WindowsCredentialStore

from .bluetooth_audio import WindowsBluetoothHeadphoneDetector
from .config import MusicConfig, MusicConfigStore, MusicDeviceConfig, default_data_dir
from .device_router import RECENT_PLAYBACK_SECONDS, choose_playback_device
from .home_assistant_tv import HomeAssistantAppleTVAdapter
from .intent_parser import MusicIntent, MusicIntentParser
from .windows_app import WindowsAppleMusicAdapter


_DEFAULT_HEADPHONE_DETECTOR = WindowsBluetoothHeadphoneDetector()


class MusicController:
    """Deterministic music intents, live destination routing, and typed playback commands."""

    def __init__(
        self,
        config_store: MusicConfigStore | None = None,
        credential_store: WindowsCredentialStore | None = None,
        windows_adapter: WindowsAppleMusicAdapter | None = None,
        headphone_detector: WindowsBluetoothHeadphoneDetector | None = None,
        apple_tv_adapter: HomeAssistantAppleTVAdapter | None = None,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.config_store = config_store or MusicConfigStore()
        self.credential_store = credential_store or WindowsCredentialStore(
            default_data_dir() / "developer-token.bin",
            entropy=b"osun-music:apple-musickit:v1",
            description="Osun Apple Music developer token",
        )
        self.clock = clock
        self.parser = MusicIntentParser()
        self.windows_adapter = windows_adapter or WindowsAppleMusicAdapter()
        self.headphone_detector = headphone_detector or _DEFAULT_HEADPHONE_DETECTOR
        self.config = self.config_store.load()
        self.apple_tv_adapter = apple_tv_adapter or HomeAssistantAppleTVAdapter(
            selection_provider=self._media_center_selection,
        )
        self._last_played: dict[str, float] = {}
        self._requests: dict[str, dict[str, Any]] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def status(self) -> dict[str, Any]:
        with self._lock:
            now = self.clock()
            token_configured = self.credential_store.load() is not None
            pending = self._latest_request({"needs_device", "ready", "running"})
            devices = self._devices(now)
            return {
                "enabled": self.config.enabled,
                "mode": self.config.mode,
                "effective_mode": (
                    "musickit"
                    if self.config.mode == "musickit" and token_configured
                    else "simulator"
                    if self.config.mode == "musickit"
                    else self.config.mode
                ),
                "developer_token_configured": token_configured,
                "windows_app_available": self.windows_adapter.available(),
                "autonomous_execution": self.config.autonomous_execution,
                "media_center": {
                    "entity_id": self.config.media_center_entity_id,
                    "name": self._media_center_selection()[1],
                },
                "recent_window_seconds": RECENT_PLAYBACK_SECONDS,
                "devices": devices,
                "pending": deepcopy(pending),
            }

    def message(self, text: str, *, allow_bare_play: bool = False) -> dict[str, Any]:
        with self._lock:
            now = self.clock()
            devices = self._devices(now)
            pending_device_request = self._latest_request({"needs_device"})
            device_choice = self.parser.device_choice(text, devices)
            if pending_device_request and device_choice:
                device = self._device(device_choice, now)
                pending_device_request["device_id"] = device_choice
                pending_device_request["device_name"] = device["name"]
                pending_device_request["selection_reason"] = "owner_selected"
                pending_device_request["state"] = "ready"
                return {
                    "text": f"Routing {self._action_description(pending_device_request)} to {device['name']} as requested.",
                    "request": deepcopy(pending_device_request),
                }
            intent = self.parser.parse(text, devices)
            if intent is None and allow_bare_play:
                intent = self.parser.parse_bare_play(text, devices)
            if intent is None:
                return {
                    "text": "Tell me what to play, pause, resume, skip, or go back to in Apple Music.",
                    "request": None,
                }
            if intent.action == "list_devices":
                available_devices = [device for device in devices if device.get("enabled") is True]
                return {
                    "text": self._device_listing_text(available_devices),
                    "request": None,
                    "view": "devices",
                    "devices": deepcopy(available_devices),
                }
            decision = choose_playback_device(
                devices,
                now=now,
                requested_device_id=intent.requested_device_id,
                action=intent.action,
                headphones_or_tv=True,
            )
            self._supersede_pending_requests()
            request = self._new_request(intent, decision.device_id, decision.reason, now)
            self._requests[request["request_id"]] = request
            self._trim_requests()
            if request["state"] == "needs_device":
                action = self._action_description(request)
                television = next((device for device in devices if device.get("kind") == "apple_tv"), None)
                television_name = str(television.get("name")) if television else "the configured media center"
                text_reply = (
                    f"Bluetooth headphones are connected. Would you like me to {action} on Headphones "
                    f"or {television_name}?"
                    if decision.reason == "ask_headphones_or_tv"
                    else f"Which available device should I use to {action}?"
                )
            else:
                device = self._device(request["device_id"], now)
                if decision.reason == "recent_playback":
                    text_reply = (
                        f"Routing {self._action_description(request)} to {device['name']} because it was the most "
                        "recent music device."
                    )
                elif decision.reason == "headphones_unavailable_default_tv":
                    text_reply = (
                        f"Bluetooth headphones are not connected, so I’ll use {device['name']} to "
                        f"{self._action_description(request)}."
                    )
                elif decision.reason == "default_tv":
                    text_reply = f"Routing {self._action_description(request)} to {device['name']}."
                else:
                    text_reply = f"Routing {self._action_description(request)} to {device['name']} as requested."
            return {"text": text_reply, "request": deepcopy(request)}

    def can_resolve_device_follow_up(self, text: str) -> bool:
        with self._lock:
            return bool(
                self._latest_request({"needs_device"})
                and self.parser.device_choice(text, self._devices(self.clock()))
            )

    def recognizes_command(self, text: str) -> bool:
        with self._lock:
            return self.parser.parse(text, self._devices(self.clock())) is not None

    def select_device(self, request_id: str, device_id: str) -> dict[str, Any]:
        with self._lock:
            request = self._request(request_id)
            device = self._device(device_id, self.clock())
            request["device_id"] = device_id
            request["device_name"] = device["name"]
            request["selection_reason"] = "owner_selected"
            request["state"] = "ready"
            return deepcopy(request)

    def execute(self, request_id: str) -> dict[str, Any]:
        with self._lock:
            if request_id in self._results:
                return deepcopy(self._results[request_id])
            request = self._request(request_id)
            if request["state"] == "needs_device" or not request.get("device_id"):
                raise ValueError("Choose a music playback device first")
            device = self._device(str(request["device_id"]), self.clock())
            if not self.config.enabled:
                raise ValueError("The Music agent is disabled in Settings")
            if request["state"] == "running":
                raise ValueError("This music request is already running")
            if self.config.mode == "simulator":
                now = self.clock()
                if request["action"] != "pause":
                    self._last_played[str(device["device_id"])] = now
                request["state"] = "playing" if request["action"] in {"play", "resume"} else "complete"
                result = {
                    "state": "simulated",
                    "request_id": request_id,
                    "device_id": device["device_id"],
                    "device_name": device["name"],
                    "summary": f"Simulated {self._action_description(request)} on {device['name']}.",
                    "request": deepcopy(request),
                }
                self._results[request_id] = result
                return deepcopy(result)
            if self.config.mode == "windows_app":
                if device["kind"] in {"windows_app", "windows_headphones"}:
                    playback_adapter = self.windows_adapter
                elif device["kind"] == "apple_tv":
                    playback_adapter = self.apple_tv_adapter
                else:
                    raise ValueError("This music device does not have an installed playback adapter")
                request["state"] = "running"
                action = str(request["action"])
                query = str(request.get("query") or "")
            else:
                playback_adapter = None
                action = ""
                query = ""
        if action:
            if playback_adapter is None:
                raise ValueError("This music destination does not have an installed playback adapter")
            outcome = playback_adapter.execute(action, query)
            return self.playback_result(
                request_id,
                str(device["device_id"]),
                success=outcome.success,
                verified=outcome.verified,
                playback_active=outcome.playback_active,
                now_playing=outcome.now_playing,
                evidence=outcome.evidence,
                error=outcome.error,
            )
        with self._lock:
            request = self._request(request_id)
            device = self._device(str(request["device_id"]), self.clock())
            if self.credential_store.load() is None:
                raise ValueError("Connect Apple Music in Settings before playback")
            if device["kind"] not in {"browser", "windows_app", "windows_headphones"}:
                raise ValueError("This music device does not have an installed playback adapter")
            request["state"] = "running"
            return {
                "state": "client_required",
                "request_id": request_id,
                "device_id": device["device_id"],
                "device_name": device["name"],
                "command": {
                    "action": request["action"],
                    "query": request.get("query"),
                },
                "request": deepcopy(request),
            }

    def client_config(self) -> dict[str, str]:
        with self._lock:
            if not self.config.enabled:
                raise ValueError("The Music agent is disabled in Settings")
            if self.config.mode != "musickit":
                raise ValueError("Apple Music playback is not enabled")
            token = self.credential_store.load()
            if token is None:
                raise ValueError("An Apple Music developer token has not been saved")
            return {
                "developer_token": token,
                "script_url": "https://js-cdn.music.apple.com/musickit/v3/musickit.js",
            }

    def playback_result(
        self,
        request_id: str,
        device_id: str,
        *,
        success: bool,
        verified: bool = True,
        playback_active: bool | None = None,
        now_playing: str = "",
        evidence: str = "",
        error: str = "",
    ) -> dict[str, Any]:
        with self._lock:
            if request_id in self._results:
                return deepcopy(self._results[request_id])
            request = self._request(request_id)
            if request.get("device_id") != device_id:
                raise ValueError("Music playback result came from the wrong device")
            device = self._device(device_id, self.clock())
            safe_title = " ".join(now_playing.split())[:200]
            safe_error = " ".join(error.split())[:240]
            safe_evidence = " ".join(evidence.split())[:80]
            if success:
                if request["action"] != "pause" and (verified or playback_active is True):
                    self._last_played[device_id] = self.clock()
                request["state"] = "playing" if request["action"] in {"play", "resume"} else "complete"
                summary = (
                    f"Playing {safe_title} on {device['name']}."
                    if safe_title and request["action"] == "play"
                    else f"Completed {self._action_description(request)} on {device['name']}."
                    if verified
                    else f"Sent {self._action_description(request)} to Apple Music on {device['name']}; playback read-back was unavailable."
                )
                state = "verified" if verified else "completed"
            else:
                request["state"] = "failed"
                summary = safe_error or "Apple Music could not complete the playback command."
                state = "failed"
            result = {
                "state": state,
                "request_id": request_id,
                "device_id": device_id,
                "device_name": device["name"],
                "summary": summary,
                "now_playing": safe_title,
                "verified": verified if success else False,
                "evidence": safe_evidence,
                "request": deepcopy(request),
            }
            self._results[request_id] = result
            return deepcopy(result)

    def test_windows_app(self) -> dict[str, Any]:
        result = self.windows_adapter.probe()
        headphones = self.headphone_detector.status()
        apple_tv_probe_method = getattr(self.apple_tv_adapter, "probe", None)
        apple_tv_probe = (
            apple_tv_probe_method()
            if callable(apple_tv_probe_method)
            else {"success": self.apple_tv_adapter.available(), "error": ""}
        )
        raw_headphone_names = headphones.get("names")
        headphone_names = raw_headphone_names if isinstance(raw_headphone_names, list) else []
        return {
            "success": result.get("success") is True,
            "installed": result.get("installed") is True,
            "running": result.get("running") is True,
            "session_available": result.get("session_available") is True,
            "automation_available": result.get("automation_available") is True,
            "playback_active": (
                result.get("playback_active") if isinstance(result.get("playback_active"), bool) else None
            ),
            "now_playing": " ".join(str(result.get("now_playing", "")).split())[:200],
            "evidence": " ".join(str(result.get("evidence", "")).split())[:80],
            "error": " ".join(str(result.get("error", "")).split())[:240],
            "bluetooth_headphones_connected": headphones.get("connected") is True,
            "headphone_names": [" ".join(str(name).split())[:80] for name in headphone_names[:8]],
            "apple_tv_available": apple_tv_probe.get("success") is True,
            "apple_tv_entity_id": " ".join(str(apple_tv_probe.get("entity_id", "")).split())[:80],
            "apple_tv_name": " ".join(str(apple_tv_probe.get("friendly_name", "")).split())[:80],
            "apple_tv_error": " ".join(str(apple_tv_probe.get("error", "")).split())[:240],
        }

    def discover_media_centers(self) -> dict[str, Any]:
        discovery = getattr(self.apple_tv_adapter, "discover_media_centers", None)
        if not callable(discovery):
            raise ValueError("The installed media-center adapter does not support discovery")
        media_centers = discovery()
        if not isinstance(media_centers, list):
            raise ValueError("Home Assistant returned an invalid media-center list")
        return {
            "media_centers": deepcopy(media_centers[:100]),
            "selected_entity_id": self.config.media_center_entity_id,
        }

    def save_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            mode = str(payload.get("mode", self.config.mode)).strip()
            enabled_raw = payload.get("enabled", self.config.enabled)
            autonomous_raw = payload.get("autonomous_execution", self.config.autonomous_execution)
            if not isinstance(enabled_raw, bool) or not isinstance(autonomous_raw, bool):
                raise ValueError("Music policy switches must be true or false")
            enabled = enabled_raw
            autonomous = autonomous_raw
            token = str(payload.get("developer_token", "")).strip()
            entity_raw = payload.get("media_center_entity_id", self.config.media_center_entity_id)
            name_raw = payload.get("media_center_name", self._media_center_selection()[1])
            if not isinstance(entity_raw, str) or not isinstance(name_raw, str):
                raise ValueError("Media-center selection must use text values")
            media_center_entity_id = entity_raw.strip()
            media_center_name = " ".join(name_raw.split())
            if not media_center_name or len(media_center_name) > 80:
                raise ValueError("Media center requires a short display name")
            devices = [
                MusicDeviceConfig(
                    device_id=device.device_id,
                    name=media_center_name if device.kind == "apple_tv" else device.name,
                    kind=device.kind,
                    enabled=device.enabled,
                )
                for device in self.config.devices
            ]
            config = MusicConfig(
                mode=mode,
                enabled=enabled,
                autonomous_execution=autonomous,
                media_center_entity_id=media_center_entity_id,
                devices=devices,
            )
            config.validate()
            if token:
                if len(token) > 8_192 or token.count(".") != 2:
                    raise ValueError("Apple Music developer token must be a signed JWT")
                self.credential_store.save(token)
            self.config_store.save(config)
            self.config = config
            return self.status()

    def delete_credential(self) -> dict[str, Any]:
        with self._lock:
            self.credential_store.delete()
            if self.config.mode == "musickit":
                self.config.mode = "windows_app" if self.windows_adapter.available() else "simulator"
            self.config_store.save(self.config)
            return self.status()

    def cancel(self) -> dict[str, bool]:
        with self._lock:
            self._requests.clear()
            self._results.clear()
            return {"cleared": True}

    def _new_request(
        self,
        intent: MusicIntent,
        device_id: str | None,
        reason: str,
        now: float,
    ) -> dict[str, Any]:
        device_name = self._device(device_id, now)["name"] if device_id else None
        return {
            "request_id": secrets.token_urlsafe(12),
            "action": intent.action,
            "query": intent.query,
            "state": "ready" if device_id else "needs_device",
            "device_id": device_id,
            "device_name": device_name,
            "selection_reason": reason,
            "created_at": now,
        }

    def _devices(self, now: float) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        headphone_status = self.headphone_detector.status()
        headphones_connected = headphone_status.get("connected") is True
        raw_headphone_names = headphone_status.get("names")
        headphone_names = (
            [" ".join(str(name).split())[:80] for name in raw_headphone_names[:8]]
            if isinstance(raw_headphone_names, list)
            else []
        )
        apple_tv_available = self.apple_tv_adapter.available()
        for configured in self.config.devices:
            last_played = self._last_played.get(configured.device_id)
            seconds_ago = round(now - last_played) if last_played is not None else None
            connected = None
            enabled = configured.enabled
            detail = ""
            if configured.kind == "windows_headphones":
                connected = headphones_connected
                adapter_available = self.config.mode != "windows_app" or self.windows_adapter.available()
                enabled = enabled and headphones_connected and adapter_available
                detail = headphone_names[0] if headphone_names else "Bluetooth audio"
            elif configured.kind == "apple_tv":
                connected = apple_tv_available
                enabled = enabled and apple_tv_available
                detail = "Home Assistant Apple TV"
            rows.append(
                {
                    "device_id": configured.device_id,
                    "name": configured.name,
                    "kind": configured.kind,
                    "enabled": enabled,
                    "connected": connected,
                    "detail": detail,
                    "last_played_at": last_played,
                    "seconds_since_playback": seconds_ago,
                    "recent": seconds_ago is not None and 0 <= seconds_ago <= RECENT_PLAYBACK_SECONDS,
                }
            )
        return rows

    def _media_center_selection(self) -> tuple[str, str]:
        configured = next((device for device in self.config.devices if device.kind == "apple_tv"), None)
        return (
            self.config.media_center_entity_id,
            configured.name if configured else "Living Room Apple TV",
        )

    def _device(self, device_id: str | None, now: float) -> dict[str, Any]:
        for device in self._devices(now):
            if device["device_id"] == device_id and device["enabled"]:
                return device
        raise ValueError("The selected music device is unavailable")

    def _request(self, request_id: str) -> dict[str, Any]:
        request = self._requests.get(request_id)
        if request is None:
            raise ValueError("The music request is missing or expired")
        return request

    @staticmethod
    def _action_description(request: dict[str, Any]) -> str:
        action = str(request["action"])
        if action == "play":
            return f"play {request.get('query') or 'music'}"
        return {"pause": "pause music", "resume": "resume music", "next": "skip to the next song", "previous": "go to the previous song"}.get(action, action)

    @staticmethod
    def _device_listing_text(devices: list[dict[str, Any]]) -> str:
        if not devices:
            return "No enabled music playback devices are currently registered. Open Music settings to add or enable one."
        details: list[str] = []
        for device in devices:
            kind = str(device.get("kind", ""))
            adapter = {
                "windows_app": "Windows Apple Music app",
                "windows_headphones": "Bluetooth headphones through the Windows Apple Music app",
                "apple_tv": "Apple Music on Living Room Apple TV",
                "browser": "Apple Music in this Osun window",
                "companion": "registered companion",
            }.get(kind, "registered playback device")
            recent = "; recently active" if device.get("recent") is True else ""
            details.append(f"{device.get('name', 'Unnamed device')} ({adapter}{recent})")
        count = len(details)
        noun = "device" if count == 1 else "devices"
        return f"Osun currently has {count} available playback {noun}: {', '.join(details)}."

    def _trim_requests(self) -> None:
        while len(self._requests) > 20:
            oldest = next(iter(self._requests))
            self._requests.pop(oldest, None)
            self._results.pop(oldest, None)

    def _latest_request(self, states: set[str]) -> dict[str, Any] | None:
        return next(
            (
                request
                for request in reversed(self._requests.values())
                if request.get("state") in states
            ),
            None,
        )

    def _supersede_pending_requests(self) -> None:
        for request in self._requests.values():
            if request.get("state") in {"needs_device", "ready"}:
                request["state"] = "superseded"
