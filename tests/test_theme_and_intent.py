from __future__ import annotations

import unittest
from datetime import datetime

from osun_lights.intent_parser import IntentParser
from osun_lights.models import IntentKind, LightAction
from osun_lights.theme_engine import ThemeEngine


class ThemeEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ThemeEngine()
        self.parser = IntentParser(self.engine)

    def test_ocean_request_resolves_to_deep_blue_theme(self) -> None:
        intent = self.parser.parse("I want to feel like I'm in the ocean")
        self.assertEqual(IntentKind.THEME, intent.kind)
        self.assertEqual("ocean", intent.theme_key)
        theme = self.engine.get("ocean")
        self.assertEqual("Deep Ocean", theme.name)
        self.assertTrue(all(blue > red for red, _green, blue in theme.palette))

    def test_unknown_atmosphere_generates_stable_bounded_palette(self) -> None:
        first = self.engine.generate("bioluminescent cave")
        second = self.engine.generate("bioluminescent cave")
        self.assertTrue(first.generated)
        self.assertEqual(first.key, second.key)
        self.assertEqual(first.palette, second.palette)
        self.assertEqual(4, len(first.palette))
        self.assertTrue(all(0 <= channel <= 255 for color in first.palette for channel in color))

    def test_suggestion_is_time_aware_but_deterministic(self) -> None:
        morning = self.engine.suggest(datetime(2026, 7, 27, 8, 0))
        evening = self.engine.suggest(datetime(2026, 7, 27, 20, 0))
        self.assertIn(morning.key, {"energize", "focus", "forest"})
        self.assertIn(evening.key, {"sunset", "cozy", "ocean", "aurora"})

    def test_normal_light_commands(self) -> None:
        off = self.parser.parse("turn all the lights off over 4 seconds")
        self.assertEqual(LightAction.TURN_OFF, off.action)
        self.assertEqual(4.0, off.transition_seconds)

        brightness = self.parser.parse("set these lights to 35 percent")
        self.assertEqual(LightAction.TURN_ON, brightness.action)
        self.assertEqual(35, brightness.brightness_pct)

        color = self.parser.parse("make them purple at 42%")
        self.assertEqual((142, 58, 230), color.rgb_color)
        self.assertEqual(42, color.brightness_pct)

    def test_zero_percent_becomes_off_and_bounds_are_clamped(self) -> None:
        zero = self.parser.parse("brightness 0 percent")
        self.assertEqual(LightAction.TURN_OFF, zero.action)
        high = self.parser.parse("brightness 900 percent")
        self.assertEqual(100, high.brightness_pct)

    def test_unrecognized_request_does_not_create_action(self) -> None:
        intent = self.parser.parse("write an email for me")
        self.assertEqual(IntentKind.UNKNOWN, intent.kind)
        self.assertIsNone(intent.action)


if __name__ == "__main__":
    unittest.main()
