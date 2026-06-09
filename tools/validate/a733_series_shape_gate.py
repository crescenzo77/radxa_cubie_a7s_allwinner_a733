#!/usr/bin/env python3
"""Gate an exported A733 patch series against the current upstream strategy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


FORBIDDEN_SUBJECTS = {
    "local-ccu-binding": re.compile(r"\bdt-bindings:\s+clock:.*\bA733\b", re.IGNORECASE),
    "local-ccu-driver": re.compile(r"\bclk:\s+sunxi-ng:.*\bA733\b", re.IGNORECASE),
    "local-pinctrl-binding": re.compile(r"\bdt-bindings:\s+pinctrl:.*\bA733\b", re.IGNORECASE),
    "local-pinctrl-driver": re.compile(r"\bpinctrl:\s+sunxi:.*\bA733\b", re.IGNORECASE),
    "standalone-mmc-compatible": re.compile(r"\bdt-bindings:\s+mmc:.*\bA733\b", re.IGNORECASE),
    "maintainers-sun60i-pattern": re.compile(r"\bMAINTAINERS:.*\bsun60i\b", re.IGNORECASE),
}

REQUIRED_SUBJECTS = {
    "soc-dtsi": re.compile(r"\barm64:\s+dts:\s+allwinner:.*\bA733\b.*\bSoC\b", re.IGNORECASE),
    "board-dts": re.compile(r"\barm64:\s+dts:\s+allwinner:.*\bRadxa Cubie A7S\b", re.IGNORECASE),
}

DEPENDENCY_IDS = {
    "20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech",
    "20250821004232.8134-1-andre.przywara@arm.com",
}

VENDOR_POLLUTION = {
    "vendor-compatible": re.compile(r"\barm,sun60iw2p1\b"),
    "vendor-path-alias": re.compile(r"\bsoc@3000000|sdmmc@4020000\b"),
    "fdt-workaround": re.compile(r"\bfdt_high\b"),
    "hardcoded-memory": re.compile(r"\bmemory@40000000\b"),
}

FEATURE_CREEP = {
    "ethernet-gmac": re.compile(r"\b(?:ethernet|gmac[0-9]*|emac[0-9]*)\b", re.IGNORECASE),
    "vpu-video": re.compile(r"\b(?:vpu[0-9]*|video-codec|cedrus)\b", re.IGNORECASE),
    "display-drm": re.compile(r"\b(?:display|drm|hdmi[0-9]*|tcon[0-9]*|de[0-9]*)\b", re.IGNORECASE),
    "wireless": re.compile(r"\b(?:wifi|wi-fi|bluetooth|bt)\b", re.IGNORECASE),
    "pcie-usbc": re.compile(r"\b(?:pcie[0-9]*|usb-c|typec|type-c)\b", re.IGNORECASE),
}


def patch_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("000*.patch"))


def read_patch(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    subject = ""
    for line in text.splitlines():
        if line.startswith("Subject:"):
            subject = line.removeprefix("Subject:").strip()
            break
    added_lines = []
    in_diff = False
    for line in text.splitlines():
        if line.startswith("diff --git "):
            in_diff = True
            continue
        if not in_diff or not line.startswith("+"):
            continue
        if line.startswith("+++") or line.startswith("+-- "):
            continue
        added_lines.append(line[1:])
    return {
        "path": str(path),
        "name": path.name,
        "subject": subject,
        "text": text,
        "added_text": "\n".join(added_lines),
    }


def find_matches(patterns: dict[str, re.Pattern[str]], text: str) -> list[str]:
    return [name for name, pattern in patterns.items() if pattern.search(text)]


def classify(path: Path, max_patches: int) -> dict[str, Any]:
    patches = [read_patch(item) for item in patch_files(path)]
    non_cover = [item for item in patches if not item["name"].startswith("0000-")]
    subjects = "\n".join(item["subject"] for item in patches)
    full_text = "\n".join(item["text"] for item in patches)
    added_text = "\n".join(item["added_text"] for item in patches)

    findings: list[dict[str, Any]] = []
    if not patches:
        findings.append({"kind": "missing-patches", "detail": "no 000*.patch files found"})
    if len(non_cover) > max_patches:
        findings.append(
            {
                "kind": "too-many-patches",
                "detail": f"{len(non_cover)} non-cover patches found; expected at most {max_patches}",
            }
        )

    for kind in find_matches(FORBIDDEN_SUBJECTS, subjects):
        findings.append({"kind": kind, "detail": "forbidden A733 scaffolding subject present"})

    for kind in find_matches(VENDOR_POLLUTION, added_text):
        findings.append({"kind": kind, "detail": "vendor bootloader workaround does not belong in upstream DTS"})

    feature_creep_text = "\n".join([subjects, added_text])
    for kind in find_matches(FEATURE_CREEP, feature_creep_text):
        findings.append({"kind": kind, "detail": "first A733 slice must remain UART0/SDMMC0 only"})

    missing_required = [
        name for name, pattern in REQUIRED_SUBJECTS.items() if not pattern.search(subjects)
    ]
    for name in missing_required:
        findings.append({"kind": f"missing-{name}", "detail": "minimal DTS/board series shape is incomplete"})

    dependency_text = "\n".join(
        line.strip() for line in full_text.splitlines() if "Depends-on:" in line
    )
    missing_deps = [item for item in sorted(DEPENDENCY_IDS) if item not in dependency_text]
    for dep in missing_deps:
        findings.append({"kind": "missing-depends-on", "detail": dep})

    status = "PASS" if not findings else "FAIL"
    return {
        "status": status,
        "root": str(path),
        "patch_count": len(non_cover),
        "patches": [{"name": item["name"], "subject": item["subject"]} for item in patches],
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Patch file or directory containing 000*.patch files")
    parser.add_argument("--max-patches", type=int, default=2)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = classify(Path(args.path).resolve(), args.max_patches)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status={result['status']}")
        print(f"patch_count={result['patch_count']}")
        for patch in result["patches"]:
            print(f"patch={patch['name']} subject={patch['subject'] or 'unknown'}")
        for finding in result["findings"]:
            print(f"{finding['kind']}: {finding['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
