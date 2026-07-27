from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_SCANNED_BYTES = 2_000_000
WORKFLOW_DIR = Path(".github/workflows")
MERGE_WORKFLOW = WORKFLOW_DIR / "merge-gate.yml"

FORBIDDEN_NAMES = {
    ".env",
    "credential.bin",
    "credentials.bin",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,255}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("Slack token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{20,}")),
)
ACTION_REFERENCE = re.compile(r"(?m)^\s*-?\s*uses:\s*([^\s#]+)")
IMMUTABLE_ACTION = re.compile(r"^[^/@\s]+/[^@\s]+(?:/[^@\s]+)?@[0-9a-fA-F]{40}$")


def tracked_files() -> tuple[Path, ...]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return tuple(Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item)


def inspect_text(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(f"{path.as_posix()}: contains a possible {label}")

    if path.parts[:2] == WORKFLOW_DIR.parts:
        if "pull_request_target:" in text:
            findings.append(f"{path.as_posix()}: pull_request_target is prohibited")
        if re.search(r"(?m)^\s*permissions:\s*write-all\s*$", text):
            findings.append(f"{path.as_posix()}: write-all workflow permissions are prohibited")
        if re.search(r"(?m)^\s*[a-z-]+:\s*write\s*$", text):
            findings.append(f"{path.as_posix()}: write permissions require an explicit security review")
        for reference in ACTION_REFERENCE.findall(text):
            if not reference.startswith("./") and not IMMUTABLE_ACTION.fullmatch(reference):
                findings.append(f"{path.as_posix()}: action is not pinned to a full commit SHA: {reference}")

    if path == MERGE_WORKFLOW:
        required_fragments = (
            "pull_request:",
            "merge_group:",
            "permissions:",
            "contents: read",
            "Merge gate passed",
            "python scripts/security_gate.py",
        )
        for fragment in required_fragments:
            if fragment not in text:
                findings.append(f"{path.as_posix()}: missing required merge control: {fragment}")
    return findings


def inspect_path(path: Path) -> list[str]:
    findings: list[str] = []
    lowered_name = path.name.casefold()
    if lowered_name in FORBIDDEN_NAMES or (lowered_name.startswith(".env.") and lowered_name != ".env.example"):
        findings.append(f"{path.as_posix()}: credential-bearing filename must not be tracked")
    if path.suffix.casefold() in {".key", ".p12", ".pfx", ".pem"}:
        findings.append(f"{path.as_posix()}: private credential container must not be tracked")

    absolute = ROOT / path
    data = absolute.read_bytes()
    if len(data) > MAX_SCANNED_BYTES or b"\0" in data:
        return findings
    return findings + inspect_text(path, data.decode("utf-8", errors="replace"))


def run() -> list[str]:
    files = tracked_files()
    findings = [finding for path in files for finding in inspect_path(path)]
    if MERGE_WORKFLOW not in files:
        findings.append(f"{MERGE_WORKFLOW.as_posix()}: required merge workflow is not tracked")
    return findings


def main() -> int:
    findings = run()
    if findings:
        print("Security gate failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("Security gate passed: tracked secrets, workflow permissions, and action pins are clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
