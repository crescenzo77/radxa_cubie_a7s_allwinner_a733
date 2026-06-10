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

Do not use broad generated research summaries as the deciding source for this
series when they conflict with the local proofs. The active upstream context is
not "no LKML A733 work"; it includes A733 RTC, CCU/PRCM, pinctrl, and pmdomain
series. For the minimal Cubie A7S DTS proof, Ethernet, VPU, display, USB-C, and
NPU/GPU notes are background only.

## Pre-Send Patch Hygiene Queue

Do not rewrite the patches until the runtime clock blocker is understood, but
carry these as must-fix items before any mailout:

- Drop the vendor-tree `allwinner,pinmux = <2>;` property. The current export
  has it in patch 3 `sun60i-a733.dtsi` for `mmc0_pins` and in patch 4
  `sun60i-a733-cubie-a7s.dts` for `uart0_pb9_pb10_pins`. Keep the upstream
  `function = "mmc0";` and `function = "uart0";` properties.
- Re-check the schematic before adding UART RX bias. `PB10` may need
  `bias-pull-up`, but do not guess.
- Be ready to explain `reg_vcc3v3` as an always-on fixed rail unless schematic
  evidence shows a GPIO-enable regulator.
- Keep the current export numbered as a 4-patch review series. Any older
  8-patch/9-patch wording is historical only.

## Runtime Proof Update

The old corrected-root blocker is resolved for the historical v4 runtime proof:
the panic was caused by the `root=UUID=...` plus no-initramfs bootargs path, not
by a DTS MMC failure. The passing proof used PARTUUID, showed MMC partition
enumeration, and mounted the root filesystem read-only.

The exact regenerated review-v2 artifact was then built on Strix from:

```text
/srv/projects/a733-prereq-stack-current
branch: codex/a733-cubie-review-v2
head: d9aa2e15caae5085b51a28529fc0c35d189df543
```

Normal corrected-root boot reached `ttyS0` and then stalled after:

```text
clk: Disabling unused clocks
```

It did not reach `sunxi-mmc 4020000.mmc`, `mmcblk0`, or root mount.

A lab-only retry of the same Image/DTB with `clk_ignore_unused` succeeded:

```text
log: tools/hardware-logs/cubie-uart/20260609T195725Z-a733-review-v2-d9aa2e15caae-clkignore-ro-proof-autopower-full-ttyUSB0.uart.log
sha256: 728fedf08a63775c9cdfadcc5151fadf2332677111d1f3addb23e049afb5d492
```

Observed pass lines:

- `Linux version 7.1.0-rc5-00177-gd9aa2e15caae`
- `Machine model: Radxa Cubie A7S`
- `clk: Not disabling unused clocks`
- `sunxi-mmc 4020000.mmc: initialized`
- `mmcblk0: p1 p2 p3`
- `EXT4-fs (mmcblk0p3): mounted filesystem ... ro without journal`
- `Run /bin/sh as init process`

Follow-up clock-summary capture from the same label:

```text
log: tools/hardware-logs/cubie-uart/20260609T200716Z-a733-review-v2-d9aa2e15caae-clkignore-clksummary-autopower-ttyUSB0.uart.log
sha256: cdb6b1d94e5bc7028cc6592bc2ea61621d7486faccba0cd94c8692818ca7c3ed
```

Useful lines:

- `mmc0` is enabled by `4020000.mmc` after probe.
- `bus-mmc0` is enabled by `4020000.mmc` after probe.
- `ahb-store` and `mbus-store` remain enabled only because
  `clk_ignore_unused` prevented unused-clock shutdown; both show zero consumer
  count in the captured `clk_summary`.

Diagnostic follow-up on Strix ruled out the first two simple fixes:

