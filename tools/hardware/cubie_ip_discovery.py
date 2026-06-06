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
    is_a733 = proc.returncode == 0 and (
        "sun60iw2" in model.lower()
        or "a733" in model.lower()
        or (hostname.startswith("cubie") and arch == "aarch64")
    )
    return {
        "ip": ip,
        "ssh_returncode": proc.returncode,
        "hostname": hostname,
        "arch": arch,
        "model": model,
        "is_a733_cubie_candidate": is_a733,
        "error": "" if proc.returncode == 0 else text.strip().splitlines()[-1:],
    }


def scan_network(network: str, port: int, timeout: float, workers: int) -> list[str]:
    ips = [str(ip) for ip in ipaddress.ip_network(network, strict=False).hosts()]
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
    open_ips = scan_network(args.network, args.port, args.timeout, args.workers)
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
    return {
        "network": args.network,
        "inventory": str(Path(args.inventory)),
        "ssh_open_count": len(open_ips),
        "a733_candidate_count": len(candidates),
        "a733_candidates": candidates,
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
    parser.add_argument("--user", default="radxa")
    parser.add_argument("--identity", default="~/.ssh/id_ed25519")
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
