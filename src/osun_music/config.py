from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


DEVICE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def default_data_dir() -> Path:
    override = os.environ.get("OSUN_MUSIC_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / "Osun" / "music"
    return Path.home() / ".osun" / "music"


@dataclass(slots=True)
class MusicDeviceConfig:
    device_id: str = "agent-box-browser"
    name: str = "This PC"
    kind: str = "browser"
    enabled: bool = True

    def validate(self) -> None:
        if not DEVICE_ID.fullmatch(self.device_id):
            raise ValueError("Music device IDs must use lowercase letters, numbers, hyphens, or underscores")
        self.name = " ".join(self.name.split())
        if not self.name or len(self.name) > 80:
            raise ValueError("Music devices require a short display name")
        if self.kind not in {"browser", "companion"}:
            raise ValueError("Unknown music device kind")


def _default_devices() -> list[MusicDeviceConfig]:
    return [MusicDeviceConfig()]


@dataclass(slots=True)
class MusicConfig:
    mode: str = "simulator"
    enabled: bool = True
    autonomous_execution: bool = False
    devices: list[MusicDeviceConfig] = field(default_factory=_default_devices)

    def validate(self) -> None:
        if self.mode not in {"simulator", "musickit"}:
            raise ValueError("Unknown music mode")
        seen: set[str] = set()
        for device in self.devices:
            device.validate()
            if device.device_id in seen:
                raise ValueError("Music device IDs must be unique")
            seen.add(device.device_id)
        if not self.devices:
            raise ValueError("At least one music playback device is required")


class MusicConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_data_dir() / "config.json"

    def load(self) -> MusicConfig:
        if not self.path.exists():
            return MusicConfig()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            devices = [
                MusicDeviceConfig(
                    device_id=str(item.get("device_id", "")),
                    name=str(item.get("name", "")),
                    kind=str(item.get("kind", "browser")),
                    enabled=bool(item.get("enabled", True)),
                )
                for item in raw.get("devices", [])
                if isinstance(item, dict)
            ]
            config = MusicConfig(
                mode=str(raw.get("mode", "simulator")),
                enabled=bool(raw.get("enabled", True)),
                autonomous_execution=bool(raw.get("autonomous_execution", False)),
                devices=devices or _default_devices(),
            )
            config.validate()
            return config
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return MusicConfig()

    def save(self, config: MusicConfig) -> None:
        config.validate()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(config), indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, self.path)
