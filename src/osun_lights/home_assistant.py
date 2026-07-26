from __future__ import annotations

import json
import ipaddress
import ssl
import time
from collections.abc import Callable
from http.client import HTTPResponse
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

from .models import (
    ExecutionItem,
    ExecutionReport,
    LightAction,
    LightInfo,
    LightingProposal,
    ResultState,
)


class HomeAssistantError(RuntimeError):
    """A content-minimized Home Assistant adapter error."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args: Any, **_kwargs: Any) -> None:
        return None


def _is_local_host(hostname: str) -> bool:
    try:
        address = ipaddress.ip_address(hostname)
        return address.is_private or address.is_loopback or address.is_link_local
    except ValueError:
        normalized = hostname.rstrip(".").casefold()
        return (
            normalized == "localhost"
            or "." not in normalized
            or normalized.endswith((".local", ".lan", ".home", ".internal", ".localdomain"))
        )


class HomeAssistantClient:
    mode = "home_assistant"

    def __init__(
        self,
        base_url: str,
        token: str,
        allowed_entities: set[str] | frozenset[str],
        *,
        timeout: float = 6.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        parsed = urlparse(base_url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Home Assistant URL must be an http:// or https:// address")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Home Assistant URL cannot contain credentials, query, or fragment")
        if parsed.path not in {"", "/"}:
            raise ValueError("Prototype Home Assistant URL must not contain a path")
        if not parsed.hostname or not _is_local_host(parsed.hostname):
            raise ValueError("Prototype Home Assistant URL must resolve through a local hostname or private IP address")
        if not token.strip():
            raise ValueError("A Home Assistant access token is required")
        if any(not entity.startswith("light.") for entity in allowed_entities):
            raise ValueError("The Home Assistant allowlist may contain only light.* entities")
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self._token = token.strip()
        self.allowed_entities = frozenset(allowed_entities)
        self.timeout = timeout
        self._sleep = sleep
        self._opener = build_opener(
            ProxyHandler({}),
            _NoRedirect(),
            HTTPSHandler(context=ssl.create_default_context()),
        )

    def check(self) -> bool:
        payload = self._request("GET", "/api/")
        return isinstance(payload, dict) and payload.get("message") == "API running."

    def discover_lights(self) -> tuple[LightInfo, ...]:
        states = self._request("GET", "/api/states")
        if not isinstance(states, list):
            raise HomeAssistantError("Home Assistant returned an invalid state list")
        lights: list[LightInfo] = []
        for item in states:
            if not isinstance(item, dict):
                continue
            entity_id = item.get("entity_id")
            if not isinstance(entity_id, str) or not entity_id.startswith("light."):
                continue
            attributes = item.get("attributes") if isinstance(item.get("attributes"), dict) else {}
            modes = attributes.get("supported_color_modes")
            if not isinstance(modes, list) or not all(isinstance(mode, str) for mode in modes):
                modes = ["brightness"] if attributes.get("brightness") is not None else ["onoff"]
            rgb = attributes.get("rgb_color")
            rgb_value = None
            if isinstance(rgb, list) and len(rgb) >= 3 and all(isinstance(value, (int, float)) for value in rgb[:3]):
                rgb_value = tuple(int(value) for value in rgb[:3])
            lights.append(
                LightInfo(
                    entity_id=entity_id,
                    friendly_name=str(attributes.get("friendly_name") or entity_id.removeprefix("light.").replace("_", " ").title()),
                    state=str(item.get("state") or "unknown"),
                    supported_color_modes=tuple(modes),
                    brightness=attributes.get("brightness") if isinstance(attributes.get("brightness"), int) else None,
                    rgb_color=rgb_value,
                )
            )
        return tuple(sorted(lights, key=lambda light: (light.friendly_name.casefold(), light.entity_id)))

    def list_lights(self) -> tuple[LightInfo, ...]:
        return tuple(light for light in self.discover_lights() if light.entity_id in self.allowed_entities)

    def apply(self, proposal: LightingProposal) -> ExecutionReport:
        items: list[ExecutionItem] = []
        for change in proposal.changes:
            if change.entity_id not in self.allowed_entities or not change.entity_id.startswith("light."):
                items.append(ExecutionItem(change.entity_id, ResultState.DENIED, "Entity is not in the live light allowlist"))
                continue
            try:
                before = self._get_state(change.entity_id) if change.action == LightAction.TOGGLE else None
                service, payload = self._service_payload(change)
                self._request("POST", f"/api/services/light/{service}", payload)
                self._sleep(min(max(change.transition_seconds, 0.1), 2.0))
                after = self._get_state(change.entity_id)
                items.append(self._verify(change, before, after))
            except HomeAssistantError as exc:
                items.append(ExecutionItem(change.entity_id, ResultState.FAILED, str(exc)))

        states = {item.state for item in items}
        if states == {ResultState.VERIFIED}:
            overall = ResultState.VERIFIED
        elif ResultState.VERIFIED in states:
            overall = ResultState.PARTIAL
        elif ResultState.DENIED in states and len(states) == 1:
            overall = ResultState.DENIED
        else:
            overall = ResultState.FAILED
        return ExecutionReport(proposal.proposal_id, overall, tuple(items), self.mode)

    @staticmethod
    def _service_payload(change: Any) -> tuple[str, dict[str, Any]]:
        payload: dict[str, Any] = {"entity_id": change.entity_id}
        if change.transition_seconds:
            payload["transition"] = change.transition_seconds
        if change.action == LightAction.TURN_OFF:
            return "turn_off", payload
        if change.action == LightAction.TOGGLE:
            return "toggle", payload
        if change.brightness_pct is not None:
            payload["brightness_pct"] = change.brightness_pct
        if change.rgb_color is not None:
            payload["rgb_color"] = list(change.rgb_color)
        if change.color_temp_kelvin is not None:
            payload["color_temp_kelvin"] = change.color_temp_kelvin
        return "turn_on", payload

    def _get_state(self, entity_id: str) -> dict[str, Any]:
        state = self._request("GET", f"/api/states/{quote(entity_id, safe='._')}")
        if not isinstance(state, dict):
            raise HomeAssistantError("Home Assistant returned an invalid light state")
        return state

    @staticmethod
    def _verify(change: Any, before: dict[str, Any] | None, after: dict[str, Any]) -> ExecutionItem:
        observed = str(after.get("state") or "unknown")
        if change.action == LightAction.TURN_OFF:
            expected = "off"
        elif change.action == LightAction.TURN_ON:
            expected = "on"
        else:
            prior = str((before or {}).get("state") or "unknown")
            expected = "off" if prior == "on" else "on" if prior == "off" else "unknown"
        if expected == "unknown" or observed != expected:
            return ExecutionItem(change.entity_id, ResultState.PARTIAL, f"Read-back was {observed}; expected {expected}", observed)

        attributes = after.get("attributes") if isinstance(after.get("attributes"), dict) else {}
        mismatches: list[str] = []
        if change.brightness_pct is not None and isinstance(attributes.get("brightness"), int):
            expected_brightness = round(change.brightness_pct * 255 / 100)
            if abs(attributes["brightness"] - expected_brightness) > 10:
                mismatches.append("brightness")
        if change.rgb_color is not None and isinstance(attributes.get("rgb_color"), list):
            observed_rgb = attributes["rgb_color"][:3]
            if len(observed_rgb) == 3 and any(abs(int(a) - int(b)) > 28 for a, b in zip(observed_rgb, change.rgb_color)):
                mismatches.append("color")
        if mismatches:
            return ExecutionItem(
                change.entity_id,
                ResultState.PARTIAL,
                f"State changed but read-back differs for {', '.join(mismatches)}",
                observed,
            )
        return ExecutionItem(change.entity_id, ResultState.VERIFIED, "Home Assistant read-back matches", observed)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Osun-Lights/0.1",
            },
        )
        try:
            response: HTTPResponse
            with self._opener.open(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            if exc.code == 401:
                raise HomeAssistantError("Home Assistant rejected the credential (401)") from None
            raise HomeAssistantError(f"Home Assistant request failed with HTTP {exc.code}") from None
        except (URLError, TimeoutError, OSError):
            raise HomeAssistantError("Home Assistant is unavailable or timed out") from None
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise HomeAssistantError("Home Assistant returned an invalid JSON response") from None
