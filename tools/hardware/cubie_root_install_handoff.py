#!/usr/bin/env python3
"""Print the exact Cubie root-install handoff from verified staging state."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_boot_staging_status


REPO_ROOT = Path(__file__).resolve().parents[2]
STRIX_HOST = os.environ.get("KERNEL_STRIX_HOST", "192.168.50.11")
STRIX_SSH_TARGET = os.environ.get("KERNEL_STRIX_SSH_TARGET", f"enzo@{STRIX_HOST}")
STRIX_REPO = os.environ.get("KERNEL_STRIX_REPO", "/srv/projects/homelab")
STRIX_REMOTE = os.environ.get("KERNEL_STRIX_REMOTE", "mac-mini")


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


def selected_row(staging: dict[str, Any], key: str) -> dict[str, Any] | None:
    rows = staging.get("rows", [])
    selected = [row for row in rows if row.get(key)]
    return selected[0] if selected else None


def install_command(row: dict[str, Any], user: str) -> str:
    ip = row.get("ip") or "unknown-ip"
    stage = row.get("stage") or cubie_boot_staging_status.DEFAULT_STAGE
    target = shlex.quote(f"{user}@{ip}")
    sudo = "sudo -n" if row.get("sudo_status") == "noninteractive-ok" else "sudo"
    remote = f"cd {shlex.quote(stage)} && {sudo} ./install-extlinux-entry.sh"
    return f"ssh -t {target} {shlex.quote(remote)}"


def local_board_command(row: dict[str, Any]) -> str:
    stage = row.get("stage") or cubie_boot_staging_status.DEFAULT_STAGE
    sudo = "sudo -n" if row.get("sudo_status") == "noninteractive-ok" else "sudo"
    return f"cd {shlex.quote(stage)}\n{sudo} ./install-extlinux-entry.sh"


def capture_label(row: dict[str, Any]) -> str:
    return str(row.get("capture_label") or f"{Path(row.get('stage') or cubie_boot_staging_status.DEFAULT_STAGE).name}-boot")


def capture_command(row: dict[str, Any]) -> str:
    capture = capture_label(row)
    return f"scripts/cubie-uart-interactive-boot-session {shlex.quote(capture)}"


def interactive_install_command(row: dict[str, Any]) -> str:
    ip = row.get("ip") or "unknown-ip"
    return f"scripts/cubie-interactive-root-install-session --confirm-target-ip {shlex.quote(str(ip))}"


def strix_interactive_install_command(row: dict[str, Any]) -> str:
    return shlex.join(
        [
            "ssh",
            "-tt",
            STRIX_SSH_TARGET,
            f"cd {shlex.quote(STRIX_REPO)} && "
            f"git pull --ff-only {shlex.quote(STRIX_REMOTE)} main && "
            f"{interactive_install_command(row)}",
        ]
    )


def capture_argv(row: dict[str, Any]) -> list[str]:
    return [
        str(REPO_ROOT / "scripts" / "cubie-uart-interactive-boot-session"),
        capture_label(row),
    ]


def extlinux_label(row: dict[str, Any]) -> str:
    return str(row.get("extlinux_menu_label") or row.get("extlinux_label") or "the staged non-default label")


def extlinux_bootargs(row: dict[str, Any]) -> str:
    return str(row.get("extlinux_append_override") or row.get("extlinux_extra_args") or "none")


def render(staging: dict[str, Any], args: argparse.Namespace) -> str:
    installed = selected_row(staging, "root_install_complete")
    ready = selected_row(staging, "ready_for_root_install")
    excluded = ", ".join(staging.get("excluded_targets", [])) or "none"
    lines = [
        "# Cubie Root Install Handoff",
        "",
        f"Stage: `{staging.get('stage')}`",
        f"Excluded targets: `{excluded}`",
        f"Ready for root install: `{staging.get('ready_count', 0)}/{staging.get('target_count', 0)}`",
        f"Installed boot entry: `{staging.get('installed_count', 0)}/{staging.get('target_count', 0)}`",
        "",
    ]
    if installed:
        lines.extend(
            [
                "Status: `boot-selection-required`",
                "",
                "Root install is already detected and installed artifact checks passed.",
                "",
                "Next command from this repo:",
                "",
                "```sh",
                capture_command(installed),
                "```",
                "",
                "Select this non-default U-Boot label over UART:",
                "",
                f"`{extlinux_label(installed)}`",
                "",
                "Before selecting the label, run this RAM-only U-Boot step:",
                "",
                "```text",
                "setenv drm_debug 1",
                "run bootcmd",
                "```",
                "",
                "Expected bootargs:",
                "",
                f"`{extlinux_bootargs(installed)}`",
            ]
        )
        return "\n".join(lines)
    if ready:
        host = ready.get("hostname") or "target board"
        ip = ready.get("ip") or "unknown IP"
        lines.extend(
            [
                "Status: `root-install-required`",
                "",
                f"Target: `{host}` `{ip}`",
                f"Sudo preflight: `{ready.get('sudo_status', 'unknown')}`",
                "",
                "Preferred live command from Codex Desktop:",
                "",
                "```sh",
                strix_interactive_install_command(ready),
                "```",
                "",
                "This keeps the live UART/root-install session on Strix, where the USB serial adapters are attached.",
                "",
                "Run on the board:",
                "",
                "```sh",
                local_board_command(ready),
                "```",
                "",
                "Or from a terminal with an interactive SSH TTY:",
                "",
                "```sh",
                install_command(ready, args.user),
                "```",
                "",
                "After the installer succeeds, run:",
                "",
                "```sh",
                capture_command(ready),
                "```",
                "",
                "Select this non-default U-Boot label over UART:",
                "",
                f"`{extlinux_label(ready)}`",
                "",
                "Before selecting the label, run this RAM-only U-Boot step:",
                "",
                "```text",
                "setenv drm_debug 1",
                "run bootcmd",
                "```",
                "",
                "Expected bootargs:",
                "",
                f"`{extlinux_bootargs(ready)}`",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            "Status: `staging-not-ready`",
            "",
            staging.get("next_action", "Repair staging before attempting boot proof."),
        ]
    )
    return "\n".join(lines)


def poll(args: argparse.Namespace) -> dict[str, Any]:
    deadline = time.monotonic() + args.wait
    last: dict[str, Any] = {}
    while True:
        last = cubie_boot_staging_status.build_status(staging_args(args))
        if last.get("installed_count", 0) > 0 or args.wait <= 0 or time.monotonic() >= deadline:
            return last
        time.sleep(max(1.0, args.interval))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", default=",".join(cubie_boot_staging_status.DEFAULT_TARGETS))
    parser.add_argument("--stage", default=cubie_boot_staging_status.DEFAULT_STAGE)
    parser.add_argument("--user", default=cubie_boot_staging_status.DEFAULT_USER)
    parser.add_argument("--identity", default=cubie_boot_staging_status.DEFAULT_IDENTITY)
    parser.add_argument("--timeout", type=int, default=cubie_boot_staging_status.DEFAULT_TIMEOUT)
    parser.add_argument("--exclude-target", action="append", default=list(cubie_boot_staging_status.DEFAULT_EXCLUDED_TARGETS))
    parser.add_argument("--wait", type=int, default=0, help="Poll up to this many seconds for root install completion.")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero until installed boot artifacts are verified.")
    parser.add_argument(
        "--run-capture",
        action="store_true",
        help="After installed artifacts are verified, run the interactive UART boot session. This does not reboot or power-cycle.",
    )
    args = parser.parse_args()

    staging = poll(args)
    installed = selected_row(staging, "root_install_complete")
    if args.json:
        print(json.dumps(staging, indent=2, sort_keys=True))
    else:
        print(render(staging, args))
    if args.run_capture:
        if not installed:
            print("capture_not_started=root-install-required", file=sys.stderr)
            return 1
        return subprocess.run(capture_argv(installed), check=False).returncode
    if args.strict and staging.get("installed_count", 0) == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
