#!/usr/bin/env python3
"""Build read-only Cubie UART inventory update proposals."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import difflib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_event_log
import cubie_uart_map_candidates


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_LOG_DIR = REPO_ROOT / "tools" / "hardware-logs" / "cubie-uart"
DEFAULT_EVENT_LOG = cubie_event_log.DEFAULT_EVENT_LOG


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def load_inventory(path: Path) -> dict[str, Any]:
    return cubie_uart_map_candidates.load_inventory(path)


def board_by_name(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    boards: dict[str, dict[str, Any]] = {}
    for item in inventory.get("boards", []):
        if isinstance(item, dict) and item.get("name"):
            boards[str(item["name"])] = item
    return boards


def adapter_by_device(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    adapters: dict[str, dict[str, Any]] = {}
    for item in inventory.get("uart_adapters", []):
        if not isinstance(item, dict):
            continue
        for key in ("device", "by_path", "by_id"):
            value = item.get(key)
            if value:
                adapters[str(value)] = item
    return adapters


def candidate_rows(inventory: dict[str, Any], inventory_path: Path, log_dir: Path, event_log: Path) -> list[dict[str, Any]]:
    captures = cubie_uart_map_candidates.load_captures(log_dir)
    events = cubie_uart_map_candidates.read_events(event_log)
    _report, data = cubie_uart_map_candidates.build_report(
        inventory,
        captures,
        events,
        log_dir,
        inventory_path,
        event_log,
    )
    return [
        row
        for row in data.get("rows", [])
        if row.get("strength") == "strong-candidate" and (row.get("bytes") or 0) > 0
    ]


def proposal_for_row(row: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any] | None:
    boards = [
        board
        for board in (row.get("detected_boards") or row.get("manual_boards", []))
        if board in {"cubie2", "cubie3"}
    ]
    if len(boards) != 1:
        return None
    board_name = boards[0]
    board = board_by_name(inventory).get(board_name, {})
    current_uart = board.get("uart") if isinstance(board.get("uart"), dict) else {}
    proposed_device = row.get("by_path") or row.get("resolved_device")
    if (
        current_uart.get("device") == proposed_device
        and str(current_uart.get("mapping_status", "")).startswith("confirmed")
    ):
        return None
    adapter = (
        adapter_by_device(inventory).get(str(row.get("by_path")))
        or adapter_by_device(inventory).get(str(row.get("resolved_device")))
        or {}
    )
    host = current_uart.get("host") or adapter.get("host") or inventory.get("uart_host") or "unknown"
    proposed_uart = {
        "host": host,
        "device": proposed_device,
        "resolved_device": row.get("resolved_device"),
        "baud": current_uart.get("baud") or 115200,
        "mapping_status": "candidate-needs-human-confirmation",
    }
    return {
        "board": board_name,
        "label": row.get("label"),
        "strength": row.get("strength"),
        "evidence": {
            "bytes": row.get("bytes"),
            "markers": row.get("markers") or [],
            "resolved_device": row.get("resolved_device"),
            "by_path": row.get("by_path"),
        },
        "current_uart": current_uart or None,
        "proposed_uart": proposed_uart,
        "human_required": True,
        "apply_automatically": False,
    }


def inventory_with_proposals(inventory: dict[str, Any], proposals: list[dict[str, Any]]) -> dict[str, Any]:
    proposed = copy.deepcopy(inventory)
    boards = proposed.get("boards")
    if not isinstance(boards, list):
        proposed["boards"] = []
        boards = proposed["boards"]
    by_name = {item.get("name"): item for item in boards if isinstance(item, dict)}
    for proposal in proposals:
        board = by_name.get(proposal["board"])
        if not isinstance(board, dict):
            continue
        current_uart = board.get("uart") if isinstance(board.get("uart"), dict) else {}
        next_uart = dict(current_uart)
        next_uart.update(proposal["proposed_uart"])
        board["uart"] = next_uart
    return proposed


def inventory_diff(inventory: dict[str, Any], proposed: dict[str, Any], inventory_path: Path) -> str:
    before = json.dumps(inventory, indent=2, sort_keys=True).splitlines(keepends=True)
    after = json.dumps(proposed, indent=2, sort_keys=True).splitlines(keepends=True)
    diff = difflib.unified_diff(
        before,
        after,
        fromfile=str(inventory_path),
        tofile=f"{inventory_path} (proposed)",
    )
    return "".join(diff)


def build_proposals(inventory_path: Path, log_dir: Path, event_log: Path) -> dict[str, Any]:
    inventory = load_inventory(inventory_path)
    rows = candidate_rows(inventory, inventory_path, log_dir, event_log)
    proposals = [proposal for row in rows if (proposal := proposal_for_row(row, inventory))]
    proposed_inventory = inventory_with_proposals(inventory, proposals)
    diff = inventory_diff(inventory, proposed_inventory, inventory_path) if proposals else ""
    return {
        "generated_at_utc": utc_now(),
        "inventory": str(inventory_path),
        "log_dir": str(log_dir),
        "event_log": str(event_log),
        "proposal_count": len(proposals),
        "status": "proposal-ready" if proposals else "no-proposal",
        "proposals": proposals,
        "inventory_diff": diff,
        "proposed_inventory": proposed_inventory if proposals else None,
        "next_action": (
            "human should verify the proposed board-to-UART mapping before editing inventory"
            if proposals
            else "run scripts/cubie-manual-boot-session 120 cubie-manual-boot and manually reset exactly one Cubie"
        ),
    }


def md_escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "/").replace("\n", " ")


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Cubie UART Inventory Proposal",
        "",
        f"Generated: `{data['generated_at_utc']}`",
        f"Status: `{data['status']}`",
        f"Proposals: `{data['proposal_count']}`",
        "",
        "This report is read-only. It does not edit inventory.",
        "",
        "| board | label | strength | proposed_device | resolved_device | markers |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if not data["proposals"]:
        lines.append("| none | none | none | none | none | none |")
    for item in data["proposals"]:
        markers = "; ".join(str(marker) for marker in item["evidence"].get("markers", [])) or "-"
        lines.append(
            "| "
            f"{md_escape(item.get('board'))} | "
            f"{md_escape(item.get('label'))} | "
            f"{md_escape(item.get('strength'))} | "
            f"`{md_escape(item['proposed_uart'].get('device'))}` | "
            f"`{md_escape(item['evidence'].get('resolved_device'))}` | "
            f"{md_escape(markers)} |"
        )
    lines.extend(["", "## Inventory Diff Preview", ""])
    if data.get("inventory_diff"):
        lines.extend(["```diff", str(data["inventory_diff"]).rstrip(), "```"])
    else:
        lines.append("No inventory diff is available because there is no proposal.")
    lines.extend(["", "## Next Action", "", data["next_action"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build read-only Cubie UART inventory proposals.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--event-log", default=str(DEFAULT_EVENT_LOG))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", default="", help="Optional output path.")
    args = parser.parse_args()

    data = build_proposals(Path(args.inventory), Path(args.log_dir), Path(args.event_log))
    output = json.dumps(data, indent=2, sort_keys=True) + "\n" if args.json else markdown(data) + "\n"
    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
        print(f"wrote={out}")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