```text
store fabric critical log: tools/hardware-logs/cubie-uart/20260609T202146Z-a733-diag-storeboth-06bdeb25a675-ro-proof-fixedbootargs-autopower-full-ttyUSB0.uart.log
sha256: c10dcf332bee953c8ff6bcb127b4b67bde44bcec79fb26371e1e777fceadb7c4

MMC0 leaf critical log: tools/hardware-logs/cubie-uart/20260609T204515Z-a733-mmc0crit-drmdebug-runbootcmd-full-ttyUSB0.uart.log
sha256: 8678b4f6d325db3f61063cbaa8d4866b2f52694cf7540718a7607d2974f79469
```

Both lab-only kernels used the same corrected PARTUUID root proof shape and
the RAM-only U-Boot `drm_debug` bypass. Both reached the same failure point:
`Linux version ...`, `Machine model: Radxa Cubie A7S`, correct kernel command
line, UART0 enabled, then `clk: Disabling unused clocks`, with no
`sunxi-mmc 4020000.mmc` or `mmcblk0` lines afterward.

Therefore, simply marking `ahb-store` plus `mbus-store` critical is not enough,
and simply marking `mmc0` plus `bus-mmc0` critical is not enough.

Clock-trace instrumentation then produced a valid boot log:

```text
log: tools/hardware-logs/cubie-uart/20260609T212724Z-a733-clktrace-extlinux-verified-ttyUSB0.uart.log
sha256: f4c7e525285f0bea013af54f7916bd66c31be7b5d1636a0d4982a364a3b25891
```

The diagnostic Image/DTB booted the expected kernel
`7.1.0-rc5-00178-g5596fe20533f`, reached `clk: Disabling unused clocks`, and
logged unused-clock shutdown through `gic` and then `pll-periph0-480M` before
the UART stopped. It still did not reach `sunxi-mmc 4020000.mmc`.

Follow-up critical-clock tests ruled out that simple explanation:

```text
GIC critical log: tools/hardware-logs/cubie-uart/20260609T220105Z-a733-giccrit-185b3e014002-direct-shortpaths-cleanreboot-ttyUSB0.uart.log
sha256: 7c060d15ca65dd6a91733d25376be8f6b51c58485ad280bff53290712cd3a2f7

GIC plus pll-periph0-480M critical log: tools/hardware-logs/cubie-uart/20260609T220926Z-a733-gicpllcrit-d0fd57e26969-direct-shortpaths-cleanreboot-ttyUSB0.uart.log
sha256: 4ed7ab87c1214b3193e26ac6dfb59b7d2c1983c2c6d5fd057f3a22bdfac1e530
```

Both direct U-Boot loads used the expected Image/DTB, a valid FDT magic, the
correct PARTUUID bootargs, and the RAM-only `drm_debug=1` workaround. Both
started the expected mainline diagnostic kernel and still stopped at
`clk: Disabling unused clocks`, before `sunxi-mmc 4020000.mmc`.

Combined trace/critical-clock follow-up narrowed the failure pattern but did
not produce an upstreamable critical-clock answer:

```text
clktrace + gic + pll-periph0-480M critical log: tools/hardware-logs/cubie-uart/20260609T221905Z-a733-clktrace-gicpllcrit-a3a572c840cc-direct-shortpaths-cleanreboot-ttyUSB0.uart.log
sha256: ed106b72eb6a174078472a0d3a9a9ccbfa15d15538f28ef3b4366ba68782cfc9

plus cpu-peri critical log: tools/hardware-logs/cubie-uart/20260609T222656Z-a733-clktrace-gicpll-cpuperi-0966c05830db-direct-shortpaths-cleanreboot-ttyUSB0.uart.log
sha256: 23232193d94438e846c107c2393134202dc1d97b666a83000328e5c72e3662ad

plus AHB IOMMU0 sys critical log: tools/hardware-logs/cubie-uart/20260609T224017Z-a733-clktrace-gicpll-cpuperi-iommu0-bd46c5ba0138-direct-shortpaths-from-prompt-ttyUSB0.uart.log
sha256: ed61b515b46c43764ad947b68f5f4bcd29a2541a0cc52274cae8c2c31170bc19

plus AHB IOMMU0/IOMMU1 sys critical log: tools/hardware-logs/cubie-uart/20260609T224744Z-a733-clktrace-gicpll-cpuperi-iommu01-11f058e059ac-direct-shortpaths-from-prompt-ttyUSB0.uart.log
sha256: e1be8a02dc58a2c4a33e637f2de2b363770961ad0f8326db06b139d07e13c50d
```

