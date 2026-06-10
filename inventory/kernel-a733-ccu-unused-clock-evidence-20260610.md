# A733 CCU Unused-Clock Evidence Note

Date: 2026-06-10

Purpose: capture the narrow runtime blocker for the Radxa Cubie A7S review-v2
kernel proof, without rewriting or submitting kernel patches yet.

## Current Conclusion

The review-v2 kernel/DTB boots to SDMMC/root only with lab-only
`clk_ignore_unused`. Without that bootarg, it starts Linux and UART0, then
stalls during `clk_disable_unused()` before `sunxi-mmc 4020000.mmc`.

This is not the old rootfs/UUID problem, not MMC DT wiring, and not a reason to
add vendor U-Boot compatibility properties to DTS. The strongest evidence points
to unsafe gate-status reads while unused-clock cleanup walks R-CCU and RTC CCU
clocks for peripherals absent from the minimal DTS.

Follow-up diagnostic result: removing the absent `ext-osc32k-gate` from the
A733 RTC CCU registration path, on top of the existing R-CCU and RTC DCXO
unused-cleanup skips, gets past the previous RTC CCU stop and reaches MMC probe.
It does not yet mount root: MMC then reports repeated
`sunxi-mmc 4020000.mmc: fatal err update clk timeout` messages and waits for
the PARTUUID root device. This confirms `ext-osc32k-gate` was a real blocker in
the cleanup walk, but not the final runtime issue.

Next diagnostic result: `pd_ignore_unused` does not fix the MMC timeout. Keeping
the RTC/root oscillator clocks prepared during unused-clock cleanup does fix the
MMC update-clock timeout: `sunxi-mmc 4020000.mmc` initializes without the fatal
update-clock error. The board still waits for the PARTUUID root device because
no `mmcblk0` line appears yet. This narrows the next blocker to MMC card
enumeration after the clock-update timeout is removed.

Latest diagnostic result: stacking the vendor SDMMC0 reset-cell test with
lab-only critical storage fabric clocks (`ahb-store`, `mbus-store`, and
`mbus-msi-lite0`) restores SDMMC0 register access and advances card
enumeration through CMD0, CMD8, ACMD41, CMD2, CMD3, CMD9, CMD7, and CMD55. The
current stop is ACMD51/SCR, the first data transfer. Data/DMA tracing shows the
request is mapped, the internal DMA descriptor is prepared, and `DMAC`/`IDIE`
are armed, but no later data/DMA completion is observed in the captured tail.
The next blocker is therefore the SDMMC data/DMA path after basic command
enumeration, still within lab-only CCU/reset/storage-fabric diagnostics and not
board DTS feature expansion.

## External Context Rechecked

- A733 CCU/PRCM active reference remains Junhui Liu's RFC series:
  `20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech`.
- A733 pinctrl active reference remains Andre Przywara's RFC series:
  `20250821004232.8134-1-andre.przywara@arm.com`.
- Search found no obvious newer A733 CCU/PRCM or A733 pinctrl v2 superseding
  those series.

## Repro Shape

Use Strix as operator. Keep Cubie1 excluded.

- kernel tree on Strix: `/srv/projects/a733-prereq-stack-current`
- branch: `codex/a733-cubie-review-v2`
- head: `d9aa2e15caae`
- RAM-only U-Boot workaround: `setenv drm_debug 1`
- corrected root: `root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e`
- lab-only proof bootarg: `clk_ignore_unused`

Passing proof with `clk_ignore_unused`:

```text
tools/hardware-logs/cubie-uart/20260609T195725Z-a733-review-v2-d9aa2e15caae-clkignore-ro-proof-autopower-full-ttyUSB0.uart.log
sha256: 728fedf08a63775c9cdfadcc5151fadf2332677111d1f3addb23e049afb5d492
```

## Failure Progression

The stop moved as follows when increasingly narrow lab-only diagnostics were
tested:

