from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from .config import default_data_dir
from .models import ExecutionReport, LightingProposal


class AuditLog:
    """Content-minimized local audit. It intentionally excludes raw chat and credentials."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_data_dir() / "audit.jsonl"

    def proposal(self, proposal: LightingProposal, mode: str) -> None:
        self._write(
            {
                "event": "lighting.proposed",
                "proposal_id": proposal.proposal_id,
                "mode": mode,
                "theme": proposal.theme_name,
                "targets": [change.entity_id for change in proposal.changes],
                "actions": [change.action.value for change in proposal.changes],
            }
        )

    def result(self, report: ExecutionReport) -> None:
        self._write(
            {
                "event": "lighting.completed",
                "proposal_id": report.proposal_id,
                "mode": report.mode,
                "outcome": report.state.value,
                "items": [
                    {"entity_id": item.entity_id, "outcome": item.state.value, "observed_state": item.observed_state}
                    for item in report.items
                ],
            }
        )

    def denied(self, proposal_id: str | None, mode: str, reason: str) -> None:
        self._write(
            {
                "event": "lighting.denied",
                "proposal_id": proposal_id,
                "mode": mode,
                "reason": reason,
            }
        )

    def _write(self, payload: dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"time": datetime.now(UTC).isoformat(), **payload}
        line = json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
