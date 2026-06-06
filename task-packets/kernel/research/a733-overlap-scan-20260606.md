# A733 Overlap Scan

Generated: 2026-06-06
Research worker: `qwen36-27b-7900xt-research`
Host: `192.168.50.252`
Endpoint: `http://127.0.0.1:8092/v1`
Runtime: llama.cpp Vulkan, device `Vulkan2` / AMD Radeon RX 7900 XT

## Source Set

Public-inbox clone:

- `https://lore.kernel.org/linux-sunxi/0`
- local cache: `/tmp/lore-linux-sunxi-0.git`
- cache size observed: `102M`

Radxa public docs:

- `https://docs.radxa.com/en/cubie/a7s`
- `https://docs.radxa.com/en/cubie/a7s/hardware-use/hardware-info`

## Key Source Hits

A733 CCU/PRCM overlap:

- `a68c56676ffff76125ebf8761676f26731b54070`
  `[PATCH RFC 0/8] clk: sunxi-ng: Add support for Allwinner A733 CCU and PRCM`
  by Junhui Liu, 2026-03-10
- `7948b66650bc29ddaf7308922815478e360d7ae8`
  `[PATCH RFC 1/8] dt-bindings: clk: sun60i-a733-ccu: Add allwinner A733 support`
  by Junhui Liu, 2026-03-10
- `7a35b757194a27bd7ac47a6a2a89dc418eb66600`
  `[PATCH RFC 3/8] clk: sunxi-ng: a733: Add PRCM CCU`
  by Junhui Liu, 2026-03-10
- `cb215a2b654f9a83adfc650d09ac0f5ac9980e12`
  `[PATCH RFC 7/8] clk: sunxi-ng: a733: Add bus clock gates`
  by Junhui Liu, 2026-03-10
- `87a517b93d810c09cb84e4eb9ddfab32c8795ebb`
  `[PATCH RFC 8/8] clk: sunxi-ng: a733: Add reset lines`
  by Junhui Liu, 2026-03-10
- Follow-ups were found through 2026-05-14.

A733 pinctrl overlap:

- `5f2058d77e1f26d053ba352fcd6fd2e32834d24c`
  `[RFC PATCH 0/9] pinctrl: sunxi: Allwinner A733 support`
  by Andre Przywara, 2025-08-21
- `b2a2e564be6d75057a79cc4e41ec0b0c2f7f19c5`
  `[RFC PATCH 5/9] pinctrl: sunxi: support A733 generation MMIO register layout`
  by Andre Przywara, 2025-08-21
- `468da8f81bc98ace386edee44e08c4af5634ba94`
  `[RFC PATCH 7/9] dt-bindings: pinctrl: add compatible for Allwinner A733`
  by Andre Przywara, 2025-08-21
- `fcd19113c664dd9399f00340c99cbcf59edd2993`
  `[RFC PATCH 8/9] pinctrl: sunxi: a523-r: add a733-r compatible string`
  by Andre Przywara, 2025-08-21
- `ec3ece24c7e34f294d30393f7831b9385fb9cda0`
  `[RFC PATCH 9/9] pinctrl: sunxi: Add support for the Allwinner A733`
  by Andre Przywara, 2025-08-21
- Follow-ups were found through 2025-08-24.

Other A733 ecosystem work:

- `46348bcddd352851bdb9e5832634ae5c8bc0d3e2`
  `[PATCH 0/7] rtc: sun6i: Add support for Allwinner A733 SoC`,
  2026-01-21
- A733 PCK600 power domain controller v1/v2 work appears around
  2026-03-04 and 2026-03-05.
- A733 U-Boot work appears around 2026-01-13.

## 7900XT Research Summary

Immediate blockers:

- CCU/PRCM conflict: Junhui Liu's in-flight RFC series covers A733 CCU,
  PRCM, bus clock gates, and reset lines.
- Pinctrl conflict: Andre Przywara's in-flight RFC series covers A733
  pinctrl support, MMIO layout, and compatible strings.
- Submission hold: do not send the current candidate series until the CCU and
  pinctrl overlap is coordinated, rebased, or explicitly justified.

Useful supporting facts:

- Radxa documents Cubie A7S as Allwinner A733 based.
- Radxa documents the CPU topology as `2x Cortex-A76 + 6x Cortex-A55`.
- Radxa documents board capabilities including Gigabit Ethernet, Wi-Fi 6,
  Bluetooth 5.4, PCIe 3.0 x1, microSD, optional eMMC, and USB-C DisplayPort.
- Ethernet, VPU, display, Wi-Fi, and Bluetooth remain out of scope for the
  current candidate series.

What to query next:

- Pull the latest state of Junhui Liu's CCU/PRCM series after the 2026-05-14
  follow-ups.
- Pull the latest state of Andre Przywara's A733 pinctrl RFC after the
  2025-08-24 follow-ups.
- Determine whether the local candidate branch should drop local CCU/pinctrl
  patches, rebase onto those RFCs, or keep them only as temporary scaffolding.

Patch-workflow action:

- Pause upstream submission.
- Coordinate or rebase before presenting CCU/pinctrl support upstream.
- Keep the research packet attached to future A733 task packets so the overlap
  cannot be missed again.

## Notes

The lore web UI and raw message URLs returned an anti-bot challenge from this
environment. The public-inbox git endpoint was reachable and used instead.

This packet is research input only. It is not validation proof and does not
authorize patch submission.
