#!/usr/bin/env python3
"""Build a concise Cubie runtime evidence packet."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_network_status
import cubie_event_log
import cubie_uart_map_candidates
import cubie_uart_report


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "task-packets" / "kernel" / "reviews"
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_EVENT_LOG = cubie_event_log.DEFAULT_EVENT_LOG


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def stamp_from_utc(value: str) -> str:
    base = value.rstrip("Z").split(".")[0]
    return base.replace("-", "").replace(":", "") + "Z"


def load_inventory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"boards": [], "observations": [], "inventory_missing": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def latest_observations(inventory: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    observations = inventory.get("observations", [])
    return observations[-limit:] if isinstance(observations, list) else []


def latest_events(path: Path, limit: int = 8) -> list[dict[str, Any]]:
    events = cubie_event_log.read_events(path)
    return events[-limit:] if limit > 0 else events


def md_escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "/").replace("\n", " ")


def board_rows(inventory: dict[str, Any]) -> list[str]:
    rows = ["| board | ip | uart mapping | power switch |", "| --- | --- | --- | --- |"]
    boards = inventory.get("boards", [])
    if not boards:
        rows.append("| unknown | unknown | unknown | unknown |")
        return rows
    for board in boards:
        if not isinstance(board, dict):
            continue
        uart = board.get("uart") or {}
        if not isinstance(uart, dict):
            uart = {}
        power = board.get("power_switch") or "unconfirmed"
        rows.append(
            "| "
            f"{md_escape(board.get('name', 'unknown'))} | "
            f"`{md_escape(board.get('ip', 'unknown'))}` | "
            f"{md_escape(uart.get('mapping_status', 'unknown'))} | "
            f"{md_escape(power)} |"
        )
    if len(rows) == 2:
        rows.append("| unknown | unknown | unknown | unknown |")
    return rows


def evidence_status(captures: list[dict[str, Any]], net: dict[str, Any]) -> tuple[str, list[str]]:
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    marker_hits = [item for item in captures if item.get("markers")]
    ssh_open = [item for item in net.get("results", []) if item.get("tcp_status") == "open"]
    notes = []
    if non_empty:
        status = "runtime-evidence-present"
        notes.append(f"{len(non_empty)} UART capture(s) contain data.")
    else:
        status = "runtime-evidence-missing"
        notes.append("No non-empty UART captures are available yet.")
    if marker_hits:
        notes.append(f"{len(marker_hits)} capture(s) include boot/error markers.")
    else:
        notes.append("No UART boot/error markers have been observed.")
    if ssh_open:
        boards = ", ".join(f"{item.get('board')}:{item.get('ip')}" for item in ssh_open)
        notes.append(f"SSH port is reachable on: {boards}.")
    else:
        notes.append("No Cubie SSH port is currently reachable.")
    return status, notes


def mapping_candidate_summary(
    inventory: dict[str, Any],
    inventory_path: Path,
    log_dir: Path,
    event_log: Path,
) -> dict[str, Any]:
    map_inventory = cubie_uart_map_candidates.load_inventory(inventory_path)
    if not map_inventory.get("uart_adapters"):
        map_inventory = inventory
    captures = cubie_uart_map_candidates.load_captures(log_dir)
    events = cubie_uart_map_candidates.read_events(event_log)
    _report, data = cubie_uart_map_candidates.build_report(
        map_inventory,
        captures,
        events,
        log_dir,
        inventory_path,
        event_log,
    )
    rows = [
        row
        for row in data.get("rows", [])
        if row.get("strength") != "no-uart-output" and (row.get("bytes") or 0) > 0
    ]
    return {
        "candidate_count": data.get("candidate_count", 0),
        "non_empty_capture_count": data.get("non_empty_capture_count", 0),
        "session_count": data.get("session_count", 0),
        "rows": rows[-6:],
    }


def mapping_rows(summary: dict[str, Any]) -> list[str]:
    lines = [
        "| label | strength | manual_boards | resolved_device | by_path | bytes | markers |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    rows = summary.get("rows", [])
    if not rows:
        lines.append("| none | no-candidate | none | none | none | 0 | none |")
        return lines
    for row in rows:
        markers = "; ".join(str(marker) for marker in (row.get("markers") or [])) or "-"
        boards = ",".join(str(board) for board in (row.get("manual_boards") or [])) or "-"
        lines.append(
            "| "
            f"{md_escape(row.get('label'))} | "
            f"{md_escape(row.get('strength'))} | "
            f"{md_escape(boards)} | "
            f"`{md_escape(row.get('resolved_device'))}` | "
            f"`{md_escape(row.get('by_path'))}` | "
            f"{row.get('bytes')} | "
            f"{md_escape(markers)} |"
        )
    return lines


def build_packet(
    inventory_path: Path,
    log_dir: Path,
    event_log: Path,
    network_timeout: float,
    port: int,
    generated_at: str,
) -> str:
    inventory = load_inventory(inventory_path)
    boards = cubie_network_status.load_boards(inventory_path)
    net = cubie_network_status.check_boards(boards, network_timeout, port)
    captures = cubie_uart_report.load_captures(log_dir)
    events = latest_events(event_log)
    status, notes = evidence_status(captures, net)
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    mapping = mapping_candidate_summary(inventory, inventory_path, log_dir, event_log)

    lines = [
        "# Cubie Runtime Evidence Packet",
        "",
        f"Generated: `{generated_at}`",
        f"Inventory: `{inventory_path}`",
        f"UART log directory: `{log_dir}`",
        f"Manual event log: `{event_log}`",
        f"Evidence status: `{status}`",
        "",
        "## Boards",
        "",
        *board_rows(inventory),
        "",
        "## Network Check",
        "",
        "| board | ip | ping | tcp_port | tcp_status |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for item in net.get("results", []):
        lines.append(
            "| "
            f"{item.get('board')} | "
            f"`{item.get('ip')}` | "
            f"{item.get('ping')} | "
            f"{item.get('tcp_port')} | "
            f"{item.get('tcp_status')} |"
        )

    lines.extend(["", "## UART Evidence", ""])
    for note in notes:
        lines.append(f"- {note}")
    lines.extend(
        [
            f"- total captures: `{len(captures)}`",
            f"- non-empty captures: `{len(non_empty)}`",
            "",
        ]
    )

    if non_empty:
        lines.append("### Non-Empty Capture Excerpts")
        lines.append("")
        for item in non_empty[-4:]:
            lines.extend(
                [
                    f"#### {item.get('captured_at_utc')} {item.get('label')}",
                    "",
                    f"- device: `{item.get('device')}`",
                    f"- resolved device: `{item.get('resolved_device')}`",
                    f"- bytes: `{item.get('local_bytes')}`",
                    f"- sha256: `{item.get('local_sha256')}`",
                    "",
                    "```text",
                    str(item.get("excerpt") or "").rstrip(),
                    "```",
                    "",
                ]
            )
    else:
        lines.append("No runtime boot proof can be claimed from UART yet.")
        lines.append("")

    lines.extend(
        [
            "## UART Mapping Candidates",
            "",
            f"- sessions scanned: `{mapping.get('session_count', 0)}`",
            f"- non-empty captures: `{mapping.get('non_empty_capture_count', 0)}`",
            f"- mapping candidates: `{mapping.get('candidate_count', 0)}`",
            "",
            *mapping_rows(mapping),
            "",
        ]
    )
    if not mapping.get("candidate_count"):
        lines.append("No board-to-UART mapping candidate can be proposed yet.")
        lines.append("")

    lines.extend(
        [
            "## Manual Events",
            "",
            "| observed_at_utc | board | event_type | actor | note |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if events:
        for event in events:
            lines.append(
                "| "
                f"{md_escape(event.get('observed_at_utc', 'unknown'))} | "
                f"{md_escape(event.get('board', 'unknown'))} | "
                f"{md_escape(event.get('event_type', 'unknown'))} | "
                f"{md_escape(event.get('actor', 'unknown'))} | "
                f"{md_escape(event.get('note', ''))} |"
            )
    else:
        lines.append("| none | none | none | none | none |")
    lines.append("")

    lines.extend(["## Recent Observations", ""])
    for obs in latest_observations(inventory):
        observed_at = obs.get("observed_at_utc", "unknown")
        obs_type = obs.get("type", "unknown")
        conclusion = obs.get("conclusion", "no conclusion")
        lines.append(f"- `{observed_at}` `{obs_type}`: {conclusion}")
    if not latest_observations(inventory):
        lines.append("- No inventory observations recorded.")

    lines.extend(
        [
            "",
            "## Next Safe Action",
            "",
            "Run `scripts/cubie-manual-boot-session 120 cubie-manual-boot`, "
            "then have the human operator manually reset or power exactly one "
            "Cubie board. Do not automate power and do not assume UART mapping "
            "until boot text identifies the board.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Cubie runtime evidence packet.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--log-dir", default=str(cubie_uart_report.DEFAULT_LOG_DIR))
    parser.add_argument("--event-log", default=str(DEFAULT_EVENT_LOG))
    parser.add_argument("--network-timeout", type=float, default=1.0)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--write", default="", help="Optional output path. Defaults to timestamped review packet.")
    args = parser.parse_args()

    generated_at = utc_now()
    packet = build_packet(
        Path(args.inventory),
        Path(args.log_dir),
        Path(args.event_log),
        max(0.2, args.network_timeout),
        args.port,
        generated_at,
    )
    if args.write:
        out = Path(args.write)
    else:
        stamp = stamp_from_utc(generated_at)
        out = DEFAULT_OUT_DIR / f"cubie-runtime-evidence-{stamp}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(packet, encoding="utf-8")
    print(f"wrote={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
