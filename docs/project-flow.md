# Project Flow

This document turns maintainer feedback into standing operating procedure for
the rest of the A733/Cubie A7S bring-up.

## Operating Model

Work proceeds in two separate lanes:

- private lab branches for discovery, traces, register scans, failed trials, and
  board experiments;
- clean candidate branches rebuilt from a mainline kernel base with only final
  reviewable code.

Do not promote a lab branch by trimming around its edges. Rebuild candidate
series from a clean base, one subsystem at a time, copying only the final
binding, driver, and DTS content that satisfies the maintainer acceptance
contract.

## Candidate Gate

A branch is a candidate only after all of these are true:

- every patch is atomic and independently reviewable;
- bindings are added before any DTS or driver user that needs them;
- the branch contains no fixup, WIP, diagnostic, trace, or trial commits;
- production code is silent on the normal success path;
- no generic subsystem file carries A733-only sequencing or workarounds;
- broken or unproven hardware remains disabled in board DTS files;
- required checks have been run and recorded.

Required checks for candidate publication:

```text
git diff --check
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
make dt_binding_check
make dtbs_check
```

On macOS, run kernel make targets from a path without spaces or colons. If the
project checkout lives under a path with spaces, create a temporary detached
worktree under `/tmp` and run GNU Make 4.0 or newer there.

For full-tree Linux kernel checks on macOS, use either a case-sensitive APFS
temporary volume or the `thinkcentre` Docker path. The upstream kernel contains
case-colliding paths that cannot be materialized safely on the default
case-insensitive macOS filesystem. The current remote validation pattern is to
export the candidate branch with `git archive`, unpack it under `/tmp` on
`thinkcentre`, and run a disposable Linux container with GNU Make, flex, bison,
libssl, libelf, `dtschema`, and `gcc-aarch64-linux-gnu`.

Do not treat a kernel `CHECK_DTBS=y` run as successful merely because `make`
returned zero: the kernel rule masks `dt-validate` failures with `|| true`.
Use a `dtschema` version compatible with the kernel invocation, pass multiple
`DT_SCHEMA_FILES` filters as a colon-separated list, and inspect the validation
output for real schema errors.

## Binding Inventory

No DTS/DTSI patch may use an A733-specific compatible string, clock ID, reset
ID, property, or interrupt layout before the matching binding/header support
exists in the same candidate series.

The required binding inventory for the first platform milestones is:

- A733 pinctrl: required for PIO nodes and pin groups;
- A733 CCU: required before any A733 clock/reset IDs appear in DTSI;
- A733 MMC: required before MMC nodes use the A733-specific compatible;
- Radxa Cubie A7S board compatible: required before the board DTS;
- A733 GMAC210/EMAC: later only, required before any Ethernet DTS enablement.

The current clean candidate slice covers only the A733 pinctrl binding and
driver. CCU, DTSI, board DTS, and Ethernet must remain separate candidate
slices.

## Feedback Triage

The latest review feedback is accepted as policy where it reinforces
upstreamability:

- deconstruct diagnostic patch stacks into clean subsystem series;
- formalize any IRQ clear behavior as normal SoC data or a core pinctrl quirk;
- keep Ethernet sequencing in Allwinner STMMAC glue code;
- write strict YAML bindings before DTS users for pinctrl, CCU, board
  compatible strings, and later EMAC/GMAC210;
- strip all printk/register-scan log noise from candidates.

One part is intentionally not adopted as an immediate patch sequence: Ethernet
binding and enablement remain outside the first public milestone. GMAC0 is
still unproven, so Ethernet must stay disabled until wrapper programming,
clocks, resets, MDIO, PHY reset, PHY power, and link behavior are proven.

## Pinctrl Flow

The first candidate slice is pinctrl only:

1. Add the A733 pinctrl binding.
2. Add the A733 pinctrl driver data.
3. Keep DTS users for a later platform/DTS slice.

The A733 IRQ layout must represent the missing physical Port A and the
structural IRQ bank slot explicitly. If write-zero-to-clear IRQ acknowledge
behavior is later proven necessary for production, add it as a reviewed
Allwinner pinctrl framework quirk, for example a SoC data flag in
`struct sunxi_pinctrl_desc`, with no trace prints and only a concise hardware
comment explaining the APB posted-write flush. Do not carry W0C discovery
traces in candidate code, and do not add a W0C quirk unless the hardware need
is proven outside the candidate branch.

## Ethernet Flow

Ethernet remains a later, isolated series. Candidate Ethernet work must have
this shape:

1. `dt-bindings: net: stmmac: add Allwinner A733 GMAC210`
2. `net: stmmac: add Allwinner A733 GMAC210 glue support`
3. `arm64: dts: allwinner: enable GMAC0 on Radxa Cubie A7S`

The glue driver must prepare Allwinner-specific wrapper, clock, reset, delay,
and PHY-reference state before common STMMAC code runs. Generic STMMAC files
may change only for hardware-generic defects justified independently of A733.

Candidate Ethernet code must not modify these generic files for A733-only
sequencing:

- `drivers/net/ethernet/stmicro/stmmac/stmmac_main.c`
- `drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c`
- `drivers/net/ethernet/stmicro/stmmac/dwmac-generic.c`

## Publication Rule

Public `main` remains documentation-first until a candidate series is clean
enough to be sent for review. Do not publish lab artifacts, generated files,
diagnostic patches, rejected mailboxes, or patch histories that preserve
trial-and-error discovery.
