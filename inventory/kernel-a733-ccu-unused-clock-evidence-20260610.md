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

Follow-up ACMD51 polling confirms the controller clears the command start bit
and sets raw `COMMAND_DONE`, but never sets raw `DATA_OVER`; masked status stays
zero because ADTC reads do not mask `COMMAND_DONE`, and IDMA status remains
`0x00004000`. This narrows the failure to the data phase not starting or not
finishing after command acceptance, rather than a missed receive-DMA interrupt
alone.

An unshifted IDMA address diagnostic falsified the simplest descriptor-address
hypothesis. Changing the D1-compatible `idma_des_shift` from 2 to 0 changed
`DLBA` from `0x10c00000` to `0x43000000` and descriptor buffer pointers from
shifted to unshifted DMA addresses, but ACMD51 still stopped with
`RINTR=0x00000004`, `MISTA=0x00000000`, `IDST=0x00004000`, and no `DATA_OVER`.

Removing `SDXC_WAIT_PRE_OVER` for ACMD51 was also falsified. The command value
changed from `0x2373` to `0x0373`, proving the variant was active, but the same
raw `COMMAND_DONE` only / no `DATA_OVER` state remained.

SCR-only PIO mode is the first data-path breakthrough. Commit `09bac31de352`
skips IDMA only for the 8-byte ACMD51/SCR read, sets AHB/FIFO access, and polls
the FIFO. ACMD51 then raises `DATA_OVER`, the IRQ finalizes the request, and
FIFO reads return non-zero data. The card init still fails because the
diagnostic repeatedly peeks the FIFO and corrupts the SCR consumed by the MMC
core (`unrecognised SCR structure version 5`). This proves the SD command/data
phase works without IDMA; the remaining blocker is the A733 SDMMC IDMA path or
the driver's IDMA setup for this controller.

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

poll ACMD51 after command launch
  -> RINTR=0x00000004, MISTA=0x00000000, IDST=0x00004000
  -> no DATA_OVER while CMDR start bit is clear

force idma_des_shift=0
  -> DLBA and descriptor buffer addresses become unshifted
  -> ACMD51 failure is unchanged

skip WAIT_PRE_OVER for ACMD51
  -> CMDR changes from 0x2373 to 0x0373
  -> ACMD51 failure is unchanged

SCR-only PIO diagnostic
  -> DATA_OVER appears
  -> FIFO returns non-zero words
  -> MMC core reaches SCR parse, then fails due diagnostic FIFO peeking
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

SDMMC0 ACMD51 post-launch poll diagnostic:
tools/hardware-logs/cubie-uart/20260610T040154Z-a733-acmd51-poll-ae9a05e1c4fc-ext4load-ttyUSB0.uart.log
sha256: 3666cffc6a3b45d0e0395fb244cca1e92e4048aaedad34eed71ab5fc6c213563

SDMMC0 unshifted IDMA address diagnostic:
tools/hardware-logs/cubie-uart/20260610T040952Z-a733-idma-shift0-5086bbd04ed8-ext4load-ttyUSB0.uart.log
sha256: 2ca936fcda1b5cbf3c5b2deb8db876c91123bff2586ebba504bf91ff4a45bc80

SDMMC0 ACMD51 no-WAIT_PRE_OVER diagnostic:
tools/hardware-logs/cubie-uart/20260610T041718Z-a733-acmd51-nowait-29a376421fd7-ext4load-ttyUSB0.uart.log
sha256: 95d24c65563d8950680359a7a6faccd1ce97be261eb700c20222006357e19601

SDMMC0 ACMD51 SCR-only PIO diagnostic:
tools/hardware-logs/cubie-uart/20260610T042558Z-a733-acmd51-pio-09bac31de352-ext4load-ttyUSB0.uart.log
sha256: 08bd631ec13c5245290a319e99011708970508fdf87b241a5af0f305bdf3696d
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
single-purpose check of the ACMD51 data-phase prerequisites: compare the A733
vendor command value, FIFO/watermark, GCTRL access mode, IDMA status bit
meaning, and descriptor/address programming for SCR reads. A PIO/no-IDMA
diagnostic is still useful, but the poll result says the problem is earlier
than receive-DMA completion. Do not broaden into Ethernet, VPU, display, or
public DTS changes.

Commit `ae9a05e1c4fc` adds the ACMD51 poll:

