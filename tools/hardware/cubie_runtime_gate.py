#!/usr/bin/env python3
"""Deterministically classify Cubie runtime evidence readiness."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_event_log
import cubie_network_status
import cubie_uart_map_candidates
import cubie_uart_report


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_EVENT_LOG = cubie_event_log.DEFAULT_EVENT_LOG


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def load_inventory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"boards": [], "uart_adapters": [], "inventory_missing": str(path)}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"boards": [], "uart_adapters": [], "inventory_error": str(exc)}
    return data if isinstance(data, dict) else {"boards": [], "uart_adapters": []}


def mapping_summary(inventory: dict[str, Any], inventory_path: Path, log_dir: Path, event_log: Path) -> dict[str, Any]:
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
    candidates = [
        row
        for row in data.get("rows", [])
        if row.get("strength") != "no-uart-output" and (row.get("bytes") or 0) > 0
    ]
    strong = [row for row in candidates if row.get("strength") == "strong-candidate"]
    return {
        "candidate_count": len(candidates),
        "strong_candidate_count": len(strong),
        "rows": candidates[-6:],
    }


def network_summary(inventory_path: Path, timeout: float, port: int, skip: bool) -> dict[str, Any]:
    if skip:
        return {"skipped": True, "results": []}
    boards = cubie_network_status.load_boards(inventory_path)
    return cubie_network_status.check_boards(boards, max(0.2, timeout), port)


def classify(captures: list[dict[str, Any]], mapping: dict[str, Any]) -> tuple[str, str]:
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    marker_hits = [item for item in captures if item.get("markers")]
    strong = mapping.get("strong_candidate_count", 0)
    candidates = mapping.get("candidate_count", 0)

    if marker_hits and strong:
        return "runtime-ready", "boot markers and a strong board-to-UART candidate are present"
    if marker_hits and candidates:
        return "mapping-needs-human-confirmation", "boot markers exist, but mapping candidate is not strong"
    if marker_hits:
        return "boot-text-unmapped", "boot markers exist, but no board-to-UART candidate is available"
    if non_empty:
        return "uart-data-needs-triage", "UART data exists but no known boot markers were detected"
    return "manual-capture-required", "no non-empty UART capture exists"


def next_action(status: str) -> str:
    if status == "inventory-invalid":
        return "fix the Cubie hardware inventory before relying on runtime evidence"
    if status == "runtime-ready":
        return "human should inspect the evidence packet before updating inventory or relying on the mapping"
    if status == "mapping-needs-human-confirmation":
        return "human should confirm which board was reset before updating inventory"
    if status == "boot-text-unmapped":
        return "record the manual action with label=... and rerun the mapping candidate report"
    if status == "uart-data-needs-triage":
        return "inspect non-empty UART excerpts for baud, wiring, or nonstandard boot text"
    return "run scripts/cubie-manual-boot-session 120 cubie-manual-boot and manually reset exactly one Cubie"


def build_gate(args: argparse.Namespace) -> dict[str, Any]:
    inventory_path = Path(args.inventory)
    log_dir = Path(args.log_dir)
    event_log = Path(args.event_log)
    inventory = load_inventory(inventory_path)
    captures = cubie_uart_report.load_captures(log_dir)
    mapping = mapping_summary(inventory, inventory_path, log_dir, event_log)
    network = network_summary(inventory_path, args.network_timeout, args.port, args.skip_network)
    if inventory.get("inventory_error") or inventory.get("inventory_missing"):
        status = "inventory-invalid"
        reason = str(inventory.get("inventory_error") or inventory.get("inventory_missing"))
    else:
        status, reason = classify(captures, mapping)
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    marker_hits = [item for item in captures if item.get("markers")]
    ssh_open = [item for item in network.get("results", []) if item.get("tcp_status") == "open"]

    return {
        "generated_at_utc": utc_now(),
        "status": status,
        "reason": reason,
        "next_action": next_action(status),
        "inventory": str(inventory_path),
        "inventory_error": inventory.get("inventory_error", ""),
        "inventory_missing": inventory.get("inventory_missing", ""),
        "log_dir": str(log_dir),
        "event_log": str(event_log),
        "captures": {
            "total": len(captures),
            "non_empty": len(non_empty),
            "with_boot_markers": len(marker_hits),
        },
        "mapping": mapping,
        "network": {
            "skipped": bool(network.get("skipped")),
            "ssh_open": [f"{item.get('board')}:{item.get('ip')}" for item in ssh_open],
            "results": network.get("results", []),
        },
    }


def md_escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "/").replace("\n", " ")


def markdown(data: dict[str, Any]) -> str:
    captures = data["captures"]
    mapping = data["mapping"]
    lines = [
        "# Cubie Runtime Gate",
        "",
        f"Generated: `{data['generated_at_utc']}`",
        f"Status: `{data['status']}`",
        f"Reason: {data['reason']}",
        "",
        "## Counts",
        "",
        f"- captures: `{captures['total']}`",
        f"- non-empty captures: `{captures['non_empty']}`",
        f"- captures with boot markers: `{captures['with_boot_markers']}`",
        f"- mapping candidates: `{mapping['candidate_count']}`",
        f"- strong mapping candidates: `{mapping['strong_candidate_count']}`",
        "",
        "## Network",
        "",
    ]
    if data["network"]["skipped"]:
        lines.append("- skipped")
    elif data["network"]["ssh_open"]:
        lines.append(f"- SSH open: {', '.join(data['network']['ssh_open'])}")
    else:
        lines.append("- no SSH port currently open")

    lines.extend(
        [
            "",
            "## Mapping Candidates",
            "",
            "| label | strength | manual_boards | resolved_device | by_path | bytes |",
            "| --- | --- | --- | --- | --- | ---: |",
        ]
    )
    rows = mapping.get("rows", [])
    if rows:
        for row in rows:
            boards = ",".join(str(board) for board in (row.get("manual_boards") or [])) or "-"
            lines.append(
                "| "
                f"{md_escape(row.get('label'))} | "
                f"{md_escape(row.get('strength'))} | "
                f"{md_escape(boards)} | "
                f"`{md_escape(row.get('resolved_device'))}` | "
                f"`{md_escape(row.get('by_path'))}` | "
                f"{row.get('bytes')} |"
            )
    else:
        lines.append("| none | none | none | none | none | 0 |")

    lines.extend(["", "## Next Action", "", data["next_action"], ""])
    return "\n".join(lines)


def strict_exit_code(status: str) -> int:
    return 0 if status == "runtime-ready" else 20


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify Cubie runtime evidence readiness.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--log-dir", default=str(cubie_uart_report.DEFAULT_LOG_DIR))
    parser.add_argument("--event-log", default=str(DEFAULT_EVENT_LOG))
    parser.add_argument("--network-timeout", type=float, default=1.0)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--skip-network", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero unless status is runtime-ready.")
    args = parser.parse_args()

    data = build_gate(args)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown(data))
    return strict_exit_code(data["status"]) if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
