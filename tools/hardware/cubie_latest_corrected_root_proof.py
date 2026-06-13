#!/usr/bin/env python3
"""Run the corrected-root proof gate on the latest UART log for a label."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import cubie_uart_report


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG_DIR = cubie_uart_report.DEFAULT_LOG_DIR
DEFAULT_LABEL = "a733-v4-abc8d07b0a63-partuuid-ro-proof"


def safe_label(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "_.-" else "-" for ch in value)


def log_for_meta(path: Path) -> Path:
    return path.with_suffix("") if path.name.endswith(".json") else path


def capture_stamp(meta_path: Path, meta: dict[str, object]) -> str:
    stamp = str(meta.get("captured_at_utc") or "")
    if stamp:
        return stamp
    head = meta_path.name.split("-", 1)[0]
    return head if head.startswith("20") and head.endswith("Z") else ""


def find_latest(log_dir: Path, label: str, *, prefix_ok: bool = True) -> Path | None:
    wanted = safe_label(label)
    matches: list[tuple[str, Path]] = []
    for meta_path in sorted(log_dir.glob("*.uart.log.json")):
        meta = cubie_uart_report.read_meta(meta_path)
        capture_label = str(meta.get("label") or "")
        log_path = log_for_meta(meta_path)
        if not log_path.exists():
            continue
        stamp = capture_stamp(meta_path, meta)
        if capture_label == wanted or (prefix_ok and capture_label.startswith(f"{wanted}-")):
            matches.append((stamp, log_path))
    if not matches:
        return None
    return sorted(matches)[-1][1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument(
        "--exact-label",
        action="store_true",
        help="Only match the exact capture label; by default board/retry suffixes are accepted.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    log_path = find_latest(Path(args.log_dir), args.label, prefix_ok=not args.exact_label)
    if not log_path:
        payload = {
            "status": "missing-log",
            "label": safe_label(args.label),
            "log_dir": str(Path(args.log_dir)),
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"status=missing-log label={payload['label']} log_dir={payload['log_dir']}")
        return 1 if args.strict else 0

    gate = REPO_ROOT / "scripts" / "cubie-corrected-root-proof-gate"
    argv = [str(gate), str(log_path)]
    if args.json:
        argv.append("--json")
    if args.strict:
        argv.append("--strict")
    return subprocess.run(argv, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
