from __future__ import annotations

from threading import RLock, Thread
from typing import Any

from osun_lights.runtime import LightingController
from osun_music.runtime import MusicController

from .qwen import OllamaQwenClient, QwenError


LIGHTING_HINTS = (
    "light",
    "lights",
    "lamp",
    "lamps",
    "brightness",
    "dim the room",
    "room glow",
    "lighting theme",
)
ATMOSPHERE_HINTS = (
    "feel like i am in the ocean",
    "feel like i'm in the ocean",
    "make the room feel",
    "make it cozy",
    "make it romantic",
    "give me a focus theme",
)
MUSIC_HINTS = (
    "play music",
    "play apple music",
    "put on ",
    "listen to ",
    "pause the music",
    "pause music",
    "resume the music",
    "resume music",
    "continue the music",
    "next song",
    "next track",
    "skip song",
    "skip track",
    "previous song",
    "previous track",
)


def _fallback_lighting_route(text: str) -> bool:
    normalized = " ".join(text.casefold().split())
    return any(hint in normalized for hint in LIGHTING_HINTS + ATMOSPHERE_HINTS)


def _fallback_music_route(text: str) -> bool:
    normalized = " ".join(text.casefold().split())
    return (
        normalized == "play"
        or normalized.startswith(("play ", "put on ", "listen to "))
        or any(hint in normalized for hint in MUSIC_HINTS)
    )


