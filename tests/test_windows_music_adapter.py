from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from osun_music.catalog import AppleCatalogSearch, CatalogTrack
from osun_music.config import MusicConfigStore
from osun_music.home_assistant_tv import HomeAssistantAppleTVAdapter
from osun_music.runtime import MusicController
from osun_music.windows_app import WindowsAppleMusicAdapter, WindowsMusicResult


class FakeResponse:
    def __init__(self, payload: dict[str, object], url: str = "https://itunes.apple.com/search") -> None:
        self.payload = payload
        self.url = url

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def geturl(self) -> str:
        return self.url

    def read(self, _limit: int) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class MemoryCredentialStore:
    def save(self, _value: str) -> None:
        return None

    def load(self) -> str | None:
        return None

    def delete(self) -> None:
        return None


class FakeBridge:
    def __init__(self, payload: dict[str, object] | None = None) -> None:
        self.payload = payload or {
            "success": True,
            "verified": True,
            "playback_active": True,
            "now_playing": "Blue in Green by Miles Davis",
            "evidence": "windows_media_session",
        }
        self.calls: list[tuple[str, dict[str, str]]] = []

    def available(self) -> bool:
        return True

    def run(self, action: str, **kwargs: str) -> dict[str, object]:
        self.calls.append((action, kwargs))
        return dict(self.payload)


class FakeWindowsAdapter:
    def __init__(self, outcome: WindowsMusicResult) -> None:
        self.outcome = outcome
        self.calls: list[tuple[str, str]] = []

    def available(self) -> bool:
        return True

    def execute(self, action: str, query: str = "") -> WindowsMusicResult:
        self.calls.append((action, query))
        return self.outcome

    def probe(self) -> dict[str, object]:
        return {
            "success": True,
            "installed": True,
            "running": True,
            "session_available": True,
            "automation_available": True,
            "playback_active": True,
            "now_playing": "Blue in Green by Miles Davis",
            "evidence": "windows_media_session",
        }


class FakeHeadphoneDetector:
    def status(self) -> dict[str, object]:
        return {"connected": True, "names": ["Test Headphones"], "evidence": "test"}


class FakeAppleTVAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def available(self) -> bool:
        return True

    def execute(self, action: str, query: str = "") -> WindowsMusicResult:
        self.calls.append((action, query))
        return WindowsMusicResult(success=True, verified=True, now_playing=query)


class FakeCatalog:
    def find_song(self, query: str) -> CatalogTrack:
        return CatalogTrack(
            title="Blue in Green",
            artist="Miles Davis",
            album="Kind of Blue",
            url="https://music.apple.com/us/album/kind-of-blue/3?i=4",
        )


class FakeHomeAssistantClient:
    def __init__(self) -> None:
        self.state = {
            "entity_id": "media_player.living_room_apple_tv",
            "state": "idle",
            "attributes": {"friendly_name": "Living Room Apple TV"},
        }
        self.calls: list[tuple[str, str, dict[str, object] | None]] = []

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> object:
        self.calls.append((method, path, payload))
        if method == "GET" and path == "/api/states":
            return [dict(self.state)]
        if method == "POST" and path.endswith("/play_media"):
            self.state = {
                **self.state,
                "state": "playing",
                "attributes": {
                    "friendly_name": "Living Room Apple TV",
                    "media_title": "Blue in Green",
                    "media_artist": "Miles Davis",
                },
            }
            return []
        if method == "GET" and path == f"/api/states/{self.state['entity_id']}":
            return dict(self.state)
        return []


class MissingAppleTVClient(FakeHomeAssistantClient):
    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> object:
        self.calls.append((method, path, payload))
        if method == "GET" and path == "/api/states":
            return [
                {
                    "entity_id": "media_player.bedroom_tv",
                    "state": "idle",
                    "attributes": {"friendly_name": "Bedroom TV"},
                }
            ]
        return []