```text
diag acmd51 cmdr-readback=0x80002373 wait_dma=1
diag regs acmd51-post-cmdr ... cmdr=0x00002373 imask=0x0000bbca mista=0x00000000 rint=0x00000004 idst=0x00004000 ...
diag post-acmd51 poll19 rint=0x00000004 mista=0x00000000 idst=0x00004000 idie=0x00000002 dmac=0x00000282 stas=0x00059902 cmdr=0x00002373 imask=0x0000bbca
```

Commit `5086bbd04ed8` changes `idma_des_shift` to 0 for diagnosis:

```text
diag regs dma-entry ... dlba=0x43000000 ...
diag idma_des ... sg_dma=0x0000000043000000 ... buf=0xfd800000 ...
diag post-acmd51 poll19 rint=0x00000004 mista=0x00000000 idst=0x00004000 ...
```

This means the next useful diagnostic should not be another address-shift
variant.

Commit `29a376421fd7` restores shift 2 and skips `SDXC_WAIT_PRE_OVER` only for
ACMD51:

```text
diag acmd51 skip WAIT_PRE_OVER
diag acmd51 cmdr-readback=0x80000373 wait_dma=1
diag regs acmd51-post-cmdr ... cmdr=0x00000373 ... rint=0x00000004 idst=0x00004000 ...
diag post-acmd51 poll19 rint=0x00000004 mista=0x00000000 idst=0x00004000 ...
```

Prefer checking GCTRL access mode, FIFO threshold, or a controlled PIO read path
for only the 8-byte SCR request next.

Commit `09bac31de352` tests that controlled path but still uses destructive
FIFO peeks:

```text
diag acmd51 pio mode gctrl=0xa0000010
diag regs acmd51-post-cmdr ... rint=0x0000000c mista=0x00000008 dmac=0x00000200 ...
diag acmd51 fifo peek w0=0x87844502 w1=0x00000000
diag finalize opcode=51 int_sum=0x00000008 ... data=1
mmc0: unrecognised SCR structure version 5
```

The next best step is to convert the diagnostic into a non-destructive
SCR-only PIO transfer: read exactly two FIFO words once, copy them into the
request buffer with the expected byte order, mark `bytes_xfered = 8`, and let
normal enumeration continue. If that reaches `mmcblk0`, the first real fix path
is an A733-specific PIO fallback for tiny reads or a focused IDMA-controller
fix.

Commit `84f2737f1d9c` did that non-destructive SCR PIO copy. It copies the two
FIFO words into the request buffer and enumeration advances past ACMD51 into
the next data command, CMD13/SD_STATUS (`blksz=64`). The new stop is therefore
not SCR parsing; it is the same A733 SDMMC IDMA problem on the next data read.

```text
diag acmd51 pio copy w0=0x87844502 w1=0x00000000 offset=3016 len=8
diag request opcode=13 ... data=1
diag request-data opcode=13 flags=0x200 blksz=64 blocks=1
diag idma_des ... size=0x00000040 ...
```

SDMMC0 non-destructive ACMD51 PIO copy diagnostic:
tools/hardware-logs/cubie-uart/20260610T043400Z-a733-acmd51-pio-copy-84f2737f1d9c-ext4load-ttyUSB0.uart.log
sha256: 227a4d1bf13140ab34bf416fe7fc4ebb66ee11f23b73527fbbc67a6ff354efa9

Next best proof: generalize the temporary PIO fallback to all small read data
requests during enumeration, at least ACMD51 and CMD13, to see whether the card
can reach `mmcblk0`. If it does, keep the upstream path focused on IDMA setup or
a tightly justified A733 PIO fallback.

Commit `ec9dc04be75b` generalizes the diagnostic PIO path to single-block reads
up to 64 bytes. This carries enumeration through SCR, SD_STATUS, switch/status
reads, 4-bit bus-width selection, and 50 MHz clock setup. The next failure is
the first larger read, CMD48 with a 512-byte block, which falls back to IDMA and
stops in the same class of failure.

```text
diag pio copy opcode=13 words=16 ...
diag pio copy opcode=6 words=16 ...
diag set_ios clock=50000000 power=2 bus_width=2 timing=2
diag request-data opcode=48 flags=0x200 blksz=512 blocks=1
diag idma_des ... size=0x00000200 ...
```

