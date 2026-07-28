from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


SEARCH_ENDPOINT = "https://itunes.apple.com/search"
MAX_RESPONSE_BYTES = 1_000_000
ALLOWED_TRACK_HOSTS = {"itunes.apple.com", "music.apple.com"}


@dataclass(frozen=True, slots=True)
class CatalogTrack:
    title: str
    artist: str
    album: str
    url: str

    @property
    def display_name(self) -> str:
        return f"{self.title} by {self.artist}" if self.artist else self.title


def _normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _validated_track_url(value: object) -> str | None:
    if not isinstance(value, str) or len(value) > 2_048:
        return None
    parsed = urlparse(value)
    try:
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_TRACK_HOSTS
        or parsed.username
        or parsed.password
        or port not in {None, 443}
    ):
        return None
    return value


class AppleCatalogSearch:
    """Small, bounded client for Apple's public iTunes Search API."""

    def __init__(self, opener: Callable[..., Any] = urlopen) -> None:
        self._opener = opener

    def find_song(self, query: str) -> CatalogTrack:
        query = " ".join(query.split())
        if not query or len(query) > 200:
            raise ValueError("Music searches must be between 1 and 200 characters")
        request_url = f"{SEARCH_ENDPOINT}?{urlencode({'term': query, 'country': 'US', 'media': 'music', 'entity': 'song', 'limit': 10})}"
        request = Request(request_url, headers={"Accept": "application/json", "User-Agent": "Osun/0.4"})
        try:
            with self._opener(request, timeout=8) as response:
                final_url = urlparse(response.geturl())
                if final_url.scheme != "https" or final_url.hostname != "itunes.apple.com":
                    raise RuntimeError("Apple catalog search redirected to an unexpected service")
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except (OSError, TimeoutError) as exc:
            raise RuntimeError("Apple's public music catalog is unavailable right now") from exc
        if len(raw) > MAX_RESPONSE_BYTES:
            raise RuntimeError("Apple catalog response exceeded Osun's safety limit")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Apple returned an unreadable catalog response") from exc
        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(results, list):
            raise RuntimeError("Apple returned an invalid catalog response")

        tracks: list[CatalogTrack] = []
        for item in results:
            if not isinstance(item, dict) or item.get("kind") != "song":
                continue
            url = _validated_track_url(item.get("trackViewUrl"))
            title = " ".join(str(item.get("trackName", "")).split())[:200]
            artist = " ".join(str(item.get("artistName", "")).split())[:200]
            album = " ".join(str(item.get("collectionName", "")).split())[:200]
            if url and title:
                tracks.append(CatalogTrack(title=title, artist=artist, album=album, url=url))
        if not tracks:
            raise ValueError(f"Apple Music could not find {query}.")
        return max(
            enumerate(tracks),
            key=lambda pair: (
                self._score(query, pair[1])[0] - pair[0] * 15,
                self._score(query, pair[1])[1],
            ),
        )[1]

    @staticmethod
    def _score(query: str, track: CatalogTrack) -> tuple[int, int]:
        wanted = _normalized(query)
        title = _normalized(track.title)
        artist = _normalized(track.artist)
        album = _normalized(track.album)
        wanted_tokens = set(wanted.split())
        combined_tokens = set(f"{title} {artist} {album}".split())
        overlap = len(wanted_tokens & combined_tokens)
        score = overlap * 10
        if title == wanted:
            score += 100
        if artist == wanted or album == wanted:
            score += 60
        if wanted and wanted in f"{title} {artist} {album}":
            score += 25
        return score, -abs(len(title) - len(wanted))
