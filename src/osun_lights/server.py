from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .runtime import LightingController


MAX_BODY_BYTES = 32_768


def _edge_path() -> str | None:
    candidates = [
        shutil.which("msedge"),
        str(Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
        str(Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
    ]
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


class OsunServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], controller: LightingController, session_token: str) -> None:
        self.controller = controller
        self.session_token = session_token
        self.asset_dir = Path(__file__).with_name("web")
        super().__init__(address, OsunRequestHandler)


class OsunRequestHandler(BaseHTTPRequestHandler):
    server: OsunServer

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        app_prefix = f"/app/{self.server.session_token}"
        api_prefix = f"/api/{self.server.session_token}"
        if parsed.path in {app_prefix, f"{app_prefix}/"}:
            self._file("index.html", "text/html; charset=utf-8")
            return
        if parsed.path == f"{app_prefix}/styles.css":
            self._file("styles.css", "text/css; charset=utf-8")
            return
        if parsed.path == f"{app_prefix}/app.js":
            self._file("app.js", "text/javascript; charset=utf-8")
            return
        if parsed.path == f"{api_prefix}/status":
            self._json(200, self.server.controller.status())
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        prefix = f"/api/{self.server.session_token}"
        if not parsed.path.startswith(prefix + "/"):
            self._json(404, {"error": "not_found"})
            return
        try:
            payload = self._read_json()
            route = parsed.path.removeprefix(prefix)
            if route == "/message":
                selected = payload.get("selected_entities", [])
                if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
                    raise ValueError("selected_entities must be a list")
                result = self.server.controller.message(str(payload.get("text", "")), tuple(selected))
            elif route == "/apply":
                result = self.server.controller.apply(str(payload.get("proposal_id", "")))
            elif route == "/cancel":
                result = self.server.controller.cancel()
            elif route == "/pause":
                result = self.server.controller.pause()
            elif route == "/settings/test":
                result = self.server.controller.test_connection(
                    str(payload.get("home_assistant_url", "")), str(payload.get("token", ""))
                )
            elif route == "/settings/save":
                result = self.server.controller.save_settings(payload)
            elif route == "/settings/delete-token":
                result = self.server.controller.delete_credential()
            elif route == "/shutdown":
                result = {"shutting_down": True}
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                self._json(404, {"error": "not_found"})
                return
            self._json(200, result)
        except (ValueError, RuntimeError, OSError) as exc:
            self._json(400, {"error": str(exc)})
        except Exception:
            self._json(500, {"error": "The local lighting service failed safely"})

    def _read_json(self) -> dict[str, Any]:
        origin = self.headers.get("Origin")
        expected_origin = f"http://127.0.0.1:{self.server.server_port}"
        if origin and origin != expected_origin:
            raise ValueError("Cross-origin request denied")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Invalid request length") from None
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Request body must be valid JSON") from None
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object")
        return payload

    def _file(self, name: str, content_type: str) -> None:
        path = self.server.asset_dir / name
        try:
            data = path.read_bytes()
        except OSError:
            self._json(404, {"error": "asset_not_found"})
            return
        self.send_response(200)
        self._headers(content_type, len(data))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status: int, payload: Any) -> None:
        data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._headers("application/json; charset=utf-8", len(data))
        self.end_headers()
        self.wfile.write(data)

    def _headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
        )

    def log_message(self, _format: str, *_args: object) -> None:
        return


def run(*, open_browser: bool = True, port: int = 0, session_token: str | None = None) -> None:
    session_token = session_token or secrets.token_urlsafe(24)
    controller = LightingController()
    server = OsunServer(("127.0.0.1", port), controller, session_token)
    url = f"http://127.0.0.1:{server.server_port}/app/{session_token}/"
    if open_browser:
        edge = _edge_path()
        if edge:
            subprocess.Popen([edge, f"--app={url}", "--new-window"], close_fds=True)
        else:
            webbrowser.open(url, new=1)
    print(f"Osun Lighting Assistant is running locally at {url}")
    print("Close the app with its Quit button or press Ctrl+C here.")
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Osun Lighting Assistant")
    parser.add_argument("--no-browser", action="store_true", help="Run the loopback service without opening a window")
    parser.add_argument("--port", type=int, default=0, help="Loopback port; zero chooses a free port")
    parser.add_argument("--session-token", help="Fixed local session path for testing only")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    run(open_browser=not args.no_browser, port=args.port, session_token=args.session_token)


if __name__ == "__main__":
    main()
