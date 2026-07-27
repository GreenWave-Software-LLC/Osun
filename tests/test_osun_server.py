from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from osun.qwen import QwenReply
from osun.runtime import OsunController
from osun.server import OsunServer
from osun_lights.audit import AuditLog
from osun_lights.config import ConfigStore
from osun_lights.credential_store import WindowsCredentialStore
from osun_lights.runtime import LightingController
from osun_music.config import MusicConfigStore
from osun_music.runtime import MusicController


class WidgetQwen:
    def status(self) -> dict[str, object]:
        return {
            "online": True,
            "model": "qwen3.5:9b",
            "model_available": True,
            "available_models": ["qwen3.5:9b"],
            "endpoint": "http://127.0.0.1:11434",
            "provider": "Ollama",
        }

    def chat(self, text: str, _history: tuple[dict[str, str], ...]) -> QwenReply:
        tool = "open_music_widget" if "play" in text.casefold() else "open_lighting_widget"
        return QwenReply("", (tool,))


class OsunServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        lighting = LightingController(
            ConfigStore(root / "config.json"),
            AuditLog(root / "audit.jsonl"),
            WindowsCredentialStore(root / "credential.bin"),
        )
        music = MusicController(
            MusicConfigStore(root / "music.json"),
            WindowsCredentialStore(root / "music-credential.bin"),
        )
        controller = OsunController(lighting, WidgetQwen(), music)
        self.server = OsunServer(("127.0.0.1", 0), controller, "osun-test-session")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.api = f"{self.base}/api/osun-test-session"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    def get(self, path: str) -> tuple[int, dict[str, str], bytes]:
        with urlopen(f"{self.base}{path}", timeout=3) as response:
            return response.status, dict(response.headers), response.read()

    def post(self, path: str, payload: dict[str, Any], origin: str | None = None) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        request = Request(
            f"{self.api}{path}",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers=headers,
        )
        with urlopen(request, timeout=3) as response:
            return json.loads(response.read().decode("utf-8"))

    def test_main_shell_is_neutral_and_secured(self) -> None:
        status, headers, body = self.get("/app/osun-test-session/")
        self.assertEqual(200, status)
        self.assertIn(b"Personal intelligence", body)
        self.assertNotIn(b"Lighting Assistant", body)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        self.assertIn("https://js-cdn.music.apple.com", headers["Content-Security-Policy"])

    def test_qwen_routed_lighting_request_returns_widget_before_apply(self) -> None:
        status = json.loads(self.get("/api/osun-test-session/status")[2].decode("utf-8"))
        selected = [light["entity_id"] for light in status["lighting"]["lights"]]
        reply = self.post(
            "/message",
            {"text": "I want to feel like I am in the ocean", "context": {"lighting_selected_entities": selected}},
        )
        self.assertEqual("lighting", reply["agent"])
        self.assertEqual("lighting", reply["widgets"][0]["kind"])
        self.assertEqual("Deep Ocean", reply["widgets"][0]["proposal"]["theme_name"])
        unchanged = json.loads(self.get("/api/osun-test-session/status")[2].decode("utf-8"))
        self.assertTrue(all(light["state"] == "off" for light in unchanged["lighting"]["lights"]))

    def test_cross_origin_write_is_denied(self) -> None:
        with self.assertRaises(HTTPError) as context:
            self.post("/new-chat", {}, origin="https://malicious.example")
        self.assertEqual(400, context.exception.code)
        context.exception.close()

    def test_music_device_selection_and_playback_endpoints(self) -> None:
        reply = self.post("/message", {"text": "play Kind of Blue", "context": {}})
        widget = reply["widgets"][0]
        self.assertEqual("music", widget["kind"])
        self.assertEqual("needs_device", widget["request"]["state"])

        selected = self.post(
            "/agents/music/select-device",
            {
                "request_id": widget["request"]["request_id"],
                "device_id": "agent-box-browser",
            },
        )
        result = self.post(
            "/agents/music/execute",
            {"request_id": selected["request"]["request_id"]},
        )
        self.assertEqual("simulated", result["state"])
        self.assertEqual("This PC", result["device_name"])


if __name__ == "__main__":
    unittest.main()
