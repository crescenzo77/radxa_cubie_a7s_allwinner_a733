# A733 H171 NSI update-bit design review

Captured: 2026-06-13T03:35Z

## Purpose

Review the local sunxi-ng update-bit implementation around the H153/H170
patch 3 proposal:

- `clk: sunxi-ng: a733: commit the boot-programmed NSI clock state`

This note is documentation only. It does not approve hardware runs, Cubie
staging, `/boot` writes, kernel commits, patch publication, service changes,
cron changes, or model-routing changes.

## Source inspected

Read-only inspection on the A733 split-draft worktree:

- `drivers/clk/sunxi-ng/ccu_common.h`
- `drivers/clk/sunxi-ng/ccu_common.c`
- `drivers/clk/sunxi-ng/ccu_mp.c`
- `drivers/clk/sunxi-ng/ccu_mux.c`
- `drivers/clk/sunxi-ng/ccu_gate.c`
- `drivers/clk/sunxi-ng/ccu_div.c`
- `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`
- `drivers/clk/sunxi-ng/ccu-sun55i-a523.c`

## Findings

The relevant bit definitions are:

- `CCU_FEATURE_UPDATE_BIT = BIT(11)`
- `CCU_SUNXI_UPDATE_BIT = BIT(27)`

The existing operation helpers behave differently:

- `ccu_gate_helper_enable()` and `ccu_gate_helper_disable()` OR in
  `CCU_SUNXI_UPDATE_BIT` when `CCU_FEATURE_UPDATE_BIT` is set.
- `ccu_mux_helper_set_parent()` ORs in `CCU_SUNXI_UPDATE_BIT` when
  `CCU_FEATURE_UPDATE_BIT` is set.
- `ccu_div_set_rate()` ORs in `CCU_SUNXI_UPDATE_BIT` when
  `CCU_FEATURE_UPDATE_BIT` is set.
- `ccu_mp_set_parent()` delegates to the mux helper, so parent changes can
  pulse the update bit.
- `ccu_mp_set_rate()` rewrites the M/P fields and writes the register back,
  but does not OR in `CCU_SUNXI_UPDATE_BIT`.

The common registration path sets clock bases, registers clock hardware, sets
rate ranges, registers the clock provider, and registers resets. It does not
walk `CCU_FEATURE_UPDATE_BIT` clocks and pulse update bits at registration.

On the A733 RFC source, update-bit MP-style clocks include:

- `nsi` at `0x580`
- `mbus` at `0x588`
- `dram` at `0xc00`

There is also an update-bit divider-style `gpu` clock at `0xb20`.

On the related A523 driver, update-bit MP-style clocks include:

- `mbus`
- `iommu`
- `dram`

That comparison shows A733 is not unique in having update-bit MP clocks, but
the A733 NSI clock is the one tied by hardware evidence to the SDMMC0 normal
IDMA root-device failure.

## Patch 3 implication

H153 patch 3 remains a defensible A733-specific probe fixup for the current
series because:

- the tested boot path had no normal consumer that committed the NSI state
  before SDMMC0 normal IDMA needed the fabric;
- registration does not currently commit update-bit clocks;
- `ccu_mp_set_rate()` itself does not pulse the update bit;
- parent/gate/div paths can pulse it, but only if an operation actually runs
  early enough;
- hardware evidence shows that the NSI pulse alone was insufficient, while
  the pulse plus the NSI/storage fabric keepalive set reached root.

However, a broader common change is still a legitimate maintainer discussion
point because update-bit MP clocks exist on more than just A733. The safe
wording is:

- Ask whether maintainers prefer the local A733 probe fixup or a common
  registration-time treatment for boot-programmed `CCU_FEATURE_UPDATE_BIT`
  clocks.
- Do not claim that all set-rate paths miss the update bit.
- Do not claim that the NSI pulse alone fixes SDMMC0.

## Commit-message adjustment

H170 patch 3 wording is consistent with this review:

- it says no tested boot-path consumer commits NSI before SDMMC0 IDMA;
- it says parent/gate/div helper paths can pulse the update bit;
- it says the MP rate path itself does not appear to OR in the update bit;
- it says the update pulse alone was not sufficient.

No immediate H170 text change is required from this review.

## Guardrails

- Do not create a common update-bit registration patch without explicit
  operator approval.
- Do not create kernel-source commits without explicit operator approval.
- Do not send H167 or any generated patch series without explicit operator
  approval.
