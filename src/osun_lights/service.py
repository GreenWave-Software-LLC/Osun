from __future__ import annotations

from dataclasses import dataclass

from .audit import AuditLog
from .intent_parser import IntentParser
from .models import ExecutionReport, IntentKind, LightInfo, LightingProposal, ResultState
from .proposal_builder import ProposalBuilder
from .providers import LightProvider


@dataclass(frozen=True, slots=True)
class AssistantReply:
    text: str
    proposal: LightingProposal | None = None


class LightingAssistant:
    def __init__(
        self,
        provider: LightProvider,
        *,
        paused: bool = False,
        live_enabled: bool = False,
        parser: IntentParser | None = None,
        builder: ProposalBuilder | None = None,
        audit: AuditLog | None = None,
    ) -> None:
        self.provider = provider
        self.paused = paused
        self.live_enabled = live_enabled
        self.parser = parser or IntentParser()
        self.builder = builder or ProposalBuilder(self.parser.themes)
        self.audit = audit
        self.pending: LightingProposal | None = None
        self._executed: set[str] = set()

    @property
    def mode(self) -> str:
        return self.provider.mode

    def list_lights(self) -> tuple[LightInfo, ...]:
        return self.provider.list_lights()

    def handle(self, text: str, selected_entities: tuple[str, ...] = ()) -> AssistantReply:
        intent = self.parser.parse(text)
        lights = self.list_lights()
        if selected_entities:
            selected = set(selected_entities)
            lights = tuple(light for light in lights if light.entity_id in selected)
        if intent.kind == IntentKind.HELP:
            return AssistantReply(
                "Try: “turn the lights off”, “35 percent”, “warm white”, “ocean”, "
                "“make it feel like a bioluminescent cave”, or “suggest something”."
            )
        if intent.kind == IntentKind.STATUS:
            if not lights:
                return AssistantReply("No lights are currently available in this mode.")
            details = ", ".join(f"{light.friendly_name} is {light.state}" for light in lights)
            return AssistantReply(details + ".")
        if intent.kind == IntentKind.UNKNOWN:
            return AssistantReply(intent.response or "I couldn't turn that into a safe lighting proposal.")
        if not lights:
            return AssistantReply("Select at least one available light first.")
        proposal = self.builder.suggestion(lights) if intent.kind == IntentKind.SUGGEST else self.builder.build(intent, lights)
        self.pending = proposal
        if self.audit:
            self.audit.proposal(proposal, self.mode)
        if proposal.theme_name:
            text_reply = f"{proposal.summary}. {proposal.rationale} Review the exact light settings below, then Apply if you want it."
        else:
            text_reply = f"I prepared an exact preview for {len(proposal.changes)} light(s). Nothing changes until you select Apply."
        return AssistantReply(text_reply, proposal)

    def apply(self, proposal_id: str) -> ExecutionReport:
        proposal = self.pending
        if proposal is None or proposal.proposal_id != proposal_id:
            return self._denied(proposal_id, "proposal_missing_or_replaced")
        if proposal_id in self._executed:
            return self._denied(proposal_id, "proposal_already_executed")
        if self.paused:
            return self._denied(proposal_id, "global_pause")
        if self.mode == "home_assistant" and not self.live_enabled:
            return self._denied(proposal_id, "live_control_disabled")

        self._executed.add(proposal_id)
        report = self.provider.apply(proposal)
        self.pending = None
        if self.audit:
            self.audit.result(report)
        return report

    def cancel(self) -> None:
        self.pending = None

    def set_paused(self, paused: bool) -> None:
        self.paused = paused
        if paused:
            self.pending = None

    def _denied(self, proposal_id: str | None, reason: str) -> ExecutionReport:
        from .models import ExecutionItem

        report = ExecutionReport(
            proposal_id or "none",
            ResultState.DENIED,
            (ExecutionItem("light.none", ResultState.DENIED, reason),),
            self.mode,
        )
        if self.audit:
            self.audit.denied(proposal_id, self.mode, reason)
        return report
