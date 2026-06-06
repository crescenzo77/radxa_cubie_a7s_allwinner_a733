#!/usr/bin/env python3
"""Check whether exact A733 v4 boot artifacts are staged on Cubie boards."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGETS = ["192.168.50.65", "192.168.50.95"]
DEFAULT_STAGE = "kernel-boot-artifacts/a733-v4-abc8d07b0a63-20260606T152409Z"
DEFAULT_USER = "radxa"
DEFAULT_IDENTITY = "~/.ssh/id_ed25519"
DEFAULT_TIMEOUT = 8


def ssh_probe(ip: str, user: str, identity: str, stage: str, timeout: int) -> dict[str, Any]:
    remote = r"""
set -u
stage="$1"
printf 'hostname='; hostname
printf 'arch='; uname -m
if [ -r /proc/device-tree/model ]; then
  printf 'model='
  tr '\000' '\n' </proc/device-tree/model
fi
printf 'stage=%s\n' "$stage"
if [ ! -d "$stage" ]; then
  printf 'stage_status=missing\n'
  exit 0
fi
cd "$stage" || exit 0
printf 'stage_status=present\n'
for file in Image sun60i-a733-cubie-a7s.dtb config manifest.txt SHA256SUMS install-extlinux-entry.sh; do
  if [ -e "$file" ]; then
    bytes="$(wc -c <"$file" | tr -d ' ')"
    printf 'file_%s=%s\n' "$file" "$bytes"
  else
    printf 'file_%s=missing\n' "$file"
  fi
done
if command -v sha256sum >/dev/null 2>&1 && [ -f SHA256SUMS ]; then
  if sha256sum -c SHA256SUMS >/tmp/cubie-stage-sha256.out 2>/tmp/cubie-stage-sha256.err; then
    printf 'sha256_status=ok\n'
  else
    printf 'sha256_status=fail\n'
    sed 's/^/sha256_error=/' /tmp/cubie-stage-sha256.err | head -5
  fi
else
  printf 'sha256_status=unavailable\n'
fi
if [ -f install-extlinux-entry.sh ]; then
  awk -F'"' '/^install_dir="/ { print "install_dir="$2; exit }' install-extlinux-entry.sh
  awk -F'"' '/^label="/ { print "extlinux_label="$2; exit }' install-extlinux-entry.sh
  if bash -n install-extlinux-entry.sh >/tmp/cubie-stage-bashn.out 2>/tmp/cubie-stage-bashn.err; then
    printf 'installer_syntax=ok\n'
  else
    printf 'installer_syntax=fail\n'
    sed 's/^/installer_error=/' /tmp/cubie-stage-bashn.err | head -5
  fi
else
  printf 'installer_syntax=missing\n'
fi
"""
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={timeout}",
        "-i",
        os.path.expanduser(identity),
        f"{user}@{ip}",
        "bash",
        "-s",
        "--",
        stage,
    ]
    proc = subprocess.run(
        cmd,
        input=remote,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(5, timeout + 8),
    )
    fields: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key] = value
    ok = (
        proc.returncode == 0
        and fields.get("stage_status") == "present"
        and fields.get("sha256_status") == "ok"
        and fields.get("installer_syntax") == "ok"
    )
    return {
        "ip": ip,
        "ssh_returncode": proc.returncode,
        "hostname": fields.get("hostname", ""),
        "arch": fields.get("arch", ""),
        "model": fields.get("model", ""),
        "stage": stage,
        "stage_status": fields.get("stage_status", "unknown"),
        "install_dir": fields.get("install_dir", ""),
        "extlinux_label": fields.get("extlinux_label", ""),
        "sha256_status": fields.get("sha256_status", "unknown"),
        "installer_syntax": fields.get("installer_syntax", "unknown"),
        "ready_for_root_install": ok,
        "files": {
            key.removeprefix("file_"): value
            for key, value in fields.items()
            if key.startswith("file_")
        },
        "stderr": proc.stderr.strip(),
    }


def build_status(args: argparse.Namespace) -> dict[str, Any]:
    targets = [target.strip() for target in args.targets.split(",") if target.strip()]
    rows = [ssh_probe(ip, args.user, args.identity, args.stage, args.timeout) for ip in targets]
    ready = [row for row in rows if row["ready_for_root_install"]]
    labels = sorted({row.get("extlinux_label") for row in ready if row.get("extlinux_label")})
    capture_label = f"{Path(args.stage).name}-boot"
    label_hint = f" and select {labels[0]}" if labels else ""
    return {
        "stage": args.stage,
        "targets": targets,
        "ready_count": len(ready),
        "target_count": len(rows),
        "rows": rows,
        "next_action": (
            "run the staged install-extlinux-entry.sh with sudo/root on the chosen board, "
            f"then start scripts/cubie-manual-boot-session 180 {capture_label}{label_hint}"
            if ready
            else "stage or repair boot artifacts before attempting a hardware boot proof"
        ),
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Cubie Boot Staging Status",
        "",
        f"Stage: `{data['stage']}`",
        f"Ready for root install: `{data['ready_count']}/{data['target_count']}`",
        "",
        "| ip | hostname | model | stage | sha256 | installer | ready |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["rows"]:
        lines.append(
            "| "
            f"`{row['ip']}` | "
            f"{row['hostname'] or '-'} | "
            f"{row['model'] or '-'} | "
            f"{row['stage_status']} | "
            f"{row['sha256_status']} | "
            f"{row['installer_syntax']} | "
            f"{'yes' if row['ready_for_root_install'] else 'no'} |"
        )
    lines.extend(["", "## Next Action", "", data["next_action"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", default=",".join(DEFAULT_TARGETS))
    parser.add_argument("--stage", default=DEFAULT_STAGE)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity", default=DEFAULT_IDENTITY)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = build_status(args)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
