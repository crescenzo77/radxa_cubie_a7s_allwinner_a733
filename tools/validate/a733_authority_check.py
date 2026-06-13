#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate A733 local-work authority files for workflow drift."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


AUTHORITY_FILES = {
    "workflow": Path("runbooks/kernel-a733-mainline-enablement-workflow.md"),
    "inventory": Path("inventory/hardware/cubie-a7s-lab.json"),
    "cycle": Path("task-packets/kernel/a733-cycle-ledger.md"),
    "comms": Path("task-packets/kernel/a733-unsent-communications-ledger.md"),
    "queue": Path("task-packets/kernel/a733-supervised-batch-queue.md"),
}
EVIDENCE_INDEX = Path("task-packets/kernel/a733-current-evidence-index.md")
REGENERATION_CHECKLIST = Path("task-packets/kernel/a733-local-regeneration-checklist.md")
PERIPHERAL_EVIDENCE_MAP = Path("task-packets/kernel/a733-peripheral-evidence-map.md")
ETHERNET_GMAC_EVIDENCE = Path("task-packets/kernel/a733-ethernet-gmac-evidence-sheet.md")

REQUIRED_COMM_IDS = [f"A733-COMM-{number:03d}" for number in range(1, 17)]
REQUIRED_BATCH_IDS = [f"A733-BATCH-{number:03d}" for number in range(0, 13)]
EXPECTED_BOARDS = {"cubie1", "cubie2", "cubie3"}


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def check_markdown_fences(name: str, text: str, failures: list[str]) -> None:
    fence_count = sum(1 for line in text.splitlines() if line.startswith("```"))
    if fence_count % 2:
        failures.append(f"{name}: unbalanced Markdown fences ({fence_count})")


def require_contains(name: str, text: str, needle: str, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"{name}: missing required text: {needle}")


def check_workflow(text: str, failures: list[str]) -> None:
    required = [
        "Communication mode: local work only",
        "Continuous work is allowed as repeated bounded work items",
        "Codex Desktop may run multiple bounded work items in one invocation",
        "Track Matrix",
        "Current Local Track Snapshot",
        "task-packets/kernel/a733-current-evidence-index.md",
        "sent-before-blackout",
        "historical no-resend record",
    ]
    for needle in required:
        require_contains("workflow", text, needle, failures)

    stale_active_phrases = [
        "Every autonomous invocation has exactly one cycle ledger record",
        "every communication that would otherwise have been sent is captured but unsent",
    ]
    for phrase in stale_active_phrases:
        if phrase in text:
            failures.append(f"workflow: stale active wording remains: {phrase}")


