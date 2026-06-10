# A733 / Cubie A7S Thread Quick Reference - 2026-06-08

Purpose: compact restart context for continuing Radxa Cubie A7S / Allwinner
A733 kernel patch work in this Codex thread. This is a private lab reference,
not a public submission artifact.

## Current Repositories

- Private workflow repo: `/Users/enzo/projects/homelab`
- Public-facing repo: `/Users/enzo/projects/Home Lab/cubie-a7s-armbian`
- Public GitHub record: `https://github.com/crescenzo77/radxa_cubie_a7s_allwinner_a733`
- Historical full-validation Linux fork/branch referenced by public docs:
  - fork: `https://github.com/crescenzo77/linux.git`
  - branch: `candidate/a733-platform-clean-v4`
  - head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- Current public review-export note:
  `inventory/kernel-a733-public-review-export-v2-20260609.md`
- Public repo is documentation/patch-export facing. Keep raw UART logs, model
  reviews, private topology, generated images, DTBs, and scratch notes out of
  it.

## Workflow Automation Contract

- Final mailing preparation uses `b4` from a clean generated review branch.
- Branch flow is topic branch -> candidate branch -> generated review branch;
  update dependent refs together when rebasing a stack.
- `scripts/kernel-validation-floor` is the local validation floor, mirrored by
  the public CI on candidate/topic/review/Codex branches and pull requests.
- `patches/` is a review snapshot and CI input, not the source of truth for
  upstream mailout.
- The public PR template is the stop-condition checklist for scope,
  dependencies, validation, and trailer review.

## Hardware Map

- Cubie2: `192.168.50.85`
  - A733 target, staged artifacts present, `/boot` entry not installed in the
    latest gate output.
  - Kasa wrapper on Strix: `~/.local/bin/cubie2-power`
  - Kasa plug IP: `192.168.50.74`
- Cubie3: `192.168.50.95`
  - Active proof target.
  - Exact A733 v4 boot entry installed.
  - Extlinux test entry is menu choice `50`.
  - Kasa wrapper on Strix: `~/.local/bin/cubie3-power`
  - Kasa plug IP: `192.168.50.104`
- Excluded target: `192.168.50.65`
  - Do not use for kernel work. It is reserved for Wyze/object detection.
- UART host: Strix `192.168.50.11`
  - Cubie3 UART: `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1:1.0-port0`
    -> `/dev/ttyUSB0`
  - The other CP2102 path exists at `...usb-0:1.2...` -> `/dev/ttyUSB1`, but
    Cubie2 UART proof remains weaker.

## Current Boot Artifact

AMD artifact directory:

```text
/srv/projects/kernel-work/outgoing/a733-v4-abc8d07b0a63-20260606T152409Z
```

Manifest essentials:

```text
kernel_head=abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e
Image sha256=b4584f230d436235fb3776a102546e05d8fac1d93206d25f3566aedad7e60b7d
DTB sha256=9ac58728715b7999bda4fe579bb00a4c9da7f123c7d0fb1bf9e4664cd85a0e44
config sha256=9273c649385ba95c589c9f4867a77addebb7bf39ac7a7bb3d655d4980eb7ca87
DTB size=4165 bytes
```

Cubie3 extlinux entry:

```text
50: A733 v4 public candidate abc8d07b0a63 UART proof
```

## Most Recent Hardware Result

Tracked note:

```text
inventory/hardware/cubie3-a733-v4-uart-proof-triage-20260607.md
```

Summary:

- Plain extlinux option `50` loads Image/DTB but vendor U-Boot fails before
  Linux with FDT mutation errors:
  - `sunxi_update_fdt_para_for_kernel : FDT_ERR_BADPATH`
  - `sunxi_drm_kernel_para_flush for fdt_add_subnode fail`
  - `/chosen node create failed`
- Retesting option `50` after interrupting U-Boot and running:

```text
setenv drm_debug 1
run bootcmd
```

  bypasses the vendor DRM/FDT mutation failure.
- With that temporary U-Boot env var, Linux starts, brings up 8 CPUs,
  initializes `ttyS0`, and initializes `sunxi-mmc 4020000.mmc`.
- It then panics because the extlinux entry uses filesystem `UUID=...` without
  an initramfs:

```text
Disabling rootwait; root= is invalid.
/dev/root: Can't open blockdev
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

Practical next proof action: repeat the successful U-Boot-env boot with a
kernel-native root argument such as `/dev/mmcblk0p3` or `PARTUUID=...`.

Important nuance: `drm_debug=1` must be set in U-Boot RAM. Putting it only in
Linux bootargs is not enough to bypass the vendor U-Boot DRM/FDT path.

## 2026-06-09 Review-v2 Runtime Update

Exact regenerated branch artifact:

```text
/srv/projects/a733-prereq-stack-current
branch: codex/a733-cubie-review-v2
head: d9aa2e15caae5085b51a28529fc0c35d189df543
```

Normal corrected-root boot of that artifact starts Linux and initializes
UART0, then stalls after `clk: Disabling unused clocks`, before MMC probe.

The same Image/DTB with lab-only `clk_ignore_unused` boots through MMC and
PARTUUID root:

```text
tools/hardware-logs/cubie-uart/20260609T195725Z-a733-review-v2-d9aa2e15caae-clkignore-ro-proof-autopower-full-ttyUSB0.uart.log
sha256: 728fedf08a63775c9cdfadcc5151fadf2332677111d1f3addb23e049afb5d492
```

It shows `sunxi-mmc 4020000.mmc`, `mmcblk0: p1 p2 p3`, read-only ext4 root
mount, and `/bin/sh` as init.

Clock-summary follow-up:

```text
tools/hardware-logs/cubie-uart/20260609T200716Z-a733-review-v2-d9aa2e15caae-clkignore-clksummary-autopower-ttyUSB0.uart.log
sha256: cdb6b1d94e5bc7028cc6592bc2ea61621d7486faccba0cd94c8692818ca7c3ed
```

`mmc0` and `bus-mmc0` have real `4020000.mmc` consumers after probe. Storage
fabric gates such as `ahb-store` and `mbus-store` stayed enabled under
`clk_ignore_unused`, but later diagnostics ruled them out as the complete fix.

Diagnostic follow-up:

- `ahb-store` plus `mbus-store` marked critical still stalls after
  `clk: Disabling unused clocks`, before `sunxi-mmc`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T202146Z-a733-diag-storeboth-06bdeb25a675-ro-proof-fixedbootargs-autopower-full-ttyUSB0.uart.log`
  SHA256:
  `c10dcf332bee953c8ff6bcb127b4b67bde44bcec79fb26371e1e777fceadb7c4`.
