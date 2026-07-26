from __future__ import annotations

import unittest
from typing import Any

from osun_lights.home_assistant import HomeAssistantClient
from osun_lights.models import LightAction, LightChange, LightingProposal, ResultState


class FakeHomeAssistant(HomeAssistantClient):
    def __init__(self, allowed: set[str]) -> None:
        super().__init__("http://homeassistant.local:8123", "synthetic-token", allowed, sleep=lambda _seconds: None)
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []
        self.states: dict[str, dict[str, Any]] = {
            "light.lounge": {
                "entity_id": "light.lounge",
                "state": "off",
                "attributes": {
                    "friendly_name": "Lounge",
                    "supported_color_modes": ["rgb"],
                    "brightness": 0,
                    "rgb_color": [0, 0, 0],
                },
            },
            "sensor.private": {
                "entity_id": "sensor.private",
                "state": "redacted",
                "attributes": {"friendly_name": "Not a light"},
            },
        }

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        self.calls.append((method, path, payload))
        if path == "/api/":
            return {"message": "API running."}
        if path == "/api/states":
            return list(self.states.values())
        if path.startswith("/api/states/"):
            return self.states[path.removeprefix("/api/states/")]
        if path.startswith("/api/services/light/"):
            assert payload is not None
            entity = payload["entity_id"]
            service = path.rsplit("/", 1)[-1]
            if service == "turn_off":
                self.states[entity]["state"] = "off"
            elif service == "toggle":
                self.states[entity]["state"] = "off" if self.states[entity]["state"] == "on" else "on"
            else:
                self.states[entity]["state"] = "on"
                if "brightness_pct" in payload:
                    self.states[entity]["attributes"]["brightness"] = round(payload["brightness_pct"] * 255 / 100)
                if "rgb_color" in payload:
                    self.states[entity]["attributes"]["rgb_color"] = payload["rgb_color"]
            return []
        raise AssertionError(f"Unexpected request {method} {path}")


class HomeAssistantClientTests(unittest.TestCase):
    def test_discovery_returns_only_light_entities(self) -> None:
        client = FakeHomeAssistant({"light.lounge"})
        self.assertTrue(client.check())
        lights = client.discover_lights()
        self.assertEqual(1, len(lights))
        self.assertEqual("light.lounge", lights[0].entity_id)
        self.assertTrue(lights[0].supports_color)

    def test_live_call_uses_only_light_service_and_reads_back(self) -> None:
        client = FakeHomeAssistant({"light.lounge"})
        proposal = LightingProposal(
            "Ocean",
            (
                LightChange(
                    "light.lounge",
                    "Lounge",
                    LightAction.TURN_ON,
                    brightness_pct=48,
                    rgb_color=(0, 42, 130),
                    transition_seconds=4,
                ),
            ),
        )
        report = client.apply(proposal)
        self.assertEqual(ResultState.VERIFIED, report.state)
        service_calls = [call for call in client.calls if "/api/services/" in call[1]]
        self.assertEqual(1, len(service_calls))
        method, path, payload = service_calls[0]
        self.assertEqual("POST", method)
        self.assertEqual("/api/services/light/turn_on", path)
        self.assertEqual("light.lounge", payload["entity_id"])
        self.assertEqual([0, 42, 130], payload["rgb_color"])
        self.assertTrue(any(call[1] == "/api/states/light.lounge" for call in client.calls))

    def test_non_allowlisted_entity_is_denied_before_service_call(self) -> None:
        client = FakeHomeAssistant(set())
        proposal = LightingProposal(
            "Denied",
            (LightChange("light.lounge", "Lounge", LightAction.TURN_OFF),),
        )
        report = client.apply(proposal)
        self.assertEqual(ResultState.DENIED, report.state)
        self.assertFalse(any("/api/services/" in call[1] for call in client.calls))

    def test_constructor_rejects_non_light_allowlist(self) -> None:
        with self.assertRaises(ValueError):
            HomeAssistantClient("http://homeassistant.local:8123", "synthetic", {"lock.front_door"})

    def test_constructor_rejects_public_host_for_local_prototype(self) -> None:
        with self.assertRaises(ValueError):
            HomeAssistantClient("https://example.com", "synthetic", {"light.lounge"})


if __name__ == "__main__":
    unittest.main()