```text
normal corrected-root boot
  -> clk: Disabling unused clocks
  -> no sunxi-mmc

trace/critical-clock tests
  -> bus-r-i2c2
  -> bus-r-uart1
  -> r-timer0

skip R-CCU unused cleanup
  -> hosc-ufs

skip only hosc-ufs
  -> hosc-hdmi

skip all RTC DCXO siblings
  -> ext-osc32k-gate

skip all RTC DCXO siblings and remove absent ext-osc32k-gate from RTC CCU
  -> unused-clock cleanup completes
  -> sunxi-mmc probe starts
  -> mmc update-clock timeout, no mmcblk/root yet

add pd_ignore_unused
  -> genpd reports "Not disabling unused power domains"
  -> same mmc update-clock timeout

skip root unprepare for iosc/osc19M/osc24M/osc26M
  -> no mmc update-clock timeout
  -> sunxi-mmc initializes
  -> still no mmcblk0/root

add vendor SDMMC0 reset cell 35
  -> SDMMC0 readback changes from all zero to 0x20000000
  -> still no write stick/CMD0 completion

keep ahb-store/mbus-store/mbus-msi-lite0 critical
  -> SDMMC0 register access works
  -> command enumeration reaches selected card
  -> first data transfer ACMD51/SCR stalls

trace data/DMA path
  -> ACMD51 request mapped, IDMA descriptor prepared, DMA armed
  -> no data/DMA completion in captured tail
```

Key proof logs:

```text
R-I2C critical:
tools/hardware-logs/cubie-uart/20260609T234059Z-a733-ri2ccrit-8072e669de6b-direct-ctrlc-prompt-ttyUSB0.uart.log
sha256: 6d3c58827f00b95d3c8726c4dda474a9a2db183e13dfebdd82276eda3b783d7b

R-bus critical:
tools/hardware-logs/cubie-uart/20260609T235232Z-a733-rbuscrit-a422a00f4750-direct-cleanprompt-ttyUSB0.uart.log
sha256: 16f6a6ffc5776d983f9693dbb4cacc2c3e3bdf12f7c71d5a58e7284ffbba65d4

R-CCU skip:
tools/hardware-logs/cubie-uart/20260610T000219Z-a733-rccu-skipunused-9b16e23b47c8-direct-ctrlc-prompt-ttyUSB0.uart.log
sha256: 3eee44b58ba5e8d8dad524c0ece692cf3a173de8fffcfa885d37bc2455a56285

RTC DCXO hosc-ufs trace:
tools/hardware-logs/cubie-uart/20260610T002234Z-a733-rccu-skip-16c-c5dfcb904bad-direct-retry-ttyUSB0.uart.log
sha256: 8e6d4df5eb8561a01eaba686d31f72e32faa2d76c7f609d6d0ece5c57b3cd88e

RTC DCXO hosc-hdmi sibling:
tools/hardware-logs/cubie-uart/20260610T003234Z-a733-rccu-skip-hoscufs-f651139793f7-direct-ttyUSB0.uart.log
sha256: ce97a16be401b40a4e75618740e94ce6964caccb7034faf466f793e60baefc03

RTC ahb-enable falsification:
tools/hardware-logs/cubie-uart/20260610T004850Z-a733-rtc-ahb-7e67931f4380-direct-ttyUSB0.uart.log
sha256: 124299f80226cdc11a5fbac8d1f35c16dafdd57f7039229e4d355feffd7e1bce

RTC DCXO-wide skip to ext-osc32k-gate:
tools/hardware-logs/cubie-uart/20260610T005439Z-a733-rccu-dcxo-skip-9bc09ace48d2-direct-ttyUSB0.uart.log
sha256: 4817f4dfb2b323843054dc064dd3a9f5c8c89cde10f32cf9ede10cf02a2fbd1f

RTC ext-osc32k orphan diagnostic:
tools/hardware-logs/cubie-uart/20260610T012308Z-a733-rtc-extosc-orphan-98d5978ddd56-extlinux2-ttyUSB0.uart.log
sha256: 5fc2fb7ad1833fb8d2caf739eadf68638229f1f4432bf5e33f2c08d94ec7774f

pd_ignore_unused falsification:
tools/hardware-logs/cubie-uart/20260610T022155Z-a733-rtc-extosc-orphan-pdignore-98d5978ddd56-extlinux2-ttyUSB0.uart.log
sha256: 007f2cabd5c85db2e0096a8deb89707e4f796a8b3b4cf846c45987ba7adb4971

RTC/root oscillator unprepare skip:
tools/hardware-logs/cubie-uart/20260610T022835Z-a733-osc-keep-5e6b35b07c67-extlinux2-ttyUSB0.uart.log
sha256: eb3e495db4491922288494ff7f386c5106fa59b4ffc52350ff9a06a3f10cce59

SDMMC0 reset-cell 35 diagnostic:
tools/hardware-logs/cubie-uart/20260610T033330Z-a733-mmc-resetcell-0c658caf3956-ext4load-ttyUSB0.uart.log
sha256: 9d2063d6bcd0a1b9d0cacd05fa5d61fa84190648c5c02d525e53fdf726792a24

SDMMC0 storage-fabric critical diagnostic:
tools/hardware-logs/cubie-uart/20260610T034137Z-a733-mmc-storecrit-d628a2e9120f-ext4load-ttyUSB0.uart.log
sha256: 9fb5580652c37be69d8efdc9c9f71414c473ea9717d6e5cb8499fd656b2eb129

SDMMC0 data/DMA trace diagnostic:
tools/hardware-logs/cubie-uart/20260610T035245Z-a733-mmc-datadma-fdfcd44d0f78-ext4load-ttyUSB0.uart.log
sha256: cc43ef68c7037bfc4d0eb5d696ed8237adc63bb0b4103d7dc7fc20e0ba01c41b
```

