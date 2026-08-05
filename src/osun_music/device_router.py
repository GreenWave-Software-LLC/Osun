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
    action: str = "",
    headphones_or_tv: bool = False,
) -> DeviceDecision:
    available = [device for device in devices if bool(device.get("enabled", True))]
    if requested_device_id:
        if any(device.get("device_id") == requested_device_id for device in available):
            return DeviceDecision(requested_device_id, "owner_selected")
        requested = next(
            (device for device in devices if device.get("device_id") == requested_device_id),
            None,
        )
        television = next((device for device in available if device.get("kind") == "apple_tv"), None)
        if headphones_or_tv and requested and requested.get("kind") == "windows_headphones" and television:
            return DeviceDecision(str(television["device_id"]), "headphones_unavailable_default_tv")
        return DeviceDecision(None, "requested_device_unavailable")

    if headphones_or_tv:
        headphones = [device for device in available if device.get("kind") == "windows_headphones"]
        televisions = [device for device in available if device.get("kind") == "apple_tv"]
        if action == "play":
            if headphones and televisions:
                return DeviceDecision(None, "ask_headphones_or_tv")
            if televisions:
                return DeviceDecision(str(televisions[0]["device_id"]), "headphones_unavailable_default_tv")
            if headphones:
                return DeviceDecision(str(headphones[0]["device_id"]), "only_available_destination")

    recent = [
        device
        for device in available
        if isinstance(device.get("last_played_at"), (int, float))
        and 0 <= now - float(device["last_played_at"]) <= RECENT_PLAYBACK_SECONDS
    ]
    if recent:
        selected = max(recent, key=lambda device: float(device["last_played_at"]))
        return DeviceDecision(str(selected["device_id"]), "recent_playback")
    if headphones_or_tv:
        television = next((device for device in available if device.get("kind") == "apple_tv"), None)
        if television:
            return DeviceDecision(str(television["device_id"]), "default_tv")
    return DeviceDecision(None, "ask_owner")
