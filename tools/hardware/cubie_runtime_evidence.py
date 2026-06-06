#!/usr/bin/env python3
"""Build a concise Cubie runtime evidence packet."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_network_status
import cubie_boot_staging_status
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


def excluded_ip_values(inventory: dict[str, Any]) -> list[str]:
    excluded = inventory.get("excluded_kernel_work_ips", [])
    if not isinstance(excluded, list):
        return []
    return [
        str(item.get("ip"))
        for item in excluded
        if isinstance(item, dict) and item.get("ip")
    ]


def redact_excluded_text(value: object, excluded_ips: list[str]) -> str:
    text = str(value if value is not None else "")
    for ip in excluded_ips:
        pattern = rf"(?<![0-9A-Za-z_.]){re.escape(ip)}(?![0-9A-Za-z_.])"
        text = re.sub(pattern, "[excluded-kernel-work-ip]", text)
    return text


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


def excluded_rows(inventory: dict[str, Any]) -> list[str]:
    rows = ["| ip | reason | rule |", "| --- | --- | --- |"]
    excluded = inventory.get("excluded_kernel_work_ips", [])
    if not isinstance(excluded, list) or not excluded:
        rows.append("| none | none | none |")
        return rows
    for item in excluded:
        if not isinstance(item, dict):
            continue
        rows.append(
            "| "
            f"`{md_escape(item.get('ip', 'unknown'))}` | "
            f"{md_escape(item.get('reason', 'unknown'))} | "
            f"{md_escape(item.get('rule', 'unknown'))} |"
        )
    if len(rows) == 2:
        rows.append("| none | none | none |")
    return rows


def evidence_status(captures: list[dict[str, Any]], net: dict[str, Any]) -> tuple[str, list[str]]:
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    marker_hits = [item for item in captures if item.get("markers")]
    ssh_open = [item for item in net.get("results", []) if item.get("tcp_status") == "open"]
    notes = []
    if non_empty:
        status = "uart-data-present-runtime-proof-unproven"
        notes.append(
            f"{len(non_empty)} UART capture(s) contain data, but this does not "
            "by itself prove the staged mainline boot."
        )
    else:
        status = "runtime-proof-missing"
        notes.append("No non-empty UART captures are available yet.")
    if marker_hits:
        notes.append(
            f"{len(marker_hits)} capture(s) include generic boot/login/error markers."
        )
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
        "boot_session_candidate_count": data.get("boot_session_candidate_count", 0),
        "boot_marker_candidate_count": data.get("boot_marker_candidate_count", 0),
        "runtime_marker_candidate_count": data.get("runtime_marker_candidate_count", 0),
        "non_empty_capture_count": data.get("non_empty_capture_count", 0),
        "session_count": data.get("session_count", 0),
        "rows": rows[-6:],
    }


def boot_staging_status() -> dict[str, Any]:
    args = SimpleNamespace(
        targets=",".join(cubie_boot_staging_status.DEFAULT_TARGETS),
        stage=cubie_boot_staging_status.DEFAULT_STAGE,
        user=cubie_boot_staging_status.DEFAULT_USER,
        identity=cubie_boot_staging_status.DEFAULT_IDENTITY,
        timeout=cubie_boot_staging_status.DEFAULT_TIMEOUT,
        exclude_target=list(cubie_boot_staging_status.DEFAULT_EXCLUDED_TARGETS),
        include_excluded=False,
    )
    return cubie_boot_staging_status.build_status(args)


def boot_staging_rows(staging: dict[str, Any]) -> list[str]:
    lines = [
        "| ip | hostname | stage | sha256 | installer | boot entry | boot files | boot sha256 | ready |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    rows = staging.get("rows", [])
    if not rows:
        lines.append("| none | none | none | none | none | none | none | none | no |")
        return lines
    for row in rows:
        lines.append(
            "| "
            f"`{md_escape(row.get('ip'))}` | "
            f"{md_escape(row.get('hostname') or '-')} | "
            f"{md_escape(row.get('stage_status'))} | "
            f"{md_escape(row.get('sha256_status'))} | "
            f"{md_escape(row.get('installer_syntax'))} | "
            f"{md_escape(row.get('boot_entry_status'))} | "
            f"{md_escape(row.get('boot_files_status'))} | "
            f"{md_escape(row.get('boot_sha256_status'))} | "
            f"{'yes' if row.get('ready_for_root_install') else 'no'} |"
        )
    return lines


def next_safe_action(staging: dict[str, Any], inventory: dict[str, Any]) -> str:
    excluded = excluded_ip_values(inventory)
    excluded_note = f" Do not use excluded IPs: {', '.join(excluded)}." if excluded else ""
    rows = staging.get("rows", [])
    installed = [row for row in rows if row.get("root_install_complete")]
    ready = [row for row in rows if row.get("ready_for_root_install")]
    if installed:
        row = installed[0]
        capture = row.get("capture_label") or "cubie-mainline-boot"
        label = row.get("extlinux_label") or "the staged non-default label"
        return (
            f"Run `scripts/cubie-manual-boot-session 180 {md_escape(capture)}`, "
            f"then manually reboot/reset Cubie3 and select `{md_escape(label)}` "
            f"over UART.{excluded_note}"
        )
    if ready:
        row = ready[0]
        stage = row.get("stage") or cubie_boot_staging_status.DEFAULT_STAGE
        capture = row.get("capture_label") or f"{Path(stage).name}-boot"
        label = row.get("extlinux_label") or "the staged non-default label"
        host = row.get("hostname") or "target board"
        ip = row.get("ip") or "unknown IP"
        return (
            f"On `{md_escape(host)}` `{md_escape(ip)}`, run "
            f"`cd {md_escape(stage)}` then `sudo ./install-extlinux-entry.sh`. "
            f"After that, run `scripts/cubie-manual-boot-session 180 {md_escape(capture)}` "
            f"and select `{md_escape(label)}` over UART.{excluded_note}"
        )
    return f"{md_escape(staging.get('next_action', 'repair staging before boot proof'))}.{excluded_note}"


def mapping_rows(summary: dict[str, Any]) -> list[str]:
    lines = [
        "| label | strength | evidence | manual_boards | resolved_device | by_path | bytes | markers |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- |",
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
            f"{md_escape(row.get('evidence_kind'))} | "
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
    excluded_ips = excluded_ip_values(inventory)
    boards = cubie_network_status.load_boards(inventory_path)
    net = cubie_network_status.check_boards(boards, network_timeout, port)
    captures = cubie_uart_report.load_captures(log_dir)
    events = latest_events(event_log)
    status, notes = evidence_status(captures, net)
    non_empty = [item for item in captures if (item.get("local_bytes") or 0) > 0]
    mapping = mapping_candidate_summary(inventory, inventory_path, log_dir, event_log)
    staging = boot_staging_status()

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
        "## Excluded Kernel-Work IPs",
        "",
        *excluded_rows(inventory),
        "",
        "Historical logs mentioning excluded IPs are evidence only; they are not "
        "permission to probe, stage, boot, or prove kernel work on those hosts.",
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

    lines.extend(
        [
            "",
            "## Boot Staging Gate",
            "",
            f"- ready for root install: `{staging.get('ready_count', 0)}/{staging.get('target_count', 0)}`",
            f"- installed boot entry: `{staging.get('installed_count', 0)}/{staging.get('target_count', 0)}`",
            "",
            *boot_staging_rows(staging),
            "",
        ]
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
            f"- boot-session candidates: `{mapping.get('boot_session_candidate_count', 0)}`",
            f"- boot-marker candidates: `{mapping.get('boot_marker_candidate_count', 0)}`",
            f"- runtime-marker candidates: `{mapping.get('runtime_marker_candidate_count', 0)}`",
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
                f"{md_escape(redact_excluded_text(event.get('note', ''), excluded_ips))} |"
            )
    else:
        lines.append("| none | none | none | none | none |")
    lines.append("")

    lines.extend(["## Recent Observations", ""])
    for obs in latest_observations(inventory):
        observed_at = obs.get("observed_at_utc", "unknown")
        obs_type = obs.get("type", "unknown")
        conclusion = redact_excluded_text(obs.get("conclusion", "no conclusion"), excluded_ips)
        lines.append(f"- `{observed_at}` `{obs_type}`: {conclusion}")
    if not latest_observations(inventory):
        lines.append("- No inventory observations recorded.")

    lines.extend(
        [
            "",
            "## Next Safe Action",
            "",
            next_safe_action(staging, inventory),
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