def check_inventory(raw: str, failures: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        failures.append(f"inventory: invalid JSON: {exc}")
        return None

    boards = data.get("boards")
    if not isinstance(boards, list):
        failures.append("inventory: boards is not a list")
        return data

    names = {board.get("name") for board in boards if isinstance(board, dict)}
    if names != EXPECTED_BOARDS:
        failures.append(f"inventory: expected boards {sorted(EXPECTED_BOARDS)}, got {sorted(names)}")

    for board in boards:
        if not isinstance(board, dict):
            continue
        name = board.get("name", "<unknown>")
        role = board.get("kernel_work_role", {})
        recovery = board.get("recovery", {})
        wiring = board.get("physical_wiring", {})
        if role.get("role") != "unassigned":
            failures.append(f"inventory:{name}: role is not unassigned")
        if role.get("assignment_status") != "pending-human-choice":
            failures.append(f"inventory:{name}: assignment_status is not pending-human-choice")
        if recovery.get("rung") != "soft-fallback":
            failures.append(f"inventory:{name}: recovery rung is not soft-fallback")
        if recovery.get("automation_status") != "not_drilled_for_burn_autonomy":
            failures.append(f"inventory:{name}: recovery automation_status is not conservative")
        if recovery.get("autonomous") is not False:
            failures.append(f"inventory:{name}: autonomous is not false")
        if wiring.get("boot_media") != "unknown":
            failures.append(f"inventory:{name}: boot_media no longer unknown; update queue snapshot too")

    claim = data.get("agent_coordination", {}).get("claim_service", {})
    if claim.get("status") != "planned-not-active":
        failures.append("inventory: claim_service status is not planned-not-active")
    if data.get("agent_coordination", {}).get("cross_runtime_concurrency") != "disabled":
        failures.append("inventory: cross_runtime_concurrency is not disabled")
    return data


def check_comms(text: str, failures: list[str]) -> None:
    require_contains("comms", text, "sent-before-blackout", failures)
    require_contains("comms", text, "## Historical Sent Items", failures)
    for comm_id in REQUIRED_COMM_IDS:
        require_contains("comms", text, comm_id, failures)


def check_queue(text: str, failures: list[str]) -> None:
    for batch_id in REQUIRED_BATCH_IDS:
        require_contains("queue", text, batch_id, failures)
    required = [
        "Current inventory-derived snapshot",
        "no board is eligible for autonomous burn, proving, or",
        "reference mutation",
        "cubie1",
        "cubie2",
        "cubie3",
    ]
    for needle in required:
        require_contains("queue", text, needle, failures)


def check_cycle_ledger(text: str, failures: list[str]) -> None:
    require_contains("cycle", text, "## Ordering Note", failures)
    cycle_ids = re.findall(r"^### (A733-CYCLE-\d{3})$", text, flags=re.MULTILINE)
    duplicates = sorted({item for item in cycle_ids if cycle_ids.count(item) > 1})
    if duplicates:
        failures.append(f"cycle: duplicate cycle IDs: {', '.join(duplicates)}")
    if "A733-CYCLE-000" not in cycle_ids:
        failures.append("cycle: missing A733-CYCLE-000")


def check_evidence_index(root: Path, failures: list[str]) -> None:
    path = root / EVIDENCE_INDEX
    if not path.exists():
        failures.append(f"evidence-index: missing {EVIDENCE_INDEX}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("evidence-index", text, failures)
    required = [
        "Status: local-only coordination index",
        "not a public communication",
        "de486cb24c361a86cba26738f24332df780872b0",
        "e694ae3fa8477846a5a6eaf31fed4813ff991d5b",
        "H200",
        "H201",
        "H247",
        "H253",
        "H260",
        "H265",
        "A733-COMM-013",
        "A733-COMM-014",
        "A733-COMM-015",
        "A733-COMM-016",
        "sent-before-blackout",
        "no-send",
        "local-only",
        "task-packets/kernel/a733-local-regeneration-checklist.md",
        "task-packets/kernel/a733-peripheral-evidence-map.md",
        "task-packets/kernel/a733-ethernet-gmac-evidence-sheet.md",
    ]
    for needle in required:
        require_contains("evidence-index", text, needle, failures)


def check_regeneration_checklist(root: Path, failures: list[str]) -> None:
    path = root / REGENERATION_CHECKLIST
    if not path.exists():
        failures.append(f"regeneration-checklist: missing {REGENERATION_CHECKLIST}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("regeneration-checklist", text, failures)
    required = [
        "Status: local-only checklist",
        "Do not send",
        "Do not boot",
        "H200",
        "H201",
        "H247",
        "H253",
        "H260",
        "de486cb24c361a86cba26738f24332df780872b0",
        "e694ae3fa8477846a5a6eaf31fed4813ff991d5b",
        "local-only",
        "no-send",
        "sent-before-blackout",
    ]
    for needle in required:
        require_contains("regeneration-checklist", text, needle, failures)


def check_peripheral_evidence_map(root: Path, failures: list[str]) -> None:
    path = root / PERIPHERAL_EVIDENCE_MAP
    if not path.exists():
        failures.append(f"peripheral-evidence-map: missing {PERIPHERAL_EVIDENCE_MAP}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("peripheral-evidence-map", text, failures)
    required = [
        "Status: local-only evidence map",
        "not a patch plan",
        "SDMMC",
        "eMMC",
        "Ethernet",
        "PCIe",
        "NVMe",
        "USB",
        "Wi-Fi",
        "Bluetooth",
        "display",
        "media",
        "GPU",
        "NPU",
        "RISC-V",
        "thermal",
        "cpufreq",
        "fan",
        "I2C",
        "SPI",
        "UART",
        "GPIO",
        "regulators",
        "A733-BATCH-003",
        "A733-BATCH-012",
        "A733-COMM-006",
        "A733-COMM-012",
        "local-only",
    ]
    for needle in required:
        require_contains("peripheral-evidence-map", text, needle, failures)


def check_ethernet_gmac_evidence(root: Path, failures: list[str]) -> None:
    path = root / ETHERNET_GMAC_EVIDENCE
    if not path.exists():
        failures.append(f"ethernet-gmac-evidence: missing {ETHERNET_GMAC_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("ethernet-gmac-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable Ethernet",
        "GMAC",
        "GMAC210",
        "STMMAC",
        "MDIO",
        "PHY reset",
        "PHY power",
        "clock",
        "reset",
        "A733-BATCH-007",
        "A733-COMM-007",
        "read only",
    ]
    for needle in required:
        require_contains("ethernet-gmac-evidence", text, needle, failures)


def run(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    texts: dict[str, str] = {}
    for name, rel in AUTHORITY_FILES.items():
        path = root / rel
        if not path.exists():
            failures.append(f"{name}: missing {rel}")
            continue
        if name != "inventory":
            texts[name] = read_text(root, rel)
            check_markdown_fences(name, texts[name], failures)

    inventory = None
    if (root / AUTHORITY_FILES["inventory"]).exists():
        inventory = check_inventory(read_text(root, AUTHORITY_FILES["inventory"]), failures)

    if "workflow" in texts:
        check_workflow(texts["workflow"], failures)
    if "comms" in texts:
        check_comms(texts["comms"], failures)
    if "queue" in texts:
        check_queue(texts["queue"], failures)
    if "cycle" in texts:
        check_cycle_ledger(texts["cycle"], failures)
    check_evidence_index(root, failures)
    check_regeneration_checklist(root, failures)
    check_peripheral_evidence_map(root, failures)
    check_ethernet_gmac_evidence(root, failures)

    status = "PASS" if not failures else "FAIL"
    return {
        "status": status,
        "root": str(root),
        "authority_files": {name: str(path) for name, path in AUTHORITY_FILES.items()},
        "evidence_index": str(EVIDENCE_INDEX),
        "regeneration_checklist": str(REGENERATION_CHECKLIST),
        "peripheral_evidence_map": str(PERIPHERAL_EVIDENCE_MAP),
        "ethernet_gmac_evidence": str(ETHERNET_GMAC_EVIDENCE),
        "board_count": len(inventory.get("boards", [])) if isinstance(inventory, dict) else None,
        "failures": failures,
        "failure_count": len(failures),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result = run(root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status={result['status']}")
        print(f"root={result['root']}")
        print(f"failures={result['failure_count']}")
        for failure in result["failures"]:
            print(f"  {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
