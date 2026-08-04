from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from osun_music.catalog import AppleCatalogSearch
from osun_music.config import MusicConfigStore
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


class WindowsMusicAdapterTests(unittest.TestCase):
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
            )
            music_request = controller.message("play Blue in Green on This PC")["request"]
            result = controller.execute(music_request["request_id"])
            self.assertEqual("verified", result["state"])
            self.assertEqual([("play", "Blue in Green")], adapter.calls)
            self.assertTrue(controller.status()["devices"][0]["recent"])

    def test_failed_windows_result_is_not_marked_recent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            adapter = FakeWindowsAdapter(WindowsMusicResult(success=False, error="Sign in once."))
            controller = MusicController(
                MusicConfigStore(Path(temporary) / "music.json"),
                MemoryCredentialStore(),  # type: ignore[arg-type]
                adapter,  # type: ignore[arg-type]
            )
            music_request = controller.message("play music on This PC")["request"]
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
            )
            probe = controller.test_windows_app()
            self.assertTrue(probe["installed"])
            self.assertEqual("windows_media_session", probe["evidence"])


if __name__ == "__main__":
    unittest.main()
