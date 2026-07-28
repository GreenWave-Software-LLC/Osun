from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from .catalog import AppleCatalogSearch


@dataclass(frozen=True, slots=True)
class WindowsMusicResult:
    success: bool
    verified: bool = False
    playback_active: bool | None = None
    now_playing: str = ""
    evidence: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Bridge(Protocol):
    def available(self) -> bool: ...

    def run(
        self,
        action: str,
        *,
        media_url: str = "",
        query: str = "",
        expected_title: str = "",
        expected_artist: str = "",
    ) -> dict[str, Any]: ...


class PowerShellAppleMusicBridge:
    """Invokes the bundled, closed-command Windows Apple Music bridge."""

    ACTIONS = {"probe", "play-url", "pause", "resume", "next", "previous"}

    def __init__(self, script_path: Path | None = None) -> None:
        self.script_path = script_path or Path(__file__).with_name("windows_apple_music.ps1")

    @staticmethod
    def _powershell_path() -> Path:
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        return system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"

    def available(self) -> bool:
        return os.name == "nt" and self.script_path.is_file() and self._powershell_path().is_file()

    def run(
        self,
        action: str,
        *,
        media_url: str = "",
        query: str = "",
        expected_title: str = "",
        expected_artist: str = "",
    ) -> dict[str, Any]:
        if action not in self.ACTIONS:
            raise ValueError("Unknown Windows Apple Music bridge action")
        if not self.available():
            return {"success": False, "error": "The Apple Music app is not installed for this Windows account."}
        command = [
            str(self._powershell_path()),
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(self.script_path),
            "-Action",
            action,
        ]
        for name, value in (
            ("MediaUrl", media_url),
            ("Query", query),
            ("ExpectedTitle", expected_title),
            ("ExpectedArtist", expected_artist),
        ):
            if value:
                command.extend((f"-{name}", value))
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                creationflags=creation_flags,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"success": False, "error": "Windows did not complete the Apple Music control request."}
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        try:
            payload = json.loads(lines[-1]) if lines else {}
        except json.JSONDecodeError:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        if completed.returncode != 0 or not payload:
            return {
                "success": False,
                "error": "The Windows Apple Music bridge failed safely without controlling another media app.",
            }
        return payload


class WindowsAppleMusicAdapter:
    def __init__(
        self,
        catalog: AppleCatalogSearch | None = None,
        bridge: Bridge | None = None,
    ) -> None:
        self.catalog = catalog or AppleCatalogSearch()
        self.bridge = bridge or PowerShellAppleMusicBridge()

    def available(self) -> bool:
        return self.bridge.available()

    def probe(self) -> dict[str, Any]:
        return self.bridge.run("probe")

    def execute(self, action: str, query: str = "") -> WindowsMusicResult:
        if action == "play":
            try:
                track = self.catalog.find_song(query or "music")
            except (ValueError, RuntimeError) as exc:
                return WindowsMusicResult(success=False, error=str(exc))
            payload = self.bridge.run(
                "play-url",
                media_url=track.url,
                query=query,
                expected_title=track.title,
                expected_artist=track.artist,
            )
            if payload.get("success") and not payload.get("now_playing"):
                payload["now_playing"] = track.display_name
        elif action in {"pause", "resume", "next", "previous"}:
            payload = self.bridge.run(action)
        else:
            return WindowsMusicResult(success=False, error="Unsupported Apple Music command")
        return WindowsMusicResult(
            success=payload.get("success") is True,
            verified=payload.get("verified") is True,
            playback_active=(
                payload.get("playback_active") if isinstance(payload.get("playback_active"), bool) else None
            ),
            now_playing=" ".join(str(payload.get("now_playing", "")).split())[:200],
            evidence=" ".join(str(payload.get("evidence", "")).split())[:80],
            error=" ".join(str(payload.get("error", "")).split())[:240],
        )
