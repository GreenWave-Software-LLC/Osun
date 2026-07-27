from __future__ import annotations

import unittest
from typing import Any

from osun.qwen import OllamaQwenClient


class FakeQwenClient(OllamaQwenClient):
    def __init__(self, responses: dict[tuple[str, str], Any]) -> None:
        super().__init__(timeout=0.1)
        self.responses = responses
        self.requests: list[tuple[str, str, dict[str, Any] | None]] = []

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        self.requests.append((method, path, payload))
        return self.responses[(method, path)]


class QwenClientTests(unittest.TestCase):
    def test_endpoint_must_be_loopback(self) -> None:
        with self.assertRaises(ValueError):
            OllamaQwenClient("http://192.168.1.10:11434")
        with self.assertRaises(ValueError):
            OllamaQwenClient("https://example.com")

    def test_status_identifies_installed_model(self) -> None:
        client = FakeQwenClient(
            {
                ("GET", "/api/tags"): {"models": [{"name": "qwen3.5:9b"}]},
                ("GET", "/api/ps"): {"models": [{"name": "qwen3.5:9b"}]},
            }
        )
        status = client.status()
        self.assertTrue(status["online"])
        self.assertTrue(status["model_available"])
        self.assertTrue(status["loaded"])
        self.assertEqual("http://127.0.0.1:11434", status["endpoint"])

    def test_chat_accepts_only_known_widget_tool(self) -> None:
        client = FakeQwenClient(
            {
                ("POST", "/api/chat"): {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {"function": {"name": "open_lighting_widget", "arguments": {}}},
                            {"function": {"name": "run_shell", "arguments": {"command": "whoami"}}},
                        ],
                    },
                    "prompt_eval_count": 20,
                    "eval_count": 4,
                    "total_duration": 2_500_000,
                }
            }
        )
        reply = client.chat("make it blue")
        self.assertEqual(("open_lighting_widget",), reply.tool_names)
        request_payload = client.requests[0][2]
        self.assertEqual(
            ["open_lighting_widget", "open_music_widget"],
            [tool["function"]["name"] for tool in request_payload["tools"]],
        )
        self.assertFalse(request_payload["think"])

    def test_chat_accepts_music_widget_and_rejects_unknown_tools(self) -> None:
        client = FakeQwenClient(
            {
                ("POST", "/api/chat"): {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {"function": {"name": "open_music_widget", "arguments": {}}},
                            {"function": {"name": "control_computer", "arguments": {}}},
                        ],
                    }
                }
            }
        )
        self.assertEqual(("open_music_widget",), client.chat("play some music").tool_names)

    def test_chat_history_is_bounded_and_content_is_clamped(self) -> None:
        client = FakeQwenClient({("POST", "/api/chat"): {"message": {"content": "hello"}}})
        history = tuple({"role": "user", "content": str(index) * 5_000} for index in range(20))
        client.chat("hi", history)
        messages = client.requests[0][2]["messages"]
        self.assertEqual(14, len(messages))  # system + 12 history + current user
        self.assertTrue(all(len(item["content"]) <= 4_000 for item in messages[1:-1]))

    def test_preload_and_unload_use_empty_local_generate_requests(self) -> None:
        client = FakeQwenClient({("POST", "/api/generate"): {"done": True}})
        client.preload()
        client.unload()
        self.assertEqual("30m", client.requests[0][2]["keep_alive"])
        self.assertEqual(0, client.requests[1][2]["keep_alive"])
        self.assertNotIn("prompt", client.requests[0][2])


if __name__ == "__main__":
    unittest.main()
