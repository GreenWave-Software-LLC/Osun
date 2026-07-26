from __future__ import annotations

import re

from .models import IntentKind, LightAction, ParsedIntent
from .theme_engine import ThemeEngine


NAMED_COLORS: dict[str, tuple[int, int, int]] = {
    "deep blue": (0, 42, 130),
    "blue": (30, 90, 255),
    "cyan": (0, 210, 220),
    "teal": (0, 150, 150),
    "green": (32, 190, 80),
    "purple": (142, 58, 230),
    "violet": (112, 52, 210),
    "pink": (255, 78, 158),
    "red": (240, 34, 34),
    "orange": (255, 112, 24),
    "yellow": (255, 215, 42),
    "white": (255, 244, 224),
}

MOOD_MARKERS = (
    "feel like",
    "feels like",
    "make it feel",
    "mood",
    "theme",
    "vibe",
    "atmosphere",
    "take me to",
    "imagine",
)


class IntentParser:
    def __init__(self, theme_engine: ThemeEngine | None = None) -> None:
        self.themes = theme_engine or ThemeEngine()

    def parse(self, text: str) -> ParsedIntent:
        normalized = " ".join(text.casefold().strip().split())
        if not normalized:
            return ParsedIntent(IntentKind.UNKNOWN, response="Tell me what you want the lights to do.")

        if normalized in {"help", "what can you do", "commands", "show commands"}:
            return ParsedIntent(IntentKind.HELP)
        if any(phrase in normalized for phrase in ("suggest", "surprise me", "your choice", "pick a theme")):
            return ParsedIntent(IntentKind.SUGGEST)
        if any(phrase in normalized for phrase in ("light status", "lights status", "what are the lights doing")):
            return ParsedIntent(IntentKind.STATUS)

        transition = self._extract_transition(normalized)
        brightness = self._extract_brightness(normalized)

        if self._contains_off(normalized):
            return ParsedIntent(IntentKind.ACTION, action=LightAction.TURN_OFF, transition_seconds=transition)
        if "toggle" in normalized or "flip the lights" in normalized:
            return ParsedIntent(IntentKind.ACTION, action=LightAction.TOGGLE, transition_seconds=transition)

        theme = self.themes.find(normalized)
        if theme and (theme.key == "ocean" or any(marker in normalized for marker in MOOD_MARKERS)):
            return ParsedIntent(IntentKind.THEME, theme_key=theme.key, transition_seconds=theme.transition_seconds)
        if theme and any(alias in normalized for alias in ("cozy", "focus", "energ", "relax", "calm", "sunset", "forest", "aurora", "moon")):
            return ParsedIntent(IntentKind.THEME, theme_key=theme.key, transition_seconds=theme.transition_seconds)

        if "warm white" in normalized or "warmer" in normalized:
            return ParsedIntent(
                IntentKind.ACTION,
                action=LightAction.TURN_ON,
                brightness_pct=brightness or 65,
                color_temp_kelvin=2700,
                transition_seconds=transition,
            )
        if "cool white" in normalized or "daylight" in normalized or "cooler" in normalized:
            return ParsedIntent(
                IntentKind.ACTION,
                action=LightAction.TURN_ON,
                brightness_pct=brightness or 75,
                color_temp_kelvin=5200,
                transition_seconds=transition,
            )

        for color_name in sorted(NAMED_COLORS, key=len, reverse=True):
            if re.search(rf"\b{re.escape(color_name)}\b", normalized):
                return ParsedIntent(
                    IntentKind.ACTION,
                    action=LightAction.TURN_ON,
                    brightness_pct=brightness or 60,
                    rgb_color=NAMED_COLORS[color_name],
                    transition_seconds=transition,
                )

        if brightness is not None:
            if brightness == 0:
                return ParsedIntent(IntentKind.ACTION, action=LightAction.TURN_OFF, transition_seconds=transition)
            return ParsedIntent(
                IntentKind.ACTION,
                action=LightAction.TURN_ON,
                brightness_pct=brightness,
                transition_seconds=transition,
            )

        if self._contains_on(normalized):
            return ParsedIntent(IntentKind.ACTION, action=LightAction.TURN_ON, transition_seconds=transition)

        if any(marker in normalized for marker in MOOD_MARKERS):
            return ParsedIntent(
                IntentKind.THEME,
                generated_theme_text=normalized,
                transition_seconds=4.0,
            )

        return ParsedIntent(
            IntentKind.UNKNOWN,
            response=(
                "I can turn lights on or off, set brightness or color, build a mood theme, "
                "or suggest one. Try “ocean”, “warm and cozy”, or “35 percent”."
            ),
        )

    @staticmethod
    def _contains_off(text: str) -> bool:
        return text in {"off", "all off"} or bool(
            re.search(r"\b(turn|switch|shut|set)\b.{0,16}\boff\b|\blights? off\b", text)
        )

    @staticmethod
    def _contains_on(text: str) -> bool:
        return text in {"on", "all on"} or bool(
            re.search(r"\b(turn|switch|set)\b.{0,16}\bon\b|\blights? on\b", text)
        )

    @staticmethod
    def _extract_brightness(text: str) -> int | None:
        patterns = (
            r"\b(\d{1,3})\s*%",
            r"\b(\d{1,3})\s*percent\b",
            r"\bbrightness\D{0,12}(\d{1,3})\b",
            r"\bdim\D{0,12}(\d{1,3})\b",
        )
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return max(0, min(100, int(match.group(1))))
        if "full brightness" in text or "maximum brightness" in text:
            return 100
        return None

    @staticmethod
    def _extract_transition(text: str) -> float:
        match = re.search(r"(?:over|fade(?: over| in)?)\s+(\d+(?:\.\d+)?)\s*(?:s|sec|second)", text)
        if not match:
            return 2.0
        return max(0.0, min(30.0, float(match.group(1))))
