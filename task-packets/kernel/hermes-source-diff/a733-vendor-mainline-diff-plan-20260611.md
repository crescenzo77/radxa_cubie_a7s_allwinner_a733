# A733 Vendor-vs-Upstream Diff Audit Plan

Date: 2026-06-11

## Purpose

Replace the Cubie2/Cubie3 brute-force loop with a source-backed audit of what the working vendor kernel changed compared with the closest upstream kernel base.

The goal is to find a specific, reviewable, testable difference that could explain why A733 SDMMC0 PIO works but IDMAC stalls in descriptor-read state on mainline.

## Guardrails

- Do not reboot Cubie2 or Cubie3.
- Do not start `a733-idmac-bruteforce-lab`.
- Do not patch the kernel from speculation.
- Do not expand into Ethernet, VPU, display, USB-C, GPU, NPU, or Wi-Fi.
- Do not add vendor U-Boot compatibility hacks to upstream DTS.
- Account for in-flight A733 CCU/PRCM and pinctrl RFCs.
- Prefer evidence from exact source diffs, DTS diffs, symbols, or runtime register baselines.

## Inputs On Strix

Expected source locations:

```text
/srv/projects/kernel-work/tmp/linux-orangepi-full
/srv/projects/kernel-work/tmp/orangepi-a733-mmc
/srv/projects/a733-diag-rtc-extosc-orphan
/srv/projects/homelab
```

Known working vendor runtime:

```text
Linux 5.15.147-21-a733 on Radxa Cubie A7S
```

Known mainline diagnostic symptom:

```text
SMHC0 IDMAC reaches IDST=0x4000, CHDA=DLBA, CBDA=0, descriptor OWN remains set.
PIO reads work.
```

Known positive clue:

```text
CCU register 0x02002580 bit 27 made Cubie3 IDMAC progress further during brute-force testing.
Treat this as a clue, not a fix.
```

## Work Plan For Hermes Agent

### 1. Identify exact trees

Record for each tree:

- path
- branch
- commit
- remotes
- dirty status
- whether history can identify an upstream base

If vendor history is not connected to upstream, use `git diff --no-index` on targeted subtrees.

### 2. Diff MMC driver paths

Compare vendor and mainline for:

```text
drivers/mmc/host/sunxi-mmc*
drivers/mmc/host/*sunxi*
include/linux/mmc/*
```

Extract only differences relevant to:

- descriptor format
- descriptor address shifts
- DMA mask
- coherent vs streaming DMA
- reset/init order
- IDMAC start sequence
- FIFO thresholds
- SMHC access mode
- A733/v5p3x/v5p4x conditionals

Mark each difference as already-tested, untested, or irrelevant.

### 3. Diff CCU/reset/storage-fabric paths

Compare vendor and upstream/mainline for:

```text
drivers/clk/sunxi-ng/
drivers/reset/
drivers/soc/sunxi/
drivers/bus/
drivers/dma/
drivers/iommu/
drivers/interconnect/
drivers/firmware/arm_scmi/
```

Focus on names and offsets related to:

```text
SMHC0, SDMMC0, MMC0, sdc0, mbus, nsi, store, msi-lite, ahb-mat, mbus-mat,
0x02002580, 0x02002584, 0x02002588, 0x020025c0, 0x020025e0, 0x020025e4,
0x02002d00, 0x02002d0c
```

For every candidate, record:

- vendor file and line
- upstream/mainline file and line, if present
- exact register/bit/name
- why it could affect SDMMC0 IDMAC memory access
- whether it is safe to test
- whether it belongs in CCU, reset, MMC, DTS, or firmware handoff

### 4. Diff DTS and binding metadata

Compare vendor and mainline-style A733 DTS/DTSI for:

```text
sun60iw2p1.dtsi
sun60i-a733*.dts*
*cubie*a7s*.dts*
```

Focus only on SDMMC0 dependencies:

- clocks
- resets
- power domains
- interconnects
- IOMMU properties
- DMA properties
- vendor-only `clk-init-*` metadata
- `req-page-count`
- store/MBUS/MSI-lite references

Do not propose copying vendor-only DTS pollution. Use DTS only as evidence for missing provider modeling.

### 5. Produce fixed-schema output

Write all outputs under:

```text
/srv/projects/homelab/task-packets/kernel/hermes-source-diff/
```

Required files:

```text
a733-vendor-mainline-diff-summary.md
a733-vendor-mainline-diff-candidates.json
a733-vendor-mainline-diff-report.html
```

Candidate JSON schema:

```json
{
  "generated_at": "ISO-8601 UTC",
  "trees": [],
  "candidates": [
    {
      "id": "HSD-001",
      "priority": 1,
      "area": "ccu|reset|mmc|dts|firmware|fabric",
      "vendor_evidence": "file:line plus short fact",
      "mainline_delta": "file:line plus short fact",
      "register_or_symbol": "name/address/bit if known",
      "why_it_matters": "one paragraph",
      "already_tested": true,
      "testable_next_step": "exact minimal test, or null",
      "risk": "low|medium|high",
      "recommendation": "test|do-not-test|needs-source"
    }
  ],
  "top_recommendation": "one concrete next action"
}
```

### 6. Notification

Send one Telegram message when the report is complete. Include:

- top recommendation
- number of candidates found
- local-network HTML link

Use the existing ThinkCentre Telegram bot configuration; do not hardcode tokens.

## Success Criteria

This task is complete when Hermes produces a source-backed candidate queue. A good result may be "no safe new kernel patch found"; that still improves the project by closing the full-tree diff gap.

