# Current Technical Status

Last updated: 2026-06-04

## Scope

The project is focused on Radxa Cubie A7S support in mainline Linux. Vendor
BSPs, vendor DTBs, and downstream board files are evidence only.

## Board and SoC

- Board: Radxa Cubie A7S.
- SoC: Allwinner A733.
- Target: mainline Linux, not vendor BSP forward-porting.

## Constraints

- Mainline tests use an alternate extlinux entry only.
- Vendor boot defaults are not changed.
- U-Boot environment is not saved.
- Arbitrary GPIO outputs are not driven during diagnostics.
- Ethernet is not claimed until real PHY communication and link behavior are
  proven.

## Pinctrl / GPIO IRQ

The A733 GPIO layout skips Port A in the physical GPIO banks while the IRQ bank
layout still reserves the structural slot. Local testing and upstream A523/A733
discussion point toward an 11-bank structural IRQ model with the missing Port A
slot represented as non-functional padding.

Upstream-facing requirement:

- Represent the hardware bank layout explicitly.
- Avoid lazy or accidental parent IRQ registration behavior.
- Keep the final change small enough for pinctrl review.
- Add any W0C IRQ acknowledge behavior only as a normal sunxi pinctrl quirk
  after it is proven, with no diagnostic trace code.

## GMAC0 / Ethernet

Local evidence identifies GMAC0 as:

```text
base:       0x04500000
wrapper:    0x04508000
compatible: allwinner,sunxi-gmac-210 + snps,dwmac-5.20 in vendor DT evidence
```

Vendor source evidence from Orange Pi's `orange-pi-5.15-sun60iw2` branch shows
an Allwinner GMAC210 glue driver that:

- maps the second resource as a wrapper/syscfg aperture;
- programs wrapper offset `0x00` for interface mode and delay-chain fields;
- handles the SoC-provided PHY reference clock when requested;
- calls into common STMMAC after wrapper setup.

Local mainline diagnostics have shown:

- DWMAC 5.x identity and capability registers become visible.
- The DMA software reset bit remains stuck at `DMA_BUS_MODE.SWR`.
- Generic STMMAC clock experiments alone did not clear the reset condition.
- MDIO reads have not yet proved external PHY communication.

Upstream-facing requirement:

- Do not submit generic debug traces or forced probe hacks.
- Do not modify generic STMMAC core files for A733-specific sequencing.
- Build a proper Allwinner GMAC210 glue driver, or extend an accepted
  Allwinner STMMAC glue driver, so wrapper clocks and resets are prepared before
  common STMMAC code runs.
- Define wrapper registers with named macros.
- Use standard DT binding names where possible.
- Document any new compatible string and required clocks/resets.
- Keep any upstream-facing Cubie A7S board DTS Ethernet node disabled until the
  DMA reset timeout and real external PHY communication are resolved.

## Binding Inventory

The A733 pinctrl binding now exists in the clean local candidate branch and has
passed `dt_binding_check`, and the driver object now compile-tests cleanly with
`W=1` in a remote Linux Docker build container. The Radxa Cubie A7S board-compatible
binding now exists in `candidate/a733-board-binding-clean` and has passed
`dt_binding_check`. The A733 MMC compatible binding now exists in
`candidate/a733-mmc-binding-clean` and has passed `dt_binding_check`. The A733
GMAC210/EMAC binding is intentionally deferred until Ethernet behavior is
proven.

The A733 CCU binding/header/driver slice now exists in
`candidate/a733-ccu-clean` and has passed `dt_binding_check`. The driver
object now compile-tests cleanly with `W=1` in a remote Linux Docker build
container.

The integrated non-Ethernet platform stack now exists in
`candidate/a733-platform-clean`. It keeps Ethernet absent, splits A733 SoC DTSI
from Radxa Cubie A7S board DTS, and enables only UART0 and MMC0 on the board.
It now builds arm64 `defconfig` and validates the Cubie A7S DTB through the
kernel `CHECK_DTBS=y` path on a temporary case-sensitive APFS volume. The
generated DTB also passes direct `dt-validate` against the processed in-tree
schema. The integrated branch also compile-tests both A733 driver objects in a
remote Linux Docker build container with `W=1` and an arm64 cross compiler.

## Immediate Mainline Question

Does the A733 GMAC0 DMA reset require Allwinner GMAC210 wrapper programming
before the common STMMAC DWMAC 5.20 path runs?

The next lab test should answer that question, but the public branch should not
carry the diagnostic code as an upstream candidate.

## Upstream Milestone Boundary

The first acceptable public patch goal is initial A733/Cubie A7S platform
support without claiming Ethernet. Ethernet enablement should be a separate
series after the GMAC210 wrapper model, CCU clocks, reset ordering, MDIO bus,
and PHY reset/power behavior are proven.

The latest local candidate-series audit is recorded in
[candidate-series-audit-20260604.md](candidate-series-audit-20260604.md).

The sustained project execution flow is recorded in
[project-flow.md](project-flow.md). In short: lab branches may contain
diagnostics, but candidate branches must be rebuilt as quiet, atomic,
bindings-first kernel patches. Ethernet remains later and disabled until it is
proven.
