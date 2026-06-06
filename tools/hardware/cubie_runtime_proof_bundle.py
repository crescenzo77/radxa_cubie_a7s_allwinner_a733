#!/usr/bin/env python3
"""Write a hashed Cubie runtime proof bundle."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_event_log
import cubie_ip_discovery
import cubie_runtime_evidence
import cubie_runtime_gate
import cubie_uart_inventory_proposal
import cubie_uart_map_candidates
import cubie_uart_report


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "task-packets" / "kernel" / "runtime-proof"
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_EVENT_LOG = cubie_event_log.DEFAULT_EVENT_LOG


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def stamp_from_utc(value: str) -> str:
    base = value.rstrip("Z")
    return base.replace("-", "").replace(":", "").replace(".", "") + "Z"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def mapping_payload(inventory_path: Path, log_dir: Path, event_log: Path) -> tuple[str, dict[str, Any]]:
    inventory = cubie_uart_map_candidates.load_inventory(inventory_path)
    captures = cubie_uart_map_candidates.load_captures(log_dir)
    events = cubie_uart_map_candidates.read_events(event_log)
    return cubie_uart_map_candidates.build_report(inventory, captures, events, log_dir, inventory_path, event_log)


def build_bundle(args: argparse.Namespace) -> dict[str, Any]:
    generated_at = utc_now()
    inventory_path = Path(args.inventory)
    log_dir = Path(args.log_dir)
    event_log = Path(args.event_log)
    bundle_dir = Path(args.out_dir) / f"cubie-runtime-proof-{stamp_from_utc(generated_at)}"

    evidence_md = cubie_runtime_evidence.build_packet(
        inventory_path,
        log_dir,
        event_log,
        max(0.2, args.network_timeout),
        args.port,
        generated_at,
    )
    gate_args = Namespace(
        inventory=str(inventory_path),
        log_dir=str(log_dir),
        event_log=str(event_log),
        network_timeout=args.network_timeout,
        port=args.port,
        skip_network=args.skip_network,
    )
    gate_data = cubie_runtime_gate.build_gate(gate_args)
    gate_md = cubie_runtime_gate.markdown(gate_data)
    mapping_md, mapping_data = mapping_payload(inventory_path, log_dir, event_log)
    proposal_data = cubie_uart_inventory_proposal.build_proposals(inventory_path, log_dir, event_log)
    proposal_md = cubie_uart_inventory_proposal.markdown(proposal_data)
    discovery_args = Namespace(
        network=args.discovery_network,
        inventory=str(inventory_path),
        user=args.discovery_user,
        identity=args.discovery_identity,
        port=args.port,
        timeout=args.discovery_timeout,
        ssh_timeout=args.discovery_ssh_timeout,
        workers=args.discovery_workers,
    )
    discovery_data = cubie_ip_discovery.discover(discovery_args)
    discovery_md = cubie_ip_discovery.markdown(discovery_data)

    files: dict[str, str] = {
        "runtime-evidence.md": evidence_md,
        "runtime-gate.md": gate_md,
        "ip-discovery.md": discovery_md,
        "uart-map-candidates.md": mapping_md,
        "uart-inventory-proposal.md": proposal_md,
    }
    json_files = {
        "runtime-gate.json": gate_data,
        "ip-discovery.json": discovery_data,
        "uart-map-candidates.json": mapping_data,
        "uart-inventory-proposal.json": proposal_data,
    }

    for name, text in files.items():
        write_text(bundle_dir / name, text.rstrip() + "\n")
    for name, data in json_files.items():
        write_json(bundle_dir / name, data)

    manifest = {
        "generated_at_utc": generated_at,
        "bundle_dir": str(bundle_dir),
        "inventory": str(inventory_path),
        "log_dir": str(log_dir),
        "event_log": str(event_log),
        "status": gate_data.get("status"),
        "proposal_status": proposal_data.get("status"),
        "files": {},
        "human_required": True,
        "applied_changes": False,
    }
    for path in sorted(bundle_dir.iterdir()):
        if path.is_file():
            manifest["files"][path.name] = {
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
    write_json(bundle_dir / "manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a hashed Cubie runtime proof bundle.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--log-dir", default=str(cubie_uart_report.DEFAULT_LOG_DIR))
    parser.add_argument("--event-log", default=str(DEFAULT_EVENT_LOG))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--network-timeout", type=float, default=1.0)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--skip-network", action="store_true", help="Skip network in runtime gate only.")
    parser.add_argument("--discovery-network", default="192.168.50.0/24")
    parser.add_argument("--discovery-user", default="radxa")
    parser.add_argument("--discovery-identity", default="~/.ssh/id_ed25519")
    parser.add_argument("--discovery-timeout", type=float, default=0.2)
    parser.add_argument("--discovery-ssh-timeout", type=int, default=4)
    parser.add_argument("--discovery-workers", type=int, default=64)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    manifest = build_bundle(args)
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"bundle={manifest['bundle_dir']}")
        print(f"status={manifest['status']}")
        print(f"proposal_status={manifest['proposal_status']}")
        print(f"manifest={manifest['bundle_dir']}/manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
