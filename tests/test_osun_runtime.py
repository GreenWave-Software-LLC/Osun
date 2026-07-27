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
        return QwenReply(self.content, ("open_lighting_widget",) if self.tool else ())


class OsunRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.lighting = LightingController(
            ConfigStore(root / "config.json"),
            AuditLog(root / "audit.jsonl"),
            WindowsCredentialStore(root / "credential.bin"),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_general_chat_uses_qwen_without_widget(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(content="Let's choose one priority."))
        reply = controller.message("Help me plan today")
        self.assertEqual("osun", reply["agent"])
        self.assertEqual([], reply["widgets"])
        self.assertIn("priority", reply["text"])

    def test_qwen_tool_call_opens_lighting_widget_with_raw_owner_request(self) -> None:
        qwen = FakeQwen(tool=True)
        controller = OsunController(self.lighting, qwen)
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
        controller = OsunController(self.lighting, FakeQwen(tool=True))
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
        controller = OsunController(self.lighting, FakeQwen(tool=True))
        reply = controller.message("turn the lights on")

        self.assertEqual("denied", reply["execution"]["state"])
        self.assertIn("Autonomous execution was blocked", reply["text"])
        self.assertTrue(reply["widgets"][0]["execution_policy"]["paused"])
        self.assertTrue(all(light["state"] == "off" for light in self.lighting.status()["lights"]))

    def test_model_failure_keeps_explicit_lighting_fallback(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(error="offline"))
        reply = controller.message("Set the lights to 30 percent")
        self.assertEqual("lighting", reply["agent"])
        self.assertEqual(30, reply["widgets"][0]["proposal"]["changes"][0]["brightness_pct"])

    def test_model_failure_does_not_invent_general_answer(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(error="offline"))
        reply = controller.message("What meetings do I have today?")
        self.assertEqual("osun", reply["agent"])
        self.assertFalse(reply["model"]["used"])
        self.assertIn("unavailable", reply["text"])

    def test_new_chat_clears_pending_lighting_proposal(self) -> None:
        controller = OsunController(self.lighting, FakeQwen(tool=True))
        controller.message("turn the lights on")
        self.assertIsNotNone(self.lighting.assistant.pending)
        controller.new_chat()
        self.assertIsNone(self.lighting.assistant.pending)


if __name__ == "__main__":
    unittest.main()