SDMMC0 small-read PIO diagnostic:
tools/hardware-logs/cubie-uart/20260610T044153Z-a733-smallread-pio-ec9dc04be75b-ext4load-ttyUSB0.uart.log
sha256: eb55893362ff8a6d1e8c0fb9b061b4c603df533f0a587e19a151442abfce6247

The next proof should either extend the lab PIO path to 512-byte single-block
reads or focus directly on why IDMA remains stuck when larger data reads start.

Commit `1499a30e7741` extends the diagnostic PIO read path to single-block
512-byte reads. CMD48 reads now complete via PIO and return copied data. The
next stop is CMD49, a 512-byte write, which still uses IDMA.

```text
diag pio copy opcode=48 words=128 ...
diag request-data opcode=49 flags=0x100 blksz=512 blocks=1
diag idma_des ... size=0x00000200 ...
```

SDMMC0 512-byte read PIO diagnostic:
tools/hardware-logs/cubie-uart/20260610T044931Z-a733-pio512-1499a30e7741-ext4load-ttyUSB0.uart.log
sha256: 8b997124e8388384d2f5c26c9c1e613f2bc2e02ae413eec445231a383943810a

The remaining blocker is now broader than read-DMA only: A733 IDMA also blocks
the first observed write path. The next lab-only proof should either force PIO
for writes as well or skip/tame the tuning/switch write path if possible.

Commit `11c21c6b7871` adds PIO write support for single-block 512-byte
diagnostic transfers. This completes CMD49 and reaches real block-device
enumeration:

```text
diag pio write opcode=49 words=128 ...
mmc0: new high speed SDXC card at address 544c
mmcblk0: mmc0:544c USD00 117 GiB
```

The next stop is a normal block-layer multi-block read, CMD18 with 8 blocks
(`4096` bytes), which still uses IDMA and stalls.

```text
diag request-data opcode=18 flags=0x200 blksz=512 blocks=8
diag idma_des ... size=0x00001000 ...
```

SDMMC0 PIO write diagnostic:
tools/hardware-logs/cubie-uart/20260610T045812Z-a733-piowrite-11c21c6b7871-ext4load-ttyUSB0.uart.log
sha256: 12132f01a7f9246b48753ebe0c5fc667ff8662488c8f41bc8eb4ddb15f3dd939

The runtime proof has now separated SD/MMC protocol functionality from IDMA:
PIO can enumerate the card and create `mmcblk0`; IDMA remains the blocker for
normal block I/O.

Commit `b42a6fff9d87` tries to extend the diagnostic PIO path to the first
multi-block read, CMD18 (`8 x 512` bytes). It does not complete. The log shows
PIO mode is active and raw status reaches `0x24` (`COMMAND_DONE` plus
`RX_DATA_REQUEST`), but no finalizing interrupt arrives. This is expected to
need more than the single-block PIO path because CMD18 uses stop/auto-stop
completion semantics.

```text
diag request-data opcode=18 flags=0x200 blksz=512 blocks=8 stop=1
diag pio mode gctrl=0xa0000010
diag post-data poll5 rint=0x00000024 mista=0x00000000 ... cmdr=0x00003352 imask=0x0000fbc2
```

SDMMC0 multi-block PIO read diagnostic:
tools/hardware-logs/cubie-uart/20260610T050629Z-a733-pio-multiread-b42a6fff9d87-ext4load-ttyUSB0.uart.log
sha256: 569ebe5f61f34fe1a3b9ec696a8380a55155bade2c50746a1ce18f9cefaf29b8

Next best diagnostic: do not keep broadening PIO blindly. Either add a narrow
manual-stop/finalize path for CMD18 PIO, or pivot to the real issue: why IDMA
never progresses for A733 despite PIO proving register/card/data-path function.

Commit `990459ec2015` tests a narrow A733 IDMA setup change: clear
`SDXC_ACCESS_BY_AHB` before DMA and issue `SDXC_IDMAC_REFETCH_DES`, while
restoring CMD18 to the IDMA path. It still reaches `mmcblk0`, then stalls on
the first block-layer CMD18 read after descriptor setup:

```text
mmcblk0: mmc0:544c USD00 117 GiB
diag request-data opcode=18 flags=0x200 blksz=512 blocks=8 sg_len=1 stop=1
diag idma_des ... des0=0x8000003c size=0x00001000 buf=0x3f600000
diag regs dma-exit ... gctrl=0x20000030 dmac=0x00000282 idie=0x00000002
```

