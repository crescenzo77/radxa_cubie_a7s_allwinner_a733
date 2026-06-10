# A733 SDMMC0 IDMAC Descriptor-Fetch Question Packet

Status: draft, not sent
Created: 2026-06-10T20:18:15Z
Project: Radxa Cubie A7S / Allwinner A733 mainline bring-up

## Intended Use

This is the H029 coordination artifact. Use it to ask Linux MMC/sunxi
maintainers, Radxa, or Allwinner contacts for the missing A733/SUN60IW2 SDMMC0
descriptor-fetch precondition before building another local behavior patch.

Do not submit this as a patch. Do not attach lab-only diagnostics as proposed
upstream code.

## Draft Subject

```text
Question: Allwinner A733 SDMMC0 IDMAC remains in DESC_READ under mainline, vendor kernel advances descriptors
```

## Short Problem Statement

I am bringing up a Radxa Cubie A7S with Allwinner A733/SUN60IW2 on mainline
Linux. Basic SDMMC0 operation is proven: card init, pre-mmcblk CMD17, small PIO
CMD18 reads, partition discovery, CMD49 cache-enable through a narrowly scoped
PIO write, and read-only EXT4 root mount all work when IDMA is bypassed.

The remaining blocker is SDMMC0 IDMAC descriptor fetch. A one-descriptor,
8-block CMD18 read launches, but IDMAC remains in descriptor-read state:

```text
IDST=0x00004000  (DESC_READ)
CHDA=DLBA
CBDA=0x00000000
CBCR=0x00000400
BBCR=0x00000000
descriptor checksum unchanged
descriptor OWN bit still set
```

The descriptor memory remains CPU-visible and unchanged after a CPU-side sync.
This looks like the controller never consumes descriptor word 0, rather than a
later data transfer failure.

## Hardware and Software Context

- Board: Radxa Cubie A7S
- SoC: Allwinner A733 / SUN60IW2
- Test target: Cubie3 lab board
- Known-good vendor kernel: `5.15.147-21-a733`
- Current diagnostic mainline kernel head: `9c631195b6633e6ad7c82b807ec9aee9c9bed27a`
- Latest booted diagnostic subject: `mmc: test A733 vendor normal IDMAC address path`
- Mainline work intentionally avoids Ethernet, VPU, display, USB, PCIe, Wi-Fi,
  and vendor U-Boot DTS policy.
- A733 CCU/PRCM and pinctrl are treated as dependencies because related RFCs
  are already in flight:
  - `20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech`
  - `20250821004232.8134-1-andre.przywara@arm.com`

## Evidence Summary

| Item | Evidence | Interpretation |
| --- | --- | --- |
| PIO reads | CMD17 and small CMD18 PIO reads complete; mmcblk partitions appear. | SD card protocol, clocks sufficient for non-IDMA reads, and rootfs data path are not fundamentally broken. |
| Read-only root | EXT4 root mounts read-only and `/bin/sh` starts when reads avoid IDMA. | Board DTS/rootfs proof is real; blocker is not the PARTUUID/rootfs handoff anymore. |
| One descriptor | One 4096-byte CMD18 IDMA descriptor stalls before partition parsing. | Failure is not only large multi-descriptor block I/O. |
| Descriptor geometry | Vendor live samples and mainline diagnostics use practical 4 KiB descriptor geometry, shifted data/next addresses, size `0x1000`, descriptor control `0x8000001c`/`0x0000001c`. | Obvious descriptor layout mismatch is unlikely. |
| DMAC bit 0x200 | Vendor working reads also show `DMAC=0x200/0x282`. | Sticky bit is not a mainline-only clue. |
| GCTRL access mode | Mainline cleaned leftover AHB/PIO access mode before IDMA and still stalls. | PIO-to-IDMA mode contamination is closed. |
| Data buffer placement | Tests below and above 4 GiB both stall before descriptor consumption. | Data buffer address range is not the immediate cause. |
| Descriptor allocation | Coherent/CMA descriptors and streaming-mapped descriptors both stall. | Descriptor allocation class is not the immediate cause. |
| DMA mask/path | Vendor-style normal IDMAC 64-bit DMA/coherent mask, descriptor size bits `12`, `des_addr_shift=2`, and shifted DLBA still stall. | Vendor normal-IDMAC address path is not sufficient. |
| Fabric subset | Safe MSI/IOMMU fabric gates and minimum NSI CCU bits landed but did not change the stall. | Tested visible fabric/clock subset is not sufficient. |
| Firmware audit | Local boot logs and vendor DT/source show no named SDMMC/SMHC firewall, IOMMU, interconnect, NSI master, or storage permission property/write. | Further guessing locally is weak without documentation. |

## Key Local Artifacts

Private artifact paths, available on request:

```text
H027 result:
/Users/enzo/projects/homelab/task-packets/kernel/a733-h027-idmac-vendor64-result-20260610T2007Z.json

H027 UART:
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260610T200205Z-a733-h027-idmac-vendor64-9c631195b663-ttyUSB0.uart.log

H028 firmware inventory:
/Users/enzo/projects/homelab/task-packets/kernel/a733-h028-firmware-handoff-inventory-20260610T2014Z.json

Hypothesis queue:
/Users/enzo/projects/homelab/task-packets/kernel/a733-hypothesis-queue.json
```

## Specific Questions

1. On A733/SUN60IW2, does SDMMC0 normal IDMAC descriptor fetch depend on a
   non-obvious master permission, security/firewall, TZASC/SMPU, or firmware
   handoff state not represented in the vendor SDMMC0 DT node?

2. Is SDMMC0 descriptor fetch routed through MSI-lite1, MSI-lite2, STORE/MBUS,
   or another SUN60IW2 fabric path that is not named as `sdmmc`/`smhc` in the
   available vendor NSI PMU enum?

3. Should SDMMC0 be represented as an IOMMU, interconnect, or NSI/MBUS master
   in mainline DT/bindings, or is that intentionally absent on A733?

4. Is there a required reset or clock ordering for SDMMC0 IDMAC descriptor
   fetch beyond the visible SDMMC0 clocks: `osc24m`, `pll_periph`,
   `pll_periph_2`, `mmc`, `ahb`, `mmc_store`, `mmc_mbus`, and `mmc_msi_lite`?

5. Does vendor boot0/BL31/SCP/ARISC configure an SDMMC/SMHC master permission
   that Linux must preserve or reapply? If yes, which register block owns it?

6. Is `IDST=0x4000` with `CHDA=DLBA`, `CBDA=0`, and unchanged OWN descriptor a
   known failure signature on sunxi v5p3x/v5p3-style MMC hosts?

## Explicit Anti-Goals

- No vendor U-Boot compatibility strings, aliases, or path names in upstream
  DTS just to satisfy vendor U-Boot fixups.
- No Ethernet, VPU, display, USB-C, PCIe, Wi-Fi, NPU, or GPU expansion in the
  first board slice.
- No competing local CCU or pinctrl submissions while A733 RFCs are in flight.
- No undocumented broad fabric gates in a submit-ready patch.

## Desired Outcome

A pointer to the missing A733/SUN60IW2 SDMMC0 descriptor-fetch precondition:
register block, clock/reset dependency, firmware handoff, master ID, binding
expectation, or known erratum. With that, the next local step can be one narrow
runtime proof instead of another exploratory descriptor/fabric variant.
