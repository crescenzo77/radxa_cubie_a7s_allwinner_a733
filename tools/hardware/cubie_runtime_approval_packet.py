#!/usr/bin/env python3
"""Write a human approval packet for Cubie runtime proof work."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_ARTIFACT = "/srv/projects/kernel-work/outgoing/a733-v4-abc8d07b0a63-20260606T152409Z"


def load_inventory(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_board(inventory: dict[str, Any], name: str) -> dict[str, Any]:
    for board in inventory.get("boards", []):
        if board.get("name") == name:
            return board
    raise SystemExit(f"board not found in inventory: {name}")


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def packet_text(board: dict[str, Any], artifact_dir: str, inventory_path: Path) -> str:
    generated = utc_stamp()
    board_name = board.get("name", "")
    ip = board.get("ip", "")
    uart = board.get("uart", {})
    excluded = board.get("kernel_work_status") == "excluded"
    status = "blocked-excluded-board" if excluded else "needs-approval"
    stage_command = f"scripts/cubie-stage-boot-artifacts {ip}" if ip else "scripts/cubie-stage-boot-artifacts <BOARD_IP>"

    lines = [
        f"# {board_name} Runtime Proof Approval Packet",
        "",
        f"Generated: {generated}",
        f"Status: `{status}`",
        "",
        "## Board",
        "",
        f"- Board: `{board_name}`",
        f"- IP: `{ip or 'unknown'}`",
        f"- UART host: `{uart.get('host', 'unknown')}`",
        f"- UART device: `{uart.get('device', 'unknown')}`",
        f"- UART resolved device: `{uart.get('resolved_device', 'unknown')}`",
        f"- UART mapping status: `{uart.get('mapping_status', 'unknown')}`",
        f"- Inventory: `{inventory_path}`",
        "",
        "## Artifact",
        "",
        f"- Artifact directory: `{artifact_dir}`",
        "- Required checksums are enforced by `scripts/cubie-stage-boot-artifacts` and the generated installer.",
        "",
        "## Approval Requested",
        "",
        "Approve these steps separately:",
        "",
        "1. Stage artifacts into the board user's home directory.",
        "2. Run the generated root-required installer that writes `/boot`.",
        "3. Reboot or select the new boot entry and capture UART evidence.",
        "",
        "## Exact First Command After Approval",
        "",
        "```sh",
        stage_command,
        "```",
        "",
        "## Stop Conditions",
        "",
        "- Do not run this for `cubie1` unless its exclusion is explicitly lifted.",
        "- Do not write `/boot` without explicit approval for the installer step.",
        "- Do not reboot or change boot defaults without explicit approval.",
        "- Capture UART evidence and run `scripts/cubie-corrected-root-proof-gate` before claiming runtime proof.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", default="cubie2")
    parser.add_argument("--artifact-dir", default=DEFAULT_ARTIFACT)
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--out")
    parser.add_argument("--print-only", action="store_true")
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    board = find_board(load_inventory(inventory_path), args.board)
    text = packet_text(board, args.artifact_dir, inventory_path)
    if args.print_only:
        print(text)
        return 0

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out) if args.out else REPO_ROOT / "task-packets" / "kernel" / "approvals" / f"a733-{args.board}-runtime-proof-approval-{stamp}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"packet={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
