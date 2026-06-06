#!/usr/bin/env python3
"""Suggest Cubie board-to-UART mapping candidates from captured boot logs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_LOG_DIR = REPO_ROOT / "tools" / "hardware-logs" / "cubie-uart"
DEFAULT_EVENT_LOG = REPO_ROOT / "tools" / "hardware-logs" / "cubie-events.jsonl"

LABEL_RE = re.compile(r"(?:^|\s)label=([A-Za-z0-9_.-]+)")
DURING_LABEL_RE = re.compile(r"\bduring\s+([A-Za-z0-9_.-]+)\b")
MANUAL_EVENT_TYPES = {
    "manual-reset",
    "manual-power-on",
    "manual-power-off",
    "manual-power-cycle",
}
BOOT_MARKER_RE = re.compile(
    r"(U-Boot|SPL|DRAM|MMC|mmc|Starting kernel|Linux version|Kernel command line|"
    r"OF:|devicetree|console|login:|panic|Oops|ERROR|WARNING)",
    re.IGNORECASE,
)
LOGIN_BOARD_RE = re.compile(r"\b(cubie)[-_ ]?([23])\s+login:", re.IGNORECASE)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - diagnostics should keep going.
        return {"metadata_error": str(exc)}


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


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def log_for_meta(path: Path) -> Path:
    return path.with_suffix("") if path.name.endswith(".json") else path


def decode_log(path: Path, limit: int = 65536) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return ""
    text = path.read_bytes()[:limit].decode("utf-8", errors="replace")
    return "".join(ch if ch == "\n" or ch == "\t" or ord(ch) >= 32 else "." for ch in text)


def marker_lines(text: str, limit: int = 8) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or not BOOT_MARKER_RE.search(line):
            continue
        short = line[:180]
        if short in seen:
            continue
        seen.add(short)
        lines.append(short)
        if len(lines) >= limit:
            break
    return lines


def detected_boards(text: str) -> list[str]:
    boards = {f"{match.group(1).lower()}{match.group(2)}" for match in LOGIN_BOARD_RE.finditer(text)}
    return sorted(boards)


def extract_label(note: object) -> str:
    text = str(note or "")
    match = LABEL_RE.search(text)
    if match:
        return match.group(1)
    match = DURING_LABEL_RE.search(text)
    return match.group(1) if match else ""


def load_captures(log_dir: Path) -> list[dict[str, Any]]:
    captures: list[dict[str, Any]] = []
    for meta_path in sorted(log_dir.glob("*.uart.log.json")):
        meta = read_json(meta_path)
        log_path = log_for_meta(meta_path)
        text = decode_log(log_path)
        label = str(meta.get("label") or "")
        session_label = label.rsplit("-uart", 1)[0] if "-uart" in label else label
        captures.append(
            {
                "captured_at_utc": meta.get("captured_at_utc"),
                "label": label,
                "session_label": session_label,
                "device": meta.get("device"),
                "resolved_device": meta.get("resolved_device"),
                "bytes": log_path.stat().st_size if log_path.exists() else 0,
                "sha256": sha256_file(log_path),
                "markers": marker_lines(text),
                "detected_boards": detected_boards(text),
                "excerpt": text[:400],
                "metadata_error": meta.get("metadata_error"),
            }
        )
    return captures


def load_inventory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"boards": [], "uart_adapters": []}
    data = read_json(path)
    if not isinstance(data.get("boards"), list):
        data["boards"] = []
    if not isinstance(data.get("uart_adapters"), list):
        data["uart_adapters"] = []
    return data


def adapter_lookup(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_device: dict[str, dict[str, Any]] = {}
    for item in inventory.get("uart_adapters", []):
        if not isinstance(item, dict):
            continue
        for key in ("device", "by_path", "by_id"):
            value = item.get(key)
            if value:
                by_device[str(value)] = item
    return by_device


def session_events(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    sessions: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        label = extract_label(event.get("note"))
        if not label:
            continue
        sessions.setdefault(label, []).append(event)
    return sessions


def candidate_strength(captures: list[dict[str, Any]], events: list[dict[str, Any]]) -> str:
    non_empty = [item for item in captures if (item.get("bytes") or 0) > 0]
    detected = {
        board
        for item in non_empty
        for board in item.get("detected_boards", [])
        if board in {"cubie2", "cubie3"}
    }
    manual = [event for event in events if event.get("event_type") in MANUAL_EVENT_TYPES]
    boards = {event.get("board") for event in manual if event.get("board") in {"cubie2", "cubie3"}}
    if not non_empty:
        return "no-uart-output"
    if len(detected) == 1:
        return "strong-candidate"
    if len(non_empty) == 1 and len(boards) == 1:
        return "strong-candidate"
    if len(non_empty) == 1:
        return "uart-active-board-unknown"
    if len(boards) == 1:
        return "ambiguous-uart-multiple-active"
    return "ambiguous"


def md_escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def build_report(
    inventory: dict[str, Any],
    captures: list[dict[str, Any]],
    events: list[dict[str, Any]],
    log_dir: Path,
    inventory_path: Path,
    event_log_path: Path,
) -> tuple[str, dict[str, Any]]:
    adapters = adapter_lookup(inventory)
    events_by_label = session_events(events)
    captures_by_label: dict[str, list[dict[str, Any]]] = {}
    for capture in captures:
        captures_by_label.setdefault(str(capture["session_label"]), []).append(capture)

    labels = sorted(set(events_by_label) | set(captures_by_label))
    rows: list[dict[str, Any]] = []
    for label in labels:
        label_captures = captures_by_label.get(label, [])
        label_events = events_by_label.get(label, [])
        non_empty = [item for item in label_captures if (item.get("bytes") or 0) > 0]
        manual = [event for event in label_events if event.get("event_type") in MANUAL_EVENT_TYPES]
        manual_boards = sorted({str(event.get("board")) for event in manual if event.get("board")})
        detected = sorted(
            {
                board
                for item in label_captures
                for board in item.get("detected_boards", [])
                if board in {"cubie2", "cubie3"}
            }
        )
        strength = candidate_strength(label_captures, label_events)
        for capture in non_empty or label_captures:
            adapter = adapters.get(str(capture.get("resolved_device"))) or adapters.get(str(capture.get("device"))) or {}
            rows.append(
                {
                    "label": label,
                    "strength": strength,
                    "manual_boards": manual_boards,
                    "detected_boards": detected,
                    "capture_label": capture.get("label"),
                    "resolved_device": capture.get("resolved_device") or capture.get("device"),
                    "by_path": adapter.get("by_path", ""),
                    "bytes": capture.get("bytes"),
                    "markers": capture.get("markers", []),
                    "sha256": capture.get("sha256"),
                }
            )

    candidate_rows = [
        row for row in rows if row["strength"] != "no-uart-output" and (row.get("bytes") or 0) > 0
    ]
    data = {
        "generated_at_utc": utc_now(),
        "inventory": str(inventory_path),
        "log_dir": str(log_dir),
        "event_log": str(event_log_path),
        "session_count": len(labels),
        "capture_count": len(captures),
        "non_empty_capture_count": sum(1 for item in captures if (item.get("bytes") or 0) > 0),
        "candidate_count": len(candidate_rows),
        "rows": rows,
    }

    lines = [
        "# Cubie UART Mapping Candidates",
        "",
        f"Generated: `{data['generated_at_utc']}`",
        f"Log directory: `{log_dir}`",
        "",
        "This report is read-only. Do not update inventory until a human confirms the board that was reset or powered.",
        "",
        "## Summary",
        "",
        f"- sessions: `{data['session_count']}`",
        f"- captures: `{data['capture_count']}`",
        f"- non-empty captures: `{data['non_empty_capture_count']}`",
        f"- mapping candidates: `{data['candidate_count']}`",
        "",
        "## Candidate Rows",
        "",
        "| label | strength | manual_boards | detected_boards | capture_label | resolved_device | by_path | bytes | markers |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]

    if not rows:
        lines.append("| none | no-uart-output | none | none | none | none | 0 | none |")
    else:
        for row in rows:
            markers = "; ".join(row["markers"]) or "-"
            boards = ",".join(row["manual_boards"]) or "-"
            detected = ",".join(row.get("detected_boards", [])) or "-"
            lines.append(
                "| "
                f"{md_escape(row['label'])} | "
                f"{md_escape(row['strength'])} | "
                f"{md_escape(boards)} | "
                f"{md_escape(detected)} | "
                f"{md_escape(row['capture_label'])} | "
                f"`{md_escape(row['resolved_device'])}` | "
                f"`{md_escape(row['by_path'])}` | "
                f"{row['bytes']} | "
                f"{md_escape(markers)} |"
            )

    if not candidate_rows:
        lines.extend(["", "No non-empty UART captures are available yet, so no board-to-UART mapping can be proposed."])

    return "\n".join(lines).rstrip() + "\n", data


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest Cubie board-to-UART mapping candidates.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--dir", default=str(DEFAULT_LOG_DIR), help="Local UART log directory.")
    parser.add_argument("--event-log", default=str(DEFAULT_EVENT_LOG))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", default="", help="Optional report path.")
    args = parser.parse_args()

    inventory = load_inventory(Path(args.inventory))
    captures = load_captures(Path(args.dir))
    events = read_events(Path(args.event_log))
    report, data = build_report(
        inventory,
        captures,
        events,
        Path(args.dir),
        Path(args.inventory),
        Path(args.event_log),
    )

    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n" if args.json else report, encoding="utf-8")
        print(f"wrote={out}")
    elif args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
