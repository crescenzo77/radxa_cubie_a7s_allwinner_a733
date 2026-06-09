#!/usr/bin/env python3
"""Audit a Linux tree for the A733 prerequisite stack expected by DTS prep."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


RTC_BINDING = Path("Documentation/devicetree/bindings/rtc/allwinner,sun6i-a31-rtc.yaml")
RTC_CLOCK_HEADER = Path("include/dt-bindings/clock/sun60i-a733-rtc.h")
RTC_DRIVER = Path("drivers/clk/sunxi-ng/ccu-sun60i-a733-rtc.c")

CCU_BINDING = Path("Documentation/devicetree/bindings/clock/allwinner,sun60i-a733-ccu.yaml")
CCU_CLOCK_HEADER = Path("include/dt-bindings/clock/sun60i-a733-ccu.h")
CCU_RESET_HEADER = Path("include/dt-bindings/reset/sun60i-a733-ccu.h")
CCU_DRIVER = Path("drivers/clk/sunxi-ng/ccu-sun60i-a733.c")
R_CCU_CLOCK_HEADER = Path("include/dt-bindings/clock/sun60i-a733-r-ccu.h")
R_CCU_RESET_HEADER = Path("include/dt-bindings/reset/sun60i-a733-r-ccu.h")
R_CCU_DRIVER = Path("drivers/clk/sunxi-ng/ccu-sun60i-a733-r.c")

PINCTRL_BINDING_DIR = Path("Documentation/devicetree/bindings/pinctrl")
PINCTRL_DRIVER = Path("drivers/pinctrl/sunxi/pinctrl-sun60i-a733.c")

MMC_BINDING = Path("Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml")
SOC_DTSI = Path("arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi")

A733_RTC_COMPAT = "allwinner,sun60i-a733-rtc"
A733_CCU_COMPAT = "allwinner,sun60i-a733-ccu"
A733_PINCTRL_COMPAT = "allwinner,sun60i-a733-pinctrl"
A733_MMC_COMPAT = "allwinner,sun60i-a733-mmc"
D1_MMC_FALLBACK = "allwinner,sun20i-d1-mmc"
CCU_CLOCK_NAMES = ["hosc", "losc", "iosc", "losc-fanout"]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def rel(path: Path) -> str:
    return path.as_posix()


def git_value(tree: Path, argv: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(tree), *argv],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def git_info(tree: Path) -> dict[str, Any]:
    return {
        "head": git_value(tree, ["rev-parse", "HEAD"]),
        "head_short": git_value(tree, ["rev-parse", "--short", "HEAD"]),
        "branch": git_value(tree, ["branch", "--show-current"]),
        "dirty": bool(git_value(tree, ["status", "--short"])),
    }


def add_finding(findings: list[dict[str, str]], kind: str, detail: str) -> None:
    findings.append({"kind": kind, "detail": detail})


def contains_all(text: str, needles: list[str]) -> bool:
    return all(needle in text for needle in needles)


def binding_files_with_compatible(root: Path, directory: Path, compatible: str) -> list[str]:
    base = root / directory
    if not base.is_dir():
        return []
    matches = []
    for path in sorted(base.glob("*.yaml")):
        if compatible in read(path):
            matches.append(rel(path.relative_to(root)))
    return matches


def ccu_node_body(text: str) -> str:
    match = re.search(
        r"ccu:\s+clock-controller@2002000\s*\{(?P<body>.*?)^\s*\};",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    return match.group("body") if match else ""


def dtsi_ccu_clock_names(text: str) -> list[str]:
    body = ccu_node_body(text)
    match = re.search(r"clock-names\s*=\s*(?P<names>[^;]+);", body, flags=re.DOTALL)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group("names"))


def dtsi_ccu_clock_count(text: str) -> int | None:
    body = ccu_node_body(text)
    match = re.search(r"clocks\s*=\s*(?P<clocks>[^;]+);", body, flags=re.DOTALL)
    if not match:
        return None
    return len(re.findall(r"<[^>]+>", match.group("clocks")))


def mmc_binding_has_a733_fallback(text: str) -> bool:
    if A733_MMC_COMPAT not in text:
        return False
    pattern = re.compile(
        rf"const:\s+{re.escape(A733_MMC_COMPAT)}(?P<body>.{{0,500}}?)"
        rf"const:\s+{re.escape(D1_MMC_FALLBACK)}",
        flags=re.DOTALL,
    )
    return bool(pattern.search(text))


def audit(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    facts: dict[str, Any] = {}

    if not root.exists():
        add_finding(findings, "tree-missing", f"{root} does not exist")
        return {"status": "FAIL", "root": str(root), "git": {}, "facts": facts, "findings": findings}
    if not root.is_dir():
        add_finding(findings, "tree-not-directory", f"{root} is not a directory")
        return {"status": "FAIL", "root": str(root), "git": {}, "facts": facts, "findings": findings}

    rtc_binding = read(root / RTC_BINDING)
    facts["rtc_binding"] = rel(RTC_BINDING) if rtc_binding else ""
    facts["rtc_binding_has_a733"] = A733_RTC_COMPAT in rtc_binding
    facts["rtc_clock_header"] = rel(RTC_CLOCK_HEADER) if (root / RTC_CLOCK_HEADER).exists() else ""
    facts["rtc_driver"] = rel(RTC_DRIVER) if (root / RTC_DRIVER).exists() else ""
    if not facts["rtc_binding_has_a733"]:
        add_finding(findings, "rtc-binding-missing", f"{rel(RTC_BINDING)} lacks {A733_RTC_COMPAT}")
    if not facts["rtc_clock_header"]:
        add_finding(findings, "rtc-clock-header-missing", f"{rel(RTC_CLOCK_HEADER)} is missing")
    if not facts["rtc_driver"]:
        add_finding(findings, "rtc-ccu-driver-missing", f"{rel(RTC_DRIVER)} is missing")

    ccu_binding = read(root / CCU_BINDING)
    facts["ccu_binding"] = rel(CCU_BINDING) if ccu_binding else ""
    facts["ccu_binding_has_a733"] = A733_CCU_COMPAT in ccu_binding
    facts["ccu_binding_clock_names"] = {
        name: name in ccu_binding for name in CCU_CLOCK_NAMES
    }
    facts["ccu_clock_header"] = rel(CCU_CLOCK_HEADER) if (root / CCU_CLOCK_HEADER).exists() else ""
    facts["ccu_reset_header"] = rel(CCU_RESET_HEADER) if (root / CCU_RESET_HEADER).exists() else ""
    facts["ccu_driver"] = rel(CCU_DRIVER) if (root / CCU_DRIVER).exists() else ""
    facts["r_ccu_clock_header"] = rel(R_CCU_CLOCK_HEADER) if (root / R_CCU_CLOCK_HEADER).exists() else ""
    facts["r_ccu_reset_header"] = rel(R_CCU_RESET_HEADER) if (root / R_CCU_RESET_HEADER).exists() else ""
    facts["r_ccu_driver"] = rel(R_CCU_DRIVER) if (root / R_CCU_DRIVER).exists() else ""
    if not ccu_binding:
        add_finding(findings, "ccu-binding-missing", f"{rel(CCU_BINDING)} is missing")
    elif not facts["ccu_binding_has_a733"]:
        add_finding(findings, "ccu-compatible-missing", f"{rel(CCU_BINDING)} lacks {A733_CCU_COMPAT}")
    if ccu_binding and not contains_all(ccu_binding, CCU_CLOCK_NAMES):
        missing = [name for name in CCU_CLOCK_NAMES if name not in ccu_binding]
        add_finding(findings, "ccu-binding-clock-inputs-mismatch", "missing clock input names: " + ", ".join(missing))
    if not facts["ccu_clock_header"]:
        add_finding(findings, "ccu-clock-header-missing", f"{rel(CCU_CLOCK_HEADER)} is missing")
    if not facts["ccu_reset_header"]:
        add_finding(findings, "ccu-reset-header-missing", f"{rel(CCU_RESET_HEADER)} is missing")
    if not facts["ccu_driver"]:
        add_finding(findings, "ccu-driver-missing", f"{rel(CCU_DRIVER)} is missing")
    if not facts["r_ccu_clock_header"]:
        add_finding(findings, "r-ccu-clock-header-missing", f"{rel(R_CCU_CLOCK_HEADER)} is missing")
    if not facts["r_ccu_reset_header"]:
        add_finding(findings, "r-ccu-reset-header-missing", f"{rel(R_CCU_RESET_HEADER)} is missing")
    if not facts["r_ccu_driver"]:
        add_finding(findings, "r-ccu-driver-missing", f"{rel(R_CCU_DRIVER)} is missing")

    pinctrl_bindings = binding_files_with_compatible(root, PINCTRL_BINDING_DIR, A733_PINCTRL_COMPAT)
    facts["pinctrl_bindings"] = pinctrl_bindings
    facts["pinctrl_driver"] = rel(PINCTRL_DRIVER) if (root / PINCTRL_DRIVER).exists() else ""
    if not pinctrl_bindings:
        add_finding(findings, "pinctrl-binding-missing", f"no pinctrl binding contains {A733_PINCTRL_COMPAT}")
    if not facts["pinctrl_driver"]:
        add_finding(findings, "pinctrl-driver-missing", f"{rel(PINCTRL_DRIVER)} is missing")

    mmc_binding = read(root / MMC_BINDING)
    facts["mmc_binding"] = rel(MMC_BINDING) if mmc_binding else ""
    facts["mmc_binding_has_a733"] = A733_MMC_COMPAT in mmc_binding
    facts["mmc_binding_has_d1_fallback"] = mmc_binding_has_a733_fallback(mmc_binding)
    if not facts["mmc_binding_has_a733"]:
        add_finding(
            findings,
            "mmc-binding-missing",
            f"{rel(MMC_BINDING)} lacks {A733_MMC_COMPAT}; add one focused MMC binding patch if this is the chosen base",
        )
    elif not facts["mmc_binding_has_d1_fallback"]:
        add_finding(
            findings,
            "mmc-binding-fallback-mismatch",
            f"{A733_MMC_COMPAT} is present without the expected {D1_MMC_FALLBACK} fallback pattern",
        )

    dtsi = read(root / SOC_DTSI)
    facts["soc_dtsi"] = rel(SOC_DTSI) if dtsi else ""
    if dtsi and A733_CCU_COMPAT in dtsi:
        names = dtsi_ccu_clock_names(dtsi)
        count = dtsi_ccu_clock_count(dtsi)
        facts["dtsi_ccu_clock_names"] = names
        facts["dtsi_ccu_clock_count"] = count
        if "losc-fanout" not in names:
            add_finding(
                findings,
                "dtsi-ccu-clock-names-missing-losc-fanout",
                f"{rel(SOC_DTSI)} CCU clock-names are {names or 'missing'}",
            )
        if count is not None and count < 4:
            add_finding(
                findings,
                "dtsi-ccu-clock-input-count",
                f"{rel(SOC_DTSI)} CCU clocks has {count} entries; expected at least 4",
            )

    status = "PASS" if not findings else "FAIL"
    return {
        "status": status,
        "root": str(root),
        "git": git_info(root),
        "facts": facts,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tree", help="Linux source tree to audit")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = audit(Path(args.tree))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status={result['status']}")
        git = result.get("git") or {}
        if git:
            print(f"git_head={git.get('head_short') or 'unknown'}")
            print(f"git_branch={git.get('branch') or 'unknown'}")
            print(f"git_dirty={'yes' if git.get('dirty') else 'no'}")
        for finding in result["findings"]:
            print(f"{finding['kind']}: {finding['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
