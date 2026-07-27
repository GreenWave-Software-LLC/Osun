from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class LightAction(StrEnum):
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    TOGGLE = "toggle"


class IntentKind(StrEnum):
    ACTION = "action"
    THEME = "theme"
    SUGGEST = "suggest"
    STATUS = "status"
    HELP = "help"
    UNKNOWN = "unknown"


class ResultState(StrEnum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    FAILED = "failed"
    DENIED = "denied"


COLOR_MODES = frozenset({"hs", "rgb", "rgbw", "rgbww", "xy"})


@dataclass(frozen=True, slots=True)
class LightInfo:
    entity_id: str
    friendly_name: str
    state: str = "off"
    supported_color_modes: tuple[str, ...] = ("rgb",)
    brightness: int | None = None
    rgb_color: tuple[int, int, int] | None = None

    def __post_init__(self) -> None:
        if not self.entity_id.startswith("light."):
            raise ValueError("Lighting entities must use the light.* domain")

    @property
    def supports_color(self) -> bool:
        return bool(COLOR_MODES.intersection(self.supported_color_modes))

    @property
    def supports_color_temperature(self) -> bool:
        return "color_temp" in self.supported_color_modes

    @property
    def supports_brightness(self) -> bool:
        return self.supported_color_modes != ("onoff",)


@dataclass(frozen=True, slots=True)
class LightChange:
    entity_id: str
    friendly_name: str
    action: LightAction
    brightness_pct: int | None = None
    rgb_color: tuple[int, int, int] | None = None
    color_temp_kelvin: int | None = None
    transition_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not self.entity_id.startswith("light."):
            raise ValueError("Lighting changes can target only light.* entities")
        if self.brightness_pct is not None and not 1 <= self.brightness_pct <= 100:
            raise ValueError("brightness_pct must be between 1 and 100")
        if self.rgb_color is not None:
            if len(self.rgb_color) != 3 or any(not 0 <= channel <= 255 for channel in self.rgb_color):
                raise ValueError("rgb_color channels must be between 0 and 255")
        if self.color_temp_kelvin is not None and not 2000 <= self.color_temp_kelvin <= 6500:
            raise ValueError("color_temp_kelvin must be between 2000 and 6500")
        if self.rgb_color is not None and self.color_temp_kelvin is not None:
            raise ValueError("A change may contain only one color representation")
        if not 0 <= self.transition_seconds <= 30:
            raise ValueError("transition_seconds must be between 0 and 30")
        if self.action != LightAction.TURN_ON and any(
            value is not None for value in (self.brightness_pct, self.rgb_color, self.color_temp_kelvin)
        ):
            raise ValueError("Only turn_on changes may include brightness or color")

    def preview(self) -> str:
        if self.action == LightAction.TURN_OFF:
            detail = "off"
        elif self.action == LightAction.TOGGLE:
            detail = "toggle"
        else:
            parts = ["on"]
            if self.brightness_pct is not None:
                parts.append(f"{self.brightness_pct}%")
            if self.rgb_color is not None:
                parts.append(f"RGB {self.rgb_color[0]}, {self.rgb_color[1]}, {self.rgb_color[2]}")
            if self.color_temp_kelvin is not None:
                parts.append(f"{self.color_temp_kelvin} K")
            detail = " · ".join(parts)
        if self.transition_seconds:
            detail += f" · {self.transition_seconds:g}s fade"
        return f"{self.friendly_name}: {detail}"


@dataclass(frozen=True, slots=True)
class LightingProposal:
    summary: str
    changes: tuple[LightChange, ...]
    theme_name: str | None = None
    rationale: str | None = None
    proposal_id: str = field(default_factory=lambda: f"lgt_{uuid4().hex}")
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    requires_confirmation: bool = True

    def __post_init__(self) -> None:
        if not self.changes:
            raise ValueError("A lighting proposal needs at least one change")
        ids = [change.entity_id for change in self.changes]
        if len(ids) != len(set(ids)):
            raise ValueError("A lighting proposal cannot target an entity twice")

    def preview_lines(self) -> tuple[str, ...]:
        return tuple(change.preview() for change in self.changes)


@dataclass(frozen=True, slots=True)
class ParsedIntent:
    kind: IntentKind
    action: LightAction | None = None
    brightness_pct: int | None = None
    rgb_color: tuple[int, int, int] | None = None
    color_temp_kelvin: int | None = None
    transition_seconds: float = 2.0
    theme_key: str | None = None
    generated_theme_text: str | None = None
    response: str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionItem:
    entity_id: str
    state: ResultState
    detail: str
    observed_state: str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    proposal_id: str
    state: ResultState
    items: tuple[ExecutionItem, ...]
    mode: str
    completed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def summary(self) -> str:
        if self.state == ResultState.DENIED and self.items:
            messages = {
                "global_pause": "execution is paused",
                "live_control_disabled": "live light execution is disabled",
                "proposal_missing_or_replaced": "the proposal is no longer current",
                "proposal_already_executed": "the proposal was already applied",
            }
            reason = messages.get(self.items[0].detail, self.items[0].detail.replace("_", " "))
            return f"Lighting change denied: {reason}."
        verified = sum(item.state == ResultState.VERIFIED for item in self.items)
        return f"{verified}/{len(self.items)} light changes verified ({self.state})."


def public_light_state(light: LightInfo) -> dict[str, Any]:
    """Return the minimum UI-safe state; credentials and raw provider data never enter it."""

    return {
        "entity_id": light.entity_id,
        "friendly_name": light.friendly_name,
        "state": light.state,
        "supported_color_modes": list(light.supported_color_modes),
        "brightness": light.brightness,
        "rgb_color": list(light.rgb_color) if light.rgb_color else None,
    }
