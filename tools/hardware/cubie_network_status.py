#!/usr/bin/env python3
"""Check Cubie network reachability with bounded timeouts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import socket
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"
DEFAULT_BOARDS = [
    {"name": "cubie2", "ip": "192.168.50.85"},
    {"name": "cubie3", "ip": "192.168.50.95"},
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def ping_once(ip: str, timeout: float) -> str:
    wait_arg = str(max(1, math.ceil(timeout)))
    try:
        proc = subprocess.run(
            ["ping", "-c", "1", "-W", wait_arg, ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 1,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "timeout"
    return "reply" if proc.returncode == 0 else "no-reply"


def tcp_probe(ip: str, port: int, timeout: float) -> str:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return "open"
    except socket.timeout:
        return "timeout"
    except OSError as exc:
        name = exc.__class__.__name__
        return f"closed-or-filtered:{name}"


def load_boards(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return DEFAULT_BOARDS
    data = json.loads(path.read_text(encoding="utf-8"))
    boards = []
    for item in data.get("boards", []):
        name = item.get("name")
        ip = item.get("ip")
        if name and ip:
            boards.append({"name": str(name), "ip": str(ip)})
    return boards or DEFAULT_BOARDS


def check_boards(boards: list[dict[str, str]], timeout: float, port: int) -> dict[str, Any]:
    observed_at = utc_now()
    results = []
    for board in boards:
        ip = board["ip"]
        results.append(
            {
                "board": board["name"],
                "ip": ip,
                "ping": ping_once(ip, timeout),
                "tcp_port": port,
                "tcp_status": tcp_probe(ip, port, timeout),
            }
        )
    return {"observed_at_utc": observed_at, "results": results}


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def markdown_report(data: dict[str, Any]) -> str:
    lines = [
        "# Cubie Network Status",
        "",
        f"Observed: `{data['observed_at_utc']}`",
        "",
        "| board | ip | ping | tcp_port | tcp_status |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for item in data["results"]:
        lines.append(
            "| "
            f"{md_escape(item['board'])} | "
            f"`{md_escape(item['ip'])}` | "
            f"{md_escape(item['ping'])} | "
            f"{md_escape(item['tcp_port'])} | "
            f"{md_escape(item['tcp_status'])} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded Cubie network reachability check.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY), help="Cubie hardware inventory JSON.")
    parser.add_argument("--timeout", type=float, default=2.0, help="Per-probe timeout in seconds.")
    parser.add_argument("--port", type=int, default=22, help="TCP port to probe.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    boards = load_boards(Path(args.inventory))
    data = check_boards(boards, max(0.2, args.timeout), args.port)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown_report(data), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