## Source Findings

Local source on Strix:

```text
/srv/projects/a733-prereq-stack-current
branch: codex/a733-cubie-review-v2
head: d9aa2e15caae
```

A733 R-CCU gates exposed by the walk:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733-r.c
bus-r-uart1: 0x18c BIT(1)
bus-r-i2c2:  0x19c BIT(2)
r-timer0:    0x100 mux/div/gate
```

A733 RTC CCU gates exposed by the walk:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733-rtc.c
ext-osc32k-gate: 0x0 BIT(4), parent name "ext-osc32k"
hosc-ufs:        DCXO_GATING_REG 0x16c BIT(0)
hosc-hdmi:       DCXO_GATING_REG 0x16c BIT(1)
hosc-serdes0:    DCXO_GATING_REG 0x16c BIT(4)
hosc-serdes1:    DCXO_GATING_REG 0x16c BIT(5)
```

The A733 DTS currently supplies five RTC clocks:

```text
clock-names = "bus", "osc19M", "osc24M", "osc26M", "ahb";
```

The binding allows an optional sixth `ext-osc32k`, but the minimal Cubie A7S DTS
does not provide it. Enabling the optional RTC `ahb` clock in `rtc-sun6i` was
tested and did not solve the stall.

Important contrast: generic `ccu-sun6i-rtc.c` has explicit logic to not register
`ext-osc32k-gate` when there is no external 32 kHz parent. The A733 RTC CCU
driver currently registers `ext-osc32k-gate` directly as part of its clock list.
That matched the prior runtime stop and remains a concrete review target. The
diagnostic branch `codex/a733-diag-rtc-extosc-orphan`, commit `98d5978ddd56`,
removes that absent gate from registration and proves the boot advances to MMC.

The new stop happens after unused-clock cleanup completes. The tail shows root
oscillator cleanup, then PM genpd cleanup, then MMC clock-update timeouts:

```text
clk-unused: unprepare-root name=iosc
clk-unused: unprepare-root name=osc26M
clk-unused: unprepare-root name=osc24M
clk-unused: unprepare-root name=osc19M
PM: genpd: Disabling unused power domains
sunxi-mmc 4020000.mmc: fatal err update clk timeout
sunxi-mmc 4020000.mmc: initialized, max. request size: 2048 KB, uses new timings mode
Waiting for root device PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e...
```

Commit `5e6b35b07c67` adds a lab-only skip for unpreparing `iosc`, `osc19M`,
`osc24M`, and `osc26M`. That removes the update-clock timeout:

```text
clk-unused: diag-skip-a733-osc-unprepare name=iosc
clk-unused: diag-skip-a733-osc-unprepare name=osc26M
clk-unused: diag-skip-a733-osc-unprepare name=osc24M
clk-unused: diag-skip-a733-osc-unprepare name=osc19M
sunxi-mmc 4020000.mmc: initialized, max. request size: 2048 KB, uses new timings mode
Waiting for root device PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e...
```

