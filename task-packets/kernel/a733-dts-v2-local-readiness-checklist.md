# A733 DTS v2 Local Readiness Checklist

Status: local-only sendable-held checklist
Updated: 2026-06-13

This checklist defines the local gate before any future Radxa Cubie A7S DTS v2
work can be considered ready-held. It is not a patch, not a draft cover letter,
not send approval, and not permission to run hardware.

## Current Boundary

- Do not send DTS v2 during local-only mode.
- Do not run `b4 send`, `git send-email`, list replies, GitHub comments, pull
  requests, or public pushes from this checklist.
- Do not boot, reboot, install kernels, capture UART, power-cycle boards, or
  mutate hardware from this checklist.
- Do not add Ethernet, eMMC, PCIe, USB-C, Wi-Fi, Bluetooth, display, media,
  NPU, RISC-V MCU, fan, thermal, or cpufreq support to minimal DTS v2.
- Do not treat the current post-v1 b4 revision as sendable without a fresh
  local final gate.

## Trigger To Reopen DTS v2 Work

DTS v2 remains held until at least one of these is true:

- maintainer feedback requests a v2
- a prerequisite clock/reset/pinctrl/MMC dependency lands or changes in a way
  that requires a rebase
- a concrete local correction is found that is safe, minimal, and
  maintainer-standard without needing fresh review judgment
- the operator explicitly reopens the communication and hardware gates

## Minimal Scope

Allowed minimal DTS v2 scope:

- A733 SoC DTSI cleanup needed by the board DTS
- Cubie A7S board DTS
- UART0 console
- SD-card boot through SDMMC0 only

Disallowed in minimal DTS v2:

- Ethernet / GMAC
- eMMC
- PCIe / NVMe
- USB / USB-C / OTG
- Wi-Fi / Bluetooth
- display / DP / eDP / HDMI / MIPI DSI / media / VPU / GPU
- NPU / RISC-V MCU / remoteproc / firmware
- thermal / cpufreq / fan
- broad regulator, PMIC, power-domain, or OPP additions beyond source-backed
  SDMMC0 supply needs

## Required Local Cleanup

- Before editing a kernel tree, read
  `task-packets/kernel/a733-dts-v2-local-delta-plan.md`.
- Move `uart0_pb9_pb10_pins` from
  `sun60i-a733-cubie-a7s.dts` into `sun60i-a733.dtsi`.
- Keep Cubie A7S board DTS referencing the SoC-level UART0 pin group.
- Keep Ethernet disabled/absent unless a future source-backed GMAC proof path
  clears A733-BATCH-007.
- Keep SDMMC0 as SD-card boot only with `no-mmc` and `no-sdio` unless future
  storage evidence clears the eMMC or Wi-Fi/Bluetooth gates.
- Re-check any sashiko-bot or dt-schema findings before considering a resend.
- Rebase on the current applicable A733 prerequisite stack instead of carrying
  private CCU/pinctrl scaffolding as board-DTS proof.

## Required Static Proof

- `make ARCH=arm64 dtbs_check` for the touched DTS/bindings scope, or record
  why the exact command is not available locally.
- `make ARCH=arm64 allwinner/sun60i-a733-cubie-a7s.dtb`, or equivalent
  targeted DTB build from the selected kernel tree.
- `git diff --check` over the kernel patch range.
- `scripts/checkpatch.pl --strict` on generated patches, with any remaining
  warning explicitly justified.
- `scripts/get_maintainer.pl` output captured for the would-send series.
- `b4 prep --show-info` or equivalent b4 metadata review if the branch is
  still managed by b4.

## Required Runtime Proof Before Send

Runtime proof remains queued-only while hardware roles and recovery are not
ready. Before a real v2 send, A733-BATCH-002 must provide:

- exact kernel tree, base commit, branch, Image hash, DTB hash, and extlinux
  entry
- board role, UART by-path, power path, recovery rung, and recovery drill
- boot log showing model, UART0 console, SDMMC0 probe, card/partition
  enumeration, root mount, and shell or init boundary
- rollback path to a known-good entry
- proof that the same candidate did not rely on local unsubmitted CCU or
  pinctrl scaffolding unless those dependencies are explicitly represented

## Held Communication Mapping

- A733-COMM-002: future DTS v2 cover letter.
- A733-COMM-003: future DTS v2 changelog note.
- A733-COMM-016: historical DTS v1 sent/indexed record; do not resend.

Any future draft must be generated only after the cleanup, validation, proof,
recipient, b4, and operator-approval gates are refreshed.

## Current Local Finding

Read-only source inspection of the clean sparse checkout
`/Users/enzo/projects/linux-a733-sparse` at
`candidate/a733-platform-clean-v4` / `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
still shows `uart0_pb9_pb10_pins` inside
`sun60i-a733-cubie-a7s.dts`, not in `sun60i-a733.dtsi`. The quarantined full
checkout `/Users/enzo/projects/linux-a733` at
`candidate/a733-platform-clean-v6` / `b1f20d455a600d33999cf893fdf0df8fb2ace538`
shows the same pattern by read-only inspection, but must not be used for patch
export while its non-A733 dirty-file quarantine remains active. It must not be used for patch export.
This is consistent with the known v1 feedback and means local DTS v2 cleanup
is not complete. The local DTS v2 cleanup is not complete.

## Stop Condition

If a future worker cannot positively prove every static and runtime gate above,
the correct state remains `sendable-held` or `question-held`, not sent.
