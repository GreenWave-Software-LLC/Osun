from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from osun_lights.audit import AuditLog
from osun_lights.models import LightAction, LightInfo, ResultState
from osun_lights.service import LightingAssistant
from osun_lights.simulator import SimulatedLightProvider


class FakeHomeAssistantProvider(SimulatedLightProvider):
    mode = "home_assistant"


class ProposalAndServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lights = (
            LightInfo("light.color_one", "Color One", "off", ("rgb",)),
            LightInfo("light.color_two", "Color Two", "off", ("xy",)),
            LightInfo("light.white", "White", "off", ("color_temp",)),
            LightInfo("light.switch_only", "Switch Only", "off", ("onoff",)),
        )
        self.provider = SimulatedLightProvider(self.lights)
        self.assistant = LightingAssistant(self.provider)

    def test_theme_is_preview_only_until_apply(self) -> None:
        reply = self.assistant.handle("ocean")
        self.assertIsNotNone(reply.proposal)
        self.assertTrue(all(light.state == "off" for light in self.provider.list_lights()))
        proposal = reply.proposal
        assert proposal is not None
        self.assertEqual("Deep Ocean", proposal.theme_name)
        self.assertEqual(4, len(proposal.changes))
        self.assertIsNotNone(proposal.changes[0].rgb_color)
        self.assertIsNotNone(proposal.changes[2].color_temp_kelvin)
        self.assertIsNone(proposal.changes[3].brightness_pct)

        report = self.assistant.apply(proposal.proposal_id)
        self.assertEqual(ResultState.VERIFIED, report.state)
        self.assertTrue(all(light.state == "on" for light in self.provider.list_lights()))

    def test_selected_targets_only(self) -> None:
        reply = self.assistant.handle("turn off", ("light.color_two",))
        proposal = reply.proposal
        assert proposal is not None
        self.assertEqual(("light.color_two",), tuple(change.entity_id for change in proposal.changes))

    def test_pause_cancels_and_denies_execution(self) -> None:
        reply = self.assistant.handle("turn on")
        proposal = reply.proposal
        assert proposal is not None
        self.assistant.set_paused(True)
        report = self.assistant.apply(proposal.proposal_id)
        self.assertEqual(ResultState.DENIED, report.state)
        self.assertEqual("Lighting change denied: execution is paused.", report.summary)
        self.assertTrue(all(light.state == "off" for light in self.provider.list_lights()))

    def test_same_proposal_does_not_execute_twice(self) -> None:
        reply = self.assistant.handle("turn on")
        proposal = reply.proposal
        assert proposal is not None
        first = self.assistant.apply(proposal.proposal_id)
        second = self.assistant.apply(proposal.proposal_id)
        self.assertEqual(ResultState.VERIFIED, first.state)
        self.assertEqual(ResultState.DENIED, second.state)

    def test_live_disabled_denial_is_plain_language(self) -> None:
        assistant = LightingAssistant(FakeHomeAssistantProvider(self.lights), live_enabled=False)
        proposal = assistant.handle("turn on", ("light.color_one",)).proposal
        assert proposal is not None
        report = assistant.apply(proposal.proposal_id)
        self.assertEqual(ResultState.DENIED, report.state)
        self.assertEqual("Lighting change denied: live light execution is disabled.", report.summary)

    def test_normal_off_proposal_contains_only_off_actions(self) -> None:
        proposal = self.assistant.handle("off").proposal
        assert proposal is not None
        self.assertTrue(all(change.action == LightAction.TURN_OFF for change in proposal.changes))
        self.assertTrue(all(change.rgb_color is None for change in proposal.changes))

    def test_audit_excludes_raw_chat(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            assistant = LightingAssistant(self.provider, audit=AuditLog(path))
            secret_phrase = "ocean PRIVATE_RAW_CHAT_MARKER"
            reply = assistant.handle(secret_phrase)
            proposal = reply.proposal
            assert proposal is not None
            assistant.apply(proposal.proposal_id)
            audit_text = path.read_text(encoding="utf-8")
            self.assertNotIn("PRIVATE_RAW_CHAT_MARKER", audit_text)
            self.assertNotIn(secret_phrase, audit_text)
            self.assertIn(proposal.proposal_id, audit_text)


if __name__ == "__main__":
    unittest.main()
