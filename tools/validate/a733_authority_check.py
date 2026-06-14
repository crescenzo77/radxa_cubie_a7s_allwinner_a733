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
DTS_V2_LOCAL_DELTA_PLAN = Path("task-packets/kernel/a733-dts-v2-local-delta-plan.md")
DTS_V2_STATIC_PROOF_PLAN = Path(
    "task-packets/kernel/a733-dts-v2-static-proof-plan.md"
)
DTS_V2_STATIC_VALIDATION_HOSTS = Path(
    "task-packets/kernel/a733-dts-v2-static-validation-hosts.md"
)
DTS_V2_STATIC_PROOF_COMMAND_PACKET = Path(
    "task-packets/kernel/a733-dts-v2-static-proof-command-packet.md"
)
DTS_V2_STATIC_PROOF_PREFLIGHT = Path(
    "task-packets/kernel/a733-dts-v2-static-proof-preflight.md"
)
DTS_V2_STATIC_PROOF_ISOLATED_COPY = Path(
    "task-packets/kernel/a733-dts-v2-static-proof-isolated-copy-packet.md"
)
CLAIM_SERVICE_ACTIVATION_CHECKLIST = Path(
    "task-packets/kernel/a733-claim-service-activation-checklist.md"
)
PREREQ_STACK_SELECTION_NOTE = Path(
    "task-packets/kernel/a733-prereq-stack-selection-note.md"
)
CLEAN_PREREQ_STACK_CONSTRUCTION_PLAN = Path(
    "task-packets/kernel/a733-clean-prereq-stack-construction-plan.md"
)
GATED_TRANSITION_APPROVAL_PACKET = Path(
    "task-packets/kernel/a733-gated-transition-approval-packet.md"
)
DTS_V2_UART_PINCTRL_PREVIEW = Path(
    "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch"
)
DTS_V2_HELD_COVER_CHANGELOG_DRAFT = Path(
    "task-packets/kernel/a733-dts-v2-held-cover-changelog-draft.md"
)
AUDIO_I2S_EVIDENCE = Path("task-packets/kernel/a733-audio-i2s-evidence-sheet.md")
PWM_BACKLIGHT_FAN_EVIDENCE = Path(
    "task-packets/kernel/a733-pwm-backlight-fan-evidence-sheet.md"
)
KERNEL_CHECKOUT_QUARANTINE = Path("inventory/kernel-checkout-quarantine-20260606.md")
KERNEL_WORKFLOW_PATHS = Path("inventory/kernel-workflow-paths.json")
FINAL_SEND_CHECKLIST = Path("task-packets/kernel/a733-final-send-checklist.json")
GATED_TRANSITION_APPROVAL_BRIEF = Path("scripts/a733-gated-transition-approval-brief")
CURRENT_SLICE = Path("CURRENT_SLICE.md")
KERNEL_WORKFLOW_STATUS = Path("tools/inventory/kernel_workflow_status.py")

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
    require_contains("comms", text, "drafted-not-reviewed", failures)
    require_contains(
        "comms",
        text,
        "task-packets/kernel/a733-dts-v2-held-cover-changelog-draft.md",
        failures,
    )
    require_contains("comms", text, "static validation", failures)
    require_contains("comms", text, "runtime proof", failures)
    require_contains("comms", text, "recipient refresh", failures)
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
        "task-packets/kernel/a733-dts-v2-local-delta-plan.md",
        "task-packets/kernel/a733-dts-v2-static-proof-plan.md",
        "task-packets/kernel/a733-dts-v2-static-validation-hosts.md",
        "task-packets/kernel/a733-dts-v2-static-proof-command-packet.md",
        "task-packets/kernel/a733-dts-v2-static-proof-preflight.md",
        "task-packets/kernel/a733-dts-v2-static-proof-isolated-copy-packet.md",
        "task-packets/kernel/a733-claim-service-activation-checklist.md",
        "Strix's observed A733 DTS/DTSI prerequisite files were",
        "committed prerequisite branch",
        "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch",
        "task-packets/kernel/a733-dts-v2-held-cover-changelog-draft.md",
        "task-packets/kernel/a733-audio-i2s-evidence-sheet.md",
        "task-packets/kernel/a733-pwm-backlight-fan-evidence-sheet.md",
        "inventory/kernel-checkout-quarantine-20260606.md",
        "inventory/kernel-workflow-paths.json",
        "task-packets/kernel/a733-prereq-stack-selection-note.md",
        "task-packets/kernel/a733-clean-prereq-stack-construction-plan.md",
        "task-packets/kernel/a733-gated-transition-approval-packet.md",
        "scripts/a733-gated-transition-approval-brief",
        "task-packets/kernel/a733-final-send-checklist.json",
        "scripts/kernel-final-send-status",
    ]
    for needle in required:
        require_contains("evidence-index", text, needle, failures)