- `mmc0` plus `bus-mmc0` marked critical also stalls at the same point.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T204515Z-a733-mmc0crit-drmdebug-runbootcmd-full-ttyUSB0.uart.log`
  SHA256:
  `8678b4f6d325db3f61063cbaa8d4866b2f52694cf7540718a7607d2974f79469`.
- Putting `drm_debug=1` only in Linux bootargs is not enough; without the
  U-Boot RAM env var, vendor U-Boot still reaches `FDT creation failed`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T204026Z-a733-mmc0crit-autopower-full-ttyUSB0.uart.log`
  SHA256:
  `33a7ab80433c8b1ddc8ac2d841a192881e57376437b50bffc7bbb4b26e8e8da1`.
- The vendor U-Boot prompt can be stopped with a Ctrl-C flood despite
  `Hit any key to stop autoboot:  0`; plain space flood was consumed by BOOT0
  and did not reliably stop U-Boot.
- Cubie3 was recovered with direct vendor boot and restored to a minimal
  vendor-default extlinux entry. Normal reboot verified:
  `5.15.147-21-a733`, hostname `cubie-3`.

Valid clktrace boot evidence:

```text
tools/hardware-logs/cubie-uart/20260609T212724Z-a733-clktrace-extlinux-verified-ttyUSB0.uart.log
sha256: f4c7e525285f0bea013af54f7916bd66c31be7b5d1636a0d4982a364a3b25891
```

The diagnostic kernel reached unused-clock shutdown and then stopped after:

```text
clk-unused: disable-begin name=gic parent=pll-periph0-480M ...
clk-unused: disable-end name=gic parent=pll-periph0-480M ...
clk-unused: disable-begin name=pll-periph0-480M parent=pll-periph0-4x ...
clk-unused: disable-end name=pll-periph0-480M parent=pll-periph0-4x ...
```

No `sunxi-mmc 4020000.mmc` or `mmcblk0` lines followed.

Follow-up critical-clock tests:

- `gic` marked critical still stalls after `clk: Disabling unused clocks`,
  before MMC.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T220105Z-a733-giccrit-185b3e014002-direct-shortpaths-cleanreboot-ttyUSB0.uart.log`
  SHA256:
  `7c060d15ca65dd6a91733d25376be8f6b51c58485ad280bff53290712cd3a2f7`.
- `gic` plus `pll-periph0-480M` marked critical also stalls before MMC.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T220926Z-a733-gicpllcrit-d0fd57e26969-direct-shortpaths-cleanreboot-ttyUSB0.uart.log`
  SHA256:
  `4ed7ab87c1214b3193e26ac6dfb59b7d2c1983c2c6d5fd057f3a22bdfac1e530`.

Later clktrace/critical-clock progression:

- `clktrace + gic + pll-periph0-480M` reached `cpu-peri`, then stopped.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T221905Z-a733-clktrace-gicpllcrit-a3a572c840cc-direct-shortpaths-cleanreboot-ttyUSB0.uart.log`
  SHA256:
  `ed106b72eb6a174078472a0d3a9a9ccbfa15d15538f28ef3b4366ba68782cfc9`.
- Adding `cpu-peri` critical advanced through many gates and stopped after
  `ahb-iommu0-sys`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T222656Z-a733-clktrace-gicpll-cpuperi-0966c05830db-direct-shortpaths-cleanreboot-ttyUSB0.uart.log`
  SHA256:
  `23232193d94438e846c107c2393134202dc1d97b666a83000328e5c72e3662ad`.
- Adding `ahb-iommu0-sys` critical advanced to `ahb_iommu1-sys`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T224017Z-a733-clktrace-gicpll-cpuperi-iommu0-bd46c5ba0138-direct-shortpaths-from-prompt-ttyUSB0.uart.log`
  SHA256:
  `ed61b515b46c43764ad947b68f5f4bcd29a2541a0cc52274cae8c2c31170bc19`.
- Adding both AHB IOMMU sys gates critical advanced to `ahb-ve-dec`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T224744Z-a733-clktrace-gicpll-cpuperi-iommu01-11f058e059ac-direct-shortpaths-from-prompt-ttyUSB0.uart.log`
  SHA256:
  `e1be8a02dc58a2c4a33e637f2de2b363770961ad0f8326db06b139d07e13c50`.

Enhanced trace follow-up:

- `0x58c`/`0x5c0` gate-write plus unlock/child trace showed all `0x5c0` AHB
  feature gates, including `ahb-ve-dec`, write and return cleanly. The walk then
  advanced to `sys-24M` -> `r-apb1` -> `bus-r-i2c2`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T225856Z-a733-clktrace-regtrace-21eef905ee2a-direct-shortpaths-cleanreboot-ttyUSB0.uart.log`
  SHA256:
  `0567eeded281335119e65a0e7ea89dee5cc443b25e802d0c26d22de8fe95c271`.
- Adding R-CCU `0x19c` write tracing produced no `0x19c` write line; the stop
  stayed at `bus-r-i2c2`, before disable.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T230553Z-a733-clktrace-rregtrace-20542876293f-direct-shortpaths-cleanreboot-ttyUSB0.uart.log`
  SHA256:
  `a57f468b2298ba3467d6e42dd1a9b535f0c8a6e253ff97fe52a3bfd9890f6aaa`.
- Adding pre-lock/is-enabled markers showed
  `is-enabled-begin name=bus-r-i2c2` as the last line. There is no
  `is-enabled-true` or `is-enabled-false`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T231232Z-a733-clktrace-preisen-2220d0d49616-direct-shortpaths-cleanreboot-ttyUSB0.uart.log`
  SHA256:
  `547dd2f5dcd2e9a3559ef357ae2652368712adffddbf577f751632fb0444b53c`.
- Appending `drm_debug=1` only to Linux extlinux bootargs did not bypass the
  vendor U-Boot FDT mutation path. U-Boot still failed FDT creation, so the
  workaround must be RAM-only U-Boot environment state before boot.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T233547Z-a733-ri2ccrit-8072e669de6b-extlinux2-ttyUSB0.uart.log`
  SHA256:
  `c6876730c3942399d54b05607e1c9a15d1ecb09b0ed0dd1cd5adf61a96993f1a`.
