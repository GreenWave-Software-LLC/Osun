from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


DEVICE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
MEDIA_PLAYER_ENTITY = re.compile(r"^media_player\.[a-z0-9_]+$")
HEADPHONES_DEVICE_ID = "bluetooth-headphones"
APPLE_TV_DEVICE_ID = "living-room-apple-tv"


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
    device_id: str = HEADPHONES_DEVICE_ID
    name: str = "Headphones"
    kind: str = "windows_headphones"
    enabled: bool = True

    def validate(self) -> None:
        if not DEVICE_ID.fullmatch(self.device_id):
            raise ValueError("Music device IDs must use lowercase letters, numbers, hyphens, or underscores")
        self.name = " ".join(self.name.split())
        if not self.name or len(self.name) > 80:
            raise ValueError("Music devices require a short display name")
        if self.kind not in {"windows_app", "windows_headphones", "apple_tv", "browser", "companion"}:
            raise ValueError("Unknown music device kind")


def _default_devices() -> list[MusicDeviceConfig]:
    return [
        MusicDeviceConfig(
            device_id=HEADPHONES_DEVICE_ID,
            name="Headphones",
            kind="windows_headphones",
        ),
        MusicDeviceConfig(
            device_id=APPLE_TV_DEVICE_ID,
            name="Living Room Apple TV",
            kind="apple_tv",
        ),
    ]


def _is_legacy_pc_only(devices: list[MusicDeviceConfig]) -> bool:
    return (
        len(devices) == 1
        and devices[0].device_id == "agent-box-windows"
        and devices[0].kind == "windows_app"
    )


@dataclass(slots=True)
class MusicConfig:
    mode: str = "windows_app"
    enabled: bool = True
    autonomous_execution: bool = False
    media_center_entity_id: str = ""
    devices: list[MusicDeviceConfig] = field(default_factory=_default_devices)

    def validate(self) -> None:
        if self.mode not in {"simulator", "windows_app", "musickit"}:
            raise ValueError("Unknown music mode")
        self.media_center_entity_id = self.media_center_entity_id.strip()
        if self.media_center_entity_id and not MEDIA_PLAYER_ENTITY.fullmatch(self.media_center_entity_id):
            raise ValueError("Media center must be a Home Assistant media_player entity")
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
                    kind=str(item.get("kind", "windows_app")),
                    enabled=bool(item.get("enabled", True)),
                )
                for item in raw.get("devices", [])
                if isinstance(item, dict)
            ]
            config = MusicConfig(
                mode=str(raw.get("mode", "windows_app")),
                enabled=bool(raw.get("enabled", True)),
                autonomous_execution=bool(raw.get("autonomous_execution", False)),
                media_center_entity_id=str(raw.get("media_center_entity_id", "")),
                devices=_default_devices() if not devices or _is_legacy_pc_only(devices) else devices,
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
