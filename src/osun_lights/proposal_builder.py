from __future__ import annotations

from .models import IntentKind, LightAction, LightChange, LightInfo, LightingProposal, ParsedIntent
from .theme_engine import Theme, ThemeEngine


class ProposalBuilder:
    def __init__(self, themes: ThemeEngine | None = None) -> None:
        self.themes = themes or ThemeEngine()

    def build(self, intent: ParsedIntent, lights: tuple[LightInfo, ...]) -> LightingProposal:
        if not lights:
            raise ValueError("Select at least one light")
        if intent.kind == IntentKind.THEME:
            theme = self.themes.get(intent.theme_key) if intent.theme_key else self.themes.generate(intent.generated_theme_text or "custom")
            return self._theme_proposal(theme, lights)
        if intent.kind != IntentKind.ACTION or intent.action is None:
            raise ValueError("This intent does not produce a lighting proposal")

        changes = tuple(self._action_change(intent, light) for light in lights)
        action_label = {
            LightAction.TURN_ON: "Turn on",
            LightAction.TURN_OFF: "Turn off",
            LightAction.TOGGLE: "Toggle",
        }[intent.action]
        return LightingProposal(summary=f"{action_label} {len(lights)} selected light(s)", changes=changes)

    def suggestion(self, lights: tuple[LightInfo, ...]) -> LightingProposal:
        return self._theme_proposal(self.themes.suggest(), lights)

    def _theme_proposal(self, theme: Theme, lights: tuple[LightInfo, ...]) -> LightingProposal:
        changes: list[LightChange] = []
        color_index = 0
        for light in lights:
            rgb = None
            kelvin = None
            brightness = theme.brightness_pct if light.supports_brightness else None
            if light.supports_color:
                rgb = theme.palette[color_index % len(theme.palette)]
                color_index += 1
            elif light.supports_color_temperature:
                kelvin = theme.white_kelvin
            changes.append(
                LightChange(
                    entity_id=light.entity_id,
                    friendly_name=light.friendly_name,
                    action=LightAction.TURN_ON,
                    brightness_pct=brightness,
                    rgb_color=rgb,
                    color_temp_kelvin=kelvin,
                    transition_seconds=theme.transition_seconds,
                )
            )
        label = "Generated theme" if theme.generated else "Theme"
        return LightingProposal(
            summary=f"{label}: {theme.name}",
            changes=tuple(changes),
            theme_name=theme.name,
            rationale=theme.description,
        )

    @staticmethod
    def _action_change(intent: ParsedIntent, light: LightInfo) -> LightChange:
        brightness = intent.brightness_pct if light.supports_brightness else None
        rgb = intent.rgb_color if light.supports_color else None
        kelvin = intent.color_temp_kelvin if light.supports_color_temperature else None
        if intent.color_temp_kelvin is not None and not light.supports_color_temperature and light.supports_color:
            rgb = (255, 176, 92) if intent.color_temp_kelvin <= 3500 else (210, 228, 255)
        return LightChange(
            entity_id=light.entity_id,
            friendly_name=light.friendly_name,
            action=intent.action or LightAction.TURN_ON,
            brightness_pct=brightness,
            rgb_color=rgb,
            color_temp_kelvin=kelvin,
            transition_seconds=intent.transition_seconds,
        )
