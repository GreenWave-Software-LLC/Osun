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
        cls.windows_music_bridge = (ROOT / "src/osun_music/windows_apple_music.ps1").read_text(encoding="utf-8")

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

    def test_windows_music_settings_and_bridge_are_targeted(self) -> None:
        self.assertIn('value="windows_app" checked', self.html)
        self.assertIn('id="musicAppTestButton"', self.html)
        self.assertIn('/agents/music/settings/test-windows-app', self.javascript)
        self.assertIn("[ValidateSet('probe', 'play-url', 'pause', 'resume', 'next', 'previous')]", self.windows_music_bridge)
        self.assertIn("AppleInc.AppleMusicWin_nzyj5cx40ttqa!App", self.windows_music_bridge)
        self.assertIn("Test-AppleMusicPath", self.windows_music_bridge)
        self.assertIn("WindowsApps\\AppleInc.AppleMusicWin_", self.windows_music_bridge)
        self.assertIn("GetForegroundWindow", self.windows_music_bridge)
        self.assertNotIn("VK_MEDIA", self.windows_music_bridge)


if __name__ == "__main__":
    unittest.main()
