#!/usr/bin/env python3
"""Find live Cubie-like A733 boards without trusting stale inventory IPs."""

from __future__ import annotations

import argparse
import concurrent.futures
import ipaddress
import json
import os
import re
import socket
import subprocess
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_COMMAND = (
    'printf "hostname="; hostname; '
    'printf "\\narch="; uname -m; '
    'if [ -r /proc/device-tree/model ]; then '
    'printf "\\nmodel="; tr "\\000" "\\n" </proc/device-tree/model; fi'
)
DEFAULT_USER = "radxa"
DEFAULT_IDENTITY = "~/.ssh/id_ed25519"
DEFAULT_EXCLUDED_IPS = ["192.168.50.65"]


def load_inventory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"boards": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"boards": []}
    return data if isinstance(data, dict) else {"boards": []}


def inventory_ips(data: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for board in data.get("boards", []):
        name = str(board.get("name") or "")
        ip = str(board.get("ip") or "")
        if name and ip:
            result[ip] = name
    return result


def tcp_open(ip: str, port: int, timeout: float) -> bool:
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        return sock.connect_ex((ip, port)) == 0
    finally:
        sock.close()


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def split_csv_items(values: list[str] | str) -> list[str]:
    if isinstance(values, str):
        values = [values]
    result: list[str] = []
    for value in values:
        result.extend(split_csv(value))
    return result


def is_a733_cubie(model: str, hostname: str, arch: str, returncode: int) -> bool:
    return returncode == 0 and (
        "sun60iw2" in model.lower()
        or "a733" in model.lower()
        or (hostname.startswith("cubie") and arch == "aarch64")
    )


def arp_table() -> dict[str, str]:
    try:
        proc = subprocess.run(
            ["arp", "-an"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return {}
    rows: dict[str, str] = {}
    pattern = re.compile(r"\((?P<ip>[0-9.]+)\) at (?P<mac>[^ ]+)")
    for line in proc.stdout.splitlines():
        match = pattern.search(line)
        if match and match.group("mac") != "(incomplete)":
            rows[match.group("ip")] = match.group("mac")
    return rows


def ssh_probe(
    ip: str,
    user: str,
    identity: str,
    connect_timeout: int,
    known_hosts: str,
) -> dict[str, Any]:
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={connect_timeout}",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        f"UserKnownHostsFile={known_hosts}",
        "-i",
        os.path.expanduser(identity),
        f"{user}@{ip}",
        DEFAULT_COMMAND,
    ]
    proc = subprocess.run(
        cmd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    fields: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    text = "\n".join([proc.stdout, proc.stderr])
    model = fields.get("model", "")
    hostname = fields.get("hostname", "")
    arch = fields.get("arch", "")
    lines = text.strip().splitlines()
    return {
        "ip": ip,
        "user": user,
        "ssh_returncode": proc.returncode,
        "hostname": hostname,
        "arch": arch,
        "model": model,
        "is_a733_cubie_candidate": is_a733_cubie(model, hostname, arch, proc.returncode),
        "error": "" if proc.returncode == 0 else (lines[-1] if lines else ""),
    }


def classify_target(
    ip: str,
    users: list[str],
    identity: str,
    port: int,
    timeout: float,
    ssh_timeout: int,
    known_hosts: str,
) -> dict[str, Any]:
    port_open = tcp_open(ip, port, timeout)
    probes: list[dict[str, Any]] = []
    if port_open:
        probes = [ssh_probe(ip, user, identity, ssh_timeout, known_hosts) for user in users]
    successful = [probe for probe in probes if probe.get("ssh_returncode") == 0]
    candidates = [probe for probe in successful if probe.get("is_a733_cubie_candidate")]
    if candidates:
        classification = "a733-cubie-candidate"
        selected = candidates[0]
    elif successful:
        classification = "not-a733-cubie"
        selected = successful[0]
    elif port_open:
        classification = "ssh-auth-blocked"
        selected = probes[0] if probes else {}
    else:
        classification = "ssh-closed-or-filtered"
        selected = {}
    return {
        "ip": ip,
        "tcp_port": port,
        "tcp_status": "open" if port_open else "closed-or-filtered",
        "classification": classification,
        "hostname": selected.get("hostname", ""),
        "arch": selected.get("arch", ""),
        "model": selected.get("model", ""),
        "selected_user": selected.get("user", ""),
        "is_a733_cubie_candidate": bool(candidates),
        "probes": probes,
    }


def excluded_target(ip: str, port: int) -> dict[str, Any]:
    return {
        "ip": ip,
        "tcp_port": port,
        "tcp_status": "excluded",
        "classification": "excluded-from-kernel-work",
        "hostname": "",
        "arch": "",
        "model": "",
        "selected_user": "",
        "is_a733_cubie_candidate": False,
        "excluded_from_kernel_work": True,
        "probes": [],
    }


def scan_network(
    network: str,
    port: int,
    timeout: float,
    workers: int,
    excluded: set[str] | None = None,
) -> list[str]:
    excluded = excluded or set()
    ips = [
        str(ip)
        for ip in ipaddress.ip_network(network, strict=False).hosts()
        if str(ip) not in excluded
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        checks = {executor.submit(tcp_open, ip, port, timeout): ip for ip in ips}
        open_ips: list[str] = []
        for future in concurrent.futures.as_completed(checks):
            ip = checks[future]
            try:
                if future.result():
                    open_ips.append(ip)
            except OSError:
                pass
    return sorted(open_ips, key=lambda value: tuple(int(part) for part in value.split(".")))


def discover(args: argparse.Namespace) -> dict[str, Any]:
    inventory = load_inventory(Path(args.inventory))
    known_inventory_ips = inventory_ips(inventory)
    excluded = set(
        []
        if getattr(args, "include_excluded", False)
        else split_csv_items(getattr(args, "exclude_ip", DEFAULT_EXCLUDED_IPS))
    )
    target_ips = list(getattr(args, "target", []) or [])
    if target_ips:
        default_user = getattr(args, "user", DEFAULT_USER) or DEFAULT_USER
        users = split_csv(getattr(args, "probe_users", "")) or [default_user]
        arp = arp_table()
        probe_ips = [ip for ip in target_ips if ip not in excluded]
        with tempfile.NamedTemporaryFile(prefix="cubie-known-hosts-") as known_hosts:
            targets = [
                classify_target(
                    ip,
                    users,
                    args.identity,
                    args.port,
                    args.timeout,
                    args.ssh_timeout,
                    known_hosts.name,
                )
                for ip in probe_ips
            ]
        targets.extend(excluded_target(ip, args.port) for ip in target_ips if ip in excluded)
        for target in targets:
            target["inventory_name"] = known_inventory_ips.get(target["ip"], "")
            target["mac"] = arp.get(target["ip"], "")
        candidates = [target for target in targets if target["is_a733_cubie_candidate"]]
        return {
            "mode": "target",
            "network": args.network,
            "inventory": str(Path(args.inventory)),
            "ssh_open_count": sum(1 for target in targets if target["tcp_status"] == "open"),
            "a733_candidate_count": len(candidates),
            "a733_candidates": candidates,
            "target_results": targets,
            "excluded_ips": sorted(excluded.intersection(target_ips)),
            "stale_inventory_entries": [],
            "ssh_open_ips": [target["ip"] for target in targets if target["tcp_status"] == "open"],
        }
    open_ips = scan_network(args.network, args.port, args.timeout, args.workers, excluded)
    arp = arp_table()
    with tempfile.NamedTemporaryFile(prefix="cubie-known-hosts-") as known_hosts:
        probes = [
            ssh_probe(ip, args.user, args.identity, args.ssh_timeout, known_hosts.name)
            for ip in open_ips
        ]
    for probe in probes:
        probe["inventory_name"] = known_inventory_ips.get(probe["ip"], "")
        probe["mac"] = arp.get(probe["ip"], "")
    stale = [
        {"name": name, "ip": ip}
        for ip, name in sorted(known_inventory_ips.items())
        if ip not in open_ips
    ]
    candidates = [probe for probe in probes if probe["is_a733_cubie_candidate"]]
    non_candidates = [probe for probe in probes if not probe["is_a733_cubie_candidate"]]
    return {
        "mode": "network",
        "network": args.network,
        "inventory": str(Path(args.inventory)),
        "ssh_open_count": len(open_ips),
        "a733_candidate_count": len(candidates),
        "a733_candidates": candidates,
        "non_a733_ssh_hosts": non_candidates,
        "excluded_ips": sorted(excluded),
        "stale_inventory_entries": stale,
        "ssh_open_ips": open_ips,
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Cubie IP Discovery",
        "",
        f"Network: `{data['network']}`",
        f"Inventory: `{data['inventory']}`",
        f"SSH-open hosts: `{data['ssh_open_count']}`",
        f"A733 candidates: `{data['a733_candidate_count']}`",
        f"Excluded IPs: `{', '.join(data.get('excluded_ips', [])) or 'none'}`",
        "",
        "## A733 Candidates",
        "",
        "| ip | inventory | hostname | arch | model | mac |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["a733_candidates"]:
        lines.append(
            "| "
            f"`{row['ip']}` | "
            f"{row['inventory_name'] or '-'} | "
            f"{row['hostname'] or '-'} | "
            f"{row['arch'] or '-'} | "
            f"{row['model'] or '-'} | "
            f"`{row['mac'] or '-'}` |"
        )
    if not data["a733_candidates"]:
        lines.append("| none | - | - | - | - | - |")
    if data.get("target_results"):
        lines.extend(
            [
                "",
                "## Target Results",
                "",
                "| ip | inventory | classification | user | hostname | arch | model | mac |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in data["target_results"]:
            lines.append(
                "| "
                f"`{row['ip']}` | "
                f"{row.get('inventory_name') or '-'} | "
                f"{row['classification']} | "
                f"{row.get('selected_user') or '-'} | "
                f"{row.get('hostname') or '-'} | "
                f"{row.get('arch') or '-'} | "
                f"{row.get('model') or '-'} | "
                f"`{row.get('mac') or '-'}` |"
            )
    elif data.get("non_a733_ssh_hosts"):
        lines.extend(
            [
                "",
                "## SSH-Open Non-Candidates",
                "",
                "| ip | inventory | ssh_rc | hostname | arch | model | mac |",
                "| --- | --- | ---: | --- | --- | --- | --- |",
            ]
        )
        for row in data["non_a733_ssh_hosts"]:
            lines.append(
                "| "
                f"`{row['ip']}` | "
                f"{row.get('inventory_name') or '-'} | "
                f"{row['ssh_returncode']} | "
                f"{row.get('hostname') or '-'} | "
                f"{row.get('arch') or '-'} | "
                f"{row.get('model') or '-'} | "
                f"`{row.get('mac') or '-'}` |"
            )
    lines.extend(["", "## Stale Inventory Entries", ""])
    if data["stale_inventory_entries"]:
        for row in data["stale_inventory_entries"]:
            lines.append(f"- `{row['name']}` at `{row['ip']}` did not have SSH open")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", default="192.168.50.0/24")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument(
        "--probe-users",
        default="",
        help="Comma-separated users for --target probes. Defaults to --user.",
    )
    parser.add_argument("--identity", default=DEFAULT_IDENTITY)
    parser.add_argument("--target", action="append", default=[], help="Probe a specific IP instead of scanning.")
    parser.add_argument("--exclude-ip", action="append", default=list(DEFAULT_EXCLUDED_IPS))
    parser.add_argument("--include-excluded", action="store_true")
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--timeout", type=float, default=0.2)
    parser.add_argument("--ssh-timeout", type=int, default=4)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = discover(args)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
