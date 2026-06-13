#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate A733 local-work authority files for workflow drift."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


AUTHORITY_FILES = {
    "workflow": Path("runbooks/kernel-a733-mainline-enablement-workflow.md"),
    "inventory": Path("inventory/hardware/cubie-a7s-lab.json"),
    "cycle": Path("task-packets/kernel/a733-cycle-ledger.md"),
    "comms": Path("task-packets/kernel/a733-unsent-communications-ledger.md"),
    "queue": Path("task-packets/kernel/a733-supervised-batch-queue.md"),
}
EVIDENCE_INDEX = Path("task-packets/kernel/a733-current-evidence-index.md")
REGENERATION_CHECKLIST = Path("task-packets/kernel/a733-local-regeneration-checklist.md")
PERIPHERAL_EVIDENCE_MAP = Path("task-packets/kernel/a733-peripheral-evidence-map.md")
SD_EMMC_EVIDENCE = Path("task-packets/kernel/a733-sd-emmc-evidence-sheet.md")
ETHERNET_GMAC_EVIDENCE = Path("task-packets/kernel/a733-ethernet-gmac-evidence-sheet.md")
USB_OTG_FEL_EVIDENCE = Path("task-packets/kernel/a733-usb-otg-fel-evidence-sheet.md")
THERMAL_CPUFREQ_FAN_EVIDENCE = Path(
    "task-packets/kernel/a733-thermal-cpufreq-fan-evidence-sheet.md"
)
PCIE_NVME_EVIDENCE = Path("task-packets/kernel/a733-pcie-nvme-evidence-sheet.md")
LOW_SPEED_IO_EVIDENCE = Path("task-packets/kernel/a733-low-speed-io-evidence-sheet.md")
WIFI_BLUETOOTH_EVIDENCE = Path(
    "task-packets/kernel/a733-wifi-bluetooth-evidence-sheet.md"
)
DISPLAY_MEDIA_EVIDENCE = Path("task-packets/kernel/a733-display-media-evidence-sheet.md")
NPU_RISCV_BOUNDARY = Path("task-packets/kernel/a733-npu-riscv-boundary-sheet.md")
REGULATOR_POWER_DOMAIN_EVIDENCE = Path(
    "task-packets/kernel/a733-regulator-power-domain-evidence-sheet.md"
)
LOCAL_PENDING_PREP_CHECKPOINT = Path(
    "task-packets/kernel/a733-local-pending-prep-checkpoint.md"
)
DTS_V2_READINESS_CHECKLIST = Path(
    "task-packets/kernel/a733-dts-v2-local-readiness-checklist.md"
)
AUDIO_I2S_EVIDENCE = Path("task-packets/kernel/a733-audio-i2s-evidence-sheet.md")
PWM_BACKLIGHT_FAN_EVIDENCE = Path(
    "task-packets/kernel/a733-pwm-backlight-fan-evidence-sheet.md"
)

REQUIRED_COMM_IDS = [f"A733-COMM-{number:03d}" for number in range(1, 17)]
REQUIRED_BATCH_IDS = [f"A733-BATCH-{number:03d}" for number in range(0, 17)]
EXPECTED_BOARDS = {"cubie1", "cubie2", "cubie3"}


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def check_markdown_fences(name: str, text: str, failures: list[str]) -> None:
    fence_count = sum(1 for line in text.splitlines() if line.startswith("```"))
    if fence_count % 2:
        failures.append(f"{name}: unbalanced Markdown fences ({fence_count})")


def require_contains(name: str, text: str, needle: str, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"{name}: missing required text: {needle}")