class OsunController:
    def __init__(
        self,
        lighting: LightingController | None = None,
        qwen: OllamaQwenClient | None = None,
        music: MusicController | None = None,
    ) -> None:
        self.lighting = lighting or LightingController()
        self.music = music or MusicController()
        self.qwen = qwen or OllamaQwenClient()
        self._history: list[dict[str, str]] = []
        self._lock = RLock()
        self._last_model_error: str | None = None
        self._warming = False
        if hasattr(self.qwen, "preload"):
            self._warming = True
            Thread(target=self._preload_model, name="osun-qwen-preload", daemon=True).start()

    def status(self) -> dict[str, Any]:
        with self._lock:
            box_status = self.qwen.status()
            box_status["warming"] = self._warming
            return {
                "app": {"name": "Osun", "version": "0.5.0", "surface": "main_chat"},
                "agent_box": box_status,
                "agents": [
                    {
                        "id": "osun",
                        "name": "Osun",
                        "state": "active",
                        "description": "Local Qwen conversation and agent routing",
                    },
                    {
                        "id": "lighting",
                        "name": "Lighting",
                        "state": "available",
                        "description": "Themes and allowlisted Home Assistant lights",
                    },
                    {
                        "id": "music",
                        "name": "Music",
                        "state": "available",
                        "description": "Apple Music playback with Bluetooth Headphones and Apple TV routing",
                    },
                ],
                "lighting": self.lighting.status(),
                "music": self.music.status(),
                "last_model_error": self._last_model_error,
                "privacy": {"chat_persisted": False, "model_endpoint": "loopback_only"},
            }

    def message(self, text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        text = text.strip()
        if not text:
            raise ValueError("Message cannot be empty")
        if len(text) > 2_000:
            raise ValueError("Messages are limited to 2,000 characters")
        context = context or {}
        selected_raw = context.get("lighting_selected_entities", [])
        if not isinstance(selected_raw, list) or not all(isinstance(item, str) for item in selected_raw):
            raise ValueError("Lighting selection must be a list of entity IDs")
        selected = tuple(selected_raw)

        with self._lock:
            qwen_content = ""
            tool_names: tuple[str, ...] = ()
            metrics: dict[str, int] | None = None
            music_device_follow_up = self.music.can_resolve_device_follow_up(text)
            explicit_music_request = self.music.recognizes_command(text)
            if not music_device_follow_up and not explicit_music_request:
                try:
                    reply = self.qwen.chat(text, tuple(self._history))
                    qwen_content = reply.content
                    tool_names = reply.tool_names
                    metrics = {
                        "prompt_tokens": reply.prompt_tokens,
                        "output_tokens": reply.output_tokens,
                        "duration_ms": reply.total_duration_ms,
                    }
                    self._last_model_error = None
                except QwenError as exc:
                    self._last_model_error = str(exc)

            lighting_requested = "open_lighting_widget" in tool_names or (
                not qwen_content and _fallback_lighting_route(text)
            )
            music_requested = (
                music_device_follow_up
                or explicit_music_request
                or "open_music_widget" in tool_names
                or (not qwen_content and _fallback_music_route(text))
            )
            if lighting_requested:
                lighting_reply = self.lighting.message(text, selected)
                visible_text = lighting_reply["text"]
                result = {
                    "text": visible_text,
                    "agent": "lighting",
                    "widgets": [
                        self._lighting_widget(
                            lighting_reply.get("proposal"),
                            lighting_reply.get("execution"),
                        )
                    ],
                    "execution": lighting_reply.get("execution"),
                    "model": {"used": bool(tool_names), "metrics": metrics},
                }
            elif music_requested:
                music_reply = self.music.message(
                    text,
                    allow_bare_play="open_music_widget" in tool_names,
                )
                visible_text = music_reply["text"]
                result = {
                    "text": visible_text,
                    "agent": "music",
                    "widgets": [
                        self._music_widget(
                            music_reply.get("request"),
                            view=str(music_reply.get("view") or "request"),
                        )
                    ],
                    "execution": None,
                    "model": {"used": bool(tool_names), "metrics": metrics},
                }
            elif qwen_content:
                visible_text = qwen_content
                result = {
                    "text": visible_text,
                    "agent": "osun",
                    "widgets": [],
                    "model": {"used": True, "metrics": metrics},
                }
            else:
                visible_text = (
                    "My local Qwen model is unavailable right now. Lighting controls still work—mention a light, lamp, "
                    "brightness, or lighting theme—or open Settings to check the Agent Box."
                )
                result = {
                    "text": visible_text,
                    "agent": "osun",
                    "widgets": [],
                    "model": {"used": False, "error": self._last_model_error},
                }

            self._history.extend(
                [
                    {"role": "user", "content": text},
                    {"role": "assistant", "content": visible_text},
                ]
            )
            self._history = self._history[-12:]
            return result

    def new_chat(self) -> dict[str, bool]:
        with self._lock:
            self._history.clear()
            self.lighting.cancel()
            self.music.cancel()
            return {"cleared": True}

    def shutdown(self) -> None:
        if hasattr(self.qwen, "unload"):
            try:
                self.qwen.unload()
            except QwenError:
                pass

    def lighting_apply(self, proposal_id: str) -> dict[str, Any]:
        return self.lighting.apply(proposal_id)

    def lighting_cancel(self) -> dict[str, bool]:
        return self.lighting.cancel()

    def lighting_pause(self) -> dict[str, Any]:
        return self.lighting.pause()

    def lighting_test(self, url: str, token: str) -> dict[str, Any]:
        return self.lighting.test_connection(url, token)

    def lighting_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.lighting.save_settings(payload)

    def lighting_delete_credential(self) -> dict[str, Any]:
        return self.lighting.delete_credential()

    def music_select_device(self, request_id: str, device_id: str) -> dict[str, Any]:
        request = self.music.select_device(request_id, device_id)
        return self._music_widget(request)

    def music_execute(self, request_id: str) -> dict[str, Any]:
        return self.music.execute(request_id)

    def music_client_config(self) -> dict[str, str]:
        return self.music.client_config()

    def music_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        success = payload.get("success", False)
        if not isinstance(success, bool):
            raise ValueError("Music playback success must be true or false")
        return self.music.playback_result(
            str(payload.get("request_id", "")),
            str(payload.get("device_id", "")),
            success=success,
            now_playing=str(payload.get("now_playing", "")),
            error=str(payload.get("error", "")),
        )

    def music_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.music.save_settings(payload)

    def music_test_windows_app(self) -> dict[str, Any]:
        return self.music.test_windows_app()

    def music_delete_credential(self) -> dict[str, Any]:
        return self.music.delete_credential()

    def _lighting_widget(
        self,
        proposal: dict[str, Any] | None,
        execution: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        status = self.lighting.status()
        return {
            "id": "lighting",
            "kind": "lighting",
            "title": "Lighting",
            "agent": "lighting",
            "proposal": proposal or status.get("pending"),
            "mode": status.get("effective_mode"),
            "paused": status.get("paused"),
            "live_enabled": status.get("live_enabled"),
            "autonomous_execution": status.get("autonomous_execution"),
            "execution_policy": {
                "autonomous": bool(status.get("autonomous_execution")),
                "paused": bool(status.get("paused")),
            },
            "execution": execution,
            "lights": status.get("lights", []),
            "warning": status.get("warning"),
        }

    def _music_widget(
        self,
        request: dict[str, Any] | None,
        execution: dict[str, Any] | None = None,
        *,
        view: str = "request",
    ) -> dict[str, Any]:
        status = self.music.status()
        safe_view = "devices" if view == "devices" else "request"
        return {
            "id": "music",
            "kind": "music",
            "title": "Music",
            "agent": "music",
            "view": safe_view,
            "request": None if safe_view == "devices" else request or status.get("pending"),
            "mode": status.get("effective_mode"),
            "developer_token_configured": status.get("developer_token_configured"),
            "windows_app_available": status.get("windows_app_available"),
            "autonomous_execution": status.get("autonomous_execution"),
            "recent_window_seconds": status.get("recent_window_seconds"),
            "devices": status.get("devices", []),
            "execution": execution,
        }

    def _preload_model(self) -> None:
        try:
            self.qwen.preload()
            with self._lock:
                self._last_model_error = None
        except QwenError as exc:
            with self._lock:
                self._last_model_error = str(exc)
        finally:
            with self._lock:
                self._warming = False
