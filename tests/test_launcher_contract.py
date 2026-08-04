from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LauncherContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = (ROOT / "run_osun.ps1").read_text(encoding="utf-8")
        cls.gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    def test_machine_local_model_store_is_ignored_and_validated(self) -> None:
        self.assertIn(".osun-local/", self.gitignore)
        self.assertIn(".osun-local\\ollama-models.path", self.launcher)
        self.assertIn("[System.IO.Path]::IsPathRooted", self.launcher)
        self.assertIn("$env:OLLAMA_MODELS = $configuredModelStore", self.launcher)

    def test_empty_reboot_runtime_is_restarted_against_local_store(self) -> None:
        self.assertIn("/api/tags", self.launcher)
        self.assertIn("$expectedModel -notin $availableModels", self.launcher)
        self.assertIn("Get-Process ollama", self.launcher)
        self.assertIn("Stop-Process -Force", self.launcher)
        self.assertIn("-ArgumentList 'serve' -WindowStyle Hidden", self.launcher)


if __name__ == "__main__":
    unittest.main()
