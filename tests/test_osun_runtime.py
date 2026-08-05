from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from osun.qwen import QwenError, QwenReply
from osun.runtime import OsunController
from osun_lights.audit import AuditLog
from osun_lights.config import ConfigStore
from osun_lights.credential_store import WindowsCredentialStore
from osun_lights.runtime import LightingController
from osun_music.config import MusicConfigStore
from osun_music.runtime import MusicController
from osun_music.windows_app import WindowsMusicResult


class FakeQwen:
    def __init__(self, *, tool: bool = False, content: str = "", error: str | None = None) -> None:
        self.tool = tool
        self.content = content
        self.error = error
        self.received: list[str] = []

    def status(self) -> dict[str, object]:
        return {
            "online": self.error is None,
            "model": "qwen-test",
            "model_available": self.error is None,
            "available_models": ["qwen-test"] if self.error is None else [],
            "endpoint": "http://127.0.0.1:11434",
            "provider": "Ollama",
        }

    def chat(self, user_text: str, _history: tuple[dict[str, str], ...]) -> QwenReply:
        self.received.append(user_text)
        if self.error:
            raise QwenError(self.error)
        tool_name = self.tool if isinstance(self.tool, str) else "open_lighting_widget"
        return QwenReply(self.content, (tool_name,) if self.tool else ())


class FakeHeadphoneDetector:
    def status(self) -> dict[str, object]:
        return {"connected": True, "names": ["Test Bluetooth Headphones"], "evidence": "test"}


class UnavailableWindowsAdapter:
    def available(self) -> bool:
        return False


class FakeAppleTVAdapter:
    def available(self) -> bool:
        return True

    def execute(self, action: str, query: str = "") -> WindowsMusicResult:
        return WindowsMusicResult(success=True, verified=True, now_playing=query)


class OsunRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.lighting = LightingController(
            ConfigStore(root / "config.json"),
            AuditLog(root / "audit.jsonl"),
            WindowsCredentialStore(root / "credential.bin"),
        )
        self.music = MusicController(
            MusicConfigStore(root / "music.json"),
            WindowsCredentialStore(root / "music-credential.bin"),
            windows_adapter=UnavailableWindowsAdapter(),  # type: ignore[arg-type]
            headphone_detector=FakeHeadphoneDetector(),  # type: ignore[arg-type]
            apple_tv_adapter=FakeAppleTVAdapter(),  # type: ignore[arg-type]
        )
        self.music.save_settings({"mode": "simulator"})

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_general_chat_uses_qwen_without_widget(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(content="Let's choose one priority."), self.music)
        reply = controller.message("Help me plan today")
        self.assertEqual("osun", reply["agent"])
        self.assertEqual([], reply["widgets"])
        self.assertIn("priority", reply["text"])

    def test_qwen_tool_call_opens_lighting_widget_with_raw_owner_request(self) -> None:
        qwen = FakeQwen(tool=True)
        controller = OsunController(self.lighting, qwen, self.music)
        reply = controller.message("I want to feel like I am in the ocean")
        self.assertEqual("lighting", reply["agent"])
        self.assertEqual("Deep Ocean", reply["widgets"][0]["proposal"]["theme_name"])
        self.assertEqual("I want to feel like I am in the ocean", qwen.received[0])
        self.assertIsNone(reply["execution"])
        self.assertFalse(reply["widgets"][0]["execution_policy"]["autonomous"])
        self.assertTrue(all(light["state"] == "off" for light in self.lighting.status()["lights"]))

    def test_widget_autonomy_executes_exact_proposal_without_apply(self) -> None:
        self.lighting.save_settings(
            {
                "mode": "simulator",
                "live_enabled": False,
                "global_pause": False,
                "autonomous_execution": True,
            }
        )
        controller = OsunController(self.lighting, FakeQwen(tool=True), self.music)
        reply = controller.message("I want to feel like I am in the ocean")

        self.assertEqual("verified", reply["execution"]["state"])
        self.assertIn("Applied autonomously", reply["text"])
        self.assertFalse(reply["widgets"][0]["proposal"]["requires_confirmation"])
        self.assertTrue(reply["widgets"][0]["execution_policy"]["autonomous"])
        self.assertIsNone(self.lighting.assistant.pending)
        self.assertTrue(all(light["state"] == "on" for light in self.lighting.status()["lights"]))
        audit_text = self.lighting.audit.path.read_text(encoding="utf-8")
        self.assertIn("lighting.autonomous_requested", audit_text)
        self.assertNotIn("I want to feel like I am in the ocean", audit_text)

    def test_emergency_pause_overrides_widget_autonomy(self) -> None:
        self.lighting.save_settings(
            {
                "mode": "simulator",
                "live_enabled": False,
                "global_pause": True,
                "autonomous_execution": True,
            }
        )
        controller = OsunController(self.lighting, FakeQwen(tool=True), self.music)
        reply = controller.message("turn the lights on")

        self.assertEqual("denied", reply["execution"]["state"])
        self.assertIn("Autonomous execution was blocked", reply["text"])
        self.assertTrue(reply["widgets"][0]["execution_policy"]["paused"])
        self.assertTrue(all(light["state"] == "off" for light in self.lighting.status()["lights"]))

    def test_model_failure_keeps_explicit_lighting_fallback(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(error="offline"), self.music)
        reply = controller.message("Set the lights to 30 percent")
        self.assertEqual("lighting", reply["agent"])
        self.assertEqual(30, reply["widgets"][0]["proposal"]["changes"][0]["brightness_pct"])

    def test_model_failure_does_not_invent_general_answer(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(error="offline"), self.music)
        reply = controller.message("What meetings do I have today?")
        self.assertEqual("osun", reply["agent"])
        self.assertFalse(reply["model"]["used"])
        self.assertIn("unavailable", reply["text"])

    def test_new_chat_clears_pending_lighting_proposal(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(tool=True), self.music)
        controller.message("turn the lights on")
        self.assertIsNotNone(self.lighting.assistant.pending)
        controller.new_chat()
        self.assertIsNone(self.lighting.assistant.pending)

    def test_music_tool_call_asks_between_connected_headphones_and_tv_each_time(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(tool="open_music_widget"), self.music)
        first = controller.message("play Kind of Blue")
        self.assertEqual("music", first["agent"])
        self.assertEqual("needs_device", first["widgets"][0]["request"]["state"])
        selected = controller.music_select_device(
            first["widgets"][0]["request"]["request_id"],
            "bluetooth-headphones",
        )
        controller.music_execute(selected["request"]["request_id"])

        second = controller.message("play Blue in Green")
        self.assertEqual("needs_device", second["widgets"][0]["request"]["state"])
        self.assertEqual("ask_headphones_or_tv", second["widgets"][0]["request"]["selection_reason"])

    def test_music_device_follow_up_bypasses_qwen_and_resolves_pending_request(self) -> None:
        qwen = FakeQwen(tool="open_music_widget")
        controller = OsunController(self.lighting, qwen, self.music)
        first = controller.message("play Cardi B")
        request_id = first["widgets"][0]["request"]["request_id"]

        follow_up = controller.message("my pc")

        self.assertEqual("music", follow_up["agent"])
        self.assertEqual(request_id, follow_up["widgets"][0]["request"]["request_id"])
        self.assertEqual("ready", follow_up["widgets"][0]["request"]["state"])
        self.assertEqual("bluetooth-headphones", follow_up["widgets"][0]["request"]["device_id"])
        self.assertEqual([], qwen.received)

    def test_model_scoped_music_fragment_fills_play_query(self) -> None:
        controller = OsunController(
            self.lighting,
            FakeQwen(tool="open_music_widget"),
            self.music,
        )
        reply = controller.message("a cardi b song")
        self.assertEqual("music", reply["agent"])
        self.assertEqual("cardi b", reply["widgets"][0]["request"]["query"])

    def test_explicit_my_pc_alias_is_ready_for_immediate_execution(self) -> None:
        controller = OsunController(
            self.lighting,
            FakeQwen(tool="open_music_widget"),
            self.music,
        )
        reply = controller.message("play cardi b on my pc")
        music_request = reply["widgets"][0]["request"]
        self.assertEqual("ready", music_request["state"])
        self.assertEqual("cardi b", music_request["query"])
        self.assertEqual("bluetooth-headphones", music_request["device_id"])

    def test_exact_play_command_is_deterministic_when_qwen_returns_general_text(self) -> None:
        qwen = FakeQwen(content="Which song would you like?")
        controller = OsunController(self.lighting, qwen, self.music)
        reply = controller.message("play")
        self.assertEqual("music", reply["agent"])
        self.assertEqual("music", reply["widgets"][0]["request"]["query"])
        self.assertEqual([], qwen.received)

    def test_playback_device_question_bypasses_qwen_and_opens_device_inventory(self) -> None:
        qwen = FakeQwen(content="I do not have access to your playback devices.")
        controller = OsunController(self.lighting, qwen, self.music)
        reply = controller.message("what devices are available to play on?")

        self.assertEqual("music", reply["agent"])
        self.assertIn("Headphones", reply["text"])
        self.assertIn("Living Room Apple TV", reply["text"])
        self.assertEqual([], qwen.received)
        self.assertEqual("devices", reply["widgets"][0]["view"])
        self.assertIsNone(reply["widgets"][0]["request"])
        self.assertEqual(
            ["Headphones", "Living Room Apple TV"],
            [device["name"] for device in reply["widgets"][0]["devices"]],
        )


if __name__ == "__main__":
    unittest.main()
