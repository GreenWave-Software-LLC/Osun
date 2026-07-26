from __future__ import annotations

from threading import RLock
from typing import Any

from .audit import AuditLog
from .config import AppConfig, ConfigStore, default_data_dir
from .credential_store import CredentialStoreError, WindowsCredentialStore
from .home_assistant import HomeAssistantClient, HomeAssistantError
from .models import ExecutionReport, LightingProposal, public_light_state
from .service import LightingAssistant
from .simulator import SimulatedLightProvider


def credential_store() -> WindowsCredentialStore:
    return WindowsCredentialStore(default_data_dir() / "secrets" / "home_assistant_token.bin")


def proposal_json(proposal: LightingProposal | None) -> dict[str, Any] | None:
    if proposal is None:
        return None
    return {
        "proposal_id": proposal.proposal_id,
        "summary": proposal.summary,
        "theme_name": proposal.theme_name,
        "rationale": proposal.rationale,
        "created_at": proposal.created_at,
        "requires_confirmation": proposal.requires_confirmation,
        "changes": [
            {
                "entity_id": change.entity_id,
                "friendly_name": change.friendly_name,
                "action": change.action.value,
                "brightness_pct": change.brightness_pct,
                "rgb_color": list(change.rgb_color) if change.rgb_color else None,
                "color_temp_kelvin": change.color_temp_kelvin,
                "transition_seconds": change.transition_seconds,
                "preview": change.preview(),
            }
            for change in proposal.changes
        ],
    }


def report_json(report: ExecutionReport) -> dict[str, Any]:
    return {
        "proposal_id": report.proposal_id,
        "state": report.state.value,
        "mode": report.mode,
        "summary": report.summary,
        "completed_at": report.completed_at,
        "items": [
            {
                "entity_id": item.entity_id,
                "state": item.state.value,
                "detail": item.detail,
                "observed_state": item.observed_state,
            }
            for item in report.items
        ],
    }


class LightingController:
    def __init__(
        self,
        config_store: ConfigStore | None = None,
        audit: AuditLog | None = None,
        credential: WindowsCredentialStore | None = None,
    ) -> None:
        self.config_store = config_store or ConfigStore()
        self.audit = audit or AuditLog()
        self.credential = credential or credential_store()
        self._lock = RLock()
        self.config = self.config_store.load()
        self.assistant, self.warning = self._build_assistant()

    def status(self) -> dict[str, Any]:
        with self._lock:
            try:
                lights = self.assistant.list_lights()
                light_error = None
            except Exception as exc:
                lights = ()
                light_error = str(exc)
            return {
                "effective_mode": self.assistant.mode,
                "paused": self.assistant.paused,
                "live_enabled": self.assistant.live_enabled,
                "warning": light_error or self.warning,
                "lights": [public_light_state(light) for light in lights],
                "pending": proposal_json(self.assistant.pending),
                "settings": {
                    "mode": self.config.mode,
                    "home_assistant_url": self.config.home_assistant_url,
                    "allowed_entities": list(self.config.allowed_entities),
                    "live_enabled": self.config.live_enabled,
                    "global_pause": self.config.global_pause,
                    "credential_saved": self._credential_exists(),
                },
            }

    def message(self, text: str, selected_entities: tuple[str, ...]) -> dict[str, Any]:
        if len(text) > 2_000:
            raise ValueError("Lighting requests are limited to 2,000 characters")
        with self._lock:
            reply = self.assistant.handle(text, selected_entities)
            return {"text": reply.text, "proposal": proposal_json(reply.proposal)}

    def apply(self, proposal_id: str) -> dict[str, Any]:
        with self._lock:
            return report_json(self.assistant.apply(proposal_id))

    def cancel(self) -> dict[str, bool]:
        with self._lock:
            self.assistant.cancel()
            return {"canceled": True}

    def pause(self) -> dict[str, Any]:
        with self._lock:
            self.assistant.set_paused(True)
            self.config.global_pause = True
            self.config_store.save(self.config)
            return {"paused": True}

    def test_connection(self, url: str, token: str) -> dict[str, Any]:
        effective_token = token.strip() or self.credential.load()
        if not effective_token:
            raise CredentialStoreError("Enter a token or keep an existing saved token")
        client = HomeAssistantClient(url, effective_token, set(), timeout=6.0, sleep=lambda _seconds: None)
        if not client.check():
            raise HomeAssistantError("The endpoint did not identify itself as Home Assistant")
        lights = client.discover_lights()
        return {"connected": True, "lights": [public_light_state(light) for light in lights]}

    def save_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        mode = str(payload.get("mode", "simulator"))
        url = str(payload.get("home_assistant_url", "")).strip()
        token = str(payload.get("token", "")).strip()
        allowed_raw = payload.get("allowed_entities", [])
        if not isinstance(allowed_raw, list) or not all(isinstance(item, str) for item in allowed_raw):
            raise ValueError("allowed_entities must be a list of light entity IDs")
        allowed = sorted(set(allowed_raw))
        updated = AppConfig(
            mode=mode,
            home_assistant_url=url,
            allowed_entities=allowed,
            live_enabled=bool(payload.get("live_enabled", False)),
            global_pause=bool(payload.get("global_pause", True)),
        )
        updated.validate()

        if mode == "home_assistant":
            effective_token = token or self.credential.load()
            if not effective_token:
                raise CredentialStoreError("A tested Home Assistant token is required")
            client = HomeAssistantClient(url, effective_token, set(), timeout=6.0, sleep=lambda _seconds: None)
            if not client.check():
                raise HomeAssistantError("The endpoint did not identify itself as Home Assistant")
            discovered = {light.entity_id for light in client.discover_lights()}
            unknown = set(allowed).difference(discovered)
            if unknown:
                raise ValueError("One or more allowed light entities no longer exist")
            if updated.live_enabled and not allowed:
                raise ValueError("Select at least one light before enabling live execution")
            if token:
                self.credential.save(token)

        with self._lock:
            self.config_store.save(updated)
            self.config = updated
            self.assistant, self.warning = self._build_assistant()
        return self.status()

    def delete_credential(self) -> dict[str, Any]:
        with self._lock:
            self.credential.delete()
            self.config = AppConfig(
                mode="simulator",
                home_assistant_url=self.config.home_assistant_url,
                allowed_entities=[],
                live_enabled=False,
                global_pause=True,
            )
            self.config_store.save(self.config)
            self.assistant, self.warning = self._build_assistant()
            return self.status()

    def _build_assistant(self) -> tuple[LightingAssistant, str | None]:
        if self.config.mode == "home_assistant":
            try:
                token = self.credential.load()
                if not token:
                    raise CredentialStoreError("No protected Home Assistant token is saved")
                provider = HomeAssistantClient(
                    self.config.home_assistant_url,
                    token,
                    set(self.config.allowed_entities),
                )
                return (
                    LightingAssistant(
                        provider,
                        paused=self.config.global_pause,
                        live_enabled=self.config.live_enabled,
                        audit=self.audit,
                    ),
                    None,
                )
            except (CredentialStoreError, ValueError) as exc:
                return LightingAssistant(SimulatedLightProvider(), audit=self.audit), str(exc)
        return LightingAssistant(SimulatedLightProvider(), audit=self.audit), None

    def _credential_exists(self) -> bool:
        try:
            return self.credential.load() is not None
        except CredentialStoreError:
            return False
