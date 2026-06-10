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
