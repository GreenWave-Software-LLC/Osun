from __future__ import annotations

from dataclasses import replace
from threading import Lock

from .models import (
    ExecutionItem,
    ExecutionReport,
    LightAction,
    LightInfo,
    LightingProposal,
    ResultState,
)


DEFAULT_LIGHTS = (
    LightInfo("light.living_room_left", "Living Room Left", "off", ("rgb",)),
    LightInfo("light.living_room_right", "Living Room Right", "off", ("rgb",)),
    LightInfo("light.desk_lamp", "Desk Lamp", "off", ("color_temp",)),
    LightInfo("light.hall_light", "Hall Light", "off", ("brightness",)),
)


class SimulatedLightProvider:
    mode = "simulator"

    def __init__(self, lights: tuple[LightInfo, ...] = DEFAULT_LIGHTS) -> None:
        self._lights = {light.entity_id: light for light in lights}
        self._lock = Lock()

    def list_lights(self) -> tuple[LightInfo, ...]:
        with self._lock:
            return tuple(self._lights.values())

    def apply(self, proposal: LightingProposal) -> ExecutionReport:
        items: list[ExecutionItem] = []
        with self._lock:
            for change in proposal.changes:
                current = self._lights.get(change.entity_id)
                if current is None:
                    items.append(
                        ExecutionItem(change.entity_id, ResultState.DENIED, "Entity is not in the simulator allowlist")
                    )
                    continue
                if change.action == LightAction.TURN_OFF:
                    updated = replace(current, state="off", brightness=None, rgb_color=None)
                elif change.action == LightAction.TOGGLE:
                    updated = replace(current, state="off" if current.state == "on" else "on")
                else:
                    brightness = current.brightness
                    if change.brightness_pct is not None:
                        brightness = round(change.brightness_pct * 255 / 100)
                    updated = replace(current, state="on", brightness=brightness, rgb_color=change.rgb_color or current.rgb_color)
                self._lights[change.entity_id] = updated
                items.append(
                    ExecutionItem(change.entity_id, ResultState.VERIFIED, "Simulator state matches proposal", updated.state)
                )

        state = ResultState.VERIFIED if all(item.state == ResultState.VERIFIED for item in items) else ResultState.PARTIAL
        return ExecutionReport(proposal.proposal_id, state, tuple(items), self.mode)
