#!/usr/bin/env python3
"""Run the Cubie root install through an interactive SSH TTY, then verify/capture."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cubie_boot_staging_status
import cubie_root_install_handoff


REPO_ROOT = Path(__file__).resolve().parents[2]


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", default=",".join(cubie_boot_staging_status.DEFAULT_TARGETS))
    parser.add_argument("--stage", default=cubie_boot_staging_status.DEFAULT_STAGE)
    parser.add_argument("--user", default=cubie_boot_staging_status.DEFAULT_USER)
    parser.add_argument("--identity", default=cubie_boot_staging_status.DEFAULT_IDENTITY)
    parser.add_argument("--timeout", type=int, default=cubie_boot_staging_status.DEFAULT_TIMEOUT)
    parser.add_argument("--exclude-target", action="append", default=list(cubie_boot_staging_status.DEFAULT_EXCLUDED_TARGETS))
    parser.add_argument("--wait", type=int, default=90, help="Seconds to wait for installed boot artifacts after sudo install.")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-capture", action="store_true", help="Only run the interactive installer; skip post-install capture.")
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

    print(f"target={row.get('hostname') or row.get('ip')} ip={row.get('ip')}")
    print(f"stage={row.get('stage') or args.stage}")
    print(f"sudo_status={row.get('sudo_status', 'unknown')}")
    if already_installed:
        print("status=boot-selection-required")
    else:
        print("status=root-install-required")
    print(f"install_command={shell_join(install_cmd)}")
    if not args.no_capture:
        print(f"post_install_command={shell_join(capture_cmd)}")

    if args.dry_run:
        return 0
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
