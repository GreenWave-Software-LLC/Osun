from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MusicIntent:
    action: str
    query: str | None = None
    requested_device_id: str | None = None


class MusicIntentParser:
    _CONTROL_PATTERNS = (
        ("pause", re.compile(r"^\s*(?:pause|stop)(?:\s+(?:the\s+)?music)?\s*$", re.IGNORECASE)),
        ("resume", re.compile(r"^\s*(?:resume|continue)(?:\s+(?:the\s+)?music)?\s*$", re.IGNORECASE)),
        ("next", re.compile(r"^\s*(?:next(?:\s+(?:song|track))?|skip(?:\s+(?:this\s+)?(?:song|track))?)\s*$", re.IGNORECASE)),
        ("previous", re.compile(r"^\s*(?:previous|last)(?:\s+(?:song|track))?\s*$|^\s*go\s+back\s*$", re.IGNORECASE)),
    )
    _PLAY_PREFIX = re.compile(
        r"^\s*(?:please\s+)?(?:play|put on|listen to)\s+(?:some\s+)?(?:apple\s+music\s+)?",
        re.IGNORECASE,
    )

    def parse(self, text: str, devices: list[dict[str, object]]) -> MusicIntent | None:
        normalized = " ".join(text.split())
        requested_device = self._requested_device(normalized, devices)
        control_text = normalized
        if requested_device:
            device = next(device for device in devices if device.get("device_id") == requested_device)
            control_text = re.sub(
                rf"\s+on\s+{re.escape(str(device.get('name', '')))}\s*$",
                "",
                normalized,
                flags=re.IGNORECASE,
            )
        for action, pattern in self._CONTROL_PATTERNS:
            if pattern.search(control_text):
                return MusicIntent(action=action, requested_device_id=requested_device)
        if not self._PLAY_PREFIX.match(normalized):
            return None
        query = self._PLAY_PREFIX.sub("", normalized, count=1).strip(" .")
        requested = requested_device
        if requested:
            device = next(device for device in devices if device.get("device_id") == requested)
            query = re.sub(
                rf"\s+on\s+{re.escape(str(device.get('name', '')))}\s*$",
                "",
                query,
                flags=re.IGNORECASE,
            ).strip(" .")
        return MusicIntent(action="play", query=query or "music", requested_device_id=requested)

    @staticmethod
    def _requested_device(text: str, devices: list[dict[str, object]]) -> str | None:
        folded = text.casefold()
        for device in devices:
            name = str(device.get("name", "")).strip()
            if name and re.search(rf"\bon\s+{re.escape(name.casefold())}\s*$", folded):
                return str(device.get("device_id"))
        return None
