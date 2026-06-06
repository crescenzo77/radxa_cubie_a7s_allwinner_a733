#!/usr/bin/env python3
"""Record and summarize manual Cubie lab events."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVENT_LOG = REPO_ROOT / "tools" / "hardware-logs" / "cubie-events.jsonl"
EVENT_TYPES = [
    "manual-reset",
    "manual-power-on",
    "manual-power-off",
    "manual-power-cycle",
    "manual-note",
    "capture-start",
    "capture-end",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            event = {
                "event_type": "parse-error",
                "line": line_no,
                "error": str(exc),
                "raw": line,
            }
        events.append(event)
    return events


def resolve_log_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    else:
        path = path.resolve()

    allowed_root = (REPO_ROOT / "tools" / "hardware-logs").resolve()
    try:
        path.relative_to(allowed_root)
    except ValueError as exc:
        raise SystemExit(f"event log must stay under {allowed_root}: {path}") from exc
    return path


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.write(json.dumps(event, sort_keys=True))
        handle.write("\n")
        handle.flush()
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown(events: list[dict[str, Any]], limit: int) -> str:
    shown = events[-limit:] if limit > 0 else events
    lines = [
        "# Cubie Manual Event Log",
        "",
        f"events: `{len(events)}`",
        "",
        "| observed_at_utc | board | event_type | actor | note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for event in shown:
        lines.append(
            "| "
            f"{md_escape(event.get('observed_at_utc', 'unknown'))} | "
            f"{md_escape(event.get('board', 'unknown'))} | "
            f"{md_escape(event.get('event_type', 'unknown'))} | "
            f"{md_escape(event.get('actor', 'unknown'))} | "
            f"{md_escape(event.get('note', ''))} |"
        )
    if not shown:
        lines.append("| none | none | none | none | none |")
    return "\n".join(lines) + "\n"


def command_add(args: argparse.Namespace) -> int:
    log_path = resolve_log_path(args.log)
    event = {
        "observed_at_utc": args.observed_at or utc_now(),
        "board": args.board,
        "event_type": args.event,
        "actor": args.actor,
        "note": args.note,
        "source": "codex-desktop-manual-entry",
    }
    append_event(log_path, event)
    print(json.dumps(event, indent=2, sort_keys=True))
    return 0


def command_list(args: argparse.Namespace) -> int:
    events = read_events(resolve_log_path(args.log))
    if args.json:
        print(json.dumps(events, indent=2, sort_keys=True))
    else:
        print(markdown(events, args.limit), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record manual Cubie lab events.")
    parser.add_argument("--log", default=str(DEFAULT_EVENT_LOG))
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("--board", choices=["cubie2", "cubie3", "unknown"], required=True)
    add.add_argument("--event", choices=EVENT_TYPES, required=True)
    add.add_argument("--note", required=True)
    add.add_argument("--actor", default="human-operator")
    add.add_argument("--observed-at", default="", help="UTC timestamp override.")
    add.set_defaults(func=command_add)

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--limit", type=int, default=12)
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.set_defaults(func=command_list)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