Observed progression:

- With `gic` and `pll-periph0-480M` held critical, the trace reached
  `cpu-peri` and stopped there.
- Holding `cpu-peri` critical advanced the trace through many unused gates and
  stopped after `ahb-iommu0-sys`.
- Holding `ahb-iommu0-sys` critical advanced the trace to
  `ahb_iommu1-sys`.
- Holding both AHB IOMMU sys gates critical advanced the trace to
  `ahb-ve-dec`.

Enhanced trace follow-up then showed the video-engine gate was not the final
root cause:

```text
unlock/gate-register trace log: tools/hardware-logs/cubie-uart/20260609T225856Z-a733-clktrace-regtrace-21eef905ee2a-direct-shortpaths-cleanreboot-ttyUSB0.uart.log
sha256: 0567eeded281335119e65a0e7ea89dee5cc443b25e802d0c26d22de8fe95c271

R-CCU 0x19c write-trace log: tools/hardware-logs/cubie-uart/20260609T230553Z-a733-clktrace-rregtrace-20542876293f-direct-shortpaths-cleanreboot-ttyUSB0.uart.log
sha256: a57f468b2298ba3467d6e42dd1a9b535f0c8a6e253ff97fe52a3bfd9890f6aaa

pre-is-enabled trace log: tools/hardware-logs/cubie-uart/20260609T231232Z-a733-clktrace-preisen-2220d0d49616-direct-shortpaths-cleanreboot-ttyUSB0.uart.log
sha256: 547dd2f5dcd2e9a3559ef357ae2652368712adffddbf577f751632fb0444b53c

extlinux-only drm_debug proof log: tools/hardware-logs/cubie-uart/20260609T233547Z-a733-ri2ccrit-8072e669de6b-extlinux2-ttyUSB0.uart.log
sha256: c6876730c3942399d54b05607e1c9a15d1ecb09b0ed0dd1cd5adf61a96993f1a

R-I2C-critical proof log: tools/hardware-logs/cubie-uart/20260609T234059Z-a733-ri2ccrit-8072e669de6b-direct-ctrlc-prompt-ttyUSB0.uart.log
sha256: 6d3c58827f00b95d3c8726c4dda474a9a2db183e13dfebdd82276eda3b783d7b

R-bus-critical proof log: tools/hardware-logs/cubie-uart/20260609T235232Z-a733-rbuscrit-a422a00f4750-direct-cleanprompt-ttyUSB0.uart.log
sha256: 16f6a6ffc5776d983f9693dbb4cacc2c3e3bdf12f7c71d5a58e7284ffbba65d4

R-CCU-skip proof log: tools/hardware-logs/cubie-uart/20260610T000219Z-a733-rccu-skipunused-9b16e23b47c8-direct-ctrlc-prompt-ttyUSB0.uart.log
sha256: 3eee44b58ba5e8d8dad524c0ece692cf3a173de8fffcfa885d37bc2455a56285

RTC DCXO 0x16c read-trace proof log: tools/hardware-logs/cubie-uart/20260610T002234Z-a733-rccu-skip-16c-c5dfcb904bad-direct-retry-ttyUSB0.uart.log
sha256: 8e6d4df5eb8561a01eaba686d31f72e32faa2d76c7f609d6d0ece5c57b3cd88e

RTC DCXO sibling-gate proof log: tools/hardware-logs/cubie-uart/20260610T003234Z-a733-rccu-skip-hoscufs-f651139793f7-direct-ttyUSB0.uart.log
sha256: ce97a16be401b40a4e75618740e94ce6964caccb7034faf466f793e60baefc03

RTC ahb-enable falsification log: tools/hardware-logs/cubie-uart/20260610T004850Z-a733-rtc-ahb-7e67931f4380-direct-ttyUSB0.uart.log
sha256: 124299f80226cdc11a5fbac8d1f35c16dafdd57f7039229e4d355feffd7e1bce

RTC DCXO-wide skip to ext-osc32k-gate log: tools/hardware-logs/cubie-uart/20260610T005439Z-a733-rccu-dcxo-skip-9bc09ace48d2-direct-ttyUSB0.uart.log
sha256: 4817f4dfb2b323843054dc064dd3a9f5c8c89cde10f32cf9ede10cf02a2fbd1f
```

