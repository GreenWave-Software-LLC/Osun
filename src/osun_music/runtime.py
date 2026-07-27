from __future__ import annotations

import secrets
import time
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Callable

from osun_lights.credential_store import WindowsCredentialStore

from .config import MusicConfig, MusicConfigStore, default_data_dir
from .device_router import RECENT_PLAYBACK_SECONDS, choose_playback_device
from .intent_parser import MusicIntent, MusicIntentParser


class MusicController:
    """Deterministic music intents, five-minute device routing, and typed playback commands."""

    def __init__(
        self,
        config_store: MusicConfigStore | None = None,
        credential_store: WindowsCredentialStore | None = None,
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
        self.config = self.config_store.load()
        self._last_played: dict[str, float] = {}
        self._requests: dict[str, dict[str, Any]] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def status(self) -> dict[str, Any]:
        with self._lock:
            now = self.clock()
            token_configured = self.credential_store.load() is not None
            pending = next(
                (
                    request
                    for request in reversed(self._requests.values())
                    if request.get("state") in {"needs_device", "ready", "running"}
                ),
                None,
            )
            return {
                "enabled": self.config.enabled,
                "mode": self.config.mode,
                "effective_mode": (
                    "musickit" if self.config.mode == "musickit" and token_configured else "simulator"
                ),
                "developer_token_configured": token_configured,
                "autonomous_execution": self.config.autonomous_execution,
                "recent_window_seconds": RECENT_PLAYBACK_SECONDS,
                "devices": self._devices(now),
                "pending": deepcopy(pending),
            }

    def message(self, text: str) -> dict[str, Any]:
        with self._lock:
            now = self.clock()
            devices = self._devices(now)
            intent = self.parser.parse(text, devices)
            if intent is None:
                return {
                    "text": "Tell me what to play, pause, resume, skip, or go back to in Apple Music.",
                    "request": None,
                }
            decision = choose_playback_device(
                devices,
                now=now,
                requested_device_id=intent.requested_device_id,
            )
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
            if self.credential_store.load() is None:
                raise ValueError("Connect Apple Music in Settings before playback")
            if device["kind"] != "browser":
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
        now_playing: str = "",
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
            if success:
                if request["action"] != "pause":
                    self._last_played[device_id] = self.clock()
                request["state"] = "playing" if request["action"] in {"play", "resume"} else "complete"
                summary = (
                    f"Playing {safe_title} on {device['name']}."
                    if safe_title and request["action"] == "play"
                    else f"Completed {self._action_description(request)} on {device['name']}."
                )
                state = "verified"
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
                "request": deepcopy(request),
            }
            self._results[request_id] = result
            return deepcopy(result)

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
            self.config.mode = "simulator"
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

    def _trim_requests(self) -> None:
        while len(self._requests) > 20:
            oldest = next(iter(self._requests))
            self._requests.pop(oldest, None)
            self._results.pop(oldest, None)
