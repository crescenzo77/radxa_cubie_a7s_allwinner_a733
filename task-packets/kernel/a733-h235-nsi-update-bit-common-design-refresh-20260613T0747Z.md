# A733-SDMMC-H235: NSI Update-Bit Common Design Refresh

Captured: 2026-06-13T07:47:05Z

## Purpose

Refresh the maintainer-facing design analysis for H215 patch 3:

```text
clk: sunxi-ng: a733: commit the boot-programmed NSI clock state
```

This packet is documentation only. It is not a resend approval, not a new mail
draft, not a source change, and not a hardware action.

## Source Checked

Read-only inspection used the exact H200 source state:

```text
de486cb24c361a86cba26738f24332df780872b0
```

Relevant files inspected:

- `drivers/clk/sunxi-ng/ccu_common.c`
- `drivers/clk/sunxi-ng/ccu_mp.c`
- `drivers/clk/sunxi-ng/ccu_mux.c`
- `drivers/clk/sunxi-ng/ccu_gate.c`
- `drivers/clk/sunxi-ng/ccu_div.c`
- `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`
- `drivers/clk/sunxi-ng/ccu-sun55i-a523.c`

## Findings

The update-bit definitions are:

```text
CCU_FEATURE_UPDATE_BIT = BIT(11)
CCU_SUNXI_UPDATE_BIT  = BIT(27)
```

Existing helper behavior:

- gate enable/disable helpers OR in `CCU_SUNXI_UPDATE_BIT` when
  `CCU_FEATURE_UPDATE_BIT` is set;
- mux parent changes OR in `CCU_SUNXI_UPDATE_BIT`;
- divider rate changes OR in `CCU_SUNXI_UPDATE_BIT`;
- MP parent changes delegate to the mux helper, so parent changes can pulse the
  update bit;
- MP rate changes rewrite M/P fields but do not OR in `CCU_SUNXI_UPDATE_BIT`;
- common CCU registration sets bases, registers clocks, sets rate ranges, adds
  the clock provider, and registers resets, but does not walk update-bit clocks
  and pulse their boot-programmed state.

The exact H200 A733 source has update-bit clocks beyond NSI:

- `nsi`
- `mbus`
- `gpu`
- `dram`

The related A523 driver also has update-bit MP clocks:

- `mbus`
- `iommu`
- `dram`

## Design Assessment

The current H215 patch 3 is defensible as a narrow A733-specific fix because:

- the hardware evidence ties the SDMMC0 normal-IDMA failure to the A733 NSI
  fabric path;
- the tested boot path had no early consumer that committed NSI before SDMMC0
  needed it;
- the source shows common registration does not currently commit update-bit
  clock state;
- the source shows MP rate changes do not currently OR in the update bit;
- the exact H200/H215 stack with the A733 NSI probe-time pulse reached SDMMC0
  card enumeration, read-only root mount, and `/bin/sh` on Radxa Cubie A7S.

A common registration-time treatment is also a plausible maintainer-directed
alternative, but it has broader behavioral scope:

- it would affect every `CCU_FEATURE_UPDATE_BIT` clock in a CCU descriptor, not
  only A733 NSI;
- it could affect other A733 clocks such as `mbus`, `gpu`, and `dram`;
- it could affect other SoCs with update-bit clocks, including A523;
- it would need careful placement relative to base/lock setup, clock
  registration, rate-range setup, provider registration, and reset
  registration;
- it would need a clear rule for clocks where the update bit is self-clearing
  and where boot firmware already left a stable state.

## Maintainer-Ready Framing

If maintainers ask why patch 3 is local to A733:

```text
The submitted form is deliberately narrow: it commits the A733 NSI
boot-programmed state at probe time because that is the specific path tied to
the Cubie A7S SDMMC0 normal-IDMA failure. The common sunxi-ng registration path
does not currently pulse CCU_FEATURE_UPDATE_BIT clocks, and MP rate changes do
not OR in CCU_SUNXI_UPDATE_BIT, so there was no early consumer committing NSI
before SDMMC0 used the fabric in the tested boot path.
```

If maintainers prefer a common treatment:

```text
I can respin this as a common sunxi-ng registration-time update-bit commit if
that is preferred. That would be broader than the tested A733 NSI fix because
A733 and A523 both have multiple update-bit clocks, so I kept the initial RFC/RFT
shape local to the hardware-proven failure path.
```

## Decision

Do not replace H215 patch 3 with a common sunxi-ng patch by default. Keep H215's
A733-specific NSI probe-time commit as the current hardware-proven expression.

Prepare a common implementation only if maintainers request it or if a new
review decision explicitly chooses the broader scope.

## Next Action

Keep H235 alongside H218/H233 as response prep. Continue waiting for H215 public
indexing or maintainer response.
