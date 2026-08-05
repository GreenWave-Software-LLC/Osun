from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from osun_music.config import MusicConfigStore
from osun_music.device_router import choose_playback_device
from osun_music.runtime import MusicController
from osun_music.windows_app import WindowsMusicResult


class FakeClock:
    def __init__(self, now: float = 1_000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


class MemoryCredentialStore:
    def __init__(self) -> None:
        self.value: str | None = None

    def save(self, value: str) -> None:
        self.value = value

    def load(self) -> str | None:
        return self.value

    def delete(self) -> None:
        self.value = None


class FakeHeadphoneDetector:
    def __init__(self, connected: bool = True) -> None:
        self.connected = connected

    def status(self) -> dict[str, object]:
        return {
            "connected": self.connected,
            "names": ["Test Bluetooth Headphones"] if self.connected else [],
            "evidence": "test",
        }


class UnavailableWindowsAdapter:
    def available(self) -> bool:
        return False


class FakeAppleTVAdapter:
    def __init__(self, available: bool = True) -> None:
        self.is_available = available
        self.calls: list[tuple[str, str]] = []

    def available(self) -> bool:
        return self.is_available

    def execute(self, action: str, query: str = "") -> WindowsMusicResult:
        self.calls.append((action, query))
        return WindowsMusicResult(
            success=True,
            verified=True,
            playback_active=action != "pause",
            now_playing=query,
            evidence="test_apple_tv",
        )


class MusicAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.clock = FakeClock()
        self.credentials = MemoryCredentialStore()
        self.headphones = FakeHeadphoneDetector()
        self.apple_tv = FakeAppleTVAdapter()
        self.controller = MusicController(
            MusicConfigStore(self.root / "music.json"),
            self.credentials,  # type: ignore[arg-type]
            windows_adapter=UnavailableWindowsAdapter(),  # type: ignore[arg-type]
            headphone_detector=self.headphones,  # type: ignore[arg-type]
            apple_tv_adapter=self.apple_tv,  # type: ignore[arg-type]
            clock=self.clock,
        )
        self.controller.save_settings({"mode": "simulator"})

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_first_play_request_asks_for_device_then_records_success(self) -> None:
        reply = self.controller.message("play Kind of Blue")
        music_request = reply["request"]

        self.assertEqual("needs_device", music_request["state"])
        self.assertIn("Would you like", reply["text"])
        selected = self.controller.select_device(music_request["request_id"], "bluetooth-headphones")
        self.assertEqual("ready", selected["state"])
        result = self.controller.execute(music_request["request_id"])
        self.assertEqual("simulated", result["state"])
        self.assertEqual("Headphones", result["device_name"])
        self.assertTrue(self.controller.status()["devices"][0]["recent"])

    def test_no_headphones_defaults_new_play_to_living_room_apple_tv(self) -> None:
        self.headphones.connected = False

        reply = self.controller.message("play Kind of Blue")

        self.assertEqual("ready", reply["request"]["state"])
        self.assertEqual("living-room-apple-tv", reply["request"]["device_id"])
        self.assertEqual("headphones_unavailable_default_tv", reply["request"]["selection_reason"])
        self.assertIn("not connected", reply["text"])

    def test_explicit_pc_falls_back_to_tv_when_headphones_disconnect(self) -> None:
        self.headphones.connected = False

        reply = self.controller.message("play Kind of Blue on my pc")

        self.assertEqual("living-room-apple-tv", reply["request"]["device_id"])
        self.assertEqual("headphones_unavailable_default_tv", reply["request"]["selection_reason"])

    def test_connected_headphones_are_asked_again_for_each_new_play(self) -> None:
        first = self.controller.message("play Kind of Blue")["request"]
        self.controller.select_device(first["request_id"], "bluetooth-headphones")
        self.controller.execute(first["request_id"])

        self.clock.now += 300
        follow_up = self.controller.message("play Blue in Green")
        self.assertEqual("needs_device", follow_up["request"]["state"])
        self.assertEqual("ask_headphones_or_tv", follow_up["request"]["selection_reason"])

    def test_recent_headphones_are_reused_for_transport_controls(self) -> None:
        first = self.controller.message("play Kind of Blue")["request"]
        self.controller.select_device(first["request_id"], "bluetooth-headphones")
        self.controller.execute(first["request_id"])

        self.clock.now += 300
        follow_up = self.controller.message("pause")
        self.assertEqual("ready", follow_up["request"]["state"])
        self.assertEqual("bluetooth-headphones", follow_up["request"]["device_id"])
        self.assertEqual("recent_playback", follow_up["request"]["selection_reason"])

    def test_explicit_device_bypasses_recent_device_question(self) -> None:
        reply = self.controller.message("play Discovery on Headphones")
        self.assertEqual("ready", reply["request"]["state"])
        self.assertEqual("owner_selected", reply["request"]["selection_reason"])
        self.assertEqual("Discovery", reply["request"]["query"])

    def test_windows_device_aliases_select_this_pc_and_leave_query_clean(self) -> None:
        cases = {
            "play Cardi B on my pc": "Cardi B",
            "play Cardi B on my computer": "Cardi B",
            "play Cardi B on the agent box": "Cardi B",
        }
        for phrase, query in cases.items():
            with self.subTest(phrase=phrase):
                reply = self.controller.message(phrase)
                self.assertEqual("ready", reply["request"]["state"])
                self.assertEqual("bluetooth-headphones", reply["request"]["device_id"])
                self.assertEqual(query, reply["request"]["query"])

    def test_device_only_follow_up_resolves_latest_pending_request(self) -> None:
        first = self.controller.message("play Cardi B")["request"]
        follow_up = self.controller.message("on my pc")
        self.assertEqual(first["request_id"], follow_up["request"]["request_id"])
        self.assertEqual("Cardi B", follow_up["request"]["query"])
        self.assertEqual("ready", follow_up["request"]["state"])
        self.assertEqual("bluetooth-headphones", follow_up["request"]["device_id"])
        self.assertIn("Headphones", follow_up["text"])

    def test_new_music_request_supersedes_older_device_question(self) -> None:
        first = self.controller.message("play Cardi B")["request"]
        second = self.controller.message("play Megan Thee Stallion on my pc")["request"]
        self.assertNotEqual(first["request_id"], second["request_id"])
        self.assertEqual("ready", second["state"])
        self.controller.execute(second["request_id"])
        self.assertIsNone(self.controller.status()["pending"])

    def test_scoped_bare_music_fragments_become_play_requests(self) -> None:
        cases = {
            "a cardi b song": "cardi b",
            "anything": "music",
            "some jazz music": "jazz",
        }
        for phrase, query in cases.items():
            with self.subTest(phrase=phrase):
                reply = self.controller.message(phrase, allow_bare_play=True)
                self.assertEqual("play", reply["request"]["action"])
                self.assertEqual(query, reply["request"]["query"])

    def test_bare_fragment_requires_explicit_music_agent_scope(self) -> None:
        self.assertIsNone(self.controller.message("a cardi b song")["request"])

    def test_play_without_query_defaults_to_music(self) -> None:
        reply = self.controller.message("play")
        self.assertEqual("play", reply["request"]["action"])
        self.assertEqual("music", reply["request"]["query"])

    def test_device_inventory_questions_list_devices_without_losing_pending_playback(self) -> None:
        cases = (
            "what devices are available to play on?",
            "which playback devices are connected",
            "what devices can I play music on",
            "where can I play Apple Music?",
            "list my music devices",
        )
        for phrase in cases:
            with self.subTest(phrase=phrase):
                parsed = self.controller.parser.parse(phrase, self.controller.status()["devices"])
                self.assertIsNotNone(parsed)
                self.assertEqual("list_devices", parsed.action)

        pending = self.controller.message("play Cardi B")["request"]
        listing = self.controller.message("what devices are available to play on?")
        self.assertEqual("devices", listing["view"])
        self.assertIsNone(listing["request"])
        self.assertEqual(
            ["Headphones", "Living Room Apple TV"],
            [device["name"] for device in listing["devices"]],
        )
        self.assertIn("2 available playback devices", listing["text"])

        follow_up = self.controller.message("my pc")
        self.assertEqual(pending["request_id"], follow_up["request"]["request_id"])
        self.assertEqual("ready", follow_up["request"]["state"])

    def test_control_phrases_and_explicit_device_are_typed(self) -> None:
        cases = {
            "pause": "pause",
            "continue the music": "resume",
            "skip this song": "next",
            "go back on This PC": "previous",
            "pause on my pc": "pause",
        }
        for phrase, action in cases.items():
            with self.subTest(phrase=phrase):
                parsed = self.controller.parser.parse(phrase, self.controller.status()["devices"])
                self.assertIsNotNone(parsed)
                self.assertEqual(action, parsed.action)
        explicit = self.controller.parser.parse("go back on This PC", self.controller.status()["devices"])
        self.assertEqual("bluetooth-headphones", explicit.requested_device_id)

    def test_router_chooses_most_recent_available_device(self) -> None:
        decision = choose_playback_device(
            [
                {"device_id": "office", "enabled": True, "last_played_at": 900.0},
                {"device_id": "kitchen", "enabled": True, "last_played_at": 980.0},
                {"device_id": "disabled", "enabled": False, "last_played_at": 999.0},
            ],
            now=1_000.0,
        )
        self.assertEqual("kitchen", decision.device_id)
        self.assertEqual("recent_playback", decision.reason)

    def test_musickit_returns_typed_browser_command_and_records_verified_result(self) -> None:
        self.controller.save_settings(
            {
                "mode": "musickit",
                "enabled": True,
                "developer_token": "header.payload.signature",
            }
        )
        music_request = self.controller.message("play Oracular Spectacular on Headphones")["request"]
        command = self.controller.execute(music_request["request_id"])
        self.assertEqual("client_required", command["state"])
        self.assertEqual(
            {"action": "play", "query": "Oracular Spectacular"},
            command["command"],
        )
        result = self.controller.playback_result(
            music_request["request_id"],
            "bluetooth-headphones",
            success=True,
            now_playing="Time to Pretend by MGMT",
        )
        self.assertEqual("verified", result["state"])
        self.assertIn("Time to Pretend", result["summary"])

    def test_developer_token_is_not_written_to_config(self) -> None:
        token = "header.payload.signature"
        self.controller.save_settings({"mode": "musickit", "developer_token": token})
        raw = (self.root / "music.json").read_text(encoding="utf-8")
        self.assertNotIn(token, raw)
        self.assertNotIn("developer_token", json.loads(raw))
        self.assertEqual(token, self.credentials.value)

    def test_legacy_this_pc_config_migrates_to_headphones_and_apple_tv(self) -> None:
        path = self.root / "legacy-music.json"
        path.write_text(
            json.dumps(
                {
                    "mode": "windows_app",
                    "enabled": True,
                    "devices": [
                        {
                            "device_id": "agent-box-windows",
                            "name": "This PC",
                            "kind": "windows_app",
                            "enabled": True,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        migrated = MusicConfigStore(path).load()

        self.assertEqual(
            ["bluetooth-headphones", "living-room-apple-tv"],
            [device.device_id for device in migrated.devices],
        )

    def test_disabled_agent_rejects_even_simulated_execution(self) -> None:
        self.controller.save_settings({"mode": "simulator", "enabled": False})
        music_request = self.controller.message("play music on Headphones")["request"]
        with self.assertRaisesRegex(ValueError, "disabled"):
            self.controller.execute(music_request["request_id"])

    def test_policy_switches_reject_string_booleans(self) -> None:
        with self.assertRaisesRegex(ValueError, "true or false"):
            self.controller.save_settings({"enabled": "false"})

    def test_musickit_without_token_falls_back_to_effective_simulator(self) -> None:
        status = self.controller.save_settings({"mode": "musickit"})
        self.assertEqual("musickit", status["mode"])
        self.assertEqual("simulator", status["effective_mode"])
        self.assertFalse(status["developer_token_configured"])

    def test_completed_requests_are_not_pending_and_new_chat_clears_results(self) -> None:
        music_request = self.controller.message("play music on Headphones")["request"]
        self.controller.execute(music_request["request_id"])
        self.assertIsNone(self.controller.status()["pending"])
        self.controller.cancel()
        with self.assertRaisesRegex(ValueError, "missing or expired"):
            self.controller.execute(music_request["request_id"])

    def test_new_controller_does_not_restore_listening_recency(self) -> None:
        first = self.controller.message("play music on Headphones")["request"]
        self.controller.execute(first["request_id"])
        restarted = MusicController(
            MusicConfigStore(self.root / "music.json"),
            self.credentials,  # type: ignore[arg-type]
            headphone_detector=self.headphones,  # type: ignore[arg-type]
            apple_tv_adapter=self.apple_tv,  # type: ignore[arg-type]
            clock=self.clock,
        )
        self.assertFalse(restarted.status()["devices"][0]["recent"])


if __name__ == "__main__":
    unittest.main()