Those logs show:

- all traced `0x5c0` AHB feature gates, including `ahb-ve-dec`, write and
  return cleanly;
- the walk advances through `pll-periph0-4x`, `pll-ddr`, and into
  `sys-24M` -> `r-apb1`;
- the next stop is `bus-r-i2c2`;
- adding `0x19c` write tracing does not emit a `0x19c` write, so the failure is
  before gate disable; and
- the narrow final trace reaches `is-enabled-begin name=bus-r-i2c2` and never
  prints `is-enabled-true` or `is-enabled-false`;
- putting `drm_debug=1` only in Linux extlinux bootargs still enters the vendor
  U-Boot FDT creation failure, so `drm_debug` must be set in U-Boot RAM before
  boot; and
- marking R-I2C gates critical advances the hang to `bus-r-uart1`; marking the
  R bus gates critical advances the hang to `r-timer0`; and
- a lab-only skip for `r-*` and `bus-r-*` unused cleanup advances past the R-CCU
  group and then stops at `hosc-ufs`;
- adding RTC DCXO gate read tracing proves that `hosc-ufs` stops inside
  `ccu_gate_helper_is_enabled()` at `reg=0x16c gate=0x1`, before a read-end
  line; and
- skipping only `hosc-ufs` moves the stop to sibling `hosc-hdmi` at the same
  RTC DCXO register, `reg=0x16c gate=0x2`, again before a read-end line;
- enabling the optional RTC `ahb` clock in `rtc-sun6i` does not fix the stop;
  the kernel still stalls after unused clock cleanup starts, before MMC; and
- skipping all RTC DCXO sibling gates (`hosc-ufs`, `hosc-hdmi`,
  `hosc-serdes0`, `hosc-serdes1`) advances to `ext-osc32k-gate`, which then
  stops in the RTC CCU gate `is_enabled` path at offset `0x0`, bit 4.

Inference: the current blocker is broader than one R-I2C gate and broader than
R-CCU alone. The normal review-v2 boot wedges while unused-clock cleanup walks
A733 CCU gate state for unused peripherals. The failure path first exposed
R-CCU gates (`bus-r-i2c2`, `bus-r-uart1`, `r-timer0`), then exposed RTC DCXO
gates (`hosc-ufs`, `hosc-hdmi`) when R-CCU unused cleanup was skipped, and then
exposed `ext-osc32k-gate` when the DCXO siblings were skipped. This is not an
MMC/rootfs failure and not evidence for DTS or vendor U-Boot compatibility hacks.

Vendor DTB comparison from Cubie3's running 5.15 image shows the same R-CCU
base region:

```text
r_ccu@7010000: compatible = "allwinner,sun60iw2-r-ccu"; reg = <0x00 0x7010000 0x00 0x340>
twi@7083000: device_type = "s_twi0"; PMU aliases live here
twi@7084000: device_type = "s_twi1"
twi@7085000: device_type = "s_twi2"
```

CCU source audit notes:

- The active review-v2 CCU files are still stacked from the external A733 RTC
  and CCU/PRCM work, not a local independent CCU rewrite.
- `hosc-ufs`, `hosc-hdmi`, `hosc-serdes0`, and `hosc-serdes1` are exported by
  the A733 RTC CCU as DCXO gates at RTC offset `0x16c`, bits 0, 1, 4, and 5.
  The minimal DTS does not instantiate UFS, display/HDMI, or SerDes consumers,
  so this is unused-clock cleanup touching omitted hardware. Runtime tracing
  confirms the MMIO read of that gate register does not return in this boot
  state. Skipping only `hosc-ufs` moves the hang to sibling `hosc-hdmi`; skipping
  all four DCXO siblings moves the hang to `ext-osc32k-gate`, another RTC CCU
  gate at offset `0x0`, bit 4. The unsafe operation is broader than one
  UFS-only gate definition.
- The vendor DTB has a downstream `clk-init-gate = <0x01>` property on the
  vendor main CCU node. Do not copy that into upstream DTS; treat it only as a
  hint that the BSP handles initial gate policy differently.
- The vendor DTB also exposes UFS in its boot-device list and vendor nodes, but
  UFS remains out of scope for the first upstream slice.

Current blocker before any upstream send:

- the review-v2 artifact still only boots through MMC/root when
  `clk_ignore_unused` is present;
- the failing path is the A733 unused-clock disable walk before MMC probe, not
  rootfs, MMC DT wiring, or vendor U-Boot DTS compatibility;
- the current strongest evidence points to R-CCU and RTC CCU gate `is_enabled`
  traversal for unused peripherals as a class problem, not to the AHB
  video-engine gates themselves;
- enabling the optional RTC `ahb` clock in `rtc-sun6i` did not fix the stop;
- skipping all RTC DCXO sibling gates (`hosc-ufs`, `hosc-hdmi`,
  `hosc-serdes0`, `hosc-serdes1`) advanced only to `ext-osc32k-gate`, another
  RTC CCU gate, at offset `0x0`, bit 4; and
- map the disable-walk result back to the A733 CCU/PRCM RFC before changing any
  exported DTS, binding patch, or CCU patch; and
- re-check the RTC, CCU/PRCM, and pinctrl RFC status immediately before
  mailing.

This is not a rootfs blocker and not evidence for adding vendor U-Boot
compatibility hacks to DTS. `clk_ignore_unused` is a diagnostic bootarg only.

## Safest Next Runtime Step

Use Strix for runtime proof. Stop the one-clock-at-a-time critical clock chase:
it moved from `bus-r-i2c2` to `bus-r-uart1` to `r-timer0`, and the R-CCU-wide
skip moved the stop to RTC CCU gates, then to `ext-osc32k-gate` when all DCXO
siblings were skipped. That proves the problem is not one isolated consumer
clock.

The next proof should keep the known-good corrected-root shape:

- RAM-only U-Boot step: `setenv drm_debug 1`
- no DTS changes for vendor U-Boot
- non-default extlinux label
- `root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e`
- `rootfstype=ext4 rootwait ro rootflags=noload init=/bin/sh`
- UART capture saved under the Strix Cubie UART logs directory

Immediate technical focus:

- use `clk_ignore_unused` only as the lab proof that the exact Image/DTB can
  reach SDMMC0 and `/bin/sh`;
- audit the A733 CCU/PRCM clock definitions, especially unused gate `is_enabled`
  paths such as R-CCU gates, RTC DCXO gates, and `ext-osc32k-gate`, instead of
  adding more critical-clock guesses;
- if another runtime proof is needed, trace the specific gate-state read rather
  than marking more clocks critical; the latest trace already proves the
  RTC DCXO `0x16c` gate reads hang for both `hosc-ufs` and `hosc-hdmi`, and a
  broader DCXO skip exposes `ext-osc32k-gate`;