Vendor DTB comparison then exposed that SDMMC0 uses reset cell `0x23` while the
local RFC header names `RST_BUS_MMC0` as `0x24`, with `0x23` assigned to NAND.
Using reset cell 35 is only a lab diagnostic, but it changes the SDMMC0
readback pattern and is now part of the evidence that the local reset/provider
mapping needs RFC comparison.

Commit `d628a2e9120f` keeps the storage fabric gates critical for diagnosis:

```text
clk: diag-a733-store-critical ahb-store
clk: diag-a733-store-critical mbus-store
clk: diag-a733-store-critical mbus-msi-lite0
sunxi-mmc 4020000.mmc: diag finalize opcode=7 ...
sunxi-mmc 4020000.mmc: diag request opcode=51 ... data=1
```

Commit `fdfcd44d0f78` traces that first data transfer:

```text
sunxi-mmc 4020000.mmc: diag request-data opcode=51 flags=0x200 blksz=8 blocks=1 sg_len=1 stop=0
sunxi-mmc 4020000.mmc: diag map_dma flags=0x200 blksz=8 blocks=1 sg_len=1 dma_len=1 dir=2
sunxi-mmc 4020000.mmc: diag idma_des sg_len=1 ... des0=0x8000003c size=0x00000008 ...
sunxi-mmc 4020000.mmc: diag regs dma-exit ... dmac=0x00000282 ... idie=0x00000002 blksz=0x00000008 bcntr=0x00000008
```

No completion follows in the captured tail. The safest next runtime proof is a
single-purpose PIO/no-IDMA diagnostic for ACMD51/SCR, or an equally narrow
check of the SDMMC IDMA address/descriptor programming against A733 vendor
register behavior. Do not broaden into Ethernet, VPU, display, or public DTS
changes.

## Questions For CCU/RFC Review

1. Should the A733 RTC CCU mirror the generic RTC CCU orphan handling for
   `ext-osc32k-gate` when the optional `ext-osc32k` parent is absent?
2. Are the A733 DCXO sibling gates safe to expose as normal gates before UFS,
   HDMI/display, and SerDes consumers exist, or should their status path avoid
   MMIO reads during unused-clock cleanup?
3. Do the R-CCU gates need a parent/enable/reset sequencing change before
   `is_enabled` can read their gate registers safely?
4. Is the vendor BSP `clk-init-gate = <0x01>` hinting at initial gate policy
   that belongs in the CCU provider rather than board DTS?
5. After the RTC CCU stops are bypassed, which MMC0 clock parent or reset path
   is lost during unused-clock cleanup, causing the post-cleanup
   `fatal err update clk timeout`?
6. Why does keeping RTC/root oscillators prepared remove the MMC update-clock
   timeout, and why does card/block enumeration still not follow?

## MMC Trace Attempt

Strix diagnostic commit `b839d38b3a6c` adds lab-only traces around
`mmc_start_host()`, `mmc_rescan()`, `sunxi_mmc_set_ios()`,
`sunxi_mmc_set_clk()`, `sunxi_mmc_request()`, and `mmc_add_host()`.

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-mmc-trace-b839d38b3a6c-20260610T023652Z
Image sha256: 933ade6655bc135ffb2c68578bdc2b99b73ec6144595d92a36f43627e6f401b4
DTB sha256:   6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
```

Two attempted UART captures are invalid because they booted the vendor kernel
instead of the trace Image:

```text
tools/hardware-logs/cubie-uart/20260610T023725Z-a733-mmc-trace-b839d38b3a6c-extlinux2-ttyUSB0.uart.log
sha256: 01ef6d694540d488fc35b2f5568c3ef22d8312d5e763c5a5900ec80d0412748b