- Marking only R-I2C0/1/2 gates critical advanced the stop from `bus-r-i2c2`
  to `bus-r-uart1`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T234059Z-a733-ri2ccrit-8072e669de6b-direct-ctrlc-prompt-ttyUSB0.uart.log`
  SHA256:
  `6d3c58827f00b95d3c8726c4dda474a9a2db183e13dfebdd82276eda3b783d7b`.
- Marking the R bus gates critical advanced the stop to `r-timer0`.
  Log:
  `tools/hardware-logs/cubie-uart/20260609T235232Z-a733-rbuscrit-a422a00f4750-direct-cleanprompt-ttyUSB0.uart.log`
  SHA256:
  `16f6a6ffc5776d983f9693dbb4cacc2c3e3bdf12f7c71d5a58e7284ffbba65d4`.
- A lab-only skip for `r-*` and `bus-r-*` during unused-clock cleanup advanced
  past the R-CCU group and then stopped at `hosc-ufs`.
  Log:
  `tools/hardware-logs/cubie-uart/20260610T000219Z-a733-rccu-skipunused-9b16e23b47c8-direct-ctrlc-prompt-ttyUSB0.uart.log`
  SHA256:
  `3eee44b58ba5e8d8dad524c0ece692cf3a173de8fffcfa885d37bc2455a56285`.
- Adding RTC DCXO gate read tracing proved the `hosc-ufs` stop is inside
  `ccu_gate_helper_is_enabled()` at `reg=0x16c gate=0x1`, before a read-end
  line.
  Log:
  `tools/hardware-logs/cubie-uart/20260610T002234Z-a733-rccu-skip-16c-c5dfcb904bad-direct-retry-ttyUSB0.uart.log`
  SHA256:
  `8e6d4df5eb8561a01eaba686d31f72e32faa2d76c7f609d6d0ece5c57b3cd88e`.
- Skipping only `hosc-ufs` moved the stop to sibling `hosc-hdmi`, still inside
  the RTC DCXO gate read path, now at `reg=0x16c gate=0x2`.
  Log:
  `tools/hardware-logs/cubie-uart/20260610T003234Z-a733-rccu-skip-hoscufs-f651139793f7-direct-ttyUSB0.uart.log`
  SHA256:
  `ce97a16be401b40a4e75618740e94ce6964caccb7034faf466f793e60baefc03`.
- Enabling the optional RTC `ahb` clock in `rtc-sun6i` did not fix the stop.
  The log still shows `sun6i-rtc` registering and then stalling after unused
  clock cleanup starts, before `sunxi-mmc`.
  Log:
  `tools/hardware-logs/cubie-uart/20260610T004850Z-a733-rtc-ahb-7e67931f4380-direct-ttyUSB0.uart.log`
  SHA256:
  `124299f80226cdc11a5fbac8d1f35c16dafdd57f7039229e4d355feffd7e1bce`.
- Skipping all RTC DCXO sibling gates (`hosc-ufs`, `hosc-hdmi`,
  `hosc-serdes0`, `hosc-serdes1`) advanced past offset `0x16c`, then stopped
  at `ext-osc32k-gate` in the RTC CCU, offset `0x0`, bit 4.
  Log:
  `tools/hardware-logs/cubie-uart/20260610T005439Z-a733-rccu-dcxo-skip-9bc09ace48d2-direct-ttyUSB0.uart.log`
  SHA256:
  `4817f4dfb2b323843054dc064dd3a9f5c8c89cde10f32cf9ede10cf02a2fbd1f`.

Vendor DTB comparison from Cubie3 5.15 confirms `r_ccu@7010000` has the same
`reg = <0x00 0x7010000 0x00 0x340>` window, and vendor secure TWI nodes are
`s_twi0` at `7083000`, `s_twi1` at `7084000`, and `s_twi2` at `7085000`.
Vendor PMU aliases live under `s_twi0`.

Current blocker: the review-v2 artifact still needs lab-only
`clk_ignore_unused` to reach MMC/root. The normal path wedges during the A733
unused-clock disable walk before MMC probe. The strongest current evidence now
points to R-CCU and RTC CCU gate `is_enabled` traversal for unused peripherals
as a class problem: the stop moves from `bus-r-i2c2` to `bus-r-uart1` to
`r-timer0`, then to RTC DCXO gates when R-CCU unused cleanup is skipped.
Enabling the optional RTC `ahb` clock in `rtc-sun6i` did not fix it. Skipping
all RTC DCXO sibling gates (`hosc-ufs`, `hosc-hdmi`, `hosc-serdes0`,
`hosc-serdes1`) only advanced the stop to `ext-osc32k-gate` at RTC offset
`0x0`, bit 4. Stop the
critical-clock chase; use `clk_ignore_unused` only for lab boot proof, then
compare the clock definitions against Junhui Liu's A733 CCU/PRCM RFC and vendor
BSP clock/reset defaults. Do not add vendor U-Boot DTS hacks, and do not expand
the first upstream slice into Ethernet, VPU, display, USB-C, PCIe, or wireless.

CCU audit note: `hosc-ufs`, `hosc-hdmi`, `hosc-serdes0`, and `hosc-serdes1`
are A733 RTC CCU DCXO sibling gates at offset `0x16c`, bits 0, 1, 4, and 5.
`ext-osc32k-gate` is another RTC CCU gate at offset `0x0`, bit 4. The minimal
DTS does not instantiate UFS, display/HDMI, or SerDes consumers for those gates,
so this is unused-clock cleanup touching omitted hardware. The vendor DTB has a
downstream-only `clk-init-gate = <0x01>` on the vendor main CCU node; do not
copy that property into upstream DTS. The latest traces confirm RTC CCU gate
status reads can fail to return in the mainline boot state.

2026-06-10 follow-up: branch `codex/a733-diag-rtc-extosc-orphan`, commit
`98d5978ddd56`, removed the absent `ext-osc32k-gate` from A733 RTC CCU
registration on top of the existing R-CCU/DCXO cleanup skips. The boot advanced
past unused-clock cleanup and reached `sunxi-mmc 4020000.mmc`, proving the RTC
orphan gate was a real blocker. It still did not mount root: MMC then repeated
`fatal err update clk timeout` and waited for the PARTUUID root device. Valid
log:
`tools/hardware-logs/cubie-uart/20260610T012308Z-a733-rtc-extosc-orphan-98d5978ddd56-extlinux2-ttyUSB0.uart.log`
SHA256:
`5fc2fb7ad1833fb8d2caf739eadf68638229f1f4432bf5e33f2c08d94ec7774f`.
`pd_ignore_unused` was tested and did not fix that MMC timeout. Commit
`5e6b35b07c67` then skipped unused-root unprepare for `iosc`, `osc19M`,
`osc24M`, and `osc26M`; that removed the MMC update-clock timeout and reached
clean `sunxi-mmc 4020000.mmc: initialized`, but still did not produce `mmcblk0`
or root. Log:
`tools/hardware-logs/cubie-uart/20260610T022835Z-a733-osc-keep-5e6b35b07c67-extlinux2-ttyUSB0.uart.log`
SHA256:
`eb3e495db4491922288494ff7f386c5106fa59b4ffc52350ff9a06a3f10cce59`.
Valid direct U-Boot trace with commit `b839d38b3a6c` shows MMC host add and
rescan run, then the first request is CMD0 at 400 kHz with `ferror=0`. No
request completion, later command, `mmcblk0`, or root follows. This narrows the
current blocker to first MMC command completion or interrupt delivery after
CMD0. Log:
`tools/hardware-logs/cubie-uart/20260610T024831Z-a733-mmc-trace-b839d38b3a6c-direct-ttyUSB0.uart.log`
SHA256:
`132d87856d41b03941e192b2749ff8ef1096871b8631262196bd14873c49432c`.
Follow-up commit `a52ea49def77` traced IRQ/finalize paths and polled raw MMC
status after CMD0. The valid direct U-Boot run shows no `diag irq`, no
`diag finalize`, and repeated zero register state after CMD0:
`rint=0x00000000 mista=0x00000000 stas=0x00000000 cmdr=0x00000000
imask=0x00000000`. This narrows the blocker further to command launch or
controller state before IRQ delivery. Log:
`tools/hardware-logs/cubie-uart/20260610T030303Z-a733-mmc-irqtrace-a52ea49def77-direct-v2-ttyUSB0.uart.log`
SHA256:
`552cb242bbbc05baf84374c2425c310908e82244e7d762406d8c4ca1c7b79ed9`.
Follow-up commit `cf7b2b08344e` traced command-launch readbacks. The valid
direct U-Boot run shows the SDMMC0 register window reads all zero before CMD0
and after IMASK/CARG/CMDR writes. Even initialized registers such as `TMOUT`,
`FTRGL`, `GCTRL`, and `CLKCR` read zero. This shifts the current blocker from
command IRQ handling to SDMMC0 bus/reset/clock-domain accessibility after the
lab-only CCU cleanup skips. Log:
`tools/hardware-logs/cubie-uart/20260610T031554Z-a733-mmc-cmdlaunch-cf7b2b08344e-ext4load-ttyUSB0.uart.log`
SHA256:
`77fa1d38f8338243878d9d776dcaa3c844d49b6dc346b768562b042f839e4133`.
Follow-up commit `b9e4692d4d5c` traced enable/init/runtime-PM. The SDMMC0
window is already all zero immediately after AHB/MMC/output/sample clocks are
enabled and controller reset completes; `sunxi_mmc_init_host()` writes do not
read back. Runtime PM is active and not suspended before CMD0. Log:
`tools/hardware-logs/cubie-uart/20260610T032435Z-a733-mmc-initpm-b9e4692d4d5c-ext4load-ttyUSB0.uart.log`
SHA256:
`ca55c6f70ef7750e0ac86fcc4637b6dd1f8f31a5534611681453f47f9e6b60ea`.
Vendor DTB comparison shows SDMMC0 uses reset cell `0x23`, while the current
local header maps `RST_BUS_MMC0` to 36 (`0x24`). Commit `0c658caf3956` tested
vendor cell 35 in the lab DTS. It changed SDMMC0 readbacks from all zero to
all `0x20000000`, but still did not allow writes or CMD0 completion. This
keeps the blocker in A733 CCU/reset/storage-fabric mapping. Log:
`tools/hardware-logs/cubie-uart/20260610T033330Z-a733-mmc-resetcell-0c658caf3956-ext4load-ttyUSB0.uart.log`
SHA256:
`9d2063d6bcd0a1b9d0cacd05fa5d61fa84190648c5c02d525e53fdf726792a24`.
Commit `d628a2e9120f` then kept vendor-correlated storage fabric clocks
critical in the lab CCU: `ahb-store`, `mbus-store`, and `mbus-msi-lite0`.
Stacked with reset cell 35, SDMMC0 register access becomes sane and command
enumeration advances through CMD0/CMD8/ACMD41/CMD2/CMD3/CMD9/CMD7. The new
blocker is the first data request, ACMD51/SCR read. Log:
`tools/hardware-logs/cubie-uart/20260610T034137Z-a733-mmc-storecrit-d628a2e9120f-ext4load-ttyUSB0.uart.log`
SHA256:
`9fb5580652c37be69d8efdc9c9f71414c473ea9717d6e5cb8499fd656b2eb129`.

Focused evidence note:
`inventory/kernel-a733-ccu-unused-clock-evidence-20260610.md`.

Patch hygiene before send: remove leftover vendor-tree
`allwinner,pinmux = <2>;` from both `mmc0_pins` in the SoC DTSI and
`uart0_pb9_pb10_pins` in the board DTS. Keep the upstream `function`
properties. Do this after the runtime blocker is understood, when regenerating
the final export.

2026-06-09 diagnostic branch:

- Strix worktree: `/srv/projects/a733-diag-clktrace`
- branch: `codex/a733-diag-clktrace`
- head: `5596fe20533f`
- change: lab-only `drivers/clk/clk.c` instrumentation around
  `clk_disable_unused_subtree()` and `clk_unprepare_unused_subtree()`
- build dir: `/tmp/a733-diag-clktrace-build`
- Image SHA256:
  `e8491da1b702cfbaee07540e85add9ab4875eb7f4f57acd79ca56585242709a3`
- DTB SHA256:
  `6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a`

Additional lab-only diagnostic branches:

- `/srv/projects/a733-diag-giccrit`, branch `codex/a733-diag-giccrit`,
  head `185b3e014002`, Image SHA256
  `8f1941e2830836b782a9022a8b8017991a6015e539fc235905c6f1b0a5b97a84`.
- `/srv/projects/a733-diag-gicpllcrit`, branch `codex/a733-diag-gicpllcrit`,
  head `d0fd57e26969`, Image SHA256
  `c56e478a1667cee2a5ca10914009c27b573bcf23a04ed09ee6ac8bb7de33beb8`.
- `/srv/projects/a733-diag-clktrace-gicpllcrit`, branch
  `codex/a733-diag-clktrace-gicpllcrit`, head `a3a572c840cc`, Image SHA256
  `67cd0d03a29b1969bf976fca5bc13666679730851954fb8793f5354c94e3f677`.
- `/srv/projects/a733-diag-clktrace-gicpll-cpuperi`, branch
  `codex/a733-diag-clktrace-gicpll-cpuperi`, head `0966c05830db`, Image SHA256
  `b098cf9ec94befe2c2999f112f83356fef55a7660f4cda3cafa06c3d0a5de7a1`.
- `/srv/projects/a733-diag-clktrace-gicpll-cpuperi-iommu0`, branch
  `codex/a733-diag-clktrace-gicpll-cpuperi-iommu0`, head `bd46c5ba0138`,
  Image SHA256
  `fd242de7f5d2470f6f63c6bca79127b9fb19d8803a2ae293e574dea370dbca3b`.
- `/srv/projects/a733-diag-clktrace-gicpll-cpuperi-iommu01`, branch
  `codex/a733-diag-clktrace-gicpll-cpuperi-iommu01`, head `11f058e059ac`,
  Image SHA256
  `8b13ac9ed769b533f59ed35cb5d1c21cd86b86bab1c3b91cf3b9c6f33693cd36`.
- `/srv/projects/a733-diag-clktrace-gicpll-cpuperi-iommu01-regtrace`, branch
  `codex/a733-diag-clktrace-gicpll-cpuperi-iommu01-regtrace`, head
  `21eef905ee2a`, Image SHA256
  `d930ad29ad7711922f8a6af32084ba9b0e9179c6444ef1552eb6e9183a9bc991`.
- `/srv/projects/a733-diag-clktrace-gicpll-cpuperi-iommu01-rregtrace`, branch
  `codex/a733-diag-clktrace-gicpll-cpuperi-iommu01-rregtrace`, head
  `20542876293f`, Image SHA256
  `065ccd959e359cbb2e7401d3eda4c559708fbba8cf6a767fe1b18510c17f79c0`.
- `/srv/projects/a733-diag-clktrace-gicpll-cpuperi-iommu01-preisen`, branch
  `codex/a733-diag-clktrace-gicpll-cpuperi-iommu01-preisen`, head
  `2220d0d49616`, Image SHA256
  `18d77e43c63cf482cac17b13b38b08987f8e0cfe068a656fcaeb3331859dabee`.
- These diagnostic builds use DTB SHA256
  `6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a`.

Invalid process captures from the clktrace run:

```text
tools/hardware-logs/cubie-uart/20260609T210621Z-a733-clktrace-extlinux-drmdebug-ttyUSB0.uart.log
sha256: 393747aab437a1150a4e6ec27d2bb41b471f5fbbc27570eb0a0cf2d6eb76ccd2
```

The first artifact staging left the DTB/config/manifest as zero-byte files on
Cubie3, which made U-Boot reject the FDT.

```text
tools/hardware-logs/cubie-uart/20260609T211907Z-a733-clktrace-extlinux-restaged-ttyUSB0.uart.log
sha256: 017b456118edc82d2d409ab768e0fad805d89df83f2e2606c12efd52d7e44ecc
```

After restaging with explicit `scp`, this capture used the vendor extlinux
entry rather than the diagnostic entry. Treat both captures as process notes,
not kernel evidence.

Extra staging lesson: U-Boot's ext4 reader can see newly installed small files
as zero bytes if the board is hard power-cycled right after live staging. The
probe below showed the DTB/config/manifest files as size `0` from U-Boot even
though Linux-side hashes had passed. Future U-Boot direct-load tests should
stage over SSH, run `sync`, cleanly reboot, and load short paths such as
`/boot/gicpll/Image` and `/boot/gicpll/a733.dtb`.

```text
tools/hardware-logs/cubie-uart/20260609T215758Z-a733-giccrit-uboot-partlist-dtb-probe-ttyUSB0.uart.log
sha256: e32008eb2a1e57e556f5168e3f5e5d90abe04602b191d4ebaa11a3a2efc1ac31
```

Cubie3 was recovered again through a vendor `init=/bin/sh` UART boot and the
rootfs extlinux file was restored to a single vendor-safe entry. Recovery
evidence:

```text
tools/hardware-logs/cubie-uart/20260609T211654Z-cubie3-vendor-shell-restore-extlinux-from-prompt-ttyUSB0.uart.log
sha256: 487d4dc1b699b8dbfd25c59547c7bed98ae03f99e5b8f1c27bbbd15662922ddf
tools/hardware-logs/cubie-uart/20260609T212958Z-cubie3-vendor-shell-restore-after-clktrace-valid-ttyUSB0.uart.log
sha256: 5fc098eb7a1c135c772527e4346b1afb92ef7bfd7700a46284e9630387ffb075
```

## Historical Boot Lessons From Strix

High-value Strix source:

```text
192.168.50.11:/srv/projects/cubie-a7s-local-agent
```

Key files:

- `A733_UNCERTAINTY_REGISTER_20260530.md`
- `MAINLINE_RFC_V7_BOOT_STAGING_20260530.md`
- `VENDOR_UBOOT_DTB_HANDOFF_ANALYSIS_20260531.md`
- `VENDOR_UBOOT_SOURCE_INSPECTION_20260601.md`
- `artifacts/uart/README.md`
- `artifacts/test-dtb/README.md`

Useful conclusions:

- Vendor RadxaOS baseline boots through BOOT0 -> BL31 -> U-Boot 2018.07 ->
  extlinux -> Linux.
- Vendor console is `ttyAS0`; mainline UART0 should appear as `ttyS0`.
- Clean mainline DTB handoff under vendor U-Boot is sensitive to vendor FDT
  mutation paths.
- `dtc -R 64` reserve-map padding removes one bogus reserve-map cascade but
  does not by itself solve the `/chosen` failure.
- `setenv fdt_high 0xffffffffffffffff` did not solve the failure.
- U-Boot source inspection tied the fatal path to vendor DRM/display fixups.
- Temporary `setenv drm_debug 1` in U-Boot RAM skips that vendor DRM path and
  previously allowed clean DTBs to reach Linux.
- Older RFC v7 work already proved UART, GIC routing, SDMMC0 enumeration, and
  read-only `mmcblk0p3` rootfs mount when using a diagnostic initramfs/path.
- Do not use these vendor-boot constraints as justification for upstream DTS
  vendor-only names or display/policy nodes.

## Current Upstream Strategy

Public docs say the current 4-patch export is a review snapshot, not a
sendable upstream submission. The export is recorded publicly at commit
`57a1325 patches: refresh A733 review export` and privately in
`inventory/kernel-a733-public-review-export-v2-20260609.md`.

Current public review-export scope:

- A733 MMC compatible binding coverage
- Radxa Cubie A7S board compatible
- initial A733 SoC DTSI with CPUs, timer, GICv3, RTC oscillator provider,
  CCU/R-CCU, pinctrl, UART0, and SDMMC0
- Cubie A7S DTS with UART0 console and MMC0 storage

Historical full-validation v4 scope also carried local CCU/PRCM, pinctrl, MMC,
and MAINTAINERS scaffolding. That 9-patch shape remains validation evidence
only and must not be mailed as-is.

Cleanup and guardrails retained:

- no nonstandard AI trailers
- no deferred parent IRQ registration workaround
- no local CCU/PRCM or pinctrl driver patches in the public review export
- no Ethernet node or generic DWMAC fallback enablement
- no VPU/Cedrus/media patches
- no vendor U-Boot compatibility strings, vendor path aliases, or hardcoded
  memory
- GIC redistributor size fixed to `0x100000`
- asymmetric CPU capacities are represented
- unused GIC child-bus properties removed
- public cover letter carries explicit RTC, CCU/PRCM, and pinctrl `Depends-on:`
  references

## External Work To Coordinate

ThinkCentre research packets:

```text
192.168.50.225:/srv/projects/kernel-services/cortex/ingest
```

Key files:

- `a733-overlap-scan-20260606.md`
- `a733-inflight-ccu-pinctrl-state-20260606.md`
- `a733-rfc-recheck-20260606.md`

Current coordination state:

- Junhui Liu has an in-flight A733 CCU/PRCM RFC:
  `20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech`
- Andre Przywara has an in-flight A733 pinctrl RFC:
  `20250821004232.8134-1-andre.przywara@arm.com`
- No newer A733-specific Linux CCU/pinctrl v2 was found in the local
  public-inbox cache through 2026-06-06.
- Yixun Lan's A733 pinctrl work found in the scan is U-Boot-facing, not the
  Linux pinctrl series.

Policy:

- Do not submit local CCU/PRCM as an independent upstream series while Junhui's
  RFC remains the active reference.
- Do not submit local pinctrl as an independent upstream series while Andre's
  RFC remains the active reference.
- Expected sendable direction is a smaller DTS/board enablement series stacked
  on accepted or current CCU/PRCM and pinctrl prerequisites, unless maintainers
  request a different dependency plan.
- Current private strategy note:
  `inventory/hardware/a733-upstream-minimal-series-strategy-20260609.md`.
  It records that the local 9-patch v4 export should not be sent as-is; the
  expected sendable shape after runtime proof is a smaller SoC DTSI plus Cubie
  A7S board DTS series with explicit dependency handling for Junhui Liu's
  CCU/PRCM RFC and Andre Przywara's pinctrl RFC.

## Subsystem Guardrails

- IRQ: no workaround that bypasses irq_domain/chained irqchip expectations.
  Any A733 IRQ quirk must be modeled in normal irqchip/pinctrl paths.
- Ethernet: keep GMAC out of the first upstream slice. Need proper
  Allwinner/STMMAC glue, GMAC210 wrapper, clock/reset, MDIO, PHY reset, PHY
  power, and link evidence before enabling it.
- VPU/Cedrus: split by subsystem. Do not mix binding, clock/reset, media driver,
  and DTS in one patch.
- MMC: current evidence favors SD-only description for SDMMC0 with `no-mmc` and
  `no-sdio`; provisional `cd-gpios` should stay out until focused card-detect
  evidence exists.
- Memory: do not hard-code RAM size in DTS; rely on bootloader fixup.
- Vendor sources and Orange Pi BSP are evidence only, not implementation bases.

## Commands To Resume

Status gate:

```sh
cd /Users/enzo/projects/homelab
scripts/kernel-workflow-status --strict
```

Pull UART logs and inspect gate:

```sh
scripts/cubie-uart pull-logs
scripts/cubie-runtime-gate
```

Cubie3 Kasa state and cycle:

```sh
ssh enzo@192.168.50.11 '~/.local/bin/cubie3-power state'
ssh enzo@192.168.50.11 '~/.local/bin/cubie3-power cycle 5'
```

Check UART is free:

```sh
ssh enzo@192.168.50.11 'fuser -v /dev/ttyUSB0 2>&1 || true; test ! -e /tmp/cubie-uart-capture.lock || ls -ld /tmp/cubie-uart-capture.lock'
```

Known-good bootloader workaround shape:

```text
interrupt U-Boot
setenv drm_debug 1
run bootcmd
select extlinux option 50
```

Next likely test: same as above, but with a corrected root argument. If editing
the installed extlinux entry is needed, remember Cubie3 sudo is password-gated.

## Things Not To Do

- Do not use `192.168.50.65`.
- Do not install Docker Desktop or sustained model/container services on the
  Mac.
- Do not run models on the Mac.
- Do not put private lab paths, raw logs, AI/model notes, or topology into the
  public GitHub repo.
- Do not claim runtime success from the current A733 v4 capture; it reached
  Linux and initialized UART/MMC, but rootfs did not mount.
- Do not turn temporary `drm_debug=1` U-Boot env handling into an upstream DTS
  or Linux patch claim.

## 2026-06-10 Current Runtime State

The active blocker has moved well past the original rootfs panic. Private
diagnostics now prove SD card init, pre-`mmcblk0` CMD17, small PIO CMD18 reads,
partition discovery, CMD49 cache-enable via scoped PIO write, and read-only
EXT4 root mount to `init=/bin/sh` when IDMA is bypassed.

H009 proves the IDMA issue does not require large block I/O: a forced
8-block, one-descriptor CMD18 transfer still stalls with `RINTR=0x24`,
`IDST=0x4000`, `CHDA=DLBA`, `CBDA=0`, `CBCR=0x400`, and `BBCR=0`.

H010 vendor live descriptor-memory evidence:

```text
tools/hardware-logs/cubie-uart/20260610T162310Z-cubie3-vendor-sdmmc0-descmem-sample.log
sha256: 4b6c57a300cdfa5d86217f469c99863f4d3a9ef7602197e86fd19f6f2ae9386a

