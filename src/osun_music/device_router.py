from __future__ import annotations

from dataclasses import dataclass


RECENT_PLAYBACK_SECONDS = 5 * 60


@dataclass(frozen=True, slots=True)
class DeviceDecision:
    device_id: str | None
    reason: str


def choose_playback_device(
    devices: list[dict[str, object]],
    *,
    now: float,
    requested_device_id: str | None = None,
) -> DeviceDecision:
    available = [device for device in devices if bool(device.get("enabled", True))]
    if requested_device_id:
        if any(device.get("device_id") == requested_device_id for device in available):
            return DeviceDecision(requested_device_id, "owner_selected")
        return DeviceDecision(None, "requested_device_unavailable")

    recent = [
        device
        for device in available
        if isinstance(device.get("last_played_at"), (int, float))
        and 0 <= now - float(device["last_played_at"]) <= RECENT_PLAYBACK_SECONDS
    ]
    if not recent:
        return DeviceDecision(None, "ask_owner")
    selected = max(recent, key=lambda device: float(device["last_played_at"]))
    return DeviceDecision(str(selected["device_id"]), "recent_playback")
