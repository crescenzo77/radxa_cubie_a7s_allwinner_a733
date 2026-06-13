# A733 Current Evidence Index

Status: local-only coordination index
Updated: 2026-06-13

This index points future A733 / Radxa Cubie A7S patch-prep work at the current
local evidence packets. It is not a public communication, not a resend
approval, not a maintainer-response draft, and not new proof. It summarizes
existing local records so another worker can start from the right source of
truth without re-discovering the whole history.

Authority remains:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-cycle-ledger.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`

## Current Posture

- Local work only. Do not send mail, b4 submissions, list replies, GitHub
  comments, pull requests, public pushes, or paid third-party calls.
- Do not mutate hardware. Board roles are unassigned, recovery is not drilled
  for burn autonomy, and the claim service is planned-not-active.
- DTS v1 was already sent before the current blackout and must not be resent.
- H215 was already sent before the current blackout and must not be resent
  unless a later approved gate explicitly reopens that action.
- H253 is fallback material only if maintainers ask for common update-bit
  handling.

## Source And Proof Anchors

| Track | Current local anchor | Proof / validation packet | Use rule |
|---|---|---|---|
| Narrow A733 CCU/SDMMC0 line | H200 head `de486cb24c361a86cba26738f24332df780872b0` | H201 exact hardware proof | Current clean hardware-proven source reference; do not resend during blackout |
| H200 patch text | `task-packets/kernel/a733-h200-h199-maintainer-polish-series/` and patches-only bundle | H200 readiness plus H201 proof | Local reference for review discussion or regeneration only |
| Public-safe H200 proof excerpt | `task-packets/kernel/a733-h211-h200-public-safe-uart-proof-excerpt-20260613T0640Z.md` | Derived from H201 | Use only if a future approved response needs a concise proof excerpt |
| Common update-bit fallback | H253 head `e694ae3fa8477846a5a6eaf31fed4813ff991d5b` | H247 hardware proof plus H253 bundle gates | Fallback only if maintainers ask for common helper shape |
| Current maintainer-response playbook | H260 | H218/H224/H253/H255 references inside H260 | Event-driven local planning only; no automatic communication |
| Cubie A7S DTS v1 | H265 public sent/indexed record | H261-H264 pre-send gates, H265 send/index record | Historical sent-before-blackout item; do not resend |
| Cubie A7S DTS v2 | No current sendable action | A733-COMM-002 and A733-COMM-003 | Hold until maintainer feedback, prerequisite landing, or concrete correction |

## Key Records

### H200 / H201 Narrow CCU Line

- `task-packets/kernel/a733-h200-h199-maintainer-polish-readiness-20260613T0604Z.md`
- `task-packets/kernel/a733-h201-h200-exact-hardware-proof-20260613T0610Z.md`
- `task-packets/kernel/a733-h211-h200-public-safe-uart-proof-excerpt-20260613T0640Z.md`

H201 proves the exact H200 commit on Cubie3 through unused-clock cleanup,
unused power-domain cleanup, SDMMC0 initialization, card and partition
enumeration, read-only root mount, and `/bin/sh`. The board was restored to
vendor kernel `5.15.147-21-a733` after proof.

Do not turn this into a new public series during local-only mode. H215 is the
historical sent-before-blackout public action for this line.

### H247 / H253 Common Update-Bit Fallback

- `task-packets/kernel/a733-h247-h245-common-update-bit-v2-hardware-proof-20260613T0845Z.md`
- `task-packets/kernel/a733-h253-h252-regenerated-v2-fallback-no-send-20260613T0901Z.md`

H247 proves the H245/H253 common update-bit fallback through the same Cubie A7S
success boundary as H201/H200. H253 packages that source shape as a regenerated
no-send fallback bundle with public hygiene, apply, diff-check,
source-equivalence, and strict checkpatch gates recorded.

Use H253 only if maintainers explicitly ask for a common
`CCU_FEATURE_UPDATE_BIT` registration-time handoff shape, then refresh all
recipients, archive/upstream state, hygiene, apply, source-equivalence, build,
and communication gates before any public action.

### H260 Event Playbook

- `task-packets/kernel/a733-h260-current-maintainer-response-playbook-20260613T0920Z.md`

H260 is the current local routing table for future events:

- maintainer reply to H215
- maintainer request for common update-bit handling
- sender-mailbox evidence that H215 failed
- public appearance of H215
- public export backup need
- DTS reflect review request

During blackout, use H260 as planning input only.

### H265 DTS v1 Historical Send

- `task-packets/kernel/a733-h261-dts-b4-send-preview-gate-20260613T0922Z.md`
- `task-packets/kernel/a733-h262-dts-public-ready-branch-send-preview-pass-20260613T0931Z.md`
- `task-packets/kernel/a733-h263-dts-b4-reflect-submitted-delivery-pending-20260613T0937Z.md`
- `task-packets/kernel/a733-h264-dts-reflect-received-reviewed-pass-20260613T0945Z.md`
- `task-packets/kernel/a733-h265-dts-v1-public-sent-indexed-20260613T0950Z.md`

H265 records the public DTS v1 send and initial visibility. It is represented
in the communications ledger as `A733-COMM-016` with status
`sent-before-blackout`.

Do not send v2 automatically. V2 work remains held behind maintainer feedback,
prerequisite landing, or a concrete correction and must be refreshed before
any future public action.

## Communication Ledger Mapping

| Ledger ID | Meaning | Current action |
|---|---|---|
| A733-COMM-013 | H190 CCU RFC feedback reply | Historical sent item; no resend |
| A733-COMM-014 | H204 follow-up reply | Historical sent item; no resend |
| A733-COMM-015 | H215 RFC/RFT CCU/SDMMC0 series | Historical sent item; no resend |
| A733-COMM-016 | H265 DTS v1 b4 series | Historical sent item; no resend |
| A733-COMM-002 / A733-COMM-003 | DTS v2 cover/changelog | Draft-needed; hold |
| A733-COMM-004 through A733-COMM-012 | Future prerequisite/peripheral communications | Draft-needed; hold |

## Next Safe Local Uses

- Run `python3 tools/validate/a733_authority_check.py` before and after edits
  to the authority files.
- Use this index to choose the right packet before preparing any local-only
  response draft or proof bundle.
- Use `task-packets/kernel/a733-local-regeneration-checklist.md` before any
  local regeneration or recheck of H200/H215 narrow material or H253 fallback
  material.
- Use `task-packets/kernel/a733-peripheral-evidence-map.md` before starting
  any local-only source inventory or validation planning for peripherals.
- Use `task-packets/kernel/a733-sd-emmc-evidence-sheet.md` before any SDMMC,
  rootfs-stability, storage-write, cold-boot, or eMMC source inventory,
  validation planning, or runtime-proof queue refinement.
- Use `task-packets/kernel/a733-ethernet-gmac-evidence-sheet.md` before any
  Ethernet/GMAC source inventory, validation planning, or runtime-proof queue
  refinement.
- Use `task-packets/kernel/a733-usb-otg-fel-evidence-sheet.md` before any
  USB, USB-C, OTG, or FEL source inventory, validation planning, or
  runtime/recovery-proof queue refinement.
- Use `task-packets/kernel/a733-thermal-cpufreq-fan-evidence-sheet.md` before
  any thermal, cpufreq, OPP, PWM, fan, tach, workload, stop-threshold, or
  thermal-proof queue refinement.
- Use `task-packets/kernel/a733-pcie-nvme-evidence-sheet.md` before any PCIe,
  PCIe PHY, adapter, link-training, NVMe, storage-write, or fio proof queue
  refinement.
- Use `task-packets/kernel/a733-low-speed-io-evidence-sheet.md` before any
  I2C, SPI, UART, GPIO, pinctrl, header, connector, interrupt, loopback, or
  external-device proof queue refinement.
- Use `task-packets/kernel/a733-wifi-bluetooth-evidence-sheet.md` before any
  Wi-Fi, Bluetooth, SDIO, radio firmware, pwrseq, wake-GPIO, scan,
  association, throughput, pairing, or reconnect proof queue refinement.
- If patch text is regenerated locally, record the exact base, head, patch
  directory, validation commands, and source-equivalence target.
- If a hardware item looks necessary, queue it in
  `task-packets/kernel/a733-supervised-batch-queue.md` unless current inventory
  positively permits the board role, recovery rung, drill, and claim-service
  state.

## Do Not Use This Index For

- sending or resending any public communication
- asserting a fresh public archive state
- assigning burn/proving/reference board roles
- proving Ethernet, PCIe, USB, USB-C, OTG, FEL, Wi-Fi, Bluetooth, display,
  media, NPU, RISC-V, eMMC, thermal, cpufreq, fan, or other peripheral support
- bypassing the communication ledger, hardware queue, or workflow
