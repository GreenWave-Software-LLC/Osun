from __future__ import annotations

import secrets
import time
from copy import deepcopy
from threading import RLock
from typing import Any, Callable

from osun_lights.credential_store import WindowsCredentialStore

from .config import MusicConfig, MusicConfigStore, default_data_dir
from .device_router import RECENT_PLAYBACK_SECONDS, choose_playback_device
from .intent_parser import MusicIntent, MusicIntentParser
from .windows_app import WindowsAppleMusicAdapter


class MusicController:
    """Deterministic music intents, five-minute device routing, and typed playback commands."""

    def __init__(
        self,
        config_store: MusicConfigStore | None = None,
        credential_store: WindowsCredentialStore | None = None,
        windows_adapter: WindowsAppleMusicAdapter | None = None,
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
        self.config = self.config_store.load()
        self._last_played: dict[str, float] = {}
        self._requests: dict[str, dict[str, Any]] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def status(self) -> dict[str, Any]:
        with self._lock:
            now = self.clock()
            token_configured = self.credential_store.load() is not None
            pending = self._latest_request({"needs_device", "ready", "running"})
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
                "recent_window_seconds": RECENT_PLAYBACK_SECONDS,
                "devices": self._devices(now),
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
            )
            self._supersede_pending_requests()
            request = self._new_request(intent, decision.device_id, decision.reason, now)
            self._requests[request["request_id"]] = request
            self._trim_requests()
            if request["state"] == "needs_device":
                action = self._action_description(request)
                text_reply = (
                    f"Which device should I use to {action}? Nothing has played music on a registered device "
                    "during the last five minutes."
                )
            else:
                device = self._device(request["device_id"], now)
                text_reply = (
                    f"Routing {self._action_description(request)} to {device['name']} because it was the most "
                    "recent music device."
                    if decision.reason == "recent_playback"
                    else f"Routing {self._action_description(request)} to {device['name']} as requested."
                )
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
                if device["kind"] != "windows_app":
                    raise ValueError("This music device does not have the Windows Apple Music adapter")
                request["state"] = "running"
                action = str(request["action"])
                query = str(request.get("query") or "")
            else:
                action = ""
                query = ""
        if action:
            outcome = self.windows_adapter.execute(action, query)
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
            if device["kind"] not in {"browser", "windows_app"}:
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
                    else f"Sent {self._action_description(request)} to Apple Music on {device['name']}; Windows did not expose media read-back."
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
            config = MusicConfig(
                mode=mode,
                enabled=enabled,
                autonomous_execution=autonomous,
                devices=self.config.devices,
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
        for configured in self.config.devices:
            last_played = self._last_played.get(configured.device_id)
            seconds_ago = round(now - last_played) if last_played is not None else None
            rows.append(
                {
                    "device_id": configured.device_id,
                    "name": configured.name,
                    "kind": configured.kind,
                    "enabled": configured.enabled,
                    "last_played_at": last_played,
                    "seconds_since_playback": seconds_ago,
                    "recent": seconds_ago is not None and 0 <= seconds_ago <= RECENT_PLAYBACK_SECONDS,
                }
            )
        return rows

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
