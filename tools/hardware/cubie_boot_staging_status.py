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
DEFAULT_TARGETS = ["192.168.50.85", "192.168.50.95"]
DEFAULT_EXCLUDED_TARGETS = ["192.168.50.65"]
DEFAULT_STAGE = "kernel-boot-artifacts/a733-v4-corrected-root-proof-20260609"
DEFAULT_USER = "radxa"
DEFAULT_IDENTITY = "~/.ssh/id_ed25519"
DEFAULT_TIMEOUT = 8


def split_csv(values: list[str] | str) -> list[str]:
    if isinstance(values, str):
        values = [values]
    result: list[str] = []
    for value in values:
        result.extend(item.strip() for item in value.split(",") if item.strip())
    return result


def excluded_row(ip: str, stage: str) -> dict[str, Any]:
    return {
        "ip": ip,
        "ssh_returncode": None,
        "hostname": "",
        "arch": "",
        "model": "",
        "stage": stage,
        "stage_status": "excluded",
        "install_dir": "",
        "extlinux_label": "",
        "extlinux_menu_label": "",
        "extlinux_extra_args": "",
        "extlinux_append_override": "",
        "capture_label": "",
        "metadata_status": "excluded",
        "boot_entry_status": "excluded",
        "boot_files_status": "excluded",
        "boot_sha256_status": "excluded",
        "sha256_status": "excluded",
        "installer_syntax": "excluded",
        "sudo_status": "excluded",
        "root_install_complete": False,
        "ready_for_root_install": False,
        "excluded_from_kernel_work": True,
        "files": {},
        "stderr": "",
    }