def check_final_send_checklist(root: Path, failures: list[str]) -> None:
    path = root / FINAL_SEND_CHECKLIST
    if not path.exists():
        failures.append(f"final-send-checklist: missing {FINAL_SEND_CHECKLIST}")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"final-send-checklist: invalid JSON: {exc}")
        return
    if data.get("status") != "v1_public_sent_indexed":
        failures.append("final-send-checklist: status is not v1_public_sent_indexed")
    blockers = data.get("current_known_blockers")
    if not isinstance(blockers, list) or len(blockers) < 2:
        failures.append("final-send-checklist: current_known_blockers is incomplete")
    required = [
        "public GitHub remote",
        "/Users/enzo/projects/linux-a733-sparse",
        "DTS v2 work remains held",
    ]
    blocker_text = "\n".join(str(item) for item in blockers or [])
    for needle in required:
        require_contains("final-send-checklist", blocker_text, needle, failures)
    if data.get("current_gate_packet") != str(GATED_TRANSITION_APPROVAL_PACKET):
        failures.append("final-send-checklist: current_gate_packet is not the gated approval packet")


def check_current_slice(root: Path, failures: list[str]) -> None:
    path = root / CURRENT_SLICE
    if not path.exists():
        failures.append(f"current-slice: missing {CURRENT_SLICE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("current-slice", text, failures)
    required = [
        "## Active: A733 gated-transition preparation",
        "scripts/a733-gated-transition-approval-brief",
        "public kernel repo GitHub backup is not done",
        "selected A733 prerequisite stack is not cleanly audited",
        "do not push the public kernel repo to GitHub",
        "do not mutate kernel trees",
        "do not boot, reboot, power-cycle, SSH probe, UART capture",
        "## Prior Current State",
        "## Active: Implement local token-offload workflow",
    ]
    for needle in required:
        require_contains("current-slice", text, needle, failures)


def check_kernel_workflow_status(root: Path, failures: list[str]) -> None:
    path = root / KERNEL_WORKFLOW_STATUS
    if not path.exists():
        failures.append(f"kernel-workflow-status: missing {KERNEL_WORKFLOW_STATUS}")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "GATED_TRANSITION_APPROVAL_BRIEF",
        "gated_transition_approval_route",
        "public kernel repo GitHub backup requires explicit operator approval",
        "choose or build a clean A733 prerequisite stack before regenerating",
        "requires explicit operator approval via",
        "read gated-transition approval brief before any public push",
    ]
    for needle in required:
        require_contains("kernel-workflow-status", text, needle, failures)
    stale_phrases = [
        "push public kernel repo to its GitHub remote",
        "push public kernel repo to its GitHub remote before public handoff",
    ]
    for phrase in stale_phrases:
        if phrase in text:
            failures.append(
                f"kernel-workflow-status: stale public-push wording remains: {phrase}"
            )


