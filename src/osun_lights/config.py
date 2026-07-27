from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


def default_data_dir() -> Path:
    override = os.environ.get("OSUN_LIGHTS_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / "Osun" / "lighting"
    return Path.home() / ".osun" / "lighting"


@dataclass(slots=True)
class AppConfig:
    mode: str = "simulator"
    home_assistant_url: str = "http://homeassistant.local:8123"
    allowed_entities: list[str] = field(default_factory=list)
    live_enabled: bool = False
    global_pause: bool = True
    autonomous_execution: bool = False

    def validate(self) -> None:
        if self.mode not in {"simulator", "home_assistant"}:
            raise ValueError("Unknown lighting mode")
        if any(not item.startswith("light.") for item in self.allowed_entities):
            raise ValueError("Only light.* entities may be allowlisted")
        self.allowed_entities = sorted(set(self.allowed_entities))
        if self.mode == "home_assistant" and self.autonomous_execution and not self.live_enabled:
            raise ValueError("Enable live light execution before autonomous execution")
        if self.mode == "home_assistant" and not self.live_enabled:
            self.global_pause = True


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_data_dir() / "config.json"

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            config = AppConfig(
                mode=str(raw.get("mode", "simulator")),
                home_assistant_url=str(raw.get("home_assistant_url", "http://homeassistant.local:8123")),
                allowed_entities=list(raw.get("allowed_entities", [])),
                live_enabled=bool(raw.get("live_enabled", False)),
                global_pause=bool(raw.get("global_pause", True)),
                autonomous_execution=bool(raw.get("autonomous_execution", False)),
            )
            config.validate()
            return config
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        config.validate()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(config), indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, self.path)