tools/hardware-logs/cubie-uart/20260610T024212Z-a733-mmc-trace-b839d38b3a6c-default-ttyUSB0.uart.log
sha256: 02963046895722418ce191fe10968ff64aa37874fce51b8f855c70ca7aabb5bb
```

The board was restored to the vendor-only extlinux file after these invalid
captures. Next runtime attempt should avoid ambiguous extlinux menu selection,
preferably by reusing the known-good direct U-Boot load flow only after `mmc`
partition visibility is confirmed at the prompt.

Valid direct U-Boot trace:

```text
tools/hardware-logs/cubie-uart/20260610T024831Z-a733-mmc-trace-b839d38b3a6c-direct-ttyUSB0.uart.log
sha256: 132d87856d41b03941e192b2749ff8ef1096871b8631262196bd14873c49432c
```

This boot used direct U-Boot loading after `part list mmc 0` succeeded, so it is
a valid trace of the staged Image/DTB:

```text
Linux version 7.1.0-rc5-00193-gb839d38b3a6c
Machine model: Radxa Cubie A7S
sunxi-mmc 4020000.mmc: diag add_host done caps=0x180f caps2=0x480000 f_min=400000 f_max=200000000 removable=1 needs_poll=0
mmc0: diag rescan entry disable=0 entered=0 bus_ops=0000000000000000 caps=0x180f caps2=0x480000 f_min=400000 f_max=200000000
sunxi-mmc 4020000.mmc: initialized, max. request size: 2048 KB, uses new timings mode
mmc0: diag rescan try_freq=400000
sunxi-mmc 4020000.mmc: diag set_ios clock=400000 power=2 bus_width=0 timing=0 signal_voltage=0
sunxi-mmc 4020000.mmc: diag set_clk clock=400000 power=2 bus_width=0 timing=0
sunxi-mmc 4020000.mmc: diag request opcode=0 arg=0x00000000 flags=0xc0 data=0 clock=400000 ferror=0
```

There is no request completion, no later CMD8/ACMD41/CMD1 attempt, and no
`mmcblk0`. The next blocker is therefore first MMC command completion or IRQ
delivery after CMD0, not host-add scheduling, not card-detect polling, and not
the prior update-clock timeout.

Next trace should instrument `sunxi_mmc_irq()` and
`sunxi_mmc_finalize_request()` for raw interrupt/status registers after CMD0.

## MMC IRQ/Status Trace

Strix diagnostic commit `a52ea49def77` adds lab-only traces in
`sunxi_mmc_irq()`, `sunxi_mmc_finalize_request()`, and a short post-CMD0 poll
of raw MMC status registers.

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-mmc-irqtrace-a52ea49def77-20260610T025633Z
Image sha256: f6b7c965ac27caac727c8efd329f408f36f9a885b84fa61cc4ada8b33f4a46a6
DTB sha256:   6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
```

The first direct-boot attempt is invalid as a kernel result because U-Boot did
not load a valid DTB before `booti` and then hung in vendor FDT fixups:

```text
tools/hardware-logs/cubie-uart/20260610T025837Z-a733-mmc-irqtrace-a52ea49def77-direct-ttyUSB0.uart.log
sha256: 15ff7a0ed922b28b1065673a06fbbb56eb845ff36863fe7a30df180c0f7fa789
```

The valid retry used stricter direct U-Boot checks, including `part list mmc 0`,
Image load verification, DTB load verification, `fdt addr`, and `fdt header`
before booting:

```text
tools/hardware-logs/cubie-uart/20260610T030303Z-a733-mmc-irqtrace-a52ea49def77-direct-v2-ttyUSB0.uart.log
sha256: 552cb242bbbc05baf84374c2425c310908e82244e7d762406d8c4ca1c7b79ed9
```

Key lines:

```text
Linux version 7.1.0-rc5-00194-ga52ea49def77
Machine model: Radxa Cubie A7S
mmc0: diag start_host caps=0x180f caps2=0x480000 power_up=1 f_min=400000 f_max=200000000
sunxi-mmc 4020000.mmc: diag add_host done caps=0x180f caps2=0x480000 f_min=400000 f_max=200000000 removable=1 needs_poll=0
mmc0: diag rescan try_freq=400000
sunxi-mmc 4020000.mmc: diag request opcode=0 arg=0x00000000 flags=0xc0 data=0 clock=400000 ferror=0
sunxi-mmc 4020000.mmc: diag post-cmd0 poll0 rint=0x00000000 mista=0x00000000 stas=0x00000000 cmdr=0x00000000 imask=0x00000000
sunxi-mmc 4020000.mmc: diag post-cmd0 poll4 rint=0x00000000 mista=0x00000000 stas=0x00000000 cmdr=0x00000000 imask=0x00000000
```