def check_clean_prereq_stack_construction_plan(root: Path, failures: list[str]) -> None:
    path = root / CLEAN_PREREQ_STACK_CONSTRUCTION_PLAN
    if not path.exists():
        failures.append(
            "clean-prereq-stack-construction-plan: missing "
            f"{CLEAN_PREREQ_STACK_CONSTRUCTION_PLAN}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("clean-prereq-stack-construction-plan", text, failures)
    required = [
        "Status: local-only no-run construction plan",
        "not permission to edit kernel trees",
        "/Users/enzo/projects/linux-a733-sparse",
        "/srv/projects/a733-prereq-stack-current",
        "a1f5f546f116",
        "8fde5d1d47f6",
        "scripts/a733-prereq-stack-audit",
        "rtc-binding-missing",
        "r-ccu-driver-missing",
        "dtsi-ccu-clock-names-missing-losc-fanout",
        "Do not use the dirty full Mac-mini checkout",
        "dt_binding_check",
        "choose or build a clean A733 prerequisite stack",
    ]
    for needle in required:
        require_contains("clean-prereq-stack-construction-plan", text, needle, failures)


def check_gated_transition_approval_packet(root: Path, failures: list[str]) -> None:
    path = root / GATED_TRANSITION_APPROVAL_PACKET
    if not path.exists():
        failures.append(
            f"gated-transition-approval-packet: missing {GATED_TRANSITION_APPROVAL_PACKET}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("gated-transition-approval-packet", text, failures)
    required = [
        "Status: local-only approval packet",
        "not permission to mutate kernel trees",
        "Public GitHub Backup",
        "public-push gate",
        "public hygiene: PASS",
        "git -C \"/Users/enzo/projects/Home Lab/cubie-a7s-armbian\" push public main",
        "Clean A733 Prerequisite Stack",
        "A733 prerequisite stack audit is not clean",
        "/Users/enzo/projects/linux-a733-sparse",
        "/srv/projects/a733-prereq-stack-current",
        "Do not quietly convert this packet into permission",
    ]
    for needle in required:
        require_contains("gated-transition-approval-packet", text, needle, failures)


def check_gated_transition_approval_brief(root: Path, failures: list[str]) -> None:
    path = root / GATED_TRANSITION_APPROVAL_BRIEF
    if not path.exists():
        failures.append(
            f"gated-transition-approval-brief: missing {GATED_TRANSITION_APPROVAL_BRIEF}"
        )
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "This is read-only",
        "kernel-workflow-status",
        "kernel-public-hygiene-gate",
        "May Codex push",
        "May Codex create or update an isolated A733 prerequisite preparation tree",
        "If approval is not explicit",
    ]
    for needle in required:
        require_contains("gated-transition-approval-brief", text, needle, failures)


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
        "Status: local-only post-backup checkpoint",
        "not a public communication",
        "not permission to mutate hardware",
        "92b3a6a4b353876a2cb13c9be06af6e692766c7f",
        "main...origin/main [ahead 8]",
        "GitHub backup branch: `homelab-backup-main`",
        "GitHub public-evidence branch: `main`",
        "dac2a6f83894d1de6b6177da8d83461fef62d6c0",
        "task-packets/kernel/a733-display-media-evidence-sheet.md",
        "task-packets/kernel/a733-local-pending-prep-checkpoint.md",
        "task-packets/kernel/a733-npu-riscv-boundary-sheet.md",
        "task-packets/kernel/a733-regulator-power-domain-evidence-sheet.md",
        "task-packets/kernel/a733-audio-i2s-evidence-sheet.md",
        "task-packets/kernel/a733-pwm-backlight-fan-evidence-sheet.md",
        "task-packets/kernel/a733-dts-v2-local-delta-plan.md",
        "task-packets/kernel/a733-dts-v2-static-proof-plan.md",
        "task-packets/kernel/a733-dts-v2-static-validation-hosts.md",
        "task-packets/kernel/a733-dts-v2-static-proof-command-packet.md",
        "task-packets/kernel/a733-dts-v2-static-proof-preflight.md",
        "task-packets/kernel/a733-dts-v2-static-proof-isolated-copy-packet.md",
        "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch",
        "task-packets/kernel/a733-dts-v2-held-cover-changelog-draft.md",
        "inventory/kernel-checkout-quarantine-20260606.md",
        "inventory/kernel-workflow-paths.json",
        "tools/validate/a733_authority_check.py",
        "A733-CYCLE-033",
        "Substantive prep cycle-ledger records through A733-CYCLE-061",
        "A733-CYCLE-061",
        "Checkpoint-only refresh cycles after A733-CYCLE-061",
        "does not roll its coverage forward for refresh-only cycles",
        "prevents self-referential checkpoint churn",
        "DTS v2 local delta plan",
        "DTS v2 static proof plan",
        "DTS v2 static proof no-run command packet",
        "Strix untracked-prerequisite caveat",
        "DTS v2 static proof read-only Strix preflight packet",
        "Mac-mini kernel checkout quarantine refresh",
        "DTS v2 static-validation host suitability note",
        "DTS v2 static proof command packet",
        "DTS v2 static proof isolated-copy packet",
        "self-referential hash changes",
        "No hardware mutation",
        "No kernel tree files were edited",
        "No public kernel communication",
        "operator explicitly",
        "GitHub `main` was not overwritten",
        "Hardware runtime work remains blocked",
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
        "/Users/enzo/projects/linux-a733-sparse",
        "candidate/a733-platform-clean-v4",
        "abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e",
        "/Users/enzo/projects/linux-a733",
        "candidate/a733-platform-clean-v6",
        "b1f20d455a600d33999cf893fdf0df8fb2ace538",
        "must not be used for patch export",
        "sendable-held",
        "question-held",
        "local DTS v2 cleanup is not complete",
        "task-packets/kernel/a733-dts-v2-local-delta-plan.md",
    ]
    for needle in required:
        require_contains("dts-v2-readiness-checklist", text, needle, failures)


