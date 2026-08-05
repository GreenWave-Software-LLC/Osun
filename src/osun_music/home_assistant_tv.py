from __future__ import annotations

import re
import time
from collections.abc import Callable
from typing import Any, Protocol
from urllib.parse import quote

from osun_lights.config import ConfigStore as LightingConfigStore
from osun_lights.credential_store import CredentialStoreError
from osun_lights.home_assistant import HomeAssistantClient, HomeAssistantError
from osun_lights.runtime import credential_store as lighting_credential_store

from .catalog import AppleCatalogSearch
from .windows_app import WindowsMusicResult


APPLE_TV_ENTITY_ID = "media_player.living_room_apple_tv"
APPLE_TV_FRIENDLY_NAME = "Living Room Apple TV"
MEDIA_PLAYER_ENTITY = re.compile(r"^media_player\.[a-z0-9_]+$")


class HomeAssistantRequester(Protocol):
    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any: ...


class HomeAssistantAppleTVAdapter:
    """Allowlisted Apple TV playback through Osun's existing local Home Assistant trust path."""

    def __init__(
        self,
        catalog: AppleCatalogSearch | None = None,
        client_provider: Callable[[], HomeAssistantRequester] | None = None,
        *,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.catalog = catalog or AppleCatalogSearch()
        self._client_provider = client_provider
        self._sleep = sleep
        self._clock = clock

    def available(self) -> bool:
        if self._client_provider is not None:
            return True
        try:
            return lighting_credential_store().load() is not None
        except (OSError, CredentialStoreError):
            return False

    def probe(self) -> dict[str, Any]:
        try:
            client = self._client()
            entity_id = self._resolve_entity(client)
            state = self._state(client, entity_id)
            return {
                "success": True,
                "entity_id": entity_id,
                "state": " ".join(str(state.get("state", "unknown")).split())[:40],
                "error": "",
            }
        except (CredentialStoreError, HomeAssistantError, OSError, ValueError) as exc:
            message = " ".join(str(exc).split())[:240]
            return {
                "success": False,
                "entity_id": "",
                "state": "",
                "error": message or "Living Room Apple TV is unavailable in Home Assistant.",
            }

    def execute(self, action: str, query: str = "") -> WindowsMusicResult:
        try:
            client = self._client()
            entity_id = self._resolve_entity(client)
            before = self._state(client, entity_id)
            expected_title = ""
            if action == "play":
                track = self.catalog.find_song(query or "music")
                expected_title = track.title
                service = "play_media"
                payload = {
                    "entity_id": entity_id,
                    "media_content_type": "url",
                    "media_content_id": track.url,
                }
            else:
                service = {
                    "pause": "media_pause",
                    "resume": "media_play",
                    "next": "media_next_track",
                    "previous": "media_previous_track",
                }.get(action, "")
                if not service:
                    return WindowsMusicResult(success=False, error="Unsupported Apple TV music command")
                payload = {"entity_id": entity_id}
            client._request("POST", f"/api/services/media_player/{service}", payload)
            verified_state = self._wait_for_result(
                client,
                entity_id,
                action=action,
                expected_title=expected_title,
                previous_title=self._now_playing(before),
            )
            if verified_state is None:
                return WindowsMusicResult(
                    success=True,
                    verified=False,
                    playback_active=None,
                    now_playing=expected_title,
                    evidence="home_assistant_apple_tv_command",
                )
            state_name = str(verified_state.get("state", ""))
            return WindowsMusicResult(
                success=True,
                verified=True,
                playback_active=state_name == "playing",
                now_playing=self._now_playing(verified_state) or expected_title,
                evidence="home_assistant_apple_tv_readback",
            )
        except (CredentialStoreError, HomeAssistantError, OSError, RuntimeError, ValueError) as exc:
            message = str(exc)
            if not message or len(message) > 240:
                message = "Living Room Apple TV playback failed safely."
            return WindowsMusicResult(success=False, error=message)

    def _client(self) -> HomeAssistantRequester:
        if self._client_provider is not None:
            return self._client_provider()
        config = LightingConfigStore().load()
        token = lighting_credential_store().load()
        if not token:
            raise ValueError("Connect Home Assistant in Lighting settings before using Living Room Apple TV")
        return HomeAssistantClient(config.home_assistant_url, token, set())

    @staticmethod
    def _resolve_entity(client: HomeAssistantRequester) -> str:
        states = client._request("GET", "/api/states")
        if not isinstance(states, list):
            raise HomeAssistantError("Home Assistant returned an invalid media-player list")
        exact_id = None
        exact_name: list[str] = []
        for item in states:
            if not isinstance(item, dict):
                continue
            entity_id = item.get("entity_id")
            if not isinstance(entity_id, str) or not MEDIA_PLAYER_ENTITY.fullmatch(entity_id):
                continue
            attributes = item.get("attributes") if isinstance(item.get("attributes"), dict) else {}
            friendly_name = " ".join(str(attributes.get("friendly_name", "")).split())
            if entity_id == APPLE_TV_ENTITY_ID:
                exact_id = entity_id
            if friendly_name.casefold() == APPLE_TV_FRIENDLY_NAME.casefold():
                exact_name.append(entity_id)
        if exact_id:
            return exact_id
        if len(set(exact_name)) == 1:
            return exact_name[0]
        raise ValueError("Home Assistant could not find exactly one Living Room Apple TV media player")

    @staticmethod
    def _state(client: HomeAssistantRequester, entity_id: str) -> dict[str, Any]:
        state = client._request("GET", f"/api/states/{quote(entity_id, safe='._')}")
        if not isinstance(state, dict):
            raise HomeAssistantError("Home Assistant returned an invalid Apple TV state")
        return state

    def _wait_for_result(
        self,
        client: HomeAssistantRequester,
        entity_id: str,
        *,
        action: str,
        expected_title: str,
        previous_title: str,
    ) -> dict[str, Any] | None:
        deadline = self._clock() + 12.0
        while self._clock() < deadline:
            state = self._state(client, entity_id)
            state_name = str(state.get("state", ""))
            title = self._now_playing(state)
            if action == "pause" and state_name in {"paused", "idle", "standby"}:
                return state
            if action in {"play", "resume"} and state_name == "playing":
                if not expected_title or not title or self._title_matches(expected_title, title):
                    return state
            if action in {"next", "previous"} and title and title != previous_title:
                return state
            self._sleep(0.4)
        return None

    @staticmethod
    def _now_playing(state: dict[str, Any]) -> str:
        attributes = state.get("attributes") if isinstance(state.get("attributes"), dict) else {}
        title = " ".join(str(attributes.get("media_title", "")).split())[:120]
        artist = " ".join(str(attributes.get("media_artist", "")).split())[:80]
        return f"{title} by {artist}" if title and artist else title

    @staticmethod
    def _title_matches(expected: str, observed: str) -> bool:
        expected_folded = " ".join(expected.casefold().split())
        observed_folded = " ".join(observed.casefold().split())
        return expected_folded in observed_folded or observed_folded in expected_folded
