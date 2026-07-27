from __future__ import annotations

import unittest
from pathlib import Path

from scripts.security_gate import inspect_text, run


class SecurityGateTests(unittest.TestCase):
    def test_detects_private_key_material(self) -> None:
        marker = "-----BEGIN " + "RSA PRIVATE KEY-----"
        findings = inspect_text(Path("example.txt"), marker)
        self.assertTrue(any("private key" in finding for finding in findings))

    def test_rejects_mutable_action_reference(self) -> None:
        workflow = "- uses: actions/" + "checkout@v6\n"
        findings = inspect_text(Path(".github/workflows/example.yml"), workflow)
        self.assertTrue(any("not pinned" in finding for finding in findings))

    def test_current_repository_passes_security_invariants(self) -> None:
        self.assertEqual([], run())


if __name__ == "__main__":
    unittest.main()