def check_workflow(text: str, failures: list[str]) -> None:
    required = [
        "Communication mode: local work only",
        "Continuous work is allowed as repeated bounded work items",
        "Codex Desktop may run multiple bounded work items in one invocation",
        "Track Matrix",
        "Current Local Track Snapshot",
        "task-packets/kernel/a733-current-evidence-index.md",
        "sent-before-blackout",
        "historical no-resend record",
    ]
    for needle in required:
        require_contains("workflow", text, needle, failures)

    stale_active_phrases = [
        "Every autonomous invocation has exactly one cycle ledger record",
        "every communication that would otherwise have been sent is captured but unsent",
    ]
    for phrase in stale_active_phrases:
        if phrase in text:
            failures.append(f"workflow: stale active wording remains: {phrase}")


def check_inventory(raw: str, failures: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        failures.append(f"inventory: invalid JSON: {exc}")
        return None

    boards = data.get("boards")
    if not isinstance(boards, list):
        failures.append("inventory: boards is not a list")
        return data

    names = {board.get("name") for board in boards if isinstance(board, dict)}
    if names != EXPECTED_BOARDS:
        failures.append(f"inventory: expected boards {sorted(EXPECTED_BOARDS)}, got {sorted(names)}")

    for board in boards:
        if not isinstance(board, dict):
            continue
        name = board.get("name", "<unknown>")
        role = board.get("kernel_work_role", {})
        recovery = board.get("recovery", {})
        wiring = board.get("physical_wiring", {})
        if role.get("role") != "unassigned":
            failures.append(f"inventory:{name}: role is not unassigned")
        if role.get("assignment_status") != "pending-human-choice":
            failures.append(f"inventory:{name}: assignment_status is not pending-human-choice")
        if recovery.get("rung") != "soft-fallback":
            failures.append(f"inventory:{name}: recovery rung is not soft-fallback")
        if recovery.get("automation_status") != "not_drilled_for_burn_autonomy":
            failures.append(f"inventory:{name}: recovery automation_status is not conservative")
        if recovery.get("autonomous") is not False:
            failures.append(f"inventory:{name}: autonomous is not false")
        if wiring.get("boot_media") != "unknown":
            failures.append(f"inventory:{name}: boot_media no longer unknown; update queue snapshot too")

    claim = data.get("agent_coordination", {}).get("claim_service", {})
    if claim.get("status") != "planned-not-active":
        failures.append("inventory: claim_service status is not planned-not-active")
    if data.get("agent_coordination", {}).get("cross_runtime_concurrency") != "disabled":
        failures.append("inventory: cross_runtime_concurrency is not disabled")
    return data


def check_comms(text: str, failures: list[str]) -> None:
    require_contains("comms", text, "sent-before-blackout", failures)
    require_contains("comms", text, "## Historical Sent Items", failures)
    for comm_id in REQUIRED_COMM_IDS:
        require_contains("comms", text, comm_id, failures)


def check_queue(text: str, failures: list[str]) -> None:
    for batch_id in REQUIRED_BATCH_IDS:
        require_contains("queue", text, batch_id, failures)
    required = [
        "Current inventory-derived snapshot",
        "no board is eligible for autonomous burn, proving, or",
        "reference mutation",
        "Display/media/GPU runtime proof",
        "NPU / RISC-V MCU runtime proof",
        "cubie1",
        "cubie2",
        "cubie3",
    ]
    for needle in required:
        require_contains("queue", text, needle, failures)


def check_cycle_ledger(text: str, failures: list[str]) -> None:
    require_contains("cycle", text, "## Ordering Note", failures)
    cycle_ids = re.findall(r"^### (A733-CYCLE-\d{3})$", text, flags=re.MULTILINE)
    duplicates = sorted({item for item in cycle_ids if cycle_ids.count(item) > 1})
    if duplicates:
        failures.append(f"cycle: duplicate cycle IDs: {', '.join(duplicates)}")
    if "A733-CYCLE-000" not in cycle_ids:
        failures.append("cycle: missing A733-CYCLE-000")


def check_evidence_index(root: Path, failures: list[str]) -> None:
    path = root / EVIDENCE_INDEX
    if not path.exists():
        failures.append(f"evidence-index: missing {EVIDENCE_INDEX}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("evidence-index", text, failures)
    required = [
        "Status: local-only coordination index",
        "not a public communication",
        "de486cb24c361a86cba26738f24332df780872b0",
        "e694ae3fa8477846a5a6eaf31fed4813ff991d5b",
        "H200",
        "H201",
        "H247",
        "H253",
        "H260",
        "H265",
        "A733-COMM-013",
        "A733-COMM-014",
        "A733-COMM-015",
        "A733-COMM-016",
        "sent-before-blackout",
        "no-send",
        "local-only",
        "task-packets/kernel/a733-local-regeneration-checklist.md",
        "task-packets/kernel/a733-peripheral-evidence-map.md",
        "task-packets/kernel/a733-sd-emmc-evidence-sheet.md",
        "task-packets/kernel/a733-ethernet-gmac-evidence-sheet.md",
        "task-packets/kernel/a733-usb-otg-fel-evidence-sheet.md",
        "task-packets/kernel/a733-thermal-cpufreq-fan-evidence-sheet.md",
        "task-packets/kernel/a733-pcie-nvme-evidence-sheet.md",
        "task-packets/kernel/a733-low-speed-io-evidence-sheet.md",
        "task-packets/kernel/a733-wifi-bluetooth-evidence-sheet.md",
        "task-packets/kernel/a733-display-media-evidence-sheet.md",
        "task-packets/kernel/a733-npu-riscv-boundary-sheet.md",
        "task-packets/kernel/a733-regulator-power-domain-evidence-sheet.md",
        "task-packets/kernel/a733-local-pending-prep-checkpoint.md",
        "task-packets/kernel/a733-dts-v2-local-readiness-checklist.md",
        "task-packets/kernel/a733-audio-i2s-evidence-sheet.md",
        "task-packets/kernel/a733-pwm-backlight-fan-evidence-sheet.md",
    ]
    for needle in required:
        require_contains("evidence-index", text, needle, failures)


def check_regeneration_checklist(root: Path, failures: list[str]) -> None:
    path = root / REGENERATION_CHECKLIST
    if not path.exists():
        failures.append(f"regeneration-checklist: missing {REGENERATION_CHECKLIST}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("regeneration-checklist", text, failures)
    required = [
        "Status: local-only checklist",
        "Do not send",
        "Do not boot",
        "H200",
        "H201",
        "H247",
        "H253",
        "H260",
        "de486cb24c361a86cba26738f24332df780872b0",
        "e694ae3fa8477846a5a6eaf31fed4813ff991d5b",
        "local-only",
        "no-send",
        "sent-before-blackout",
    ]
    for needle in required:
        require_contains("regeneration-checklist", text, needle, failures)


def check_peripheral_evidence_map(root: Path, failures: list[str]) -> None:
    path = root / PERIPHERAL_EVIDENCE_MAP
    if not path.exists():
        failures.append(f"peripheral-evidence-map: missing {PERIPHERAL_EVIDENCE_MAP}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("peripheral-evidence-map", text, failures)
    required = [
        "Status: local-only evidence map",
        "not a patch plan",
        "SDMMC",
        "eMMC",
        "Ethernet",
        "PCIe",
        "NVMe",
        "USB",
        "Wi-Fi",
        "Bluetooth",
        "display",
        "media",
        "GPU",
        "NPU",
        "RISC-V",
        "Audio",
        "I2S",
        "PWM",
        "backlight",
        "thermal",
        "cpufreq",
        "fan",
        "I2C",
        "SPI",
        "UART",
        "GPIO",
        "regulators",
        "A733-BATCH-003",
        "A733-BATCH-012",
        "A733-BATCH-013",
        "A733-BATCH-014",
        "A733-BATCH-015",
        "A733-BATCH-016",
        "A733-COMM-006",
        "A733-COMM-012",
        "local-only",
    ]
    for needle in required:
        require_contains("peripheral-evidence-map", text, needle, failures)


def check_ethernet_gmac_evidence(root: Path, failures: list[str]) -> None:
    path = root / ETHERNET_GMAC_EVIDENCE
    if not path.exists():
        failures.append(f"ethernet-gmac-evidence: missing {ETHERNET_GMAC_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("ethernet-gmac-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable Ethernet",
        "GMAC",
        "GMAC210",
        "STMMAC",
        "MDIO",
        "PHY reset",
        "PHY power",
        "clock",
        "reset",
        "A733-BATCH-007",
        "A733-COMM-007",
        "read only",
    ]
    for needle in required:
        require_contains("ethernet-gmac-evidence", text, needle, failures)


def check_sd_emmc_evidence(root: Path, failures: list[str]) -> None:
    path = root / SD_EMMC_EVIDENCE
    if not path.exists():
        failures.append(f"sd-emmc-evidence: missing {SD_EMMC_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("sd-emmc-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable new SDMMC",
        "Do not write storage",
        "SDMMC0",
        "eMMC",
        "MMC",
        "IDMAC",
        "descriptor",
        "rootfs",
        "read-only",
        "write",
        "reboot",
        "cold boot",
        "mmc-utils",
        "A733-BATCH-003",
        "A733-BATCH-006",
        "A733-COMM-006",
        "local-only",
    ]
    for needle in required:
        require_contains("sd-emmc-evidence", text, needle, failures)


def check_usb_otg_fel_evidence(root: Path, failures: list[str]) -> None:
    path = root / USB_OTG_FEL_EVIDENCE
    if not path.exists():
        failures.append(f"usb-otg-fel-evidence: missing {USB_OTG_FEL_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("usb-otg-fel-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable USB",
        "Do not enter FEL",
        "USB2",
        "USB3",
        "USB-C",
        "OTG",
        "Type-C",
        "role switch",
        "VBUS",
        "PHY",
        "FEL",
        "BootROM",
        "sunxi-fel",
        "xfel",
        "A733-BATCH-009",
        "A733-BATCH-012",
        "A733-COMM-009",
        "read only",
    ]
    for needle in required:
        require_contains("usb-otg-fel-evidence", text, needle, failures)


def check_thermal_cpufreq_fan_evidence(root: Path, failures: list[str]) -> None:
    path = root / THERMAL_CPUFREQ_FAN_EVIDENCE
    if not path.exists():
        failures.append(
            f"thermal-cpufreq-fan-evidence: missing {THERMAL_CPUFREQ_FAN_EVIDENCE}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("thermal-cpufreq-fan-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not run workloads",
        "Do not control PWM",
        "thermal",
        "cpufreq",
        "fan",
        "THS",
        "OPP",
        "cooling",
        "PWM",
        "tach",
        "regulator",
        "temperature",
        "trip point",
        "workload",
        "stop threshold",
        "A733-BATCH-011",
        "local-only",
    ]
    for needle in required:
        require_contains("thermal-cpufreq-fan-evidence", text, needle, failures)


def check_pcie_nvme_evidence(root: Path, failures: list[str]) -> None:
    path = root / PCIE_NVME_EVIDENCE
    if not path.exists():
        failures.append(f"pcie-nvme-evidence: missing {PCIE_NVME_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("pcie-nvme-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable PCIe",
        "Do not run `lspci`, `nvme`, `fio`",
        "PCIe",
        "NVMe",
        "controller",
        "PHY",
        "PERST",
        "refclk",
        "CLKREQ",
        "regulator",
        "power budget",
        "adapter",
        "link training",
        "lspci",
        "fio",
        "storage-write",
        "A733-BATCH-008",
        "A733-COMM-008",
        "local-only",
    ]
    for needle in required:
        require_contains("pcie-nvme-evidence", text, needle, failures)


def check_low_speed_io_evidence(root: Path, failures: list[str]) -> None:
    path = root / LOW_SPEED_IO_EVIDENCE
    if not path.exists():
        failures.append(f"low-speed-io-evidence: missing {LOW_SPEED_IO_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("low-speed-io-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not run an I2C scan",
        "Do not toggle GPIOs",
        "I2C",
        "SPI",
        "UART",
        "GPIO",
        "pinctrl",
        "pin mux",
        "header",
        "connector",
        "interrupt",
        "loopback",
        "external device",
        "I2C scan",
        "SPI transfer",
        "GPIO toggle",
        "A733-BATCH-005",
        "A733-COMM-004",
        "A733-COMM-005",
        "local-only",
    ]
    for needle in required:
        require_contains("low-speed-io-evidence", text, needle, failures)


def check_wifi_bluetooth_evidence(root: Path, failures: list[str]) -> None:
    path = root / WIFI_BLUETOOTH_EVIDENCE
    if not path.exists():
        failures.append(f"wifi-bluetooth-evidence: missing {WIFI_BLUETOOTH_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("wifi-bluetooth-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not run a Wi-Fi scan",
        "Do not pair Bluetooth devices",
        "Wi-Fi",
        "Bluetooth",
        "SDIO",
        "UART",
        "module",
        "firmware",
        "license",
        "pwrseq",
        "regulator",
        "wake GPIO",
        "shutdown GPIO",
        "scan",
        "association",
        "throughput",
        "pairing",
        "A733-BATCH-010",
        "A733-COMM-010",
        "local-only",
    ]
    for needle in required:
        require_contains("wifi-bluetooth-evidence", text, needle, failures)


def check_display_media_evidence(root: Path, failures: list[str]) -> None:
    path = root / DISPLAY_MEDIA_EVIDENCE
    if not path.exists():
        failures.append(f"display-media-evidence: missing {DISPLAY_MEDIA_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("display-media-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable display",
        "Do not run display tests",
        "display",
        "DP",
        "eDP",
        "HDMI",
        "MIPI DSI",
        "CSI",
        "media",
        "VPU",
        "GPU",
        "DRM",
        "bridge",
        "panel",
        "connector",
        "frame capture",
        "decode",
        "render",
        "A733-BATCH-013",
        "A733-COMM-011",
        "local-only",
    ]
    for needle in required:
        require_contains("display-media-evidence", text, needle, failures)


def check_npu_riscv_boundary(root: Path, failures: list[str]) -> None:
    path = root / NPU_RISCV_BOUNDARY
    if not path.exists():
        failures.append(f"npu-riscv-boundary: missing {NPU_RISCV_BOUNDARY}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("npu-riscv-boundary", text, failures)
    required = [
        "Status: local-only source-backed boundary sheet",
        "Do not enable an NPU",
        "Do not load firmware",
        "NPU",
        "RISC-V MCU",
        "remoteproc",
        "firmware",
        "reserved-memory",
        "mailbox",
        "IOMMU",
        "OpenAMP",
        "RPMsg",
        "userspace ABI",
        "accelerator",
        "memory map",
        "Firmware license",
        "crash/recovery",
        "A733-BATCH-014",
        "A733-COMM-012",
        "local-only",
    ]
    for needle in required:
        require_contains("npu-riscv-boundary", text, needle, failures)


def check_regulator_power_domain_evidence(root: Path, failures: list[str]) -> None:
    path = root / REGULATOR_POWER_DOMAIN_EVIDENCE
    if not path.exists():
        failures.append(
            f"regulator-power-domain-evidence: missing {REGULATOR_POWER_DOMAIN_EVIDENCE}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("regulator-power-domain-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not add, rename, remove, or change regulator nodes",
        "Do not toggle rails",
        "regulator",
        "PMIC",
        "rail",
        "supply",
        "power-domain",
        "OPP",
        "voltage",
        "always-on",
        "boot-on",
        "coupled regulator",
        "Consumer map",
        "vcc-3v3",
        "A733-BATCH-004",
        "A733-BATCH-011",
        "local-only",
    ]
    for needle in required:
        require_contains("regulator-power-domain-evidence", text, needle, failures)


def check_local_pending_prep_checkpoint(root: Path, failures: list[str]) -> None:
    path = root / LOCAL_PENDING_PREP_CHECKPOINT
    if not path.exists():
        failures.append(
            f"local-pending-prep-checkpoint: missing {LOCAL_PENDING_PREP_CHECKPOINT}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("local-pending-prep-checkpoint", text, failures)
    required = [
        "Status: local-only pending-review checkpoint",
        "not a public communication",
        "not permission to mutate hardware",
        "fa27be5dc4e14fa1947f4f3e2f2119e13ca67d39",
        "main...origin/main [ahead 1]",
        "task-packets/kernel/a733-display-media-evidence-sheet.md",
        "task-packets/kernel/a733-local-pending-prep-checkpoint.md",
        "task-packets/kernel/a733-npu-riscv-boundary-sheet.md",
        "task-packets/kernel/a733-regulator-power-domain-evidence-sheet.md",
        "tools/validate/a733_authority_check.py",
        "A733-CYCLE-033",
        "A733-CYCLE-038",
        "self-referential hash changes",
        "No hardware mutation",
        "No kernel tree files were edited",
        "No public communication or public push",
        "local pending-review material",
    ]
    for needle in required:
        require_contains("local-pending-prep-checkpoint", text, needle, failures)


def check_dts_v2_readiness_checklist(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_READINESS_CHECKLIST
    if not path.exists():
        failures.append(f"dts-v2-readiness-checklist: missing {DTS_V2_READINESS_CHECKLIST}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-readiness-checklist", text, failures)
    required = [
        "Status: local-only sendable-held checklist",
        "Do not send DTS v2",
        "not send approval",
        "Do not boot",
        "uart0_pb9_pb10_pins",
        "sun60i-a733-cubie-a7s.dts",
        "sun60i-a733.dtsi",
        "UART0 console",
        "SD-card boot",
        "no-mmc",
        "no-sdio",
        "Ethernet",
        "A733-BATCH-002",
        "A733-BATCH-007",
        "A733-COMM-002",
        "A733-COMM-003",
        "A733-COMM-016",
        "dtbs_check",
        "checkpatch.pl --strict",
        "get_maintainer.pl",
        "b4 prep",
        "sendable-held",
        "question-held",
        "local DTS v2 cleanup is not complete",
    ]
    for needle in required:
        require_contains("dts-v2-readiness-checklist", text, needle, failures)


def check_audio_i2s_evidence(root: Path, failures: list[str]) -> None:
    path = root / AUDIO_I2S_EVIDENCE
    if not path.exists():
        failures.append(f"audio-i2s-evidence: missing {AUDIO_I2S_EVIDENCE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("audio-i2s-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable audio",
        "Do not run playback",
        "audio",
        "I2S",
        "codec",
        "DMIC",
        "SPDIF",
        "HDMI-audio",
        "amplifier",
        "jack",
        "speaker",
        "microphone",
        "DAI",
        "audio-routing",
        "playback",
        "capture",
        "loopback",
        "mixer",
        "A733-BATCH-015",
        "local-only",
    ]
    for needle in required:
        require_contains("audio-i2s-evidence", text, needle, failures)


def check_pwm_backlight_fan_evidence(root: Path, failures: list[str]) -> None:
    path = root / PWM_BACKLIGHT_FAN_EVIDENCE
    if not path.exists():
        failures.append(
            f"pwm-backlight-fan-evidence: missing {PWM_BACKLIGHT_FAN_EVIDENCE}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("pwm-backlight-fan-evidence", text, failures)
    required = [
        "Status: local-only source-backed evidence sheet",
        "Do not enable PWM",
        "Do not toggle PWM outputs",
        "PWM",
        "backlight",
        "fan PWM",
        "tach",
        "buzzer",
        "LED dimming",
        "header PWM",
        "duty-cycle",
        "external-load",
        "cooling-state",
        "brightness",
        "A733-BATCH-016",
        "local-only",
    ]
    for needle in required:
        require_contains("pwm-backlight-fan-evidence", text, needle, failures)


def run(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    texts: dict[str, str] = {}
    for name, rel in AUTHORITY_FILES.items():
        path = root / rel
        if not path.exists():
            failures.append(f"{name}: missing {rel}")
            continue
        if name != "inventory":
            texts[name] = read_text(root, rel)
            check_markdown_fences(name, texts[name], failures)

    inventory = None
    if (root / AUTHORITY_FILES["inventory"]).exists():
        inventory = check_inventory(read_text(root, AUTHORITY_FILES["inventory"]), failures)

    if "workflow" in texts:
        check_workflow(texts["workflow"], failures)
    if "comms" in texts:
        check_comms(texts["comms"], failures)
    if "queue" in texts:
        check_queue(texts["queue"], failures)
    if "cycle" in texts:
        check_cycle_ledger(texts["cycle"], failures)
    check_evidence_index(root, failures)
    check_regeneration_checklist(root, failures)
    check_peripheral_evidence_map(root, failures)
    check_sd_emmc_evidence(root, failures)
    check_ethernet_gmac_evidence(root, failures)
    check_usb_otg_fel_evidence(root, failures)
    check_thermal_cpufreq_fan_evidence(root, failures)
    check_pcie_nvme_evidence(root, failures)
    check_low_speed_io_evidence(root, failures)
    check_wifi_bluetooth_evidence(root, failures)
    check_display_media_evidence(root, failures)
    check_npu_riscv_boundary(root, failures)
    check_regulator_power_domain_evidence(root, failures)
    check_local_pending_prep_checkpoint(root, failures)
    check_dts_v2_readiness_checklist(root, failures)
    check_audio_i2s_evidence(root, failures)
    check_pwm_backlight_fan_evidence(root, failures)

    status = "PASS" if not failures else "FAIL"
    return {
        "status": status,
        "root": str(root),
        "authority_files": {name: str(path) for name, path in AUTHORITY_FILES.items()},
        "evidence_index": str(EVIDENCE_INDEX),
        "regeneration_checklist": str(REGENERATION_CHECKLIST),
        "peripheral_evidence_map": str(PERIPHERAL_EVIDENCE_MAP),
        "sd_emmc_evidence": str(SD_EMMC_EVIDENCE),
        "ethernet_gmac_evidence": str(ETHERNET_GMAC_EVIDENCE),
        "usb_otg_fel_evidence": str(USB_OTG_FEL_EVIDENCE),
        "thermal_cpufreq_fan_evidence": str(THERMAL_CPUFREQ_FAN_EVIDENCE),
        "pcie_nvme_evidence": str(PCIE_NVME_EVIDENCE),
        "low_speed_io_evidence": str(LOW_SPEED_IO_EVIDENCE),
        "wifi_bluetooth_evidence": str(WIFI_BLUETOOTH_EVIDENCE),
        "display_media_evidence": str(DISPLAY_MEDIA_EVIDENCE),
        "npu_riscv_boundary": str(NPU_RISCV_BOUNDARY),
        "regulator_power_domain_evidence": str(REGULATOR_POWER_DOMAIN_EVIDENCE),
        "local_pending_prep_checkpoint": str(LOCAL_PENDING_PREP_CHECKPOINT),
        "dts_v2_readiness_checklist": str(DTS_V2_READINESS_CHECKLIST),
        "audio_i2s_evidence": str(AUDIO_I2S_EVIDENCE),
        "pwm_backlight_fan_evidence": str(PWM_BACKLIGHT_FAN_EVIDENCE),
        "board_count": len(inventory.get("boards", [])) if isinstance(inventory, dict) else None,
        "failures": failures,
        "failure_count": len(failures),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result = run(root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status={result['status']}")
        print(f"root={result['root']}")
        print(f"failures={result['failure_count']}")
        for failure in result["failures"]:
            print(f"  {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
