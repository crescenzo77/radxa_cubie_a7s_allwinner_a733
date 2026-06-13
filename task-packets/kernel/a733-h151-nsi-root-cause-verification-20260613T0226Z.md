# A733 H151 NSI Root-Cause Verification

Date: 2026-06-13T02:26Z

Control rule: work performed from Codex Desktop only. No local model or
OpenRouter model dispatch was used for this verification.

## Finding

The SDMMC0 normal IDMAC descriptor-fetch blocker is now tied to the A733 NSI
clock path, not to descriptor format, DMA API geometry, card signaling, or a
raw writable H149 bit.

H149's `0x02002580 bit 27` label identifies the CCU NSI clock update bit:

- register: A733 CCU NSI clock register at offset `0x580`
- absolute address: `0x02002580`
- bit: `CCU_SUNXI_UPDATE_BIT`, the self-clearing update/commit bit for
  `CCU_FEATURE_UPDATE_BIT` clocks
- implication: unchanged readback after writing bit 27 is expected and does not
  disprove the pulse

The working shape needs both:

- pulse the NSI update bit once after the boot-time NSI mux/divider value is
  visible to Linux
- keep the NSI fabric clocks alive so `clk_disable_unused()` does not remove
  the path before SDMMC0 IDMAC can use it

## Verified Evidence

Baseline storage-fabric criticals without NSI fix:

- commit: `fca11ed605fd`
- log: `tools/hardware-logs/cubie-uart/20260613T012948Z-a733-ahbstorecrit-fca11ed605fd-ttyUSB0.uart.log`
- result: SDMMC0 host initializes but remains stuck at `Waiting for root device`.

NSI update pulse only:

- commit: `b1facfb3e0ea`
- log: `tools/hardware-logs/cubie-uart/20260613T014946Z-a733-nsifix-b1facfb3e0ea-ttyUSB0.uart.log`
- result: still stalls at `Waiting for root device`; pulse alone is not enough.

NSI update pulse plus critical NSI clocks:

- commit: `8af7499f18e6`
- log: `tools/hardware-logs/cubie-uart/20260613T015456Z-a733-nsicrit-8af7499f18e6-ttyUSB0.uart.log`
- result: SDMMC0 normal IDMA reaches the card, `mmcblk0` appears with `p1 p2 p3`,
  root mounts read-only, and `/bin/sh` starts.

## Patch Direction

Do not port H149 raw register pokes.

The next kernel patchwork step is to turn the verified diagnostic shape into an
upstreamable CCU/RFC proposal:

- decide whether the NSI update pulse belongs as an A733 probe-time fixup or a
  framework-level behavior for `CCU_FEATURE_UPDATE_BIT` clocks that already have
  boot-programmed mux/divider values
- justify any `CLK_IS_CRITICAL` use narrowly for NSI and bus-nsi, or replace it
  with a modeled consumer/clock relationship if the upstream CCU maintainers
  prefer that shape
- keep SDMMC0 DTS free of vendor policy nodes and raw register workarounds

## Guardrails

- Cubie1 remains excluded from proof work.
- No local/OpenRouter model offload for the current Codex Desktop workflow.
- No broad H149 rerun without explicit approval.
- No public send until the CCU/RFC feedback is manually reviewed.
