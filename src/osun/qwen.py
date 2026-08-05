from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from http.client import HTTPResponse
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener


class QwenError(RuntimeError):
    """A content-minimized local model error safe to show in the UI."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args: Any, **_kwargs: Any) -> None:
        return None


@dataclass(frozen=True, slots=True)
class QwenReply:
    content: str
    tool_names: tuple[str, ...]
    prompt_tokens: int = 0
    output_tokens: int = 0
    total_duration_ms: int = 0


LIGHTING_TOOL = {
    "type": "function",
    "function": {
        "name": "open_lighting_widget",
        "description": (
            "Open a review-only lighting widget when the user wants lights changed, wants a lighting theme, "
            "or describes an atmosphere they want the room lighting to create. This tool never executes lights."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
}

MUSIC_TOOL = {
    "type": "function",
    "function": {
        "name": "open_music_widget",
        "description": (
            "Open the Apple Music agent when the owner asks to play, pause, resume, skip, or go back to music. "
            "The typed music agent, not the model, chooses an authorized playback device and command."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
}


SYSTEM_PROMPT = """You are Osun, a warm, concise, local-first personal assistant for one owner.
Use open_lighting_widget when the owner asks to change, control, suggest, or create an atmosphere with room lighting. Do not use it for general informational discussion about colors, oceans, or lighting.
The lighting tool creates a visible proposal only. It never executes a device change. Never say a device changed unless a later verified result is supplied to you.
Use open_music_widget when the owner asks to play, pause, resume, skip, or go back to music or Apple Music. Do not use it for general discussion about musicians, albums, or music theory.
The music tool accepts no model-authored destination or playback parameters. Osun reparses the original owner request and applies its typed Headphones/Apple TV destination policy.
For requests that do not need an available tool, answer directly. Be useful and natural. Do not invent access to calendars, email, files, memories, sensors, the internet, or other agents."""


class OllamaQwenClient:
    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:9b",
        *,
        timeout: float = 180.0,
    ) -> None:
        parsed = urlparse(endpoint.strip())
        if parsed.scheme != "http" or not parsed.hostname or parsed.hostname.casefold() not in {
            "127.0.0.1",
            "localhost",
            "::1",
        }:
            raise ValueError("The Agent Box model endpoint must be local loopback HTTP")
        if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
            raise ValueError("The Agent Box endpoint cannot contain credentials, a path, query, or fragment")
        if not model.strip() or len(model) > 120:
            raise ValueError("A valid local Qwen model name is required")
        self.endpoint = f"http://{parsed.netloc}"
        self.model = model.strip()
        self.timeout = timeout
        self._opener = build_opener(
            ProxyHandler({}),
            _NoRedirect(),
            HTTPSHandler(context=ssl.create_default_context()),
        )

    def status(self) -> dict[str, Any]:
        try:
            payload = self._request("GET", "/api/tags", timeout=3.0)
            models = payload.get("models", []) if isinstance(payload, dict) else []
            names = sorted(
                item.get("name", "")
                for item in models
                if isinstance(item, dict) and isinstance(item.get("name"), str)
            )
            running = self._request("GET", "/api/ps", timeout=3.0)
            loaded_models = running.get("models", []) if isinstance(running, dict) else []
            loaded_names = {
                str(item.get("name") or item.get("model") or "")
                for item in loaded_models
                if isinstance(item, dict)
            }
            return {
                "online": True,
                "model": self.model,
                "model_available": self.model in names,
                "loaded": self.model in loaded_names,
                "available_models": names,
                "endpoint": self.endpoint,
                "provider": "Ollama",
            }
        except QwenError as exc:
            return {
                "online": False,
                "model": self.model,
                "model_available": False,
                "loaded": False,
                "available_models": [],
                "endpoint": self.endpoint,
                "provider": "Ollama",
                "error": str(exc),
            }

    def chat(self, user_text: str, history: tuple[dict[str, str], ...] = ()) -> QwenReply:
        if not user_text.strip():
            raise ValueError("Message cannot be empty")
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for item in history[-12:]:
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and isinstance(content, str) and content:
                messages.append({"role": role, "content": content[:4_000]})
        messages.append({"role": "user", "content": user_text[:2_000]})
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": [LIGHTING_TOOL, MUSIC_TOOL],
            "stream": False,
            "think": False,
            "keep_alive": "30m",
            "options": {"temperature": 0.2, "num_ctx": 4096},
        }
        response = self._request("POST", "/api/chat", payload)
        if not isinstance(response, dict) or not isinstance(response.get("message"), dict):
            raise QwenError("The local Qwen model returned an invalid response")
        message = response["message"]
        content = message.get("content", "")
        if not isinstance(content, str):
            raise QwenError("The local Qwen model returned invalid message content")
        names: list[str] = []
        calls = message.get("tool_calls", [])
        if calls is None:
            calls = []
        if not isinstance(calls, list):
            raise QwenError("The local Qwen model returned invalid tool calls")
        for call in calls:
            function = call.get("function") if isinstance(call, dict) else None
            name = function.get("name") if isinstance(function, dict) else None
            if name in {"open_lighting_widget", "open_music_widget"}:
                names.append(name)
        return QwenReply(
            content=content.strip()[:12_000],
            tool_names=tuple(names),
            prompt_tokens=int(response.get("prompt_eval_count") or 0),
            output_tokens=int(response.get("eval_count") or 0),
            total_duration_ms=round(int(response.get("total_duration") or 0) / 1_000_000),
        )

    def preload(self) -> None:
        self._request(
            "POST",
            "/api/generate",
            {"model": self.model, "stream": False, "keep_alive": "30m"},
        )

    def unload(self) -> None:
        self._request(
            "POST",
            "/api/generate",
            {"model": self.model, "stream": False, "keep_alive": 0},
            timeout=15.0,
        )

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.endpoint}{path}",
            data=body,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Osun/0.2",
            },
        )
        try:
            response: HTTPResponse
            with self._opener.open(request, timeout=timeout or self.timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            raise QwenError(f"The local Qwen service returned HTTP {exc.code}") from None
        except (URLError, TimeoutError, OSError):
            raise QwenError("The local Qwen service is unavailable or still waking up") from None
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise QwenError("The local Qwen service returned invalid JSON") from None