No `diag irq` and no `diag finalize` lines appear. This makes pure interrupt
routing the wrong first assumption: the controller does not expose any command
progress or completion status after CMD0 in the sampled window. The current
blocker is therefore narrower than "MMC enumeration": command launch or MMC
controller state after the oscillator/unused-clock diagnostics, before IRQ
delivery can matter.

Safest next technical step: inspect and trace the A733 SDMMC0 register state
around host reset, clock enable, `SUNXI_MMC_REG_CLKCR`, `SUNXI_MMC_REG_GCTRL`,
command issue, and any A733-specific reset/clock parent assumptions in the
CCU/RFC stack. Keep the test as a lab-only diagnostic. Do not add card-detect
GPIOs, vendor U-Boot DTS aliases, or Ethernet/VPU/display nodes to solve this.

## MMC Command-Launch Register Trace

Strix diagnostic commit `cf7b2b08344e` adds lab-only readbacks around CMD0
programming: pre-command register dump, IMASK/CARG/CMDR readbacks, and a
post-CMDR register dump.

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-mmc-cmdlaunch-cf7b2b08344e-20260610T031016Z
Image sha256: 05e9f4f2f5355ae4cac2976fabcce30aa240246f9c68f0ac363385ad6aa2be21
DTB sha256:   6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
```

Valid direct U-Boot capture:

```text
tools/hardware-logs/cubie-uart/20260610T031554Z-a733-mmc-cmdlaunch-cf7b2b08344e-ext4load-ttyUSB0.uart.log
sha256: 77fa1d38f8338243878d9d776dcaa3c844d49b6dc346b768562b042f839e4133
```

Key lines:

```text
Linux version 7.1.0-rc5-00195-gcf7b2b08344e
sunxi-mmc 4020000.mmc: diag regs cmd0-pre-lock gctrl=0x00000000 clkcr=0x00000000 width=0x00000000 cmdr=0x00000000 carg=0x00000000 imask=0x00000000 mista=0x00000000 rint=0x00000000 stas=0x00000000 ntsr=0x00000000 ftrgl=0x00000000 timeout=0x00000000
sunxi-mmc 4020000.mmc: diag cmd0 program cmd_val=0x80008000 imask=0x0000bbc6 sdio_imask=0x00000000 wait_dma=0 use_new_timings=1 actual_clock=400000
sunxi-mmc 4020000.mmc: diag cmd0 imask-readback=0x00000000
sunxi-mmc 4020000.mmc: diag cmd0 carg-readback=0x00000000
sunxi-mmc 4020000.mmc: diag cmd0 cmdr-readback=0x00000000
sunxi-mmc 4020000.mmc: diag regs cmd0-post-cmdr gctrl=0x00000000 clkcr=0x00000000 width=0x00000000 cmdr=0x00000000 carg=0x00000000 imask=0x00000000 mista=0x00000000 rint=0x00000000 stas=0x00000000 ntsr=0x00000000 ftrgl=0x00000000 timeout=0x00000000
```

This is stronger than the prior IRQ trace: the SDMMC register window reads as
all zero before CMD0 and immediately after writes that should be visible. That
includes initialization registers such as `TMOUT`, `FTRGL`, `GCTRL`, and
`CLKCR`. The current blocker is therefore likely SDMMC0 bus/reset/clock-domain
accessibility after the lab-only CCU cleanup skips, not card detection, command
timing, or interrupt delivery.

Next responsible diagnostic: trace SDMMC0 probe/init readbacks immediately
after reset deassert, after `sunxi_mmc_init_host()`, and before/after genpd
unused-domain cleanup, then compare the SDMMC0 bus gate/reset and any pmdomain
assignment against Junhui Liu's A733 CCU/PRCM and pmdomain RFCs. Keep this as
runtime evidence only; do not change the upstream DTS slice yet.

## MMC Init/Runtime-PM Trace

Strix diagnostic commit `b9e4692d4d5c` traces SDMMC0 enable, reset,
`sunxi_mmc_init_host()`, runtime-PM setup, and runtime suspend/resume.

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-mmc-initpm-b9e4692d4d5c-20260610T032233Z
Image sha256: a1aa199612c46fe3e5f9e8e6308df5e88bc38705052cbc66d92cdeeb40374242
DTB sha256:   6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
```

