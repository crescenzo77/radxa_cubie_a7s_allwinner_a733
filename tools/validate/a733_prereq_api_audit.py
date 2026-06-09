#!/usr/bin/env python3
"""Audit the public A733 DTS export against known prerequisite API contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def patch_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("000*.patch"))


def read_patch_dir(path: Path) -> tuple[list[dict[str, str]], str]:
    patches: list[dict[str, str]] = []
    texts: list[str] = []
    for patch in patch_files(path):
        text = patch.read_text(encoding="utf-8", errors="replace")
        patches.append({"name": patch.name, "text": text})
        texts.append(text)
    return patches, "\n".join(texts)


def added_text(full_text: str) -> str:
    lines: list[str] = []
    in_diff = False
    for line in full_text.splitlines():
        if line.startswith("diff --git "):
            in_diff = True
            continue
        if not in_diff or not line.startswith("+"):
            continue
        if line.startswith("+++") or line.startswith("+-- "):
            continue
        lines.append(line[1:])
    return "\n".join(lines)


def ccu_clock_names(text: str) -> list[str]:
    match = re.search(
        r"ccu:\s+clock-controller@2002000\s*\{(?P<body>.*?)^\s*\};",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    if not match:
        return []
    names = re.search(r"clock-names\s*=\s*(?P<names>[^;]+);", match.group("body"), flags=re.DOTALL)
    if not names:
        return []
    return re.findall(r'"([^"]+)"', names.group("names"))


def ccu_clocks_cell_count(text: str) -> int | None:
    match = re.search(
        r"ccu:\s+clock-controller@2002000\s*\{(?P<body>.*?)^\s*\};",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    if not match:
        return None
    clocks = re.search(r"clocks\s*=\s*(?P<clocks>[^;]+);", match.group("body"), flags=re.DOTALL)
    if not clocks:
        return None
    return len(re.findall(r"<[^>]+>", clocks.group("clocks")))


def audit(path: Path) -> dict[str, Any]:
    patches, full_text = read_patch_dir(path)
    added = added_text(full_text)
    findings: list[dict[str, str]] = []

    if not patches:
        findings.append({"kind": "missing-patches", "detail": "no 000*.patch files found"})
        return {"status": "FAIL", "root": str(path), "findings": findings}

    if 'compatible = "allwinner,sun60i-a733-ccu";' in added:
        names = ccu_clock_names(added)
        count = ccu_clocks_cell_count(added)
        if "losc-fanout" not in names:
            findings.append(
                {
                    "kind": "ccu-clock-names-missing-losc-fanout",
                    "detail": (
                        "Junhui Liu's A733 CCU RFC binding requires the main CCU "
                        "clock-names to include hosc, losc, iosc, and losc-fanout; "
                        f"current DTS names are {names or 'missing'}"
                    ),
                }
            )
        if count is not None and count < 4:
            findings.append(
                {
                    "kind": "ccu-clock-input-count",
                    "detail": (
                        "Junhui Liu's A733 CCU RFC binding has four main CCU input "
                        f"clocks; current DTS has {count}"
                    ),
                }
            )

    mmc_compatible = '"allwinner,sun60i-a733-mmc"' in added
    mmc_binding_coverage = (
        "Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml" in full_text
        and "allwinner,sun60i-a733-mmc" in full_text
    )
    if mmc_compatible and not mmc_binding_coverage:
        findings.append(
            {
                "kind": "mmc-compatible-without-binding-coverage",
                "detail": (
                    "the DTS uses allwinner,sun60i-a733-mmc, but the current export "
                    "does not document that compatible or identify an accepted base "
                    "that already contains it"
                ),
            }
        )

    if 'compatible = "allwinner,sun60i-a733-pinctrl";' in added:
        if "allwinner,pinmux" not in added:
            findings.append(
                {
                    "kind": "pinctrl-pinmux-property-missing",
                    "detail": (
                        "Andre Przywara's A733 pinctrl RFC uses DT-provided "
                        "allwinner,pinmux values; current pin groups should keep them"
                    ),
                }
            )

    status = "PASS" if not findings else "FAIL"
    return {
        "status": status,
        "root": str(path),
        "patches": [patch["name"] for patch in patches],
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Patch file or directory containing 000*.patch files")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = audit(Path(args.path).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status={result['status']}")
        for finding in result["findings"]:
            print(f"{finding['kind']}: {finding['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
