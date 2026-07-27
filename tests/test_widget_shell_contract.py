from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WidgetShellContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = (ROOT / "src/osun/web/index.html").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "src/osun/web/app.js").read_text(encoding="utf-8")
        cls.styles = (ROOT / "src/osun/web/styles.css").read_text(encoding="utf-8")

    def test_widget_dock_is_absent_until_an_agent_returns_a_widget(self) -> None:
        self.assertIn(
            'id="widgetDock" class="widget-dock" aria-label="Active agent widget" hidden',
            self.html,
        )
        self.assertNotIn('id="widgetEmpty"', self.html)
        self.assertIn("showAgentWidget(response.widgets[0]);", self.javascript)
        self.assertIn('if (state.activeWidget?.kind !== "lighting") return;', self.javascript)

    def test_new_widgets_start_compact_and_have_an_accessible_expand_control(self) -> None:
        self.assertIn("state.widgetExpanded = false;", self.javascript)
        self.assertIn('id="toggleWidget"', self.javascript)
        self.assertIn('aria-expanded="${expanded}"', self.javascript)
        self.assertIn('id="lightingWidgetBody"', self.javascript)
        self.assertIn('id="musicWidgetBody"', self.javascript)
        self.assertIn('class="widget-card music-card ${expanded ? "expanded" : "compact"}', self.javascript)
        self.assertIn('.workspace.has-widget.widget-expanded', self.styles)

    def test_music_widget_exposes_device_question_and_five_minute_reason(self) -> None:
        self.assertIn('data-music-device="${escapeHtml(device.device_id)}"', self.javascript)
        self.assertIn("Nothing has played on a registered device in the last five minutes", self.javascript)
        self.assertIn("Automatically selected from playback in the last five minutes", self.javascript)
        self.assertIn('id="musicNav"', self.html)

    def test_real_widget_operations_drive_the_running_animation(self) -> None:
        self.assertIn("setWidgetRunning(true);", self.javascript)
        self.assertIn("setWidgetRunning(false);", self.javascript)
        self.assertIn('widget-card ${expanded ? "expanded" : "compact"} ${running ? "running" : ""}', self.javascript)
        self.assertIn('aria-busy="${running}"', self.javascript)
        self.assertIn(".widget-card.running::after", self.styles)
        self.assertIn(".running .widget-orbit", self.styles)
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.styles)


if __name__ == "__main__":
    unittest.main()
