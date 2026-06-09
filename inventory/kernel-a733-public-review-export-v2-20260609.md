# A733 Cubie A7S Public Review Export v2

Date: 2026-06-09

## Operator Topology

Codex Desktop runs on the Mac, but kernel bring-up work should be executed on
Strix. Strix has the UART adapters, the Homelab scripts checkout, and SSH reach
to the Cubie boards.

Current working assumption:

- Mac Codex issues commands to Strix over SSH.
- Strix performs UART capture, kernel artifact staging, and Cubie reboot/boot
  orchestration.
- Cubie2 and Cubie3 both have a `codex` account with passwordless sudo for
  lab automation.
- Vendor U-Boot workarounds stay RAM-only in U-Boot or lab scripts.

Do not route the active UART boot proof through the Mac. The Mac is the control
surface, not the hardware operator.

## Public Export State

Public repository:

- Strix checkout: `/srv/projects/cubie-a7s-armbian-public`
- Mac checkout: `/Users/enzo/projects/Home Lab/cubie-a7s-armbian`
- GitHub remote: `https://github.com/crescenzo77/radxa_cubie_a7s_allwinner_a733.git`
- Current public commit: `57a1325 patches: refresh A733 review export`

Kernel review branch on Strix:

- stack checkout: `/srv/projects/a733-prereq-stack-current`
- branch: `codex/a733-cubie-review-v2`
- prerequisite-stack base recorded in patches: `6428b90c6af7`
- review branch head recorded in cover letter: `d9aa2e15caae`

Current public export shape:

1. `dt-bindings: mmc: add Allwinner A733 compatible`
2. `dt-bindings: arm: sunxi: add Radxa Cubie A7S`
3. `arm64: dts: allwinner: add Allwinner A733 SoC`
4. `arm64: dts: allwinner: add Radxa Cubie A7S`

The export is not a mailed upstream submission.

## Guardrails Preserved

- No vendor U-Boot compatibility strings, vendor path aliases, `fdt_high`
  hacks, or hardcoded memory were added to DTS.
- Ethernet, VPU/Cedrus, display, wireless, USB-C, PCIe, and other peripherals
  remain out of scope.
- Local CCU/PRCM and pinctrl driver patches are not carried in the public
  export.
- The cover letter uses explicit `Depends-on:` references for the active A733
  RTC, CCU/PRCM, and pinctrl RFCs.
- The DTSI is reconciled with the current prerequisite API shape:
  `hosc`, `losc`, `iosc`, and `losc-fanout` main CCU inputs from RTC outputs;
  A733 RTC fixed inputs `osc19M`, `osc24M`, and `osc26M`; A733 pinctrl as the
  10-bank PB through PK RFC shape starting at `GIC_SPI 69`.

## Validation Completed

Public export checks completed before commit `57a1325`:

- public hygiene gate: pass
- A733 series shape gate: pass, exactly 4 non-cover patches
- A733 prerequisite API audit: pass
- `git diff --cached --check`: pass
- public patch parse proof: pass, 286 inserted lines across 5 kernel files
- public patch `git am` proof against `6428b90c6af7`: pass
- checkpatch over exported patches: 0 errors; expected `FILE_PATH_CHANGES`
  warnings for new DTS files
- get-maintainer over exported patches: 13 expected Devicetree, Allwinner,
  ARM, MMC, and Linux recipients
- targeted DTB build from the regenerated branch: pass for
  `allwinner/sun60i-a733-cubie-a7s.dtb`
- direct dtschema validation of the built Cubie A7S DTB: pass

Local Strix Qwen review lane was also exercised against the staged public diff.
It reported no blockers in the visible diff. Treat this as a secondary review
hint only; deterministic gates and human review remain authoritative.

## Current Blocker

The old corrected-root blocker is resolved for the historical v4 runtime proof:
the panic was caused by the `root=UUID=...` plus no-initramfs bootargs path, not
by a DTS MMC failure. The passing proof used PARTUUID, showed MMC partition
enumeration, and mounted the root filesystem read-only.

The current blocker before any upstream send is narrower:

- prove the exact regenerated review branch artifact, not only the historical
  v4 validation branch, if the final mailed branch differs from the already
  boot-proven Image/DTB; and
- re-check the RTC, CCU/PRCM, and pinctrl RFC status immediately before
  mailing.

## Safest Next Runtime Proof

Use Strix for the next runtime proof. Build and stage a non-default boot entry
from the exact regenerated review branch head, then boot Cubie3 over Strix UART.

The proof should keep the known-good corrected-root shape:

- RAM-only U-Boot step: `setenv drm_debug 1`
- no DTS changes for vendor U-Boot
- non-default extlinux label
- `root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e`
- `rootfstype=ext4 rootwait ro rootflags=noload init=/bin/sh`
- UART capture saved under the Strix Cubie UART logs directory

Pass criteria:

- log identifies the exact regenerated kernel commit and DTB under test
- `Machine model: Radxa Cubie A7S`
- 8 CPUs and GICv3 redistributors initialize
- A733 RTC/CCU/pinctrl dependencies initialize without clock lookup failures
- UART0 console remains stable
- `sunxi-mmc 4020000.mmc` initializes
- `mmcblk0` partitions are discovered
- root filesystem mounts read-only through PARTUUID

If this proof fails before `mmcblk0` partition discovery, triage the
prerequisite clock/pinctrl/MMC binding path first. If it fails only at root
mount, keep DTS unchanged and retry with `root=/dev/mmcblk0p3` as a lab-only
bootargs fallback.
