# Public Repository Expectations

This repository must look like an upstream-facing Linux enablement project, not
a hardware lab scratchpad.

The public `main` branch should help kernel maintainers quickly answer three
questions:

1. What hardware is being enabled?
2. What facts are known and sourced?
3. What patch shape will be submitted upstream?

It should not require maintainers to filter through experiments, generated
files, failed attempts, or local-machine state.

The stricter maintainer acceptance contract is recorded in
[maintainer-acceptance-contract.md](maintainer-acceptance-contract.md).
The standing execution flow is recorded in [project-flow.md](project-flow.md).

## Public Branch Contents

The public branch may contain:

- concise project status;
- sourced hardware evidence;
- upstream submission discipline;
- AI assistance disclosure policy;
- empty or curated patch directories;
- clean candidate patches only after they are ready for review.

The public branch must not contain:

- generated kernels, DTBs, initrds, modules, or root filesystems;
- UART captures, boot logs, compressed traces, or screenshots;
- local helper scripts tied to one workstation or board setup;
- diagnostic printk patches;
- register scanning loops used only for discovery;
- generic subsystem hacks for board-specific behavior;
- DTS files with undocumented properties or synthetic clock/reset IDs;
- enabled nodes for devices that still fail probe or create boot-time noise;
- failed patch attempts or mailbox files rejected by `git am`;
- vendor BSP source dumps;
- copied vendor DTS files presented as mainline work;
- experimental DTS nodes marked `status = "okay"` for hardware that still
  times out or fails noisily.

## Patch Appearance

Any public patch candidate must be reviewable as if it were about to be sent to
LKML.

Candidate patches must:

- be generated from a clean kernel tree;
- apply with `git am`;
- pass `git diff --check`;
- pass relevant `scripts/checkpatch.pl` checks;
- pass `dt_binding_check` for binding changes;
- pass `dtbs_check` for DTS changes;
- use accepted bindings and headers only;
- avoid generic subsystem changes for board-specific behavior;
- include only a human `Signed-off-by:` after human review.

Patch branches containing fixup commits, unresolved checkpatch findings, or
unvalidated Devicetree schema changes are not public candidates.

Policy documents alone are not enough. Any branch whose code still contains
generic subsystem hacks, diagnostic scaffolding, undocumented DTS properties, or
known-broken enabled nodes must remain private or clearly marked as lab state.

Experimental work belongs on private lab branches, not public `main`.

## Devicetree Standard

Public DTS/DTSI content must describe hardware, not debugging strategy.

New compatibles, clocks, resets, power domains, and properties require matching
YAML bindings and accepted header definitions before board DTS files use them.

The required order is bindings first, then driver/header support, then DTSI,
then board enablement.

For A733, public candidate work must provide formal schemas for each subsystem
before its DTS users:

- `allwinner,sun60i-a733-pinctrl` before PIO nodes and pin groups;
- A733 CCU compatibles and clock/reset IDs before the SoC DTSI references
  them;
- Radxa Cubie A7S board compatible before the board DTS;
- A733 GMAC210/EMAC binding before Ethernet is enabled.

Hardware that is known to fail during probe must remain disabled in
upstream-facing board files. For Cubie A7S, GMAC0 stays disabled until the
Allwinner GMAC210 wrapper, CCU clocking, reset ordering, MDIO bus, PHY reset,
and PHY power behavior are proven.

## Ethernet Standard

A733-specific Ethernet sequencing must live in Allwinner STMMAC glue code. The
public repo must not present generic STMMAC core edits as the solution for
Cubie A7S-only behavior.

Do not publish A733-only reset sequencing or DWMAC 5.20 matching changes in
generic Synopsys files such as `stmmac_main.c`, `dwmac4_lib.c`, or
`dwmac-generic.c`.

Before Ethernet is represented as an upstream candidate, the project must have:

- a binding for the Allwinner GMAC210 wrapper;
- named macros for wrapper registers and fields;
- a driver path that prepares clocks, resets, and wrapper state before common
  STMMAC code runs;
- proof of real external PHY communication;
- a boot log without DMA reset timeout noise;
- a board DTS that enables Ethernet only after the above are true.

## Commit History

Public history should read as a curated technical record.

Commit messages should:

- use imperative present tense;
- state the problem and the concrete change;
- avoid diary-style debugging notes;
- avoid phrases such as "temporary", "diagnostic-only", "do not submit", or
  "test hack" in candidate patch commits;
- disclose AI assistance where it contributed to kernel patch content.

Do not preserve trial-and-error history on public `main`. Keep that history on
private branches or local notes.

## Maintainer First Impression

A maintainer opening the public repository should see:

- no generated artifacts;
- no unreviewable patch pile;
- no hidden claim that Ethernet works;
- no generic subsystem hacks for one board;
- a clear boundary between facts, hypotheses, and future patch plans.

The standard is simple: the repository should reduce reviewer work, not create
more of it.
