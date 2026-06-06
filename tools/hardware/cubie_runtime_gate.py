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
import cubie_boot_staging_status
import cubie_network_status
import cubie_uart_map_candidates
import cubie_uart_report


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_EVENT_LOG = cubie_event_log.DEFAULT_EVENT_LOG
DEFAULT_STAGING_TARGETS = ",".join(cubie_boot_staging_status.DEFAULT_TARGETS)


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


def staging_summary(args: argparse.Namespace) -> dict[str, Any]:
    if getattr(args, "skip_staging", False):
        return {"skipped": True, "ready_count": 0, "target_count": 0, "rows": []}
    staging_args = argparse.Namespace(
        targets=getattr(args, "staging_targets", DEFAULT_STAGING_TARGETS),
        stage=getattr(args, "staging_stage", cubie_boot_staging_status.DEFAULT_STAGE),
        user=getattr(args, "staging_user", cubie_boot_staging_status.DEFAULT_USER),
        identity=getattr(args, "staging_identity", cubie_boot_staging_status.DEFAULT_IDENTITY),
        timeout=getattr(args, "staging_timeout", cubie_boot_staging_status.DEFAULT_TIMEOUT),
    )
    return cubie_boot_staging_status.build_status(staging_args)


def refine_status(status: str, reason: str, staging: dict[str, Any]) -> tuple[str, str]:
    if status != "manual-capture-required":
        return status, reason
    if staging.get("skipped"):
        return status, reason
    installed_count = int(staging.get("installed_count") or 0)
    if installed_count > 0:
        return (
            "boot-selection-required",
            "boot entry is installed, but no boot capture exists yet",
        )
    ready_count = int(staging.get("ready_count") or 0)
    if ready_count > 0:
        return (
            "root-install-required",
            "boot artifacts are staged and checksum-verified, but no boot capture exists yet",
        )
    return (
        "boot-artifact-staging-required",
        "no non-empty UART capture exists and no staged boot artifacts are ready",
    )


def next_action(status: str, staging: dict[str, Any] | None = None) -> str:
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
    if status == "boot-selection-required":
        rows = (staging or {}).get("rows", [])
        installed = [row for row in rows if row.get("root_install_complete")]
        targets = ", ".join(f"{row.get('hostname') or row.get('ip')}:{row.get('ip')}" for row in installed)
        target_hint = f" while booting one installed board ({targets})" if targets else ""
        stage = str((staging or {}).get("stage") or "")
        if not stage and installed:
            stage = str(installed[0].get("stage") or "")
        capture_label = f"{Path(stage).name}-boot" if stage else "cubie-manual-boot"
        labels = sorted({row.get("extlinux_label") for row in installed if row.get("extlinux_label")})
        label_hint = f" and select {labels[0]}" if labels else " and select the staged non-default boot label"
        return f"run scripts/cubie-manual-boot-session 180 {capture_label}{target_hint}{label_hint}"
    if status == "root-install-required":
        rows = (staging or {}).get("rows", [])
        ready = [row for row in rows if row.get("ready_for_root_install")]
        targets = ", ".join(f"{row.get('hostname') or row.get('ip')}:{row.get('ip')}" for row in ready)
        target_hint = f" on one staged board ({targets})" if targets else " on one staged board"
        stage = str((staging or {}).get("stage") or "")
        if not stage and ready:
            stage = str(ready[0].get("stage") or "")
        capture_label = f"{Path(stage).name}-boot" if stage else "cubie-manual-boot"
        labels = sorted({row.get("extlinux_label") for row in ready if row.get("extlinux_label")})
        label_hint = f" and select {labels[0]}" if labels else " and select the staged non-default boot label"
        return (
            "run the staged install-extlinux-entry.sh with sudo/root"
            f"{target_hint}, then run scripts/cubie-manual-boot-session 180 "
            f"{capture_label}{label_hint}"
        )
    if status == "boot-artifact-staging-required":
        return "run scripts/cubie-stage-boot-artifacts against the chosen live A733 board, then rerun this gate"
    return "run scripts/cubie-manual-boot-session 120 cubie-manual-boot and manually reset exactly one Cubie"


def build_gate(args: argparse.Namespace) -> dict[str, Any]:
    inventory_path = Path(args.inventory)
    log_dir = Path(args.log_dir)
    event_log = Path(args.event_log)
    inventory = load_inventory(inventory_path)
    captures = cubie_uart_report.load_captures(log_dir)
    mapping = mapping_summary(inventory, inventory_path, log_dir, event_log)
    network = network_summary(inventory_path, args.network_timeout, args.port, args.skip_network)
    staging = staging_summary(args)
    if inventory.get("inventory_error") or inventory.get("inventory_missing"):
        status = "inventory-invalid"
        reason = str(inventory.get("inventory_error") or inventory.get("inventory_missing"))
    else:
        status, reason = classify(captures, mapping)
        status, reason = refine_status(status, reason, staging)
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    marker_hits = [item for item in captures if item.get("markers")]
    ssh_open = [item for item in network.get("results", []) if item.get("tcp_status") == "open"]

    return {
        "generated_at_utc": utc_now(),
        "status": status,
        "reason": reason,
        "next_action": next_action(status, staging),
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
        "staging": {
            "skipped": bool(staging.get("skipped")),
            "stage": staging.get("stage", ""),
            "ready_count": staging.get("ready_count", 0),
            "installed_count": staging.get("installed_count", 0),
            "target_count": staging.get("target_count", 0),
            "rows": staging.get("rows", []),
        },
    }


def md_escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "/").replace("\n", " ")


def markdown(data: dict[str, Any]) -> str:
    captures = data["captures"]
    mapping = data["mapping"]
    staging = data.get("staging", {})
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
            "## Boot Staging",
            "",
        ]
    )
    if staging.get("skipped"):
        lines.append("- skipped")
    else:
        lines.append(
            f"- ready for root install: `{staging.get('ready_count', 0)}/"
            f"{staging.get('target_count', 0)}`"
        )
        lines.append(
            f"- installed boot entry: `{staging.get('installed_count', 0)}/"
            f"{staging.get('target_count', 0)}`"
        )
        lines.extend(
            [
                "",
                "| ip | hostname | stage | sha256 | installer | boot entry | boot files | ready |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in staging.get("rows", []):
            lines.append(
                "| "
                f"`{md_escape(row.get('ip'))}` | "
                f"{md_escape(row.get('hostname') or '-')} | "
                f"{md_escape(row.get('stage_status'))} | "
                f"{md_escape(row.get('sha256_status'))} | "
                f"{md_escape(row.get('installer_syntax'))} | "
                f"{md_escape(row.get('boot_entry_status'))} | "
                f"{md_escape(row.get('boot_files_status'))} | "
                f"{'yes' if row.get('ready_for_root_install') else 'no'} |"
            )

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
    parser.add_argument("--skip-staging", action="store_true")
    parser.add_argument("--staging-targets", default=DEFAULT_STAGING_TARGETS)
    parser.add_argument("--staging-stage", default=cubie_boot_staging_status.DEFAULT_STAGE)
    parser.add_argument("--staging-user", default=cubie_boot_staging_status.DEFAULT_USER)
    parser.add_argument("--staging-identity", default=cubie_boot_staging_status.DEFAULT_IDENTITY)
    parser.add_argument("--staging-timeout", type=int, default=cubie_boot_staging_status.DEFAULT_TIMEOUT)
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