Valid direct U-Boot capture:

```text
tools/hardware-logs/cubie-uart/20260610T032435Z-a733-mmc-initpm-b9e4692d4d5c-ext4load-ttyUSB0.uart.log
sha256: ca55c6f70ef7750e0ac86fcc4637b6dd1f8f31a5534611681453f47f9e6b60ea
```

Key lines:

```text
sunxi-mmc 4020000.mmc: diag enable ahb on
sunxi-mmc 4020000.mmc: diag enable mmc on
sunxi-mmc 4020000.mmc: diag enable output on
sunxi-mmc 4020000.mmc: diag enable sample on
sunxi-mmc 4020000.mmc: diag reset_host done gctrl=0x00000000 clkcr=0x00000000 rint=0x00000000
sunxi-mmc 4020000.mmc: diag regs enable-exit gctrl=0x00000000 clkcr=0x00000000 width=0x00000000 cmdr=0x00000000 carg=0x00000000 imask=0x00000000 mista=0x00000000 rint=0x00000000 stas=0x00000000 ntsr=0x00000000 ftrgl=0x00000000 timeout=0x00000000
sunxi-mmc 4020000.mmc: diag regs init-host-post-basic-writes gctrl=0x00000000 clkcr=0x00000000 width=0x00000000 cmdr=0x00000000 carg=0x00000000 imask=0x00000000 mista=0x00000000 rint=0x00000000 stas=0x00000000 ntsr=0x00000000 ftrgl=0x00000000 timeout=0x00000000
sunxi-mmc 4020000.mmc: diag pm_runtime enabled active=1 suspended=0
```

No runtime suspend/resume occurs before CMD0. The all-zero SDMMC0 register
window is already present immediately after the driver enables AHB/MMC/output/
sample clocks and resets the controller, and writes in `sunxi_mmc_init_host()`
do not read back. This rules out runtime autosuspend as the cause and points
back to SDMMC0 reset, bus gate, pmdomain, or register base/compatible
assumptions in the A733 prerequisite stack.

Next responsible diagnostic: compare the current SDMMC0 DTSI clock/reset cells
and provider IDs against Junhui Liu's A733 CCU/PRCM and pmdomain RFCs and the
vendor DTB; if those match, trace the CCU reset/gate writes for `bus-mmc0` and
`mmc0` during `sunxi_mmc_enable()`.

## SDMMC0 Reset-Cell Comparison And Falsification

Local RFC-stack DTSI:

```text
mmc0: mmc@4020000
reg = <0x04020000 0x1000>
clocks = <&ccu CLK_BUS_MMC0>, <&ccu CLK_MMC0>
resets = <&ccu RST_BUS_MMC0>
```

Local A733 CCU definitions:

```text
CLK_MMC0      = 143 -> mmc0 at CCU offset 0xd00
CLK_BUS_MMC0  = 147 -> bus-mmc0 at CCU offset 0xd0c bit 0
RST_BUS_MMC0  = 36  -> reset at CCU offset 0xd0c bit 16
```

Vendor DTB comparison:

```text
sdmmc@4020000
reg = <0x00 0x4020000 0x00 0x1000>
clocks = <osc24m, pll_periph, pll_periph_2, mmc, ahb, mmc_store, mmc_mbus, mmc_msi_lite>
resets = <ccu 0x23>
```

The vendor reset cell for SDMMC0 is `0x23` (35 decimal), while the current
local binding names `RST_BUS_MMC0` as 36. Vendor SDMMC1/2/3 are `0x24`,
`0x25`, and `0x26`, which also suggests the MMC reset cells are one lower than
the local header names.

