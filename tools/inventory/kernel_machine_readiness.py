#!/usr/bin/env python3
"""Read-only readiness checks for the headless kernel workflow hosts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from dataclasses import dataclass
from typing import Any


DEFAULT_TIMEOUT = 8


@dataclass(frozen=True)
class Check:
    name: str
    command: str
    required: bool = True


@dataclass(frozen=True)
class Host:
    name: str
    ip: str | None
    role: str
    checks: tuple[Check, ...]
    sudo_check: bool = False
    notes: tuple[str, ...] = ()


HOSTS = (
    Host(
        name="local-mac",
        ip=None,
        role="Codex Desktop dispatcher only",
        checks=(
            Check("git", "command -v git"),
            Check("rg", "command -v rg"),
            Check("python3", "command -v python3"),
            Check("cmake", "command -v cmake"),
        ),
        notes=(
            "Do not run Docker Desktop, validation containers, or model workloads on the Mac.",
            "If Mac containers become necessary, pause and discuss Colima first.",
        ),
    ),
    Host(
        name="amd",
        ip="192.168.50.252",
        role="validation lab plus RTX 3090 and RX 7900XT model lanes",
        checks=(
            Check("git", "command -v git"),
            Check("rg", "command -v rg"),
            Check("docker", "command -v docker"),
            Check("docker-compose", "docker compose version"),
            Check("python3", "command -v python3"),
            Check("cmake", "command -v cmake"),
            Check("ninja", "command -v ninja"),
            Check("nvidia-smi", "command -v nvidia-smi && nvidia-smi -L"),
            Check("vulkaninfo", "command -v vulkaninfo"),
            Check("nvidia-docker-runtime", "docker info --format '{{json .Runtimes}} {{.DefaultRuntime}}' | grep -q nvidia"),
            Check("clinfo", "command -v clinfo", required=False),
            Check("rocminfo", "command -v rocminfo", required=False),
        ),
        sudo_check=True,
    ),
    Host(
        name="strix",
        ip="192.168.50.11",
        role="long-review model lane and Cubie UART host",
        checks=(
            Check("git", "command -v git"),
            Check("rg", "command -v rg"),
            Check("docker", "command -v docker"),
            Check("docker-compose", "docker compose version"),
            Check("python3", "command -v python3"),
            Check("vulkaninfo", "command -v vulkaninfo"),
            Check("screen", "command -v screen"),
            Check("cubie-uart-by-path", "test -d /dev/serial/by-path && ls /dev/serial/by-path/* >/dev/null 2>&1"),
            Check("cmake", "command -v cmake", required=False),
            Check("ninja", "command -v ninja", required=False),
            Check("picocom", "command -v picocom", required=False),
            Check("minicom", "command -v minicom", required=False),
            Check("clinfo", "command -v clinfo", required=False),
        ),
        sudo_check=True,
    ),
    Host(
        name="thinkcentre",
        ip="192.168.50.225",
        role="Qdrant/cortex and git mirror host",
        checks=(
            Check("git", "command -v git"),
            Check("rg", "command -v rg"),
            Check("docker", "command -v docker"),
            Check("docker-compose", "docker compose version"),
            Check("curl", "command -v curl"),
            Check("jq", "command -v jq"),
            Check("python3", "command -v python3"),
            Check("qdrant-health", "curl -fsS http://127.0.0.1:6333/healthz"),
            Check("ninja", "command -v ninja", required=False),
            Check("clinfo", "command -v clinfo", required=False),
        ),
        sudo_check=True,
    ),
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def run_shell(command: str, host: Host, timeout: int) -> dict[str, Any]:
    if host.ip:
        argv = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={timeout}",
            host.ip,
            command,
        ]
    else:
        argv = ["/bin/sh", "-lc", command]
    try:
        proc = subprocess.run(
            argv,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout + 2,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": "timeout"}
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def check_host(host: Host, timeout: int) -> dict[str, Any]:
    if host.ip:
        reachable = run_shell("true", host, timeout)
        if not reachable["ok"]:
            return {
                "name": host.name,
                "ip": host.ip,
                "role": host.role,
                "status": "unreachable",
                "sudo_status": "not-checked",
                "required_missing": sum(1 for check in host.checks if check.required),
                "optional_missing": sum(1 for check in host.checks if not check.required),
                "checks": [
                    {
                        "name": "ssh",
                        "required": True,
                        "ok": False,
                        "returncode": reachable["returncode"],
                        "stdout": reachable["stdout"],
                        "stderr": reachable["stderr"],
                    }
                ],
                "notes": list(host.notes),
            }

    checks = []
    required_missing = 0
    optional_missing = 0
    for check in host.checks:
        result = run_shell(check.command, host, timeout)
        if not result["ok"]:
            if check.required:
                required_missing += 1
            else:
                optional_missing += 1
        checks.append(
            {
                "name": check.name,
                "required": check.required,
                "ok": result["ok"],
                "returncode": result["returncode"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            }
        )

    sudo_status = "not-checked"
    if host.sudo_check:
        sudo = run_shell("sudo -n true", host, timeout)
        sudo_status = "noninteractive-ok" if sudo["ok"] else "password-required"

    if required_missing:
        status = "missing-required"
    elif optional_missing:
        status = "ok-with-optional-missing"
    else:
        status = "ok"

    return {
        "name": host.name,
        "ip": host.ip,
        "role": host.role,
        "status": status,
        "sudo_status": sudo_status,
        "required_missing": required_missing,
        "optional_missing": optional_missing,
        "checks": checks,
        "notes": list(host.notes),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    selected = set(args.host or [])
    hosts = [host for host in HOSTS if not selected or host.name in selected or host.ip in selected]
    if selected and not hosts:
        known = ", ".join(host.name for host in HOSTS)
        raise SystemExit(f"unknown host selection: {', '.join(sorted(selected))}; known: {known}")
    return {
        "generated_at_utc": utc_now(),
        "hosts": [check_host(host, args.timeout) for host in hosts],
    }


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Kernel Machine Readiness",
        "",
        f"Generated: `{data['generated_at_utc']}`",
        "",
        "| host | ip | role | status | sudo | required missing | optional missing |",
        "| --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for host in data["hosts"]:
        lines.append(
            "| "
            f"{md_escape(host['name'])} | "
            f"{md_escape(host['ip'] or 'local')} | "
            f"{md_escape(host['role'])} | "
            f"`{md_escape(host['status'])}` | "
            f"`{md_escape(host['sudo_status'])}` | "
            f"{host['required_missing']} | "
            f"{host['optional_missing']} |"
        )
    for host in data["hosts"]:
        lines.extend(["", f"## {host['name']}", ""])
        if host.get("notes"):
            for note in host["notes"]:
                lines.append(f"- {md_escape(note)}")
            lines.append("")
        lines.extend(["| check | required | result | detail |", "| --- | --- | --- | --- |"])
        for check in host["checks"]:
            detail = check["stdout"] or check["stderr"] or f"rc={check['returncode']}"
            lines.append(
                "| "
                f"{md_escape(check['name'])} | "
                f"{'yes' if check['required'] else 'no'} | "
                f"{'ok' if check['ok'] else 'missing'} | "
                f"`{md_escape(detail[:120])}` |"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", action="append", help="Host name or IP to check. Repeatable.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any required check is missing.")
    args = parser.parse_args()

    data = build_report(args)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown(data), end="")
    if args.strict and any(host["required_missing"] for host in data["hosts"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
