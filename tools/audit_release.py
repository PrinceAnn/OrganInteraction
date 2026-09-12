#!/usr/bin/env python3
"""Fail when a release tree contains common data or disclosure hazards."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess


BLOCKED_SUFFIXES = {
    ".7z", ".bed", ".bgen", ".bim", ".csv", ".fam", ".feather", ".gz",
    ".h5", ".hdf5", ".ipynb", ".jpeg", ".jpg", ".log", ".parquet",
    ".pdf", ".pickle", ".pkl", ".png", ".rdata", ".rds", ".svg", ".tar",
    ".tgz", ".tsv", ".vcf", ".xls", ".xlsx", ".zip",
}
BLOCKED_NAMES = {".env", ".rhistory", ".rdata", "core"}
SKIP_DIRECTORIES = {
    ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv",
    "__pycache__", "artifacts", "build", "dist", "local-data", "local-results",
    "outputs", "results", "venv",
}
MAX_FILE_BYTES = 1_000_000


def candidate_files(root: Path) -> list[Path]:
    """Use the Git index when available, otherwise audit the source tree."""
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0 and completed.stdout.strip():
        return sorted(root / line for line in completed.stdout.splitlines())
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts)
    )


def local_git_tokens(root: Path) -> list[str]:
    """Read private deny tokens from local Git configuration, never tracked files."""
    completed = subprocess.run(
        ["git", "-C", str(root), "config", "--local", "--get-all", "indnet.restrictedToken"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode not in (0, 1):
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def text_hazards(text: str, deny_tokens: list[str]) -> list[str]:
    hazards: list[str] = []
    lowered = text.casefold()
    for token in deny_tokens:
        if token and token.casefold() in lowered:
            hazards.append("restricted token")
    personal_roots = ["/" + "home" + "/", "/" + "users" + "/"]
    if any(root in lowered for root in personal_roots):
        hazards.append("absolute user path")
    private_key_marker = "begin " + "private key"
    if private_key_marker in lowered:
        hazards.append("private key material")
    assignment = re.compile(r"(?i)(password|api[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"]+['\"]")
    if assignment.search(text):
        hazards.append("hard-coded credential")
    return hazards


def audit(root: Path, deny_tokens: list[str]) -> list[str]:
    failures: list[str] = []
    for path in candidate_files(root):
        relative = path.relative_to(root)
        relative_text = relative.as_posix().casefold()
        lower_name = path.name.casefold()
        suffixes = {suffix.casefold() for suffix in path.suffixes}
        if any(token and token.casefold() in relative_text for token in deny_tokens):
            failures.append(f"{relative}: restricted token in path")
            continue
        if lower_name in BLOCKED_NAMES or suffixes.intersection(BLOCKED_SUFFIXES):
            failures.append(f"{relative}: blocked file type")
            continue
        if lower_name.startswith("core."):
            failures.append(f"{relative}: crash dump")
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            failures.append(f"{relative}: file exceeds {MAX_FILE_BYTES} bytes")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"{relative}: unexpected binary content")
            continue
        for hazard in text_hazards(text, deny_tokens):
            failures.append(f"{relative}: {hazard}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--deny-token", action="append", default=[])
    args = parser.parse_args()
    environment_tokens = [
        token.strip() for token in os.environ.get("RELEASE_DENY_TOKENS", "").split(",") if token.strip()
    ]
    root = args.root.resolve()
    deny_tokens = [*args.deny_token, *environment_tokens, *local_git_tokens(root)]
    failures = audit(root, deny_tokens)
    if failures:
        print("Release audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Release audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
