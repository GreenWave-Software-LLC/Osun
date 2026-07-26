from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from osun_lights.audit import AuditLog
from osun_lights.config import ConfigStore
from osun_lights.credential_store import WindowsCredentialStore
from osun_lights.runtime import LightingController
from osun_lights.server import OsunServer


class LocalServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        controller = LightingController(
            ConfigStore(root / "config.json"),
            AuditLog(root / "audit.jsonl"),
            WindowsCredentialStore(root / "credential.bin"),
        )
        self.server = OsunServer(("127.0.0.1", 0), controller, "synthetic-session")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.api = f"{self.base}/api/synthetic-session"

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

    def test_app_requires_session_path_and_sends_security_headers(self) -> None:
        status, headers, body = self.get("/app/synthetic-session/")
        self.assertEqual(200, status)
        self.assertIn(b"Osun Lighting Assistant", body)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual("no-store", headers["Cache-Control"])
        with self.assertRaises(HTTPError) as context:
            self.get("/app/wrong-session/")
        self.assertEqual(404, context.exception.code)
        context.exception.close()

    def test_ocean_preview_then_apply_over_local_api(self) -> None:
        status = json.loads(self.get("/api/synthetic-session/status")[2].decode("utf-8"))
        self.assertEqual(4, len(status["lights"]))
        self.assertTrue(all(light["state"] == "off" for light in status["lights"]))

        reply = self.post(
            "/message",
            {"text": "I want to feel like I am in the ocean", "selected_entities": [light["entity_id"] for light in status["lights"]]},
        )
        self.assertEqual("Deep Ocean", reply["proposal"]["theme_name"])
        unchanged = json.loads(self.get("/api/synthetic-session/status")[2].decode("utf-8"))
        self.assertTrue(all(light["state"] == "off" for light in unchanged["lights"]))

        report = self.post("/apply", {"proposal_id": reply["proposal"]["proposal_id"]})
        self.assertEqual("verified", report["state"])
        changed = json.loads(self.get("/api/synthetic-session/status")[2].decode("utf-8"))
        self.assertTrue(all(light["state"] == "on" for light in changed["lights"]))

    def test_pause_denies_pending_execution(self) -> None:
        status = json.loads(self.get("/api/synthetic-session/status")[2].decode("utf-8"))
        reply = self.post(
            "/message",
            {"text": "turn on", "selected_entities": [status["lights"][0]["entity_id"]]},
        )
        self.post("/pause", {})
        report = self.post("/apply", {"proposal_id": reply["proposal"]["proposal_id"]})
        self.assertEqual("denied", report["state"])

    def test_cross_origin_write_is_denied(self) -> None:
        with self.assertRaises(HTTPError) as context:
            self.post("/pause", {}, origin="https://malicious.example")
        self.assertEqual(400, context.exception.code)
        context.exception.close()


if __name__ == "__main__":
    unittest.main()
