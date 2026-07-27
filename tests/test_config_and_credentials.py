from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from osun_lights.config import AppConfig, ConfigStore
from osun_lights.credential_store import WindowsCredentialStore


class ConfigAndCredentialTests(unittest.TestCase):
    def test_config_never_contains_token_field(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            store = ConfigStore(path)
            store.save(
                AppConfig(
                    mode="home_assistant",
                    home_assistant_url="http://homeassistant.local:8123",
                    allowed_entities=["light.desk"],
                    live_enabled=True,
                    global_pause=True,
                    autonomous_execution=True,
                )
            )
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("token", text.casefold())
            loaded = store.load()
            self.assertEqual(["light.desk"], loaded.allowed_entities)
            self.assertTrue(loaded.global_pause)
            self.assertTrue(loaded.autonomous_execution)

    def test_autonomous_home_assistant_requires_live_execution(self) -> None:
        config = AppConfig(mode="home_assistant", autonomous_execution=True, live_enabled=False)
        with self.assertRaisesRegex(ValueError, "Enable live light execution"):
            config.validate()

    def test_autonomous_execution_defaults_off(self) -> None:
        self.assertFalse(AppConfig().autonomous_execution)

    @unittest.skipUnless(os.name == "nt", "DPAPI test requires Windows")
    def test_windows_dpapi_round_trip_and_ciphertext(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credential.bin"
            store = WindowsCredentialStore(path)
            token = "synthetic-not-a-real-token"
            store.save(token)
            self.assertNotIn(token.encode("utf-8"), path.read_bytes())
            self.assertEqual(token, store.load())
            store.delete()
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