def ssh_probe(ip: str, user: str, identity: str, stage: str, timeout: int) -> dict[str, Any]:
    remote = r"""
set -u
stage="$1"
boot_sha256_out=""
boot_sha256_err=""
sudo_out=""
sudo_err=""
trap 'rm -f "${boot_sha256_out:-}" "${boot_sha256_err:-}" "${sudo_out:-}" "${sudo_err:-}"' EXIT
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
for file in Image sun60i-a733-cubie-a7s.dtb config manifest.txt SHA256SUMS install-metadata.env install-extlinux-entry.sh; do
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
install_dir=""
extlinux_label=""
extlinux_menu_label=""
extlinux_extra_args=""
extlinux_append_override=""
capture_label=""
if [ -f install-metadata.env ]; then
  printf 'metadata_status=present\n'
  install_dir="$(awk -F= '$1 == "INSTALL_DIR" { print substr($0, index($0, "=") + 1); exit }' install-metadata.env)"
  extlinux_label="$(awk -F= '$1 == "EXTLINUX_LABEL" { print substr($0, index($0, "=") + 1); exit }' install-metadata.env)"
  extlinux_menu_label="$(awk -F= '$1 == "EXTLINUX_MENU_LABEL" { print substr($0, index($0, "=") + 1); exit }' install-metadata.env)"
  extlinux_extra_args="$(awk -F= '$1 == "EXTLINUX_EXTRA_ARGS" { print substr($0, index($0, "=") + 1); exit }' install-metadata.env)"
  extlinux_append_override="$(awk -F= '$1 == "EXTLINUX_APPEND_OVERRIDE" { print substr($0, index($0, "=") + 1); exit }' install-metadata.env)"
  capture_label="$(awk -F= '$1 == "CAPTURE_LABEL" { print substr($0, index($0, "=") + 1); exit }' install-metadata.env)"
else
  printf 'metadata_status=missing\n'
fi
if [ -f install-extlinux-entry.sh ]; then
  if [ -z "$install_dir" ]; then
    install_dir="$(awk -F'"' '/^install_dir="/ { print $2; exit }' install-extlinux-entry.sh)"
  fi
  if [ -z "$extlinux_label" ]; then
    extlinux_label="$(awk -F'"' '/^label="/ { print $2; exit }' install-extlinux-entry.sh)"
  fi
  if [ -z "$capture_label" ]; then
    capture_label="$(basename "$stage")-boot"
  fi
  printf 'install_dir=%s\n' "$install_dir"
  printf 'extlinux_label=%s\n' "$extlinux_label"
  printf 'extlinux_menu_label=%s\n' "$extlinux_menu_label"
  printf 'extlinux_extra_args=%s\n' "$extlinux_extra_args"
  printf 'extlinux_append_override=%s\n' "$extlinux_append_override"
  printf 'capture_label=%s\n' "$capture_label"
  case "$extlinux_label" in
    ""|*[!A-Za-z0-9_.-]*)
      printf 'boot_entry_status=unexpected-label\n'
      ;;
    *)
    if [ -r /boot/extlinux/extlinux.conf ] &&
      grep -Fqx "label ${extlinux_label}" /boot/extlinux/extlinux.conf; then
      printf 'boot_entry_status=installed\n'
    elif [ -r /boot/extlinux/extlinux.conf ]; then
      printf 'boot_entry_status=missing\n'
    else
      printf 'boot_entry_status=unreadable\n'
    fi
    ;;
  esac
  case "$install_dir" in
    /boot/mainline-a733-*)
      if [ -d "$install_dir" ]; then
        missing=0
        for file in Image sun60i-a733-cubie-a7s.dtb config manifest.txt; do
          [ -e "${install_dir}/${file}" ] || missing=1
        done
        if [ "$missing" -eq 0 ]; then
          printf 'boot_files_status=present\n'
        else
          printf 'boot_files_status=incomplete\n'
        fi
      else
        printf 'boot_files_status=missing\n'
      fi
      ;;
    "")
      printf 'boot_files_status=unknown\n'
      ;;
    *)
      printf 'boot_files_status=unexpected-install-dir\n'
      ;;
  esac
  if [ -n "$install_dir" ] && [ -d "$install_dir" ]; then
    if command -v sha256sum >/dev/null 2>&1 && [ -f "${install_dir}/SHA256SUMS" ]; then
      boot_sha256_out="$(mktemp)"
      boot_sha256_err="$(mktemp)"
      if (cd "$install_dir" && sha256sum -c SHA256SUMS >"$boot_sha256_out" 2>"$boot_sha256_err"); then
        printf 'boot_sha256_status=ok\n'
      else
        printf 'boot_sha256_status=fail\n'
        sed 's/^/boot_sha256_error=/' "$boot_sha256_err" | head -5
      fi
      rm -f "$boot_sha256_out" "$boot_sha256_err"
    else
      printf 'boot_sha256_status=missing\n'
    fi
  else
    printf 'boot_sha256_status=not-installed\n'
  fi
  if bash -n install-extlinux-entry.sh >/tmp/cubie-stage-bashn.out 2>/tmp/cubie-stage-bashn.err; then
    printf 'installer_syntax=ok\n'
  else
    printf 'installer_syntax=fail\n'
    sed 's/^/installer_error=/' /tmp/cubie-stage-bashn.err | head -5
  fi
else
  printf 'installer_syntax=missing\n'
fi
if command -v sudo >/dev/null 2>&1; then
  sudo_out="$(mktemp)"
  sudo_err="$(mktemp)"
  if sudo -n true >"$sudo_out" 2>"$sudo_err"; then
    printf 'sudo_status=noninteractive-ok\n'
  elif grep -qi 'password' "$sudo_err" 2>/dev/null; then
    printf 'sudo_status=password-required\n'
  else
    printf 'sudo_status=noninteractive-fail\n'
    sed 's/^/sudo_error=/' "$sudo_err" | head -5
  fi
else
  printf 'sudo_status=missing\n'
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
        "extlinux_menu_label": fields.get("extlinux_menu_label", ""),
        "extlinux_extra_args": fields.get("extlinux_extra_args", ""),
        "extlinux_append_override": fields.get("extlinux_append_override", ""),
        "capture_label": fields.get("capture_label", ""),
        "metadata_status": fields.get("metadata_status", "unknown"),
        "boot_entry_status": fields.get("boot_entry_status", "unknown"),
        "boot_files_status": fields.get("boot_files_status", "unknown"),
        "boot_sha256_status": fields.get("boot_sha256_status", "unknown"),
        "sha256_status": fields.get("sha256_status", "unknown"),
        "installer_syntax": fields.get("installer_syntax", "unknown"),
        "sudo_status": fields.get("sudo_status", "unknown"),
        "root_install_complete": (
            fields.get("boot_entry_status") == "installed"
            and fields.get("boot_files_status") == "present"
            and fields.get("boot_sha256_status") == "ok"
        ),
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
    excluded = set(
        []
        if getattr(args, "include_excluded", False)
        else split_csv(getattr(args, "exclude_target", DEFAULT_EXCLUDED_TARGETS))
    )
    rows = [
        excluded_row(ip, args.stage)
        if ip in excluded
        else ssh_probe(ip, args.user, args.identity, args.stage, args.timeout)
        for ip in targets
    ]
    ready = [row for row in rows if row["ready_for_root_install"]]
    installed = [row for row in rows if row["root_install_complete"]]
    action_rows = installed or ready
    capture_labels = sorted({row.get("capture_label") for row in action_rows if row.get("capture_label")})
    labels = sorted({row.get("extlinux_label") for row in action_rows if row.get("extlinux_label")})
    sudo_statuses = sorted({row.get("sudo_status") for row in ready if row.get("sudo_status")})
    needs_interactive_sudo = "password-required" in sudo_statuses
    sudo_hint = ""
    if "password-required" in sudo_statuses:
        sudo_hint = " using interactive sudo password entry"
    elif "noninteractive-ok" in sudo_statuses:
        sudo_hint = " using non-interactive sudo"
    capture_label = capture_labels[0] if capture_labels else f"{Path(args.stage).name}-boot"
    selection = labels[0] if labels else "the staged non-default boot label"
    if installed:
        target_names = ", ".join(f"{row.get('hostname') or row.get('ip')}:{row.get('ip')}" for row in installed)
        target_hint = f" for one installed board ({target_names})" if target_names else ""
        next_action = (
            f"run scripts/cubie-uart-interactive-boot-session {capture_label}{target_hint}; "
            f"reboot the board separately and select {selection}"
        )
    elif ready and needs_interactive_sudo:
        target_ip = ready[0].get("ip") or "TARGET_IP"
        next_action = (
            "run scripts/cubie-interactive-root-install-session "
            f"--confirm-target-ip {target_ip} from an interactive terminal; "
            "enter the Cubie sudo password when prompted, then use the capture it starts "
            f"to select {selection}"
        )
    elif ready:
        next_action = (
            "run the staged install-extlinux-entry.sh"
            f"{sudo_hint} on the chosen board, "
            f"then run scripts/cubie-uart-interactive-boot-session {capture_label} "
            f"and select {selection}"
        )
    else:
        next_action = "stage or repair boot artifacts before attempting a hardware boot proof"
    return {
        "stage": args.stage,
        "targets": targets,
        "ready_count": len(ready),
        "installed_count": len(installed),
        "target_count": len(rows),
        "excluded_targets": sorted(excluded),
        "rows": rows,
        "next_action": next_action,
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Cubie Boot Staging Status",
        "",
        f"Stage: `{data['stage']}`",
        f"Ready for root install: `{data['ready_count']}/{data['target_count']}`",
        f"Installed boot entry: `{data.get('installed_count', 0)}/{data['target_count']}`",
        f"Excluded targets: `{', '.join(data.get('excluded_targets', [])) or 'none'}`",
        "",
        "| ip | hostname | model | stage | metadata | sha256 | installer | sudo | bootargs | boot entry | boot files | boot sha256 | ready |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["rows"]:
        lines.append(
            "| "
            f"`{row['ip']}` | "
            f"{row['hostname'] or '-'} | "
            f"{row['model'] or '-'} | "
            f"{row['stage_status']} | "
            f"{row['metadata_status']} | "
            f"{row['sha256_status']} | "
            f"{row['installer_syntax']} | "
            f"{row['sudo_status']} | "
            f"{row.get('extlinux_append_override') or row.get('extlinux_extra_args') or '-'} | "
            f"{row['boot_entry_status']} | "
            f"{row['boot_files_status']} | "
            f"{row['boot_sha256_status']} | "
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
    parser.add_argument("--exclude-target", action="append", default=list(DEFAULT_EXCLUDED_TARGETS))
    parser.add_argument("--include-excluded", action="store_true")
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