tools/hardware-logs/cubie-uart/20260610T162333Z-cubie3-vendor-sdmmc0-descmem-4k-sample.log
sha256: 99ad8f9b5a3a28d7410cb5442adde8a19edb481be9490f6679bdc7edbd7f0965
```

Result: vendor working 4 KiB reads use the same practical descriptor geometry
as H009/H011: `des0` `0x8000001c` or `0x0000001c`, size `0x00001000`,
shifted data-buffer address, and shifted next-descriptor address. Descriptor
geometry is closed for now.

H011 diagnostic head: `eddc27cdf5bf` (`mmc: test A733 IDMAC control clear`).
Artifact:
`/srv/projects/kernel-work/outgoing/a733-h011-dmacclear-eddc27cdf5bf-20260610T162620Z`.
Patch archive:
`tools/kernel-patches/a733-diagnostics/eddc27cdf5bf-dmac-control-clear.patch`,
sha256 `d35eae8df6c0927f6820f76cd731b527d7341c73cead64cb6976ffa807ed13c8`.
UART:
`tools/hardware-logs/cubie-uart/20260610T163415Z-a733-h011-dmacclear-eddc27cdf5bf-ext4load-corrected-ttyUSB0.uart.log`,
sha256 `1a4df27db0edbe02c189622d828053838f7418262acc50fc93161ac11be0e671`.

Result: H011 fails usefully. A direct `REG_DMAC=0` write before IDMAC enable
immediately reads back `0x00000200`; the one-descriptor CMD18 transfer still
stalls with `DMAC=0x282`, `RINTR=0x24`, `IDST=0x4000`, `CHDA=DLBA`,
`CBDA=0`, `CBCR=0x400`, and `BBCR=0`. Do not retest direct DMAC clearing.

Next queue item: H012. Identify the source or meaning of sticky DMAC bit
`0x200` with a vendor live `GCTRL`/DMAC sample and source audit before any new
kernel behavior patch. If bit `0x200` is read-only, derived, or non-causal,
close that clue and move to hidden wrapper, coherency, or fabric evidence.

## 2026-06-10 H012/H013 GCTRL Addendum

H012 vendor live `GCTRL`/DMAC sample:

```text
tools/hardware-logs/cubie-uart/20260610T164508Z-cubie3-vendor-sdmmc0-gctrl-dmac-descmem-4k.log
sha256: 28c79bbe5f104f4fcf516e46d5f1c8c6451ee91d0d146e24d4185066ac190625
```

Result: vendor working reads also show `DMAC=0x00000200` and
`DMAC=0x00000282`. Mainline has no `REG_DMAC` bit-9 definition, so the
`0x200` readback is not a mainline-only actionable clue. The vendor working
state instead commonly shows `GCTRL=0x20000830`.

H013 diagnostic head: `9090e8b17962` (`mmc: test A733 clean DMA access mode`).
Artifact:
`/srv/projects/kernel-work/outgoing/a733-h013-cleandma-9090e8b17962-20260610T164807Z`.
Patch archive:
`tools/kernel-patches/a733-diagnostics/9090e8b17962-clean-dma-access-mode.patch`,
sha256 `f29c126d3244319db6b04370725fc88ab4de425e62c87ba6d722f55d68d3aaa0`.
UART:
`tools/hardware-logs/cubie-uart/20260610T165356Z-a733-h013-cleandma-9090e8b17962-ext4load-corrected-ttyUSB0.uart.log`,
sha256 `7534e010dd6e5c7d3df56ccce1892b6e87d67cddd685ca6f4cbb069c50f4ccf4`.

Result: H013 clears the lab PIO rail's leftover `SDXC_ACCESS_BY_AHB` before
IDMA. The failing CMD18 now launches with `GCTRL=0x20000030` instead of
H009/H011's contaminated `0xa0000030`, but IDMAC still stalls at
`IDST=0x4000`, `CHDA=DLBA`, `CBDA=0`, `CBCR=0x400`, and `BBCR=0`.

Next queue item: H014. Source-audit vendor `GCTRL` bit `0x00000800`
(`0x20000830` vendor versus `0x20000030` H013) before any further behavior
patch. Do not add an undocumented magic bit to upstream code.

## 2026-06-10 H014 No-Build Closeout

H014 audit:
`task-packets/kernel/a733-h014-gctrl-dtime-unit-audit-20260610T1702Z.json`.
Vendor timeout sample:
`tools/hardware-logs/cubie-uart/20260610T170139Z-cubie3-vendor-sdmmc0-gctrl-tmout-dtime-4k.log`,
sha256 `b86e7d06711cc48fb99ad1ab2c24396aab0893192e0fe5ebe182931ef91f3fc9`.

Result: Orange Pi A733 BSP source names `GCTRL` bit 11 as
`SDXC_DTIME_UNIT`. The v5p3x function `sunxi_mmc_set_rdtmout_reg_v5p3x()`
sets it only when read-data timeout exceeds `SDXC_MAX_RDTO`, scales timeout by
256, writes `REG_TMOUT`, and clears the bit during recovery. Runtime matches:
vendor active reads show `GCTRL=0x20000830` with `TMOUT=0x01312dff`; recovered
samples show `GCTRL=0x20000010` with `TMOUT=0xffffffff`.

Do not build a magic `GCTRL=0x800` diagnostic. It is timeout scaling, not a
source-backed descriptor-fetch control. Next queue item: H015, hidden DMA
coherency/storage-fabric audit.

## 2026-06-10 H015 Hidden DMA/Fabric Audit Closeout

H015 audit:
`task-packets/kernel/a733-h015-hidden-dma-fabric-audit-20260610T1708Z.json`.
Reference UART:
`tools/hardware-logs/cubie-uart/20260610T165356Z-a733-h013-cleandma-9090e8b17962-ext4load-corrected-ttyUSB0.uart.log`,
sha256 `7534e010dd6e5c7d3df56ccce1892b6e87d67cddd685ca6f4cbb069c50f4ccf4`.

Result: no build was warranted. Vendor and current diagnostic source now match
or already cover the cheap hidden-DMA/fabric candidates: descriptor geometry,
shifted descriptor/data addresses, 64-bit DMA mask, coherent descriptor
allocation, descriptor sync, `sg_len=dma_len=1`, explicit storage fabric
clocks, MSI-lite mapping, and descriptor page count.

Key runtime clue: H013 leaves the post-stall descriptor unchanged
(`des0=0x8000001c`, `size=0x00001000`, `buf=0x40574400`,
`next=0x3f840004`) while `IDST=0x4000`, `CHDA=DLBA`, `CBDA=0`,
`CBCR=0x400`, and `BBCR=0`. That favors IDMAC not consuming/fetching the
descriptor over stale CPU-visible descriptor contents.

## 2026-06-10 H016 Descriptor-Fetch Stamp Closeout

H016 diagnostic head: `529f1682dd48` (`mmc: trace A733 descriptor fetch
stamps`). Artifact:
`/srv/projects/kernel-work/outgoing/a733-h016-descstamp-529f1682dd48-20260610T171700Z`.
Patch archive:
`tools/kernel-patches/a733-diagnostics/529f1682dd48-desc-fetch-stamps.patch`,
sha256 `17338559d8bbedc997f902db8f2fde621e2fb295eca79e0df868acc5e02ab63a`.
UART:
`tools/hardware-logs/cubie-uart/20260610T172618Z-a733-h016-descstamp-529f1682dd48-ext4load-rerun-ttyUSB0.uart.log`,
sha256 `aaf75f763903fc3db8c6a0cb5b537ed3686126694fa66bc39da07aea3d67636a`.

Result: prompt-controlled UART automation reached the real U-Boot `=>` prompt,
loaded the H016 Image/DTB with `ext4load`, and booted Linux
`7.1.0-rc5-00274-g529f1682dd48`. The SDXC card was detected and `mmcblk0` was
created before the forced CMD18 IDMA read. Before launch, descriptor checksum
was `0x149a82eb` with `d0={8000001c,00001000,40766000,3f840004}` and stamp
`d1={00000000,a733016e,dead0001,beef0002}`. After post-data poll11 and
`dma_sync_single_for_cpu`, checksum and descriptor/stamp words were unchanged,
`OWN` remained set, `IDST=0x4000`, `CHDA=DLBA=0x3f840000`, `CBDA=0`,
`CBCR=0x400`, and `BBCR=0`.

Next queue item: H017. Do a no-build descriptor-fetch address-translation and
fabric comparison first. Only build a kernel if that comparison finds one
source-backed delta. Cubie3 was restored to vendor `5.15.147-21-a733`.

## 2026-06-10 H017/H018 Queue Update

H017 audit:
`task-packets/kernel/a733-h017-desc-fetch-address-fabric-audit-20260610T1740Z.json`.

Result: completed without a build. No remaining source-backed IOMMU,
descriptor geometry, descriptor address shift, 64-bit DMA-mask, req-page-count,
or SDMMC0 fabric-clock delta was found. Vendor working reads and H016 both use
shifted descriptor/data addresses, 4 KiB descriptor segments, coherent
descriptor rings below 4 GiB, and above-4G data buffers. H016 still shows
descriptor word 0 is not consumed.

Next queue item: H018. On Strix, replay H016 descriptor stamps while removing
only the forced A733 64-bit `dma_set_mask_and_coherent()` diagnostic path. Keep
the CMD49 PIO rail, read-only proof, and one-descriptor 8-block CMD18. The goal
is to decide whether descriptor placement/allocation is causal before moving
below visible SDMMC registers into master/fabric reachability.

## 2026-06-10 H018/H019 Queue Update

H018 head: `7adf8f1abf95` (`mmc: replay A733 descriptor stamps without DMA
mask`). Artifact:
`/srv/projects/kernel-work/outgoing/a733-h018-nodmamask-7adf8f1abf95-20260610T174729Z`.
UART:
`tools/hardware-logs/cubie-uart/20260610T174951Z-a733-h018-nodmamask-7adf8f1abf95-ext4load-ttyUSB0.uart.log`,
sha256 `5891308b45a9370cbe7ce044d891bcd9a75fbd89d75635d08fba4157db7e59ef`.
Patch:
`tools/kernel-patches/a733-diagnostics/7adf8f1abf95-h018-nodmamask.patch`,
sha256 `ff4d79cf76475a81b1f58682432c4bbc9575fe793ed485178ea921c6097fd693`.

Result: H018 failed usefully. Removing the forced A733 64-bit DMA-mask path
moved the data buffer below 4 GiB (`sg0 dma=0xfb800000`, descriptor buffer word
`0x3ee00000`) but the descriptor ring remained at `sg_dma=0xfe100000`,
`DLBA=0x3f840000`. The descriptor checksum/stamps stayed unchanged after CPU
sync, `OWN` stayed set, `CHDA=DLBA`, `CBDA=0`, and `IDST=0x4000`.

Next queue item: H019. Change the descriptor allocation/access class directly:
use a normal streaming-mapped descriptor ring with explicit
`dma_sync_single_for_device()` and `dma_sync_single_for_cpu()` around the
existing H016/H018 descriptor-stamp proof. If that still leaves the descriptor
unchanged, move below descriptor memory class toward SDMMC0 master/fabric
reachability.

## 2026-06-10 H019/H020 Queue Update

H019 head: `d903e1dcbb7d` (`mmc: test A733 streaming descriptor ring`).
Artifact:
`/srv/projects/kernel-work/outgoing/a733-h019-descstream-d903e1dcbb7d-20260610T180518Z`.
UART:
`tools/hardware-logs/cubie-uart/20260610T180716Z-a733-h019-descstream-d903e1dcbb7d-ext4load-ttyUSB0.uart.log`,
sha256 `30392cd9d2976019a258464e2b6aaa66f0c0275b5b5d67e2c071a19af4cd82cd`.
Patch:
`tools/kernel-patches/a733-diagnostics/d903e1dcbb7d-h019-descstream.patch`,
sha256 `24ab73e365c382dad6505de6a9dc9c78c7d56a75512c12c65235109511be7316`.

Result: H019 failed usefully. The descriptor ring moved out of coherent CMA to
streaming-mapped normal memory at `sg_dma=0xfa800000` / `DLBA=0x3ea00000`;
the data buffer landed at `sg0 dma=0xfa802000`. The forced CMD18 still stalled
with unchanged descriptor checksum/stamps, `OWN` set, `CHDA=DLBA`, `CBDA=0`,
`IDST=0x4000`, `CBCR=0x400`, and `BBCR=0`.

Next queue item: H020. Do a source-backed vendor/mainline non-SDMMC fabric
snapshot before another behavior patch. Inventory only the state needed for
SDMMC0 descriptor-fetch reachability: CCU/PRCM gates and resets, MBUS/store/
MSI-lite fabric state, any vendor-named storage/firewall/security registers,
and the existing SDMMC0 schema. Queue H021 only if one concrete delta remains.

## 2026-06-10 H020/H021 Queue Update

H020 head: `3b4060f731b1` (`mmc: snapshot A733 fabric registers during IDMAC
stall`). Artifact:
`/srv/projects/kernel-work/outgoing/a733-h020-fabric-3b4060f731b1-20260610T181855Z`.
Vendor snapshot:
`tools/hardware-logs/cubie-h020-vendor-fabric-snapshot-20260610T1819Z.json`,
sha256 `5a95b98b4e91db903f9ac6488d668d105a73b19cee864e37987ac9fe27815baa`.
UART:
`tools/hardware-logs/cubie-uart/20260610T182056Z-a733-h020-fabric-3b4060f731b1-ext4load-ttyUSB0.uart.log`,
sha256 `c0951bb0b48c42ed748b950391a617342ebf2e34649a2e61888c22bfcec71d0e`.
Patch:
`tools/kernel-patches/a733-diagnostics/3b4060f731b1-h020-fabric.patch`,
sha256 `b97038389fb69d80f20dfbb729a98bc27df0a2758cf617d43e2c96ac0ebc3022`.

Result: H020 found a real non-SDMMC delta. Vendor keeps a broad
fabric/MSI/IOMMU envelope enabled during working SD reads. Mainline matches
MBUS root, MSI-lite1, and MMC0 bus/reset, but leaves the rest disabled at the
IDMAC stall: `iommu0=0x00010004`, `msi0=0x00030000`, `msi2=0x00030000`,
`iommu1=0x00010004`, `ahb=0x01000000`, `mbus0=0x60000000`,
`mbus1=0x00000000`.

Historical follow-up was H021: enable only the missing MSI-lite/IOMMU fabric
subset in a lab-only diagnostic before the forced CMD18 IDMA launch. That test
is now completed; see H021/H022 below.

## 2026-06-10 H021/H022 Queue Update

H021 head: `d86d9defd93e` (`mmc: test A733 MSI IOMMU fabric subset`).
Artifact:
`/srv/projects/kernel-work/outgoing/a733-h021-msi-iommu-d86d9defd93e-20260610T182949Z`.
UART:
`tools/hardware-logs/cubie-uart/20260610T183153Z-a733-h021-msi-iommu-d86d9defd93e-ext4load-ttyUSB0.uart.log`,
sha256 `a7ee99006a12ac4bbb6cb855ff8fd72ea9c3d18e27b201d1c1729e395c3547d5`.
Patch:
`tools/kernel-patches/a733-diagnostics/d86d9defd93e-h021-msi-iommu-fabric.patch`,
sha256 `a3b05b0f7804bb87c8a392ab345e505b0cc268a9745e44711946d9e6ca5ad996`.

Result: H021 failed usefully. The safe MSI/IOMMU subset writes landed and
persisted, but the forced CMD18 still stalled with descriptor checksum
`0x0abf1f04` unchanged, `OWN` set, `CHDA=DLBA=0x3f600000`, `CBDA=0`,
`IDST=0x4000`, `CBCR=0x400`, and `BBCR=0`.

Next queue item: H022. Trace the vendor SDMMC IDMAC/fabric path from source and
logs before another behavior patch. Do not broaden from H021 into GMAC,
display, VPU, GPU, CE, DMA, or unrelated fabric bits without source evidence.
