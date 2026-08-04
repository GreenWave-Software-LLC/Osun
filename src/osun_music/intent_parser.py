from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MusicIntent:
    action: str
    query: str | None = None
    requested_device_id: str | None = None


class MusicIntentParser:
    _WINDOWS_DEVICE_ALIASES = (
        "this pc",
        "my pc",
        "pc",
        "this computer",
        "my computer",
        "computer",
        "agent box",
        "this machine",
        "my machine",
    )
    _CONTROL_PATTERNS = (
        ("pause", re.compile(r"^\s*(?:pause|stop)(?:\s+(?:the\s+)?music)?\s*$", re.IGNORECASE)),
        ("resume", re.compile(r"^\s*(?:resume|continue)(?:\s+(?:the\s+)?music)?\s*$", re.IGNORECASE)),
        ("next", re.compile(r"^\s*(?:next(?:\s+(?:song|track))?|skip(?:\s+(?:this\s+)?(?:song|track))?)\s*$", re.IGNORECASE)),
        ("previous", re.compile(r"^\s*(?:previous|last)(?:\s+(?:song|track))?\s*$|^\s*go\s+back\s*$", re.IGNORECASE)),
    )
    _PLAY_PREFIX = re.compile(
        r"^\s*(?:please\s+)?(?:play|put on|listen to)(?=\s|$)\s*(?:some\s+)?(?:apple\s+music(?:\s+|$))?",
        re.IGNORECASE,
    )
    _GENERIC_PLAY_QUERIES = {"anything", "something", "whatever", "any song", "some music"}

    def parse(self, text: str, devices: list[dict[str, object]]) -> MusicIntent | None:
        normalized = " ".join(text.split())
        requested_device = self._requested_device(normalized, devices)
        control_text = normalized
        if requested_device:
            control_text = self._strip_device_suffix(normalized, requested_device, devices)
        for action, pattern in self._CONTROL_PATTERNS:
            if pattern.search(control_text):
                return MusicIntent(action=action, requested_device_id=requested_device)
        if not self._PLAY_PREFIX.match(normalized):
            return None
        query = self._PLAY_PREFIX.sub("", normalized, count=1).strip(" .")
        requested = requested_device
        if requested:
            query = self._strip_device_suffix(query, requested, devices).strip(" .")
        return MusicIntent(action="play", query=query or "music", requested_device_id=requested)

    def parse_bare_play(self, text: str, devices: list[dict[str, object]]) -> MusicIntent | None:
        """Parse a short query only after the model has explicitly selected the Music agent."""
        normalized = " ".join(text.split()).strip(" .")
        if not normalized or self.device_choice(normalized, devices):
            return None
        requested_device = self._requested_device(normalized, devices)
        query = (
            self._strip_device_suffix(normalized, requested_device, devices).strip(" .")
            if requested_device
            else normalized
        )
        if query.casefold() in self._GENERIC_PLAY_QUERIES:
            query = "music"
        else:
            query = re.sub(r"^(?:a|an|some)\s+", "", query, flags=re.IGNORECASE)
            query = re.sub(r"\s+(?:song|track|music)\s*$", "", query, flags=re.IGNORECASE).strip(" .")
        if not query or len(query) > 200:
            return None
        return MusicIntent(action="play", query=query, requested_device_id=requested_device)

    def device_choice(self, text: str, devices: list[dict[str, object]]) -> str | None:
        """Resolve an entire utterance as a device choice, never as an arbitrary suffix."""
        folded = " ".join(text.casefold().split()).strip(" .")
        matches: set[str] = set()
        for device in devices:
            device_id = str(device.get("device_id", ""))
            for alias in self._device_aliases(device):
                if re.fullmatch(
                    rf"(?:please\s+)?(?:(?:use|on|using)\s+|play\s+(?:it\s+)?on\s+)?(?:the\s+)?{re.escape(alias)}(?:\s+please)?",
                    folded,
                ):
                    matches.add(device_id)
        return next(iter(matches)) if len(matches) == 1 else None

    @classmethod
    def _requested_device(cls, text: str, devices: list[dict[str, object]]) -> str | None:
        folded = " ".join(text.casefold().split()).strip(" .")
        matches: set[str] = set()
        for device in devices:
            device_id = str(device.get("device_id", ""))
            for alias in cls._device_aliases(device):
                if re.search(rf"\b(?:on|using)\s+(?:the\s+)?{re.escape(alias)}\s*$", folded):
                    matches.add(device_id)
        return next(iter(matches)) if len(matches) == 1 else None

    @classmethod
    def _strip_device_suffix(
        cls,
        text: str,
        device_id: str,
        devices: list[dict[str, object]],
    ) -> str:
        device = next((item for item in devices if str(item.get("device_id")) == device_id), None)
        if not device:
            return text
        result = text
        for alias in sorted(cls._device_aliases(device), key=len, reverse=True):
            stripped = re.sub(
                rf"\s+(?:on|using)\s+(?:the\s+)?{re.escape(alias)}\s*$",
                "",
                result,
                flags=re.IGNORECASE,
            )
            if stripped != result:
                return stripped
        return result

    @classmethod
    def _device_aliases(cls, device: dict[str, object]) -> tuple[str, ...]:
        aliases = {" ".join(str(device.get("name", "")).casefold().split())}
        if device.get("kind") == "windows_app" or device.get("device_id") == "agent-box-windows":
            aliases.update(cls._WINDOWS_DEVICE_ALIASES)
        aliases.discard("")
        return tuple(sorted(aliases, key=len, reverse=True))
