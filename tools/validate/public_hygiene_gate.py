#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Scan a public kernel-facing repo for private lab or AI metadata leaks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_EXTENSIONS = {".md", ".patch", ".txt"}
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache"}
FORBIDDEN_PATTERNS = {
    "private-ipv4": re.compile(r"\b(?:10|192\.168|172\.(?:1[6-9]|2[0-9]|3[0-1]))(?:\.\d{1,3}){2}\b"),
    "ai-provider": re.compile(r"\b(?:OpenAI|ChatGPT|Codex|Claude|Anthropic|Gemini)\b", re.IGNORECASE),
    "ai-metadata": re.compile(r"\b(?:Assisted-by|Generated-by|AI-assisted|AI generated|GPT-[0-9]|GPT)\b", re.IGNORECASE),
    "local-model-stack": re.compile(r"\b(?:Qwen|llama\.cpp|vLLM|model-dispatch|Open WebUI|OpenRouter)\b", re.IGNORECASE),
    "lab-hostname": re.compile(r"\b(?:strix|thinkcentre|mac[- ]?mini|framework laptop)\b", re.IGNORECASE),
    "gpu-detail": re.compile(r"\b(?:RTX 3090|7900 ?XT)\b", re.IGNORECASE),
    "private-path": re.compile(r"(?:/Users/enzo|/home/enzo|/srv/projects|\.ssh/)"),
    "non-kernel-local-topic": re.compile(r"\b(?:telegram|wyze|object detection)\b", re.IGNORECASE),
}


def iter_files(root: Path) -> list[Path]:
    if (root / ".git").exists():
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(proc.stderr.strip() or "git ls-files failed")
        return [
            root / line
            for line in sorted(proc.stdout.splitlines())
            if (root / line).is_file()
            and ((root / line).name == "README.md" or (root / line).suffix in DEFAULT_EXTENSIONS)
        ]

    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        if not path.is_file():
            continue
        if path.name in {"README.md"} or path.suffix in DEFAULT_EXTENSIONS:
            files.append(path)
    return sorted(files)


def scan_file(root: Path, path: Path) -> list[dict[str, Any]]:
    rel = str(path.relative_to(root))
    matches: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
        return [{"path": rel, "line": 0, "kind": "read-error", "text": str(exc)}]
    for lineno, line in enumerate(lines, start=1):
        for kind, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(line):
                matches.append({"path": rel, "line": lineno, "kind": kind, "text": line.strip()})
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    files = iter_files(root)
    matches: list[dict[str, Any]] = []
    for path in files:
        matches.extend(scan_file(root, path))

    status = "PASS" if not matches else "FAIL"
    result = {
        "status": status,
        "root": str(root),
        "files_scanned": len(files),
        "matches": matches,
        "match_count": len(matches),
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status={status}")
        print(f"files_scanned={len(files)}")
        print(f"matches={len(matches)}")
        for item in matches:
            print(f"{item['path']}:{item['line']}: {item['kind']}: {item['text']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
