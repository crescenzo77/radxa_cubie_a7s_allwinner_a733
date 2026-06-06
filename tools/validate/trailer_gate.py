#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Gate exported patches against unauthorized metadata trailers."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


TRAILER_RE = re.compile(r"^([A-Za-z0-9-]+):\s*(.+)$")
FORBIDDEN_RE = re.compile(
    r"(OpenAI|ChatGPT|GPT-[0-9]|GPT|Codex|Claude|Anthropic|Gemini|Llama|Qwen|AI-assisted|AI generated)",
    re.IGNORECASE,
)
DEFAULT_ALLOWED = {
    "Signed-off-by": {"Enzo Adriano <enzo.adriano.code@gmail.com>"},
}


def split_allowed(items: list[str]) -> dict[str, set[str] | None]:
    allowed: dict[str, set[str] | None] = {key: set(values) for key, values in DEFAULT_ALLOWED.items()}
    for item in items:
        if "=" in item:
            key, value = item.split("=", 1)
            allowed.setdefault(key.strip(), set())
            values = allowed[key.strip()]
            if values is not None:
                values.add(value.strip())
        else:
            allowed[item.strip()] = None
    return allowed


def commit_message_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    try:
        start = lines.index("")
    except ValueError:
        start = 0
    message = []
    for line in lines[start + 1 :]:
        if line == "---":
            break
        message.append(line)
    return message


def classify_patch(path: Path, allowed: dict[str, set[str] | None]) -> dict[str, Any]:
    message = commit_message_lines(path)
    trailers = []
    forbidden_hits = []
    unapproved = []
    for lineno, line in enumerate(message, start=1):
        match = TRAILER_RE.match(line.strip())
        if not match:
            if FORBIDDEN_RE.search(line):
                forbidden_hits.append({"line": lineno, "text": line})
            continue
        name, value = match.groups()
        trailer = {"line": lineno, "name": name, "value": value}
        trailers.append(trailer)
        if FORBIDDEN_RE.search(name) or FORBIDDEN_RE.search(value):
            forbidden_hits.append({"line": lineno, "text": line})
        allowed_values = allowed.get(name)
        if name not in allowed:
            unapproved.append({**trailer, "reason": "trailer-name-not-allowed"})
        elif allowed_values is not None and value not in allowed_values:
            unapproved.append({**trailer, "reason": "trailer-value-not-allowed"})

    return {
        "patch": str(path),
        "trailers": trailers,
        "forbidden_metadata": forbidden_hits,
        "unapproved": unapproved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allowed-trailer", action="append", default=[], help="NAME or NAME=value; default permits Enzo's Signed-off-by only.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("patches", nargs="+")
    args = parser.parse_args()

    allowed = split_allowed(args.allowed_trailer)
    patches = [Path(item).resolve() for item in args.patches]
    reports = [classify_patch(path, allowed) for path in patches]
    unapproved = [report for report in reports if report["forbidden_metadata"] or report["unapproved"]]
    status = "PASS" if not unapproved else "FAIL"
    result = {
        "status": status,
        "allowed_trailers": {
            key: sorted(values) if values is not None else ["*"]
            for key, values in sorted(allowed.items())
        },
        "patches": reports,
        "unapproved_count": len(unapproved),
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status={status}")
        print(f"patches={len(patches)}")
        print(f"unapproved={len(unapproved)}")
        for report in reports:
            if report["trailers"] or report["forbidden_metadata"] or report["unapproved"]:
                print(f"patch={report['patch']}")
                for trailer in report["trailers"]:
                    print(f"  trailer={trailer['name']}: {trailer['value']}")
                for hit in report["forbidden_metadata"]:
                    print(f"  forbidden_metadata_line={hit['line']}: {hit['text']}")
                for item in report["unapproved"]:
                    print(f"  unapproved={item['name']}: {item['value']} reason={item['reason']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