Strix diagnostic commit `0c658caf3956` tests vendor reset cell `0x23` for
SDMMC0 in the lab DTS only.

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-mmc-resetcell-0c658caf3956-20260610T033130Z
Image sha256: c1284f474f4fc8ba28497efdd12467e28e4efcecdd4bb62835c5e154e68c7cac
DTB sha256:   ed3cc474fe72c25c3e0cb96a3fc9fa243c1c01631bf4e651031d3cba8500708b
```

Valid direct U-Boot capture:

```text
tools/hardware-logs/cubie-uart/20260610T033330Z-a733-mmc-resetcell-0c658caf3956-ext4load-ttyUSB0.uart.log
sha256: 9d2063d6bcd0a1b9d0cacd05fa5d61fa84190648c5c02d525e53fdf726792a24
```

Result:

```text
baseline reset cell 36 -> all SDMMC0 register readbacks are 0x00000000
vendor reset cell 35   -> all SDMMC0 register readbacks are 0x20000000
```

This does not fix SDMMC0: writes still do not read back as programmed, CMD0
does not complete, and no block device appears. It does prove the reset cell is
not a harmless detail. The next best target is the A733 CCU/reset provider
mapping for the NAND/MMC reset block and the missing vendor storage fabric
clocks (`mmc_store`, `mmc_mbus`, `mmc_msi_lite`), not SD card detect or
interrupt delivery.

## Storage-Fabric Clock Falsification

Vendor SDMMC0 lists extra storage fabric clocks:

```text
clock-names = "osc24m", "pll_periph", "pll_periph_2", "mmc", "ahb",
              "mmc_store", "mmc_mbus", "mmc_msi_lite";
```

Mainline `sunxi-mmc` only consumes `ahb` and `mmc`, so Strix diagnostic commit
`d628a2e9120f` keeps the closest CCU fabric gates critical in the lab CCU:

```text
ahb-store
mbus-store
mbus-msi-lite0
```

This test is stacked on the vendor SDMMC0 reset cell `0x23` diagnostic.

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-mmc-storecrit-d628a2e9120f-20260610T033937Z
Image sha256: 0004cb15fefb8789669595c4d2039dc35bffbaa2f764b76472ae07e8e2c2df64
DTB sha256:   ed3cc474fe72c25c3e0cb96a3fc9fa243c1c01631bf4e651031d3cba8500708b
```

Valid direct U-Boot capture:

```text
tools/hardware-logs/cubie-uart/20260610T034137Z-a733-mmc-storecrit-d628a2e9120f-ext4load-ttyUSB0.uart.log
sha256: 9fb5580652c37be69d8efdc9c9f71414c473ea9717d6e5cb8499fd656b2eb129
```

Result: SDMMC0 register access becomes sane and command progress resumes:

```text
cmd0 cmdr-readback=0x80008000
cmd0-post-cmdr ... imask=0x0000bbc6 mista=0x00000004 rint=0x00000004
diag finalize opcode=0
diag finalize opcode=8
diag finalize opcode=55
diag finalize opcode=41
diag finalize opcode=2
diag finalize opcode=3
diag finalize opcode=9
diag finalize opcode=7
diag request opcode=51 ... data=1
```

This is the first proof that the previous all-zero/all-`0x20000000` SDMMC0
window was caused by missing storage fabric enablement plus reset mapping, not
the SD card, pinctrl, command timing, or interrupt delivery. The new blocker is
the first data transfer, ACMD51/SCR read, after command-only enumeration has
advanced.

Next responsible diagnostic: trace the data path for opcode 51, especially
IDMA setup, descriptor address, `GCTRL` DMA enable/reset bits, `IDST`, `IDIE`,
`DMAC`, `DLBA`, FIFO/status, and whether DMA or PIO mode is appropriate for the
first minimal proof. Keep the storage-fabric and reset-cell changes lab-only
until reconciled with Junhui Liu's A733 CCU/PRCM and any pmdomain/storage
fabric RFC direction.

## Guardrails

- Do not add vendor-only U-Boot properties, paths, aliases, or compatible
  strings to upstream DTS.
- Do not add Ethernet, VPU, display, USB-C, PCIe, or wireless nodes to solve
  this boot proof.
- Do not send the local CCU/pinctrl scaffolding as an independent upstream
  series while Junhui/Andre RFCs remain active.
- Keep `clk_ignore_unused` as a lab proof only, not an upstream solution.
