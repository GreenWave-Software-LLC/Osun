from __future__ import annotations

import colorsys
import hashlib
from dataclasses import dataclass
from datetime import datetime


RGB = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class Theme:
    key: str
    name: str
    description: str
    palette: tuple[RGB, ...]
    brightness_pct: int
    transition_seconds: float = 3.0
    white_kelvin: int = 4000
    generated: bool = False


THEMES: dict[str, Theme] = {
    "ocean": Theme(
        "ocean",
        "Deep Ocean",
        "Layered midnight, reef, and bioluminescent blues—immersive without being harsh.",
        ((0, 28, 96), (0, 62, 150), (0, 112, 190), (18, 172, 210)),
        48,
        4.0,
        6000,
    ),
    "calm": Theme(
        "calm",
        "Still Water",
        "Soft blue-green light with a slow transition for a quieter atmosphere.",
        ((28, 76, 120), (35, 112, 130), (52, 132, 145)),
        38,
        5.0,
        4300,
    ),
    "cozy": Theme(
        "cozy",
        "Amber Hearth",
        "Low amber and warm cream light for an easy, sheltered evening.",
        ((255, 92, 28), (255, 146, 52), (255, 198, 110)),
        55,
        3.0,
        2700,
    ),
    "focus": Theme(
        "focus",
        "Clear Focus",
        "Bright neutral-cool light with a restrained blue accent.",
        ((214, 232, 255), (154, 202, 255), (88, 148, 255)),
        82,
        2.0,
        5000,
    ),
    "energize": Theme(
        "energize",
        "Solar Spark",
        "Bright coral, gold, and clean white for an energetic lift.",
        ((255, 72, 46), (255, 166, 38), (255, 226, 150)),
        88,
        1.5,
        5200,
    ),
    "sunset": Theme(
        "sunset",
        "Desert Sunset",
        "A gradient from ember orange through rose into violet.",
        ((255, 74, 24), (255, 126, 48), (215, 56, 112), (96, 42, 150)),
        62,
        4.0,
        3000,
    ),
    "forest": Theme(
        "forest",
        "Forest Canopy",
        "Deep green, moss, and a touch of filtered golden light.",
        ((8, 60, 34), (22, 104, 58), (92, 136, 62), (206, 166, 72)),
        46,
        4.0,
        3500,
    ),
    "aurora": Theme(
        "aurora",
        "Aurora",
        "Emerald, cyan, violet, and magenta spread across the room.",
        ((0, 196, 130), (0, 164, 210), (96, 72, 210), (210, 48, 170)),
        58,
        4.0,
        4600,
    ),
    "moonlight": Theme(
        "moonlight",
        "Moonlit Room",
        "Dim silver-blue light for a calm late-night atmosphere.",
        ((28, 44, 88), (52, 72, 132), (108, 126, 176)),
        24,
        5.0,
        6000,
    ),
    "romantic": Theme(
        "romantic",
        "Rose Glow",
        "A low rose, wine, and warm amber palette.",
        ((142, 18, 54), (214, 44, 92), (255, 112, 88), (255, 170, 98)),
        38,
        4.0,
        2600,
    ),
}


ALIASES: dict[str, tuple[str, ...]] = {
    "ocean": ("ocean", "underwater", "under the sea", "deep sea", "aquatic"),
    "calm": ("calm", "relax", "peaceful", "serene", "quiet"),
    "cozy": ("cozy", "cosy", "comfortable", "snug", "warm evening"),
    "focus": ("focus", "focused", "concentrate", "study", "productive"),
    "energize": ("energize", "energized", "energy", "wake me up", "vibrant"),
    "sunset": ("sunset", "golden hour", "desert sky"),
    "forest": ("forest", "woods", "jungle", "canopy", "nature"),
    "aurora": ("aurora", "northern lights"),
    "moonlight": ("moonlight", "moonlit", "night sky"),
    "romantic": ("romantic", "romance", "date night", "intimate"),
}


class ThemeEngine:
    def find(self, text: str) -> Theme | None:
        normalized = " ".join(text.casefold().split())
        for key, aliases in ALIASES.items():
            if any(alias in normalized for alias in aliases):
                return THEMES[key]
        return None

    def get(self, key: str) -> Theme:
        return THEMES[key]

    def suggest(self, now: datetime | None = None) -> Theme:
        moment = now or datetime.now()
        if 5 <= moment.hour < 10:
            options = ("energize", "focus", "forest")
        elif 10 <= moment.hour < 17:
            options = ("focus", "forest", "aurora")
        elif 17 <= moment.hour < 22:
            options = ("sunset", "cozy", "ocean", "aurora")
        else:
            options = ("moonlight", "calm", "ocean")
        return THEMES[options[moment.toordinal() % len(options)]]

    def generate(self, description: str) -> Theme:
        normalized = " ".join(description.casefold().split()) or "custom atmosphere"
        digest = hashlib.sha256(normalized.encode("utf-8")).digest()
        hue = digest[0] / 255.0

        keyword_hues = {
            "ice": 0.55,
            "cave": 0.57,
            "storm": 0.66,
            "space": 0.72,
            "galaxy": 0.78,
            "dream": 0.82,
            "rose": 0.95,
            "fire": 0.03,
            "gold": 0.11,
            "sun": 0.09,
            "green": 0.34,
            "nature": 0.34,
        }
        for word, forced_hue in keyword_hues.items():
            if word in normalized:
                hue = forced_hue
                break

        palette: list[RGB] = []
        offsets = (-0.08, 0.0, 0.08, 0.16)
        for index, offset in enumerate(offsets):
            saturation = 0.68 + (digest[index + 1] / 255.0) * 0.22
            value = 0.48 + index * 0.12
            red, green, blue = colorsys.hsv_to_rgb((hue + offset) % 1.0, saturation, min(value, 0.92))
            palette.append((round(red * 255), round(green * 255), round(blue * 255)))

        words = [word for word in normalized.replace("'", "").split() if word.isalnum()]
        label = " ".join(words[:4]).title() or "Custom Atmosphere"
        return Theme(
            key=f"generated-{digest.hex()[:10]}",
            name=label,
            description=f"A generated four-color interpretation of “{label}”.",
            palette=tuple(palette),
            brightness_pct=52,
            transition_seconds=4.0,
            white_kelvin=4200,
            generated=True,
        )
