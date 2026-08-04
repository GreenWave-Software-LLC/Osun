from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from osun_music.config import MusicConfigStore
from osun_music.device_router import choose_playback_device
from osun_music.runtime import MusicController


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


class MusicAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.clock = FakeClock()
        self.credentials = MemoryCredentialStore()
        self.controller = MusicController(
            MusicConfigStore(self.root / "music.json"),
            self.credentials,  # type: ignore[arg-type]
            clock=self.clock,
        )
        self.controller.save_settings({"mode": "simulator"})

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_first_play_request_asks_for_device_then_records_success(self) -> None:
        reply = self.controller.message("play Kind of Blue")
        music_request = reply["request"]

        self.assertEqual("needs_device", music_request["state"])
        self.assertIn("Which device", reply["text"])
        selected = self.controller.select_device(music_request["request_id"], "agent-box-windows")
        self.assertEqual("ready", selected["state"])
        result = self.controller.execute(music_request["request_id"])
        self.assertEqual("simulated", result["state"])
        self.assertEqual("This PC", result["device_name"])
        self.assertTrue(self.controller.status()["devices"][0]["recent"])

    def test_recent_device_is_reused_through_300_seconds(self) -> None:
        first = self.controller.message("play Kind of Blue")["request"]
        self.controller.select_device(first["request_id"], "agent-box-windows")
        self.controller.execute(first["request_id"])

        self.clock.now += 300
        follow_up = self.controller.message("play Blue in Green")
        self.assertEqual("ready", follow_up["request"]["state"])
        self.assertEqual("agent-box-windows", follow_up["request"]["device_id"])
        self.assertEqual("recent_playback", follow_up["request"]["selection_reason"])

    def test_device_is_asked_again_after_300_seconds(self) -> None:
        first = self.controller.message("play Kind of Blue")["request"]
        self.controller.select_device(first["request_id"], "agent-box-windows")
        self.controller.execute(first["request_id"])

        self.clock.now += 301
        follow_up = self.controller.message("play Blue in Green")
        self.assertEqual("needs_device", follow_up["request"]["state"])
        self.assertIsNone(follow_up["request"]["device_id"])

    def test_explicit_device_bypasses_recent_device_question(self) -> None:
        reply = self.controller.message("play Discovery on This PC")
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
                self.assertEqual("agent-box-windows", reply["request"]["device_id"])
                self.assertEqual(query, reply["request"]["query"])

    def test_device_only_follow_up_resolves_latest_pending_request(self) -> None:
        first = self.controller.message("play Cardi B")["request"]
        follow_up = self.controller.message("on my pc")
        self.assertEqual(first["request_id"], follow_up["request"]["request_id"])
        self.assertEqual("Cardi B", follow_up["request"]["query"])
        self.assertEqual("ready", follow_up["request"]["state"])
        self.assertEqual("agent-box-windows", follow_up["request"]["device_id"])
        self.assertIn("This PC", follow_up["text"])

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
        self.assertEqual("agent-box-windows", explicit.requested_device_id)

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
        music_request = self.controller.message("play Oracular Spectacular on This PC")["request"]
        command = self.controller.execute(music_request["request_id"])
        self.assertEqual("client_required", command["state"])
        self.assertEqual(
            {"action": "play", "query": "Oracular Spectacular"},
            command["command"],
        )
        result = self.controller.playback_result(
            music_request["request_id"],
            "agent-box-windows",
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

    def test_disabled_agent_rejects_even_simulated_execution(self) -> None:
        self.controller.save_settings({"mode": "simulator", "enabled": False})
        music_request = self.controller.message("play music on This PC")["request"]
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
        music_request = self.controller.message("play music on This PC")["request"]
        self.controller.execute(music_request["request_id"])
        self.assertIsNone(self.controller.status()["pending"])
        self.controller.cancel()
        with self.assertRaisesRegex(ValueError, "missing or expired"):
            self.controller.execute(music_request["request_id"])

    def test_new_controller_does_not_restore_listening_recency(self) -> None:
        first = self.controller.message("play music on This PC")["request"]
        self.controller.execute(first["request_id"])
        restarted = MusicController(
            MusicConfigStore(self.root / "music.json"),
            self.credentials,  # type: ignore[arg-type]
            clock=self.clock,
        )
        self.assertFalse(restarted.status()["devices"][0]["recent"])


if __name__ == "__main__":
    unittest.main()