- compare the traced gate/register behavior against Junhui Liu's A733 CCU/PRCM
  RFC topology and the vendor BSP's clock/reset defaults;
- decide whether the issue is a missing CCU critical flag, a wrong parent/rate
  relationship, a reset/clock coupling problem, or an RFC prereq mismatch;
- avoid expanding scope into Ethernet, VPU, display, USB-C, PCIe, or wireless;
- do not rewrite or submit patches until the clock dependency is isolated.

## Clock-Trace Diagnostic Prep

A lab-only instrumentation branch now exists on Strix:

```text
/srv/projects/a733-diag-clktrace
branch: codex/a733-diag-clktrace
head: 5596fe20533f
```

It instruments the common clock unused-disable path in `drivers/clk/clk.c`.
Build outputs:

```text
Image sha256: e8491da1b702cfbaee07540e85add9ab4875eb7f4f57acd79ca56585242709a3
DTB sha256:   6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
config sha256: dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202
```

Valid clktrace boot evidence:

```text
log: tools/hardware-logs/cubie-uart/20260609T212724Z-a733-clktrace-extlinux-verified-ttyUSB0.uart.log
sha256: f4c7e525285f0bea013af54f7916bd66c31be7b5d1636a0d4982a364a3b25891
```

Last useful lines show unused-clock shutdown of:

```text
clk-unused: disable-begin name=gic parent=pll-periph0-480M ...
clk-unused: disable-end name=gic parent=pll-periph0-480M ...
clk-unused: disable-begin name=pll-periph0-480M parent=pll-periph0-4x ...
clk-unused: disable-end name=pll-periph0-480M parent=pll-periph0-4x ...
```

No later `sunxi-mmc` line appears. Treat this as evidence for a narrow
GIC/parent-clock retention diagnostic, not as evidence for DTS workarounds.

Critical-clock diagnostic branches already tested:

```text
/srv/projects/a733-diag-giccrit
branch: codex/a733-diag-giccrit
head: 185b3e014002
Image sha256: 8f1941e2830836b782a9022a8b8017991a6015e539fc235905c6f1b0a5b97a84

/srv/projects/a733-diag-gicpllcrit
branch: codex/a733-diag-gicpllcrit
head: d0fd57e26969
Image sha256: c56e478a1667cee2a5ca10914009c27b573bcf23a04ed09ee6ac8bb7de33beb8
```

Both used the same DTB SHA256
`6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a` and both
still stalled before MMC.

Earlier invalid captures remain useful only as lab-process notes: the first
staging attempt left zero-byte DTB/config/manifest files on Cubie3, and a later
capture booted the vendor extlinux entry. Those are not kernel evidence.

Additional staging lesson: when artifacts are installed while vendor Linux is
running and the board is hard power-cycled immediately, U-Boot's ext4 reader can
still see small newly written files as zero bytes. The probe log below showed
`sun60i-a733-cubie-a7s.dtb`, `config`, `manifest.txt`, and `SHA256SUMS` as size
0 even though Linux had reported successful hashes. For future direct U-Boot
tests, stage via SSH, run `sync`, cleanly reboot, then load short paths such as
`/boot/gicpll/Image` and `/boot/gicpll/a733.dtb`.

```text
log: tools/hardware-logs/cubie-uart/20260609T215758Z-a733-giccrit-uboot-partlist-dtb-probe-ttyUSB0.uart.log
sha256: e32008eb2a1e57e556f5168e3f5e5d90abe04602b191d4ebaa11a3a2efc1ac31
```

After the valid clktrace stall, Cubie3 was restored again to the vendor-safe
single-entry extlinux state:

```text
log: tools/hardware-logs/cubie-uart/20260609T212958Z-cubie3-vendor-shell-restore-after-clktrace-valid-ttyUSB0.uart.log
sha256: 5fc098eb7a1c135c772527e4346b1afb92ef7bfd7700a46284e9630387ffb075
```
