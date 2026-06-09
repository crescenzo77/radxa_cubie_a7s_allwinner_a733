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
- RTC series referenced by the CCU/PRCM RFC:
  `20260121-a733-rtc-v1-0-d359437f23a7@pigmoral.tech`
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

After this audit, the public review export metadata was updated to carry the
RTC `Depends-on:` ID as well as the CCU/PRCM and pinctrl IDs. That fixes the
dependency declaration, but not the remaining DTS/API mismatch.

A companion chosen-tree audit now exists:

```sh
scripts/a733-prereq-stack-audit /path/to/linux-tree
scripts/kernel-workflow-status --a733-prereq-stack-status
```

On 2026-06-09 it reports that `/Users/enzo/projects/linux-a733` is not a clean
candidate regeneration base: the tree is dirty, lacks the A733 RTC prerequisite
binding/header/RTC CCU driver, lacks the A733 R-CCU/PRCM pieces from the current
CCU RFC, and still has a three-input A733 CCU binding/DTSI shape. See
`inventory/hardware/a733-prereq-stack-audit-20260609.md`.

A later Strix scratch worktree proved that RTC, CCU/PRCM, pinctrl, and focused
MMC binding coverage can be stacked on `8fde5d1d47f6`. The stable Strix pointer
is `/srv/projects/a733-prereq-stack-current`, and
`scripts/a733-prereq-stack-audit` passes there at scratch head
`a1f5f546f116`. The next unresolved blocker is regenerating the public review
export against that passing stack and validating the resulting DTS/API shape.

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

### RTC Dependency

Junhui Liu's A733 CCU RFC cover letter states that the CCU work functionally
relies on the A733 RTC series:

```text
20260121-a733-rtc-v1-0-d359437f23a7@pigmoral.tech
```

The RTC series adds the A733 RTC compatible, `sun60i-a733-rtc.h`, and RTC CCU
clock outputs including `hosc`, `osc32k`, and `osc32k-fanout`. The clean
candidate branch therefore needs an explicit RTC prerequisite or an accepted
base that already contains it.

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

1. Use the passing Strix prerequisite stack at
   `/srv/projects/a733-prereq-stack-current`.
2. Regenerate the review export from that clean branch, preserving the narrow
   board-binding, optional-MMC-binding, SoC-DTSI, and board-DTS shape.
3. Reconcile the regenerated A733 DTSI with the four-input CCU/RTC binding
   shape.
4. Include the focused MMC binding patch unless the final chosen base already
   contains `allwinner,sun60i-a733-mmc`.
5. Rerun shape, prerequisite API, public hygiene, checkpatch, binding, DTB,
   build, bisectability, maintainer-recipient, and runtime gates.

This preserves the guardrails: no vendor U-Boot pollution, no Ethernet/VPU/
display expansion, and no local CCU/pinctrl driver submission while the active
RFCs remain the dependency path.
