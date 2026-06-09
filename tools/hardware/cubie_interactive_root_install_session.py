#!/usr/bin/env python3
"""Run the Cubie root install through an interactive SSH TTY, then verify/capture."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_boot_staging_status
import cubie_root_install_handoff


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = REPO_ROOT / "inventory" / "hardware" / "cubie-a7s-lab.json"


def staging_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        targets=args.targets,
        stage=args.stage,
        user=args.user,
        identity=args.identity,
        timeout=args.timeout,
        exclude_target=args.exclude_target,
        include_excluded=False,
    )


def select_target(staging: dict[str, Any]) -> dict[str, Any] | None:
    installed = cubie_root_install_handoff.selected_row(staging, "root_install_complete")
    if installed:
        return installed
    return cubie_root_install_handoff.selected_row(staging, "ready_for_root_install")


def install_argv(row: dict[str, Any], args: argparse.Namespace) -> list[str]:
    ip = str(row.get("ip") or "")
    stage = str(row.get("stage") or args.stage)
    remote = f"cd {shlex.quote(stage)} && sudo ./install-extlinux-entry.sh"
    return [
        "ssh",
        "-tt",
        "-o",
        "BatchMode=no",
        "-o",
        f"ConnectTimeout={args.timeout}",
        "-i",
        os.path.expanduser(args.identity),
        f"{args.user}@{ip}",
        remote,
    ]


def verify_capture_argv(args: argparse.Namespace) -> list[str]:
    return [
        str(REPO_ROOT / "scripts" / "cubie-root-install-handoff"),
        "--wait",
        str(args.wait),
        "--interval",
        str(args.interval),
        "--run-capture",
    ]


def shell_join(argv: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in argv)


def local_host_tokens() -> set[str]:
    tokens = {"localhost", "127.0.0.1", "::1"}
    for name in (socket.gethostname(), socket.getfqdn()):
        if name:
            tokens.add(name)
    for argv in (
        ["hostname", "-I"],
        ["ip", "-o", "addr", "show"],
        ["ifconfig"],
    ):
        try:
            proc = subprocess.run(
                argv,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=3,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if proc.returncode != 0:
            continue
        for token in re_split_host_tokens(proc.stdout):
            tokens.add(token)
    return {token for token in tokens if token}


def re_split_host_tokens(text: str) -> list[str]:
    return [
        token.split("/", 1)[0]
        for token in text.replace("\n", " ").split()
        if token and (token[0].isdigit() or ":" in token)
    ]


def is_local_host(host: str) -> bool:
    return bool(host and host in local_host_tokens())


def confirmation_error(row: dict[str, Any], confirm_target_ip: str) -> str:
    ip = str(row.get("ip") or "")
    if confirm_target_ip == ip:
        return ""
    if not confirm_target_ip:
        return f"missing --confirm-target-ip {ip}"
    return f"--confirm-target-ip {confirm_target_ip} does not match selected target {ip}"


def load_inventory(path: str) -> dict[str, Any]:
    inventory_path = Path(path)
    if not inventory_path.is_absolute():
        inventory_path = (REPO_ROOT / inventory_path).resolve()
    return json.loads(inventory_path.read_text(encoding="utf-8"))


def uart_devices_for_target(row: dict[str, Any], inventory: dict[str, Any]) -> tuple[str, list[str]]:
    ip = str(row.get("ip") or "")
    for board in inventory.get("boards", []):
        if str(board.get("ip") or "") != ip:
            continue
        uart = board.get("uart") if isinstance(board.get("uart"), dict) else {}
        host = str(uart.get("host") or inventory.get("uart_host") or "")
        devices = []
        device = str(uart.get("device") or "")
        if device:
            devices.append(device)
        return host, devices
    return "", []


def capture_window_devices(inventory: dict[str, Any]) -> tuple[str, list[str]]:
    host = str(inventory.get("uart_host") or "")
    devices = []
    for adapter in inventory.get("uart_adapters", []):
        if not isinstance(adapter, dict):
            continue
        adapter_host = str(adapter.get("host") or host)
        if host and adapter_host != host:
            continue
        if not host:
            host = adapter_host
        device = str(adapter.get("by_path") or adapter.get("device") or "")
        if device and device not in devices:
            devices.append(device)
    return host, devices


def uart_preflight(row: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if args.no_capture or args.skip_uart_preflight:
        return {"status": "skipped", "host": "", "devices": [], "error": ""}
    try:
        inventory = load_inventory(args.inventory)
    except Exception as exc:
        return {"status": "failed", "host": "", "devices": [], "error": f"inventory: {exc}"}

    target_host, target_devices = uart_devices_for_target(row, inventory)
    window_host, window_devices = capture_window_devices(inventory)
    host = target_host or window_host
    devices = []
    for device in target_devices + window_devices:
        if device and device not in devices:
            devices.append(device)
    if not host or not devices:
        return {"status": "failed", "host": host, "devices": devices, "error": "no confirmed UART capture devices"}

    remote = "\n".join(
        [
            "set -eu",
            *[
                (
                    f"test -e {shlex.quote(device)} && "
                    f"test -r {shlex.quote(device)} && "
                    f"test -w {shlex.quote(device)}"
                )
                for device in devices
            ],
        ]
    )
    if is_local_host(host):
        proc = subprocess.run(
            ["bash", "-c", remote],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=12,
        )
    else:
        proc = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", host, remote],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=12,
        )
    if proc.returncode != 0:
        return {
            "status": "failed",
            "host": host,
            "devices": devices,
            "error": (proc.stderr or proc.stdout).strip() or f"ssh rc={proc.returncode}",
        }
    return {"status": "ok", "host": host, "devices": devices, "error": ""}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", default=",".join(cubie_boot_staging_status.DEFAULT_TARGETS))
    parser.add_argument("--stage", default=cubie_boot_staging_status.DEFAULT_STAGE)
    parser.add_argument("--user", default=cubie_boot_staging_status.DEFAULT_USER)
    parser.add_argument("--identity", default=cubie_boot_staging_status.DEFAULT_IDENTITY)
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--timeout", type=int, default=cubie_boot_staging_status.DEFAULT_TIMEOUT)
    parser.add_argument("--exclude-target", action="append", default=list(cubie_boot_staging_status.DEFAULT_EXCLUDED_TARGETS))
    parser.add_argument("--wait", type=int, default=90, help="Seconds to wait for installed boot artifacts after sudo install.")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-capture", action="store_true", help="Only run the interactive installer; skip post-install capture.")
    parser.add_argument("--skip-uart-preflight", action="store_true", help="Do not verify UART capture devices before install.")
    parser.add_argument(
        "--confirm-target-ip",
        default="",
        help="Required for a live root install; must match the selected target IP.",
    )
    args = parser.parse_args()

    staging = cubie_boot_staging_status.build_status(staging_args(args))
    row = select_target(staging)
    if not row:
        print("status=staging-not-ready", file=sys.stderr)
        print(staging.get("next_action", "stage or repair boot artifacts before root install"), file=sys.stderr)
        return 1
    if row.get("excluded_from_kernel_work"):
        print(f"refusing excluded kernel-work target: {row.get('ip')}", file=sys.stderr)
        return 2

    already_installed = bool(row.get("root_install_complete"))
    install_cmd = install_argv(row, args)
    capture_cmd = verify_capture_argv(args)
    uart_status = uart_preflight(row, args)

    print(f"target={row.get('hostname') or row.get('ip')} ip={row.get('ip')}")
    print(f"stage={row.get('stage') or args.stage}")
    if row.get("extlinux_label"):
        print(f"extlinux_label={row.get('extlinux_label')}")
    if row.get("extlinux_menu_label"):
        print(f"extlinux_menu_label={row.get('extlinux_menu_label')}")
    if row.get("extlinux_append_override"):
        print(f"extlinux_append_override={row.get('extlinux_append_override')}")
    if row.get("extlinux_extra_args"):
        print(f"extlinux_extra_args={row.get('extlinux_extra_args')}")
    print(f"sudo_status={row.get('sudo_status', 'unknown')}")
    print(f"uart_preflight_status={uart_status['status']}")
    if uart_status.get("host"):
        print(f"uart_preflight_host={uart_status['host']}")
    if uart_status.get("devices"):
        print(f"uart_preflight_devices={','.join(uart_status['devices'])}")
    if uart_status.get("error"):
        print(f"uart_preflight_error={uart_status['error']}")
    if already_installed:
        print("status=boot-selection-required")
    else:
        print("status=root-install-required")
        print(f"required_confirmation=--confirm-target-ip {row.get('ip')}")
    print(f"install_command={shell_join(install_cmd)}")
    if not args.no_capture:
        print("post_install_mode=interactive-uart-boot")
        print(f"post_install_command={shell_join(capture_cmd)}")

    if args.dry_run:
        return 0
    if not already_installed:
        error = confirmation_error(row, args.confirm_target_ip)
        if error:
            print(f"refusing live root install: {error}", file=sys.stderr)
            return 2
    if not already_installed and not args.no_capture and uart_status["status"] != "ok":
        print(
            f"refusing live root install: UART preflight {uart_status['status']}",
            file=sys.stderr,
        )
        return 2
    sudo_status = row.get("sudo_status")
    if not already_installed and sudo_status != "noninteractive-ok" and not sys.stdin.isatty():
        print(
            f"refusing sudo_status={sudo_status or 'unknown'} install without an interactive TTY",
            file=sys.stderr,
        )
        return 2

    if not already_installed:
        install_rc = subprocess.run(install_cmd, check=False).returncode
        if install_rc != 0:
            return install_rc
    if args.no_capture:
        return 0
    return subprocess.run(capture_cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