SDMMC0 IDMA refetch/access-mode diagnostic:
tools/hardware-logs/cubie-uart/20260610T051643Z-a733-idma-refetch-990459ec2015-ext4load-ttyUSB0.uart.log
sha256: e2879f393284e44c4a38b8181633213c5be5f7d05eac705f73a50fcee11d4089

Recovery proof:
tools/hardware-logs/cubie-uart/20260610T052447Z-cubie3-recovery-probe-ttyUSB0.uart.log
sha256: b921ddf35db7951fd4c1a796c67f10e9e0bfef94461b2b37a2e6a0eabd049da6

Conclusion: the refetch/access-mode hypothesis is falsified for the current
diagnostic stack. The blocker remains A733 SDMMC IDMA progress on normal
multi-block I/O, not card enumeration, rootfs arguments, or board DTS scope.

Commit `4365eadc01bc` tests the next narrow IDMA address variant: keep
descriptor list base shifting (`DLBA=0x10c00000`) but write the data buffer
pointer unshifted (`buf=0xfd800000`). The corrected run confirms
`unshift_buf=1` and still stalls after CMD18 descriptor setup:

```text
mmcblk0: mmc0:544c USD00 117 GiB
diag request-data opcode=18 flags=0x200 blksz=512 blocks=8 sg_len=1 stop=1
diag idma_des ... buf=0xfd800000 ... shift=2 unshift_buf=1
diag regs dma-exit ... dmac=0x00000282 dlba=0x10c00000 idie=0x00000002
```

SDMMC0 IDMA unshifted-buffer diagnostic:
tools/hardware-logs/cubie-uart/20260610T053805Z-a733-idma-unshiftbuf-4365eadc01bc-ext4load-ttyUSB0.uart.log
sha256: 155463c97aa6dbfb1c2cd1aa2c4f27fec936c37e8f3004e23c34dc1e13fed6d8

Conclusion: the mixed address hypothesis is also falsified. Address shifting
alone no longer looks like the explanation for A733 IDMA not progressing.

Commit `ab6178c3912a` adds post-command IDMA polling for data commands. On
CMD18, the controller reports command completion plus FIFO receive request, but
IDMAC never advances past descriptor-read state:

```text
diag data cmdr-readback=0x80003352 wait_dma=1 pio=0 opcode=18 blocks=8
diag regs idma-post-cmdr ... rint=0x00000024 ... idst=0x00004000
diag post-data poll11 rint=0x00000024 ... idst=0x00004000 ... dmac=0x00000282
```

SDMMC0 IDMA post-command progress diagnostic:
tools/hardware-logs/cubie-uart/20260610T054601Z-a733-idma-postcmd-ab6178c3912a-ext4load-ttyUSB0.uart.log
sha256: 53f420cf8c6bbc273b8b164e69213639c0ddf4550dac4452f542b680930fc494

Recovery proof:
tools/hardware-logs/cubie-uart/20260610T055431Z-cubie3-recovery-probe-postcmd-ttyUSB0.uart.log
sha256: 162da3d63a80d70c369483c771b8893ce6fbeeec85d36562d6242f79ff44770f

Conclusion: the command engine is issuing CMD18 and the card/controller assert
RX request, but the internal IDMAC remains in descriptor-read state. Next work
should inspect IDMAC descriptor format/control sequencing, not DTS/rootfs/card
enumeration.

Commit `c123c45fa61b` tests a single-descriptor format variant: omit the chain
bit when `sg_len == 1`, leaving FD/LD/ER/OWN set. The descriptor changes from
`des0=0x8000003c` to `des0=0x8000002c`, but the result is unchanged:

```text
diag idma_des ... des0=0x8000002c ... unshift_buf=1 no_chain=1
diag regs idma-post-cmdr ... rint=0x00000024 ... idst=0x00004000
diag post-data poll11 ... idst=0x00004000 ... dmac=0x00000282
```

SDMMC0 IDMA no-chain single-descriptor diagnostic:
tools/hardware-logs/cubie-uart/20260610T060048Z-a733-idma-nochain-c123c45fa61b-ext4load-ttyUSB0.uart.log
sha256: 9971758304337c2b87505cda37094b981c0af0003e5ce7a8ca621d1dce9b14d0

