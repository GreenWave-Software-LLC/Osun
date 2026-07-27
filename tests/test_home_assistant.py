from __future__ import annotations

import unittest
from typing import Any

from osun_lights.home_assistant import HomeAssistantClient
from osun_lights.models import LightAction, LightChange, LightingProposal, ResultState, public_light_state


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
            "light.relax_zone": {
                "entity_id": "light.relax_zone",
                "state": "on",
                "attributes": {
                    "friendly_name": "Relax",
                    "supported_color_modes": ["rgb"],
                    "is_hue_group": True,
                    "hue_type": "zone",
                    "lights": ["Bathroom 1", "Bedroom 2"],
                },
            },
            "light.helper_group": {
                "entity_id": "light.helper_group",
                "state": "off",
                "attributes": {
                    "friendly_name": "Helper Group",
                    "supported_color_modes": ["brightness"],
                    "entity_id": ["light.lounge"],
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
        self.assertEqual(3, len(lights))
        by_id = {light.entity_id: light for light in lights}
        self.assertTrue(by_id["light.lounge"].supports_color)
        relax = by_id["light.relax_zone"]
        self.assertTrue(relax.is_zone)
        self.assertEqual("zone", relax.group_type)
        self.assertEqual(("Bathroom 1", "Bedroom 2"), relax.member_names)
        helper = by_id["light.helper_group"]
        self.assertEqual(("light.lounge",), helper.member_entity_ids)
        self.assertEqual(("Lounge",), helper.member_names)
        public = public_light_state(relax)
        self.assertEqual("zone", public["kind"])
        self.assertEqual(["Bathroom 1", "Bedroom 2"], public["member_names"])

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