class WindowsMusicAdapterTests(unittest.TestCase):
    def test_home_assistant_tv_adapter_sends_allowlisted_apple_music_deep_link(self) -> None:
        client = FakeHomeAssistantClient()
        adapter = HomeAssistantAppleTVAdapter(
            FakeCatalog(),  # type: ignore[arg-type]
            lambda: client,
            sleep=lambda _seconds: None,
        )

        probe = adapter.probe()
        result = adapter.execute("play", "Blue in Green")

        self.assertTrue(probe["success"])
        self.assertEqual("media_player.living_room_apple_tv", probe["entity_id"])
        self.assertTrue(result.success)
        self.assertTrue(result.verified)
        self.assertEqual("Blue in Green by Miles Davis", result.now_playing)
        service_call = next(call for call in client.calls if call[0] == "POST")
        self.assertEqual("/api/services/media_player/play_media", service_call[1])
        self.assertEqual(
            {
                "entity_id": "media_player.living_room_apple_tv",
                "media_content_type": "url",
                "media_content_id": "https://music.apple.com/us/album/kind-of-blue/3?i=4",
            },
            service_call[2],
        )

    def test_home_assistant_tv_adapter_fails_closed_when_living_room_tv_is_missing(self) -> None:
        client = MissingAppleTVClient()
        adapter = HomeAssistantAppleTVAdapter(FakeCatalog(), lambda: client)  # type: ignore[arg-type]

        result = adapter.execute("play", "Blue in Green")

        self.assertFalse(result.success)
        self.assertIn("Choose a Home Assistant media center", result.error)
        self.assertFalse(any(call[0] == "POST" for call in client.calls))

    def test_home_assistant_tv_adapter_targets_only_configured_media_center(self) -> None:
        client = FakeHomeAssistantClient()
        client.state = {
            "entity_id": "media_player.den_apple_tv",
            "state": "idle",
            "attributes": {"friendly_name": "My Apple TV"},
        }
        adapter = HomeAssistantAppleTVAdapter(
            FakeCatalog(),  # type: ignore[arg-type]
            lambda: client,
            lambda: ("media_player.den_apple_tv", "My Apple TV"),
            sleep=lambda _seconds: None,
        )

        probe = adapter.probe()
        result = adapter.execute("play", "Blue in Green")

        self.assertTrue(probe["success"])
        self.assertEqual("media_player.den_apple_tv", probe["entity_id"])
        self.assertEqual("My Apple TV", probe["friendly_name"])
        service_call = next(call for call in client.calls if call[0] == "POST")
        self.assertEqual("media_player.den_apple_tv", service_call[2]["entity_id"])
        self.assertTrue(result.success)
        self.assertFalse(any(call[1] == "/api/states" for call in client.calls))

    def test_missing_configured_media_center_fails_without_service_call(self) -> None:
        client = MissingAppleTVClient()
        adapter = HomeAssistantAppleTVAdapter(
            FakeCatalog(),  # type: ignore[arg-type]
            lambda: client,
            lambda: ("media_player.missing_apple_tv", "Missing Apple TV"),
        )

        result = adapter.execute("play", "Blue in Green")

        self.assertFalse(result.success)
        self.assertFalse(any(call[0] == "POST" for call in client.calls))
        self.assertFalse(any(call[1] == "/api/states" for call in client.calls))

    def test_home_assistant_media_center_discovery_is_filtered_and_bounded(self) -> None:
        client = FakeHomeAssistantClient()
        original_request = client._request

        def request(method: str, path: str, payload: dict[str, object] | None = None) -> object:
            if method == "GET" and path == "/api/states":
                rows: list[dict[str, object]] = [
                    {
                        "entity_id": f"media_player.room_{index:03d}",
                        "state": "idle",
                        "attributes": {"friendly_name": f"Room {index:03d}"},
                    }
                    for index in range(105)
                ]
                rows.extend(
                    [
                        {"entity_id": "light.not_media", "state": "on", "attributes": {}},
                        {"entity_id": "media_player.INVALID", "state": "idle", "attributes": {}},
                    ]
                )
                return rows
            return original_request(method, path, payload)

        client._request = request  # type: ignore[method-assign]
        adapter = HomeAssistantAppleTVAdapter(FakeCatalog(), lambda: client)  # type: ignore[arg-type]

        discovered = adapter.discover_media_centers()

        self.assertEqual(100, len(discovered))
        self.assertTrue(all(item["entity_id"].startswith("media_player.room_") for item in discovered))

    def test_public_catalog_is_bounded_and_ranks_exact_song(self) -> None:
        requested: list[str] = []

        def open_search(request: object, *, timeout: int) -> FakeResponse:
            self.assertEqual(8, timeout)
            requested.append(request.full_url)  # type: ignore[attr-defined]
            return FakeResponse(
                {
                    "results": [
                        {
                            "kind": "song",
                            "trackName": "Something Else",
                            "artistName": "Artist",
                            "collectionName": "Album",
                            "trackViewUrl": "https://music.apple.com/us/album/something/1?i=2",
                        },
                        {
                            "kind": "song",
                            "trackName": "Blue in Green",
                            "artistName": "Miles Davis",
                            "collectionName": "Kind of Blue",
                            "trackViewUrl": "https://music.apple.com/us/album/kind-of-blue/3?i=4",
                        },
                    ]
                }
            )

        track = AppleCatalogSearch(open_search).find_song("Blue in Green Miles Davis")
        self.assertEqual("Blue in Green", track.title)
        params = parse_qs(urlparse(requested[0]).query)
        self.assertEqual(["song"], params["entity"])
        self.assertEqual(["10"], params["limit"])

    def test_catalog_rejects_non_apple_play_links(self) -> None:
        catalog = AppleCatalogSearch(
            lambda *_args, **_kwargs: FakeResponse(
                {
                    "results": [
                        {
                            "kind": "song",
                            "trackName": "Unsafe",
                            "artistName": "Unknown",
                            "trackViewUrl": "https://malicious.example/song",
                        }
                    ]
                }
            )
        )
        with self.assertRaisesRegex(ValueError, "could not find"):
            catalog.find_song("Unsafe")

    def test_play_resolves_exact_link_before_calling_closed_bridge_command(self) -> None:
        bridge = FakeBridge()
        catalog = AppleCatalogSearch(
            lambda *_args, **_kwargs: FakeResponse(
                {
                    "results": [
                        {
                            "kind": "song",
                            "trackName": "Blue in Green",
                            "artistName": "Miles Davis",
                            "collectionName": "Kind of Blue",
                            "trackViewUrl": "https://music.apple.com/us/album/kind-of-blue/3?i=4",
                        }
                    ]
                }
            )
        )
        adapter = WindowsAppleMusicAdapter(catalog, bridge)
        result = adapter.execute("play", "Blue in Green")
        self.assertTrue(result.success)
        self.assertEqual("play-url", bridge.calls[0][0])
        self.assertEqual("https://music.apple.com/us/album/kind-of-blue/3?i=4", bridge.calls[0][1]["media_url"])
        self.assertEqual("Blue in Green Miles Davis", bridge.calls[0][1]["query"])

    def test_controller_returns_server_side_verified_windows_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            adapter = FakeWindowsAdapter(
                WindowsMusicResult(
                    success=True,
                    verified=True,
                    playback_active=True,
                    now_playing="Blue in Green by Miles Davis",
                    evidence="windows_media_session",
                )
            )
            controller = MusicController(
                MusicConfigStore(Path(temporary) / "music.json"),
                MemoryCredentialStore(),  # type: ignore[arg-type]
                adapter,  # type: ignore[arg-type]
                headphone_detector=FakeHeadphoneDetector(),  # type: ignore[arg-type]
                apple_tv_adapter=FakeAppleTVAdapter(),  # type: ignore[arg-type]
            )
            music_request = controller.message("play Blue in Green on Headphones")["request"]
            result = controller.execute(music_request["request_id"])
            self.assertEqual("verified", result["state"])
            self.assertEqual([("play", "Blue in Green")], adapter.calls)
            self.assertTrue(controller.status()["devices"][0]["recent"])

    def test_controller_dispatches_tv_selection_to_apple_tv_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            windows = FakeWindowsAdapter(WindowsMusicResult(success=True))
            apple_tv = FakeAppleTVAdapter()
            controller = MusicController(
                MusicConfigStore(Path(temporary) / "music.json"),
                MemoryCredentialStore(),  # type: ignore[arg-type]
                windows,  # type: ignore[arg-type]
                headphone_detector=FakeHeadphoneDetector(),  # type: ignore[arg-type]
                apple_tv_adapter=apple_tv,  # type: ignore[arg-type]
            )

            music_request = controller.message("play Blue in Green on the TV")["request"]
            result = controller.execute(music_request["request_id"])

            self.assertEqual("verified", result["state"])
            self.assertEqual([("play", "Blue in Green")], apple_tv.calls)
            self.assertEqual([], windows.calls)

    def test_failed_windows_result_is_not_marked_recent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            adapter = FakeWindowsAdapter(WindowsMusicResult(success=False, error="Sign in once."))
            controller = MusicController(
                MusicConfigStore(Path(temporary) / "music.json"),
                MemoryCredentialStore(),  # type: ignore[arg-type]
                adapter,  # type: ignore[arg-type]
                headphone_detector=FakeHeadphoneDetector(),  # type: ignore[arg-type]
                apple_tv_adapter=FakeAppleTVAdapter(),  # type: ignore[arg-type]
            )
            music_request = controller.message("play music on Headphones")["request"]
            result = controller.execute(music_request["request_id"])
            self.assertEqual("failed", result["state"])
            self.assertFalse(controller.status()["devices"][0]["recent"])

    def test_probe_exposes_only_bounded_adapter_health(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            adapter = FakeWindowsAdapter(WindowsMusicResult(success=True))
            controller = MusicController(
                MusicConfigStore(Path(temporary) / "music.json"),
                MemoryCredentialStore(),  # type: ignore[arg-type]
                adapter,  # type: ignore[arg-type]
                headphone_detector=FakeHeadphoneDetector(),  # type: ignore[arg-type]
                apple_tv_adapter=FakeAppleTVAdapter(),  # type: ignore[arg-type]
            )
            probe = controller.test_windows_app()
            self.assertTrue(probe["installed"])
            self.assertEqual("windows_media_session", probe["evidence"])


if __name__ == "__main__":
    unittest.main()
