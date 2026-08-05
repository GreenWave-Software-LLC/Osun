from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from threading import RLock
from typing import Any


class WindowsBluetoothHeadphoneDetector:
    """Content-minimized, cached detection of connected Bluetooth audio endpoints."""

    def __init__(
        self,
        script_path: Path | None = None,
        *,
        cache_seconds: float = 5.0,
    ) -> None:
        self.script_path = script_path or Path(__file__).with_name("windows_bluetooth_audio.ps1")
        self.cache_seconds = cache_seconds
        self._cached_at = float("-inf")
        self._cached: dict[str, Any] = {"connected": False, "names": [], "evidence": ""}
        self._lock = RLock()

    @staticmethod
    def _powershell_path() -> Path:
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        return system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"

    def status(self) -> dict[str, Any]:
        with self._lock:
            now = time.monotonic()
            if now - self._cached_at <= self.cache_seconds:
                return {**self._cached, "names": list(self._cached.get("names", []))}
            self._cached = self._probe()
            self._cached_at = time.monotonic()
            return {**self._cached, "names": list(self._cached.get("names", []))}

    def _probe(self) -> dict[str, Any]:
        powershell = self._powershell_path()
        if os.name != "nt" or not powershell.is_file() or not self.script_path.is_file():
            return {"connected": False, "names": [], "evidence": ""}
        try:
            completed = subprocess.run(
                [
                    str(powershell),
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(self.script_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=6,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired):
            return {"connected": False, "names": [], "evidence": ""}
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        try:
            payload = json.loads(lines[-1]) if lines else {}
        except json.JSONDecodeError:
            payload = {}
        if completed.returncode != 0 or not isinstance(payload, dict) or payload.get("success") is not True:
            return {"connected": False, "names": [], "evidence": ""}
        raw_names = payload.get("names") if isinstance(payload.get("names"), list) else []
        names = [" ".join(str(name).split())[:80] for name in raw_names[:8] if str(name).strip()]
        evidence = str(payload.get("evidence", ""))
        if evidence not in {
            "windows_present_bluetooth_audio_endpoint",
            "windows_active_headphone_audio_output",
        }:
            evidence = ""
        return {
            "connected": payload.get("connected") is True and bool(names),
            "names": names,
            "evidence": evidence if names else "",
        }
