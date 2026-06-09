#!/usr/bin/env python3
"""Classify a Cubie A733 corrected-root UART proof log."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_KERNEL = "Linux version 7.1.0-rc6-gabc8d07b0a63"
EXPECTED_MODEL = "Machine model: Radxa Cubie A7S"
EXPECTED_PARTUUID = "db375e07-7682-4d4e-b8bc-a923dd0b027e"


CHECKS: list[tuple[str, str, str]] = [
    (
        "uboot_image_load",
        "U-Boot loaded exact v4 Image",
        r"Retrieving file: /boot/mainline-a733-v4-abc8d07b0a63/Image",
    ),
    (
        "uboot_dtb_load",
        "U-Boot loaded exact v4 DTB",
        r"Retrieving file: /boot/mainline-a733-v4-abc8d07b0a63/sun60i-a733-cubie-a7s\.dtb",
    ),
    (
        "uboot_drm_workaround",
        "U-Boot RAM drm_debug workaround crossed",
        r"drm debug mode:\s*1",
    ),
    ("kernel_version", "exact v4 kernel version", re.escape(EXPECTED_KERNEL)),
    ("machine_model", "Radxa Cubie A7S model", re.escape(EXPECTED_MODEL)),
    ("cpu8", "all 8 CPUs booted", r"Brought up 8 CPUs|SMP: Total of 8 processors activated"),
    ("gicv3", "GICv3 initialization", r"GICv3"),
    ("pinctrl", "A733 pinctrl initialization", r"sun60i-a733-pinctrl|2000000\.pinctrl"),
    ("ttyS0", "mainline UART0 ttyS0", r"ttyS0|2500000\.serial"),
    ("sunxi_mmc", "SDMMC0 driver initialization", r"sunxi-mmc 4020000\.mmc: initialized"),
    ("root_partuuid", "correct PARTUUID in command line or mount evidence", re.escape(EXPECTED_PARTUUID)),
    ("root_ro", "read-only root command line or mount evidence", r"(?:^|\s)ro(?:\s|$)|/dev/mmcblk0p3\s+/\s+\S+\s+ro[,\s]"),
    ("rootflags_noload", "read-only ext4 noload proof intent", r"rootflags=noload|noload"),
    ("mmcblk0", "mmcblk0 block device", r"mmcblk0"),
    ("mmcblk0p3", "mmcblk0p3 partition/root evidence", r"mmcblk0p3|mmcblk0:.*p3"),
    ("shell_or_mount", "read-only shell or root mount evidence", r"init=/bin/sh|Run /bin/sh as init process|EXT4-fs .* mounted filesystem|/dev/mmcblk0p3 / "),
]

ERROR_PATTERNS: list[tuple[str, str]] = [
    ("panic", r"Kernel panic|panic - not syncing|VFS: Unable to mount root fs"),
    ("oops", r"\bOops\b"),
    ("bad_image", r"Bad Linux ARM64 Image magic"),
    ("fdt_badpath", r"FDT_ERR_BADPATH|/chosen node create failed|fdt_add_subnode fail"),
    ("old_uuid_root", r"Disabling rootwait; root= is invalid|root=UUID=6f750720-329a-45f0-a4b5-abc5797b040a"),
]


def read_log(path: Path) -> str:
    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    return "".join(ch if ch == "\n" or ch == "\t" or ord(ch) >= 32 else "." for ch in text)


def find_matches(text: str, patterns: list[tuple[str, str, str]]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for key, description, pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        results[key] = {
            "ok": bool(match),
            "description": description,
            "pattern": pattern,
            "excerpt": excerpt_for(text, match.start()) if match else "",
        }
    return results


def find_errors(text: str) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for key, pattern in ERROR_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        results[key] = {
            "present": bool(match),
            "pattern": pattern,
            "excerpt": excerpt_for(text, match.start()) if match else "",
        }
    return results


def excerpt_for(text: str, offset: int, radius: int = 160) -> str:
    start = max(0, offset - radius)
    end = min(len(text), offset + radius)
    return " ".join(text[start:end].split())


def classify(checks: dict[str, dict[str, Any]], errors: dict[str, dict[str, Any]]) -> tuple[str, str]:
    missing = [key for key, value in checks.items() if not value["ok"]]
    present_errors = [key for key, value in errors.items() if value["present"]]
    if present_errors:
        return "fail", f"error markers present: {', '.join(present_errors)}"
    if missing:
        return "incomplete", f"missing required evidence: {', '.join(missing)}"
    return "pass", "corrected-root runtime proof evidence is present without known fatal markers"


def build_gate(path: Path) -> dict[str, Any]:
    text = read_log(path)
    checks = find_matches(text, CHECKS)
    errors = find_errors(text)
    status, reason = classify(checks, errors)
    return {
        "status": status,
        "reason": reason,
        "log_path": str(path),
        "bytes": path.stat().st_size,
        "checks": checks,
        "errors": errors,
        "human_required": status != "pass",
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Cubie A733 Corrected-Root Proof Gate",
        "",
        f"Status: `{data['status']}`",
        f"Reason: {data['reason']}",
        f"Log: `{data['log_path']}`",
        "",
        "## Required Evidence",
        "",
        "| check | ok | excerpt |",
        "| --- | --- | --- |",
    ]
    for key, value in data["checks"].items():
        excerpt = str(value.get("excerpt") or "").replace("|", "/")
        lines.append(f"| `{key}` | `{value['ok']}` | {excerpt or '-'} |")
    lines.extend(["", "## Fatal Markers", "", "| marker | present | excerpt |", "| --- | --- | --- |"])
    for key, value in data["errors"].items():
        excerpt = str(value.get("excerpt") or "").replace("|", "/")
        lines.append(f"| `{key}` | `{value['present']}` | {excerpt or '-'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", help="UART .uart.log file to classify.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero unless status is pass.")
    args = parser.parse_args()

    data = build_gate(Path(args.log))
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(markdown(data), end="")
    return 1 if args.strict and data["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