def check_dts_v2_local_delta_plan(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_LOCAL_DELTA_PLAN
    if not path.exists():
        failures.append(f"dts-v2-local-delta-plan: missing {DTS_V2_LOCAL_DELTA_PLAN}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-local-delta-plan", text, failures)
    required = [
        "Status: local-only patch-prep plan",
        "not a patch",
        "not send approval",
        "not runtime proof",
        "/Users/enzo/projects/linux-a733-sparse",
        "candidate/a733-platform-clean-v4",
        "abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e",
        "sun60i-a733-cubie-a7s.dts",
        "sun60i-a733.dtsi",
        "uart0_pb9_pb10_pins",
        "Move only the pin group definition",
        "A733-BATCH-002",
        "A733-COMM-002",
        "A733-COMM-003",
        "git diff --check",
        "CHECK_DTBS=y",
        "scripts/checkpatch.pl --strict",
        "scripts/get_maintainer.pl",
        "Do not send",
        "This local delta plan does not authorize booting",
        "task-packets/kernel/a733-dts-v2-static-proof-plan.md",
        "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch",
        "git apply --check",
        "aarch64-linux-gnu-gcc",
        "local-only mode remains active",
    ]
    for needle in required:
        require_contains("dts-v2-local-delta-plan", text, needle, failures)


def check_dts_v2_static_proof_plan(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_STATIC_PROOF_PLAN
    if not path.exists():
        failures.append(f"dts-v2-static-proof-plan: missing {DTS_V2_STATIC_PROOF_PLAN}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-static-proof-plan", text, failures)
    required = [
        "Status: local-only validation plan",
        "not a patch",
        "not proof that the edit has already been made",
        "not send approval",
        "not permission to mutate hardware",
        "/Users/enzo/projects/linux-a733-sparse",
        "candidate/a733-platform-clean-v4",
        "abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e",
        "no top-level `Makefile`",
        "no `scripts/checkpatch.pl`",
        "no `scripts/get_maintainer.pl`",
        "/Users/enzo/projects/linux-a733",
        "candidate/a733-platform-clean-v6",
        "b1f20d455a600d33999cf893fdf0df8fb2ace538",
        "aarch64-linux-gnu-gcc",
        "O=/tmp/a733-dts-v2-static-proof",
        "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch",
        "task-packets/kernel/a733-dts-v2-static-validation-hosts.md",
        "task-packets/kernel/a733-dts-v2-static-proof-command-packet.md",
        "task-packets/kernel/a733-dts-v2-static-proof-preflight.md",
        "task-packets/kernel/a733-dts-v2-static-proof-isolated-copy-packet.md",
        "Strix is the best observed future static-validation host",
        "temporary clean worktree",
        "Known prerequisite caveat",
        "Current preflight result",
        "A733 prerequisite DTS/DTSI files present in the isolated tree",
        "contracted isolated copy",
        "git apply --check",
        "make O=\"$O\" ARCH=arm64",
        "CHECK_DTBS=y",
        "scripts/checkpatch.pl --strict",
        "scripts/get_maintainer.pl",
        "mark the static proof blocked",
        "no boot, no install, no UART capture, no power action",
        "local-only mode remains active",
    ]
    for needle in required:
        require_contains("dts-v2-static-proof-plan", text, needle, failures)


def check_dts_v2_static_validation_hosts(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_STATIC_VALIDATION_HOSTS
    if not path.exists():
        failures.append(
            f"dts-v2-static-validation-hosts: missing {DTS_V2_STATIC_VALIDATION_HOSTS}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-static-validation-hosts", text, failures)
    required = [
        "Status: local-only host suitability note",
        "not a build log",
        "not permission to mutate hardware or kernel trees",
        "no kernel tree edits",
        "no build commands",
        "enzos-Mac-mini.local",
        "/Users/enzo/projects/linux-a733-sparse",
        "abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e",
        "/Users/enzo/projects/linux-a733",
        "b1f20d455a600d33999cf893fdf0df8fb2ace538",
        "no `aarch64-linux-gnu-gcc` on PATH",
        "strix",
        "/srv/projects/cubie-a7s-armbian/sources/mainline-linux",
        "8fde5d1d47f69db6082dfa34500c27f8485389a5",
        "/usr/bin/aarch64-linux-gnu-gcc",
        "Strix is the best observed future static-validation host",
        "dirty and detached",
        "observed A733 DTS prerequisite files were untracked",
        "thinkcentre",
        "/srv/projects/a733-prereq-stack-current",
        "no `dtc` on PATH",
        "temporary full Linux worktree",
        "no boot, no install, no UART capture, no power action",
    ]
    for needle in required:
        require_contains("dts-v2-static-validation-hosts", text, needle, failures)


def check_dts_v2_static_proof_command_packet(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_STATIC_PROOF_COMMAND_PACKET
    if not path.exists():
        failures.append(
            "dts-v2-static-proof-command-packet: missing "
            f"{DTS_V2_STATIC_PROOF_COMMAND_PACKET}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-static-proof-command-packet", text, failures)
    required = [
        "Status: local-only; no-run; no-send",
        "not proof that the commands have been run",
        "not permission to mutate hardware",
        "Do not execute this packet",
        "task-packets/kernel/a733-dts-v2-static-validation-hosts.md",
        "task-packets/kernel/a733-dts-v2-static-proof-preflight.md",
        "task-packets/kernel/a733-dts-v2-static-proof-isolated-copy-packet.md",
        "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch",
        "strix",
        "/srv/projects/cubie-a7s-armbian/sources/mainline-linux",
        "8fde5d1d47f69db6082dfa34500c27f8485389a5",
        "Known prerequisite caveat",
        "sun60i-a733.dtsi",
        "sun60i-a733-cubie-a7s.dts",
        "untracked files",
        "temporary full worktree",
        "A733 prerequisite DTS/DTSI files are untracked",
        "aarch64-linux-gnu-gcc",
        "git -C \"$HOST_TREE\" worktree add --detach",
        "git -C \"$PROOF_TREE\" apply --check \"$PATCH\"",
        "make -C \"$PROOF_TREE\" O=\"$BUILD_DIR\" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-",
        "CHECK_DTBS=y",
        "checkpatch.pl",
        "get_maintainer.pl",
        "no boot, no install, no UART capture, no power action",
        "Do not record a pass if any command fails",
    ]
    for needle in required:
        require_contains("dts-v2-static-proof-command-packet", text, needle, failures)


def check_dts_v2_static_proof_isolated_copy(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_STATIC_PROOF_ISOLATED_COPY
    if not path.exists():
        failures.append(
            f"dts-v2-static-proof-isolated-copy: missing {DTS_V2_STATIC_PROOF_ISOLATED_COPY}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-static-proof-isolated-copy", text, failures)
    required = [
        "Status: local-only; no-run; no-send",
        "not a build log",
        "not static proof",
        "not permission to mutate kernel trees or hardware",
        "Do not execute this packet",
        "task-packets/kernel/a733-dts-v2-static-proof-preflight.md",
        "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch",
        "8fde5d1d47f69db6082dfa34500c27f8485389a5",
        "sun60i-a733.dtsi",
        "sun60i-a733-cubie-a7s.dts",
        "untracked",
        "rsync -a --delete",
        "source-prereq-sha256.txt",
        "proof-prereq-sha256.txt",
        "diff -u",
        "Stop before any patch or build command",
        "task-packets/kernel/a733-dts-v2-static-proof-command-packet.md",
        "no boot, no install, no UART capture, no power action",
        "rsync is unavailable",
        "prerequisite hashes do not match",
    ]
    for needle in required:
        require_contains("dts-v2-static-proof-isolated-copy", text, needle, failures)


def check_claim_service_activation_checklist(root: Path, failures: list[str]) -> None:
    path = root / CLAIM_SERVICE_ACTIVATION_CHECKLIST
    if not path.exists():
        failures.append(
            f"claim-service-activation-checklist: missing {CLAIM_SERVICE_ACTIVATION_CHECKLIST}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("claim-service-activation-checklist", text, failures)
    required = [
        "Status: local-only checklist; no-run; no-service-change",
        "not an implementation",
        "not approval to start services",
        "not approval to change Hermes",
        "not permission to mutate kernel trees or hardware",
        "planned-not-active",
        "ThinkCentre",
        "Fault Ledger/FastMCP",
        "SQLite-WAL",
        "AGENT_ID -> AGENT_TIER",
        "server-stamped tier",
        "atomic claim, release, heartbeat, and list operations",
        "Resource IDs cover at least",
        "Non-stale claim denial",
        "Stale burn-board claim handling marks the board `UNKNOWN`",
        "dummy resources first",
        "A733-CLAIM-DRILL-001",
        "DTS v2 isolated-copy static proof",
        "Strix source kernel tree path",
        "isolated proof tree path",
        "Hardware runtime remains blocked",
        "claim-service activation alone never enables",
        "inventory/hardware/cubie-a7s-lab.json",
        "Until then, the correct status remains `planned-not-active`",
        "Stop and log instead of activating",
        "activation would require changing Hermes, cron, services, model routing, or",
    ]
    for needle in required:
        require_contains("claim-service-activation-checklist", text, needle, failures)


def check_prereq_stack_selection_note(root: Path, failures: list[str]) -> None:
    path = root / PREREQ_STACK_SELECTION_NOTE
    if not path.exists():
        failures.append(f"prereq-stack-selection-note: missing {PREREQ_STACK_SELECTION_NOTE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("prereq-stack-selection-note", text, failures)
    required = [
        "Status: local-only read-only selection note",
        "not a patch",
        "not a build log",
        "not proof that the prerequisite stack is complete",
        "not permission to edit kernel trees",
        "/Users/enzo/projects/linux-a733-sparse",
        "/Users/enzo/projects/linux-a733",
        "inventory/kernel-workflow-paths.json",
        "candidate/a733-platform-clean-v6",
        "b1f20d455a60",
        "status: dirty",
        "candidate/a733-platform-clean-v4",
        "abc8d07b0a63",
        "status: clean",
        "rtc-binding-missing",
        "rtc-clock-header-missing",
        "rtc-ccu-driver-missing",
        "ccu-binding-clock-inputs-mismatch",
        "r-ccu-clock-header-missing",
        "r-ccu-reset-header-missing",
        "r-ccu-driver-missing",
        "dtsi-ccu-clock-names-missing-losc-fanout",
        "dtsi-ccu-clock-input-count",
        "choose or build a clean A733 prerequisite stack",
        "Do not stage, stash, reset, clean, commit, or push",
        "scripts/a733-prereq-stack-audit /Users/enzo/projects/linux-a733-sparse --json",
    ]
    for needle in required:
        require_contains("prereq-stack-selection-note", text, needle, failures)


def check_dts_v2_static_proof_preflight(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_STATIC_PROOF_PREFLIGHT
    if not path.exists():
        failures.append(
            f"dts-v2-static-proof-preflight: missing {DTS_V2_STATIC_PROOF_PREFLIGHT}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-static-proof-preflight", text, failures)
    required = [
        "Status: local-only read-only preflight",
        "not a build log",
        "not static proof",
        "not permission to mutate kernel trees or hardware",
        "no worktree creation",
        "no build commands",
        "strix",
        "/srv/projects/cubie-a7s-armbian/sources/mainline-linux",
        "8fde5d1d47f69db6082dfa34500c27f8485389a5",
        "sun60i-a733.dtsi",
        "sun60i-a733-cubie-a7s.dts",
        "untracked",
        "83fb09c191c7ac32ed680c44b3459346fecec4d1a9e13d12a49ee575169c5688",
        "19680b27e13d0454a46382f35f871c8a0392878cfa75055fe63e0ded127fa51d",
        "0b750e9ec64e35036e5be6acf18c4e19cb435e079dd3036dc809b0e4b2207bac",
        "/usr/bin/aarch64-linux-gnu-gcc",
        "/usr/bin/make",
        "/usr/bin/dtc",
        "committed prerequisite branch",
        "contracted temporary isolated copy",
        "plain detached worktree",
        "stop and log the proof as blocked",
    ]
    for needle in required:
        require_contains("dts-v2-static-proof-preflight", text, needle, failures)


def check_dts_v2_uart_pinctrl_preview(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_UART_PINCTRL_PREVIEW
    if not path.exists():
        failures.append(
            f"dts-v2-uart-pinctrl-preview: missing {DTS_V2_UART_PINCTRL_PREVIEW}"
        )
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "Local-only no-send DTS v2 preview",
        "Do not send this patch as-is",
        "not runtime proof",
        "not b4 metadata",
        "not approval to mutate hardware",
        "git apply --check",
        "CHECK_DTBS=y",
        "scripts/checkpatch.pl --strict",
        "scripts/get_maintainer.pl",
        "A733-BATCH-002",
        "A733-COMM-002",
        "A733-COMM-003",
        "sun60i-a733-cubie-a7s.dts",
        "sun60i-a733.dtsi",
        "uart0_pb9_pb10_pins",
        "uart0-pb9-pb10-pins",
        "pins = \"PB9\", \"PB10\"",
        "function = \"uart0\"",
    ]
    for needle in required:
        require_contains("dts-v2-uart-pinctrl-preview", text, needle, failures)


def check_dts_v2_held_cover_changelog_draft(root: Path, failures: list[str]) -> None:
    path = root / DTS_V2_HELD_COVER_CHANGELOG_DRAFT
    if not path.exists():
        failures.append(
            f"dts-v2-held-cover-changelog-draft: missing {DTS_V2_HELD_COVER_CHANGELOG_DRAFT}"
        )
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("dts-v2-held-cover-changelog-draft", text, failures)
    required = [
        "Status: drafted-not-reviewed; local-only; no-send",
        "A733-COMM-002",
        "A733-COMM-003",
        "not a sent message",
        "not b4 metadata",
        "not maintainer-approved",
        "not validation proof",
        "not permission to mutate hardware",
        "Communication blackout remains active",
        "Operator approval is not open",
        "Static proof is not complete",
        "Runtime proof remains queued-only under A733-BATCH-002",
        "task-packets/kernel/a733-dts-v2-local-delta-plan.md",
        "task-packets/kernel/a733-dts-v2-static-proof-plan.md",
        "task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch",
        "Subject: [PATCH v2 0/1]",
        "Move the UART0 PB9/PB10 pin group",
        "sun60i-a733-cubie-a7s.dts",
        "sun60i-a733.dtsi",
        "Do not convert unavailable tooling into a pass",
        "Public communication: closed",
        "Hardware mutation: closed",
    ]
    for needle in required:
        require_contains("dts-v2-held-cover-changelog-draft", text, needle, failures)


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


def check_kernel_checkout_quarantine(root: Path, failures: list[str]) -> None:
    path = root / KERNEL_CHECKOUT_QUARANTINE
    if not path.exists():
        failures.append(f"kernel-checkout-quarantine: missing {KERNEL_CHECKOUT_QUARANTINE}")
        return
    text = path.read_text(encoding="utf-8")
    check_markdown_fences("kernel-checkout-quarantine", text, failures)
    required = [
        "Last refreshed: 2026-06-13",
        "/Users/enzo/projects/linux-a733",
        "candidate/a733-platform-clean-v6",
        "b1f20d455a600d33999cf893fdf0df8fb2ace538",
        "known local checkout noise",
        "Do not stage, stash, reset, or clean",
        "/Users/enzo/projects/linux-a733-sparse",
        "candidate/a733-platform-clean-v4",
        "abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e",
        "Current status: clean",
        "clean validation, review, and local documentation",
        "Read-only source searches",
    ]
    for needle in required:
        require_contains("kernel-checkout-quarantine", text, needle, failures)


def check_kernel_workflow_paths(root: Path, failures: list[str]) -> None:
    path = root / KERNEL_WORKFLOW_PATHS
    if not path.exists():
        failures.append(f"kernel-workflow-paths: missing {KERNEL_WORKFLOW_PATHS}")
        return
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        failures.append(f"kernel-workflow-paths: invalid JSON: {exc}")
        return
    mac = data.get("hosts", {}).get("mac-mini", {})
    notes = " ".join(mac.get("notes", [])) if isinstance(mac.get("notes"), list) else ""
    required = [
        "/Users/enzo/projects/linux-a733",
        "/Users/enzo/projects/linux-a733-sparse",
        "inventory/kernel-checkout-quarantine-20260606.md",
        "known non-A733 dirty files",
        "clean validation",
        "Do not stage, stash, reset, or clean",
        "codex-desktop-only",
        "offload_required_for_goal_completion",
    ]
    for needle in required:
        if needle not in raw and needle not in notes:
            failures.append(f"kernel-workflow-paths: missing required text: {needle}")


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
    check_dts_v2_local_delta_plan(root, failures)
    check_dts_v2_static_proof_plan(root, failures)
    check_dts_v2_static_validation_hosts(root, failures)
    check_dts_v2_static_proof_command_packet(root, failures)
    check_dts_v2_static_proof_isolated_copy(root, failures)
    check_claim_service_activation_checklist(root, failures)
    check_prereq_stack_selection_note(root, failures)
    check_clean_prereq_stack_construction_plan(root, failures)
    check_gated_transition_approval_packet(root, failures)
    check_gated_transition_approval_brief(root, failures)
    check_dts_v2_static_proof_preflight(root, failures)
    check_dts_v2_uart_pinctrl_preview(root, failures)
    check_dts_v2_held_cover_changelog_draft(root, failures)
    check_audio_i2s_evidence(root, failures)
    check_pwm_backlight_fan_evidence(root, failures)
    check_kernel_checkout_quarantine(root, failures)
    check_kernel_workflow_paths(root, failures)
    check_final_send_checklist(root, failures)
    check_current_slice(root, failures)
    check_kernel_workflow_status(root, failures)

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
        "dts_v2_local_delta_plan": str(DTS_V2_LOCAL_DELTA_PLAN),
        "dts_v2_static_proof_plan": str(DTS_V2_STATIC_PROOF_PLAN),
        "dts_v2_static_validation_hosts": str(DTS_V2_STATIC_VALIDATION_HOSTS),
        "dts_v2_static_proof_command_packet": str(DTS_V2_STATIC_PROOF_COMMAND_PACKET),
        "dts_v2_static_proof_isolated_copy": str(DTS_V2_STATIC_PROOF_ISOLATED_COPY),
        "claim_service_activation_checklist": str(CLAIM_SERVICE_ACTIVATION_CHECKLIST),
        "prereq_stack_selection_note": str(PREREQ_STACK_SELECTION_NOTE),
        "clean_prereq_stack_construction_plan": str(CLEAN_PREREQ_STACK_CONSTRUCTION_PLAN),
        "gated_transition_approval_packet": str(GATED_TRANSITION_APPROVAL_PACKET),
        "gated_transition_approval_brief": str(GATED_TRANSITION_APPROVAL_BRIEF),
        "dts_v2_static_proof_preflight": str(DTS_V2_STATIC_PROOF_PREFLIGHT),
        "dts_v2_uart_pinctrl_preview": str(DTS_V2_UART_PINCTRL_PREVIEW),
        "dts_v2_held_cover_changelog_draft": str(DTS_V2_HELD_COVER_CHANGELOG_DRAFT),
        "audio_i2s_evidence": str(AUDIO_I2S_EVIDENCE),
        "pwm_backlight_fan_evidence": str(PWM_BACKLIGHT_FAN_EVIDENCE),
        "kernel_checkout_quarantine": str(KERNEL_CHECKOUT_QUARANTINE),
        "kernel_workflow_paths": str(KERNEL_WORKFLOW_PATHS),
        "final_send_checklist": str(FINAL_SEND_CHECKLIST),
        "current_slice": str(CURRENT_SLICE),
        "kernel_workflow_status": str(KERNEL_WORKFLOW_STATUS),
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
