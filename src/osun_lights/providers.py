from __future__ import annotations

from typing import Protocol

from .models import ExecutionReport, LightInfo, LightingProposal


class LightProvider(Protocol):
    mode: str

    def list_lights(self) -> tuple[LightInfo, ...]: ...

    def apply(self, proposal: LightingProposal) -> ExecutionReport: ...
