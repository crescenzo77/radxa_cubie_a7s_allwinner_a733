# Upstream Baseline

This is the single standing policy file for A733/Cubie A7S upstream candidate
work. Keep it short. Do not add new governance Markdown.

## Host Roles

- `mac-mini`: local workstation. Use for local repo editing, documentation, and
  macOS-side git tracking. Do not attempt loopback SSH execution to this host.
- `strix`: `192.168.50.11`, primary build host. Use for kernel object
  compilation, full `Image` builds, `make W=1`, Docker validation, and
  `dt_binding_check` loops.
- `thinkcentre`: service infrastructure and local repository synchronization
  host only. Do not use for routine development or kernel compilation.
- `mini-pc`: media server and LVM host only. Do not touch or query.

## Maintainer Constraints

- Generic STMMAC core files must not carry A733-only sequencing, reset,
  wrapper, delay-chain, clock, syscfg, PHY reference, or board workaround code.
  A733 Ethernet behavior belongs in Allwinner STMMAC glue code.
- Devicetree bindings and header IDs must land before DTS or DTSI users. New
  compatibles, clock IDs, reset IDs, properties, and interrupt layouts require
  matching YAML/header support first.
- Candidate code must have zero logging noise: no printk storms, register-scan
  loops, trace labels, diagnostic dumps, WIP comments, or lab-history prose.
  Production success paths stay quiet.
- Pinctrl quirks must be modeled as clean SoC driver data or reviewed framework
  flags, including the A733 missing Port A / structural IRQ-bank layout. Do not
  publish discovery traces as pinctrl behavior.
- Public candidate history must be atomic and squashed. No `WIP`, `fixup!`,
  `squash!`, `try`, diagnostic, failed mailbox, or trial-and-error commits may
  be publicly visible.
- DCO sign-off is human-only. AI agents must not add `Signed-off-by:` trailers.
  Add human sign-off only after human review and responsibility for the patch.
  Disclose AI help with `Assisted-by:` when AI contributed to final kernel
  patch content, review, or commit text.

## Current Direction

- Freeze Markdown policy churn. Only this file may carry terse status.
- Shift from metadata to hardware description.

## Subsystem Status

| Block | Status |
| --- | --- |
| Board compatible | Candidate Complete |
| Pinctrl | Mainline Validated |
| CCU | Mainline Validated |
| CPU topology / PMU | Mainline Validated |
| MMC0 / storage DTS | Mainline Validated |
| Ethernet / GMAC210 | Disabled SoC Node Validated; Board Enable Deferred |
| USB host / USB3 | USB host Mainline Validated; USB3 Discovery |
| Thermal / GPADC | Discovery |
| I2C / TWI | Discovery |