Conclusion: the single-descriptor chain-bit hypothesis is falsified.

Commit `d22345ac322c` clears `IDST` after IDMAC soft reset and before enabling
IDMAC. The new trace proves the status register starts clear, then returns to
descriptor-read state only after CMD18 launch:

```text
diag regs dma-after-idst-clear ... idst=0x00000000 dmac=0x00000200
diag regs idma-post-cmdr ... rint=0x00000024 ... idst=0x00004000
diag post-data poll11 ... idst=0x00004000 ... dmac=0x00000282
```

SDMMC0 IDMA status-clear diagnostic:
tools/hardware-logs/cubie-uart/20260610T060825Z-a733-idma-idstclear-d22345ac322c-ext4load-ttyUSB0.uart.log
sha256: be91743caccc0e4c6e29171320533e69627525681d3c6fe5a51bff61c6655d37

Conclusion: stale IDST state is not the cause; IDMAC actively enters and sticks
in descriptor-read state after CMD18 starts.

Commit `b97d2ada1e58` writes the descriptor list base unshifted
(`DLBA=0x43000000`) while keeping the unshifted buffer pointer and no-chain
single descriptor. CMD18 still enters descriptor-read state and does not
progress:

```text
diag regs dma-exit ... dlba=0x43000000 idst=0x00000000
diag regs idma-post-cmdr ... rint=0x00000024 ... dlba=0x43000000 idst=0x00004000
diag post-data poll11 ... idst=0x00004000 ... dmac=0x00000282
```

SDMMC0 IDMA unshifted-DLBA diagnostic:
tools/hardware-logs/cubie-uart/20260610T061551Z-a733-idma-unshiftdlba-b97d2ada1e58-ext4load-ttyUSB0.uart.log
sha256: 54faa0a45331a4f9f3ecbf4cc8883448536c4baf0b738c009b03d6390f45441b

Conclusion: descriptor-base shifting is not the immediate explanation for the
DESC_READ hang.

Commit `ae80052b9bbc` drops `SDXC_IDMAC_FIX_BURST`, changing the IDMAC control
readback from `DMAC=0x282` to `DMAC=0x280`. CMD18 still reaches
`RINTR=0x24`, and IDMAC still sticks in descriptor-read state:

```text
diag regs dma-exit ... dmac=0x00000280 dlba=0x43000000 idst=0x00000000
diag regs idma-post-cmdr ... rint=0x00000024 ... dmac=0x00000280 idst=0x00004000
diag post-data poll11 ... idst=0x00004000 ... dmac=0x00000280
```

SDMMC0 IDMA no-fixed-burst diagnostic:
tools/hardware-logs/cubie-uart/20260610T062319Z-a733-idma-nofixburst-ae80052b9bbc-ext4load-ttyUSB0.uart.log
sha256: f257e632ce7d67f56df6e626cda10bedd96c18ad92e55e927974af4cda92e31c

Conclusion: fixed-burst mode is not the immediate cause.

Commit `d4c41b4d2c94` also drops `SDXC_IDMAC_REFETCH_DES`, leaving only
`SDXC_IDMAC_IDMA_ON`. The runtime readback is still `DMAC=0x280` because
REFETCH is self-clearing in prior tests, and the failure is unchanged:

```text
diag regs dma-exit ... dmac=0x00000280 dlba=0x43000000 idst=0x00000000
diag regs idma-post-cmdr ... rint=0x00000024 ... dmac=0x00000280 idst=0x00004000
diag post-data poll11 ... idst=0x00004000 ... dmac=0x00000280
```

SDMMC0 IDMA no-refetch diagnostic:
tools/hardware-logs/cubie-uart/20260610T063040Z-a733-idma-norefetch-d4c41b4d2c94-ext4load-ttyUSB0.uart.log
sha256: 4c37e25e9e8ac86d3cc4f650106bbd422a7bbe8206999e4f5a3f167759fcefdb

Conclusion: explicit descriptor refetch is not the immediate cause.

Commit `99eb524a1bfa` skips setting `SDXC_DMA_RESET` in `GCTRL` before the
IDMAC soft reset. The transfer still reaches CMD18 command-done/RX-request and
IDMAC still sticks in descriptor-read state:

```text
diag skip gctrl dma reset
diag regs dma-exit ... gctrl=0x20000030 dmac=0x00000280 idst=0x00000000
diag regs idma-post-cmdr ... rint=0x00000024 ... idst=0x00004000
diag post-data poll11 ... idst=0x00004000 ... dmac=0x00000280
```

SDMMC0 IDMA no-GCTRL-DMA-reset diagnostic:
tools/hardware-logs/cubie-uart/20260610T063800Z-a733-idma-nogctrlreset-99eb524a1bfa-ext4load-ttyUSB0.uart.log
sha256: bed877b12e55c5f63db78347489f34f85a2bc4f9f264336d64099f3cd4f21026

Conclusion: the GCTRL DMA reset pulse is not the immediate cause.

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

## CMD18 IDMA Descriptor Ownership Diagnostic

Strix diagnostic commit `b5b9f2cd2cea` adds a post-stall dump of the first
IDMA descriptor after CMD18 polling. The tested artifact was:

```text
/srv/projects/kernel-work/outgoing/a733-idma-desafter-b5b9f2cd2cea-20260610T064602Z
Image sha256: 7e7b6ff654dbbb5309539c8b3bfda36cadefb241c98fffee94a75f200d645e0b
DTB sha256:   ed3cc474fe72c25c3e0cb96a3fc9fa243c1c01631bf4e651031d3cba8500708b
```

Valid direct U-Boot capture:

```text
tools/hardware-logs/cubie-uart/20260610T064840Z-a733-idma-desafter-b5b9f2cd2cea-ext4load-ttyUSB0.uart.log
sha256: 0a7abd6966e47bc562453fc6471cea1b74d73011bdac8346db6a4a8d543466c5
```

Result: the first block-layer request is still CMD18, 8 x 512 bytes, one
scatterlist entry. The command/FIFO side reaches `RINTR=0x00000024`, while
IDMAC stays in descriptor-read state with `IDST=0x00004000`. The descriptor is
unchanged after twelve polls:

```text
diag idma_des sg_len=1 ... des0=0x8000002c size=0x00001000 buf=0xfd800000 next=0x00000000
diag idma_des_after des0=0x8000002c size=0x00001000 buf=0xfd800000 next=0x00000000
```

Because the OWN bit remains set, the IDMAC does not appear to consume the
descriptor. This falsifies a post-fetch/FIFO-completion theory for the current
failure. The next responsible work is to explain why descriptor read never
completes: descriptor format/control sequencing, DMA-visible address
expectations, required storage-fabric/MBUS setup, or an A733-specific IDMAC
mode bit not represented by the D1-compatible mainline path.

Follow-up commit `298dc7dfd134` changes the descriptor publication barrier
from `wmb()` to `dma_wmb()` before enabling IDMAC. This does not change the
failure:

```text
/srv/projects/kernel-work/outgoing/a733-idma-dmawmb-298dc7dfd134-20260610T065456Z
Image sha256: 8ea655fc6d3de2fdbaed577cb533b690cfd57bc4b502f7e99467ac1b225885d5
DTB sha256:   ed3cc474fe72c25c3e0cb96a3fc9fa243c1c01631bf4e651031d3cba8500708b

tools/hardware-logs/cubie-uart/20260610T065721Z-a733-idma-dmawmb-298dc7dfd134-ext4load-ttyUSB0.uart.log
sha256: 2b8bb5e7ae23a2317219ea215b6cec24ae259b23dd9066e21675365193a8cef2

diag idma_des_after des0=0x8000002c size=0x00001000 buf=0xfb800000 next=0x00000000
```

Conclusion: a stronger descriptor write barrier alone is not the missing
piece; IDMAC still never takes ownership of the descriptor.

Low-descriptor-address attempt: commits `3efc8c1ee7a2` and `acbcd372ab16`
tried to constrain the coherent descriptor allocation with 28-bit and 30-bit
coherent DMA masks, respectively, to test whether descriptor fetch requires a
lower bus address. Both fail before descriptor allocation:

```text
sunxi-mmc 4020000.mmc: error -EIO: Failed to set low coherent DMA mask
sunxi-mmc 4020000.mmc: probe with driver sunxi-mmc failed with error -5
```

Artifacts/logs:

```text
/srv/projects/kernel-work/outgoing/a733-idma-lowdesc-3efc8c1ee7a2-20260610T070519Z
tools/hardware-logs/cubie-uart/20260610T070718Z-a733-idma-lowdesc-3efc8c1ee7a2-ext4load-ttyUSB0.uart.log
sha256: 58b6a76d8430764c4828ebd59219f57c297c139daa6aeaa3720b505281b80ab3

/srv/projects/kernel-work/outgoing/a733-idma-lowdesc30-acbcd372ab16-20260610T071030Z
tools/hardware-logs/cubie-uart/20260610T071340Z-a733-idma-lowdesc30-acbcd372ab16-ext4load-ttyUSB0.uart.log
sha256: 33048305b9f05bc404fce9eaf3fd1125f42c36929d24f4813623b88998847244
```

Conclusion: the generic coherent-mask API path is not a viable way to force a
lower descriptor address on this platform. It does not prove or disprove a
descriptor address-window problem; it only closes this particular test method.

Commit `34018de5c4c6` tests keeping `SDXC_ACCESS_BY_AHB` set while enabling
IDMA, instead of clearing it as mainline normally does. This changes `GCTRL`
at DMA launch from the previous `0x20000030` shape to `0xa0000030`, proving
the test is active.

```text
/srv/projects/kernel-work/outgoing/a733-idma-ahbaccess-34018de5c4c6-20260610T071930Z
Image sha256: a550ad58c4ebe42fb6a1b594ff22cf9c8b509280d42f6aedbb9de4366397caf7
DTB sha256:   ed3cc474fe72c25c3e0cb96a3fc9fa243c1c01631bf4e651031d3cba8500708b

tools/hardware-logs/cubie-uart/20260610T072133Z-a733-idma-ahbaccess-34018de5c4c6-ext4load-ttyUSB0.uart.log
sha256: 702f156eeedb6d899e5e42eb9d6f5df4d462be250bd576fae9fb539a8f8ee480

diag regs dma-exit ... gctrl=0xa0000030 ... dmac=0x00000280 dlba=0x43000000 idst=0x00000000
diag regs idma-post-cmdr ... rint=0x00000024 ... idst=0x00004000
diag idma_des_after des0=0x8000002c size=0x00001000 buf=0xfa800000 next=0x00000000
```

Conclusion: leaving AHB/FIFO access selected during IDMA does not make the
IDMAC consume the descriptor.

Commit `fe9a99200ce0` widens the diagnostic PIO path to CMD18 reads up to
8 x 512 bytes and makes the PIO copy SG-aware. This tests whether the first
block-layer request can progress without IDMA.

```text
/srv/projects/kernel-work/outgoing/a733-cmd18-pio-fe9a99200ce0-20260610T072756Z
Image sha256: 5dbb9b75ce7c2539a78563db561daffc7e6f3c3420162d94d35d37323ffc4e26
DTB sha256:   ed3cc474fe72c25c3e0cb96a3fc9fa243c1c01631bf4e651031d3cba8500708b

tools/hardware-logs/cubie-uart/20260610T072957Z-a733-cmd18-pio-fe9a99200ce0-ext4load-ttyUSB0.uart.log
sha256: 791d2227c62711b500c391f0a4254d007622cff531153c82a897f9ee13c97595

diag request-data opcode=18 flags=0x200 blksz=512 blocks=8 sg_len=1 stop=1
diag pio mode gctrl=0xa0000010
diag data cmdr-readback=0x80003352 wait_dma=0 pio=1 opcode=18 blocks=8
diag post-data poll5 rint=0x00000024 ... dmac=0x00000200 ... stas=0x02009509
```

Result: CMD18 does not complete even when IDMA is bypassed. It reaches raw
`COMMAND_DONE | RX_DATA_REQUEST` (`RINTR=0x24`) with no `DATA_OVER`, no masked
interrupt, and no PIO copy/finalize for CMD18. This narrows the next question
from "IDMAC cannot read descriptors" to "multi-block read data phase does not
complete"; IDMA descriptor-read state is likely a consequence of the same
multi-block data-phase condition rather than the only failure.

## Guardrails

- Do not add vendor-only U-Boot properties, paths, aliases, or compatible
  strings to upstream DTS.
- Do not add Ethernet, VPU, display, USB-C, PCIe, or wireless nodes to solve
  this boot proof.
- Do not send the local CCU/pinctrl scaffolding as an independent upstream
  series while Junhui/Andre RFCs remain active.
- Keep `clk_ignore_unused` as a lab proof only, not an upstream solution.
