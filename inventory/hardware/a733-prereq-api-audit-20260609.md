# A733 Prerequisite API Audit - 2026-06-09

## Purpose

Check the current public 3-patch A733/Cubie A7S review export against the
active prerequisite API shape before any clean candidate branch regeneration.

This is a non-mailing audit. It does not authorize patch submission.

## Inputs

- Public review export:
  `/Users/enzo/projects/Home Lab/cubie-a7s-armbian/patches`
- Public-inbox cache:
  `/tmp/lore-linux-sunxi-0.git`
- CCU/PRCM RFC:
  `20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech`
- Pinctrl RFC:
  `20250821004232.8134-1-andre.przywara@arm.com`
- Local review matrix card:
  `task-packets/kernel/context-cards/review-matrix-a733-prereq-api-compat-20260609-7ff8de36568c.md`

## Local Model Review

The dispatcher used all configured local lanes for an advisory review of the
current export:

- `amd-fast`
- `amd-research`
- `strix-review`

The lanes agreed on the useful high-level concern: the current export has the
right narrow patch shape, but the DTS references still need direct checking
against the prerequisite CCU/pinctrl/MMC API state before candidate
regeneration.

## Deterministic Findings

The new audit command reports:

```sh
scripts/a733-prereq-api-audit "/Users/enzo/projects/Home Lab/cubie-a7s-armbian/patches"
```

Current result:

```text
status=FAIL
ccu-clock-names-missing-losc-fanout
ccu-clock-input-count
mmc-compatible-without-binding-coverage
```

### CCU Clock Inputs

Junhui Liu's A733 CCU RFC binding patch documents the main CCU example as:

```dts
clocks = <&rtc 2>, <&rtc 1>, <&rtc 0>, <&rtc 4>;
clock-names = "hosc", "losc", "iosc", "losc-fanout";
```

The current public SoC DTSI review patch still has:

```dts
clocks = <&osc24M>, <&osc32k>, <&iosc>;
clock-names = "hosc", "losc", "iosc";
```

Conclusion: a clean candidate branch must reconcile the SoC DTSI with the
chosen CCU/RTC prerequisite stack before dt-binding or DTB validation can be
claimed.

### MMC Compatible Coverage

The current public SoC DTSI review patch uses:

```dts
compatible = "allwinner,sun60i-a733-mmc", "allwinner,sun20i-d1-mmc";
```

The recorded historical base did not contain that compatible in
`Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml`; the old
9-patch validation branch added it in a standalone local binding patch that is
now intentionally dropped from the public review export.

Conclusion: before candidate regeneration, either choose a base that already
documents `allwinner,sun60i-a733-mmc`, carry a proper binding update in the
series with maintainer-acceptable ordering, or use only an already documented
compatible if that is technically correct.

## Current Next Action

Do not prepare or send maintainer-facing patches yet. The next kernel-facing
action is to resolve this prerequisite API audit:

1. Choose the exact clean base and prerequisite stack.
2. Reconcile the A733 CCU clock inputs with the current CCU/RTC binding shape.
3. Resolve A733 MMC compatible binding coverage.
4. Regenerate the review export from that clean branch.
5. Rerun shape, prerequisite API, public hygiene, checkpatch, binding, DTB,
   build, bisectability, maintainer-recipient, and runtime gates.

This preserves the guardrails: no vendor U-Boot pollution, no Ethernet/VPU/
display expansion, and no local CCU/pinctrl driver submission while the active
RFCs remain the dependency path.
