# Upstream Submission Discipline

This project treats LKML and subsystem review as the target environment.

The public branch appearance contract is recorded in
[public-repo-expectations.md](public-repo-expectations.md).

## Repository Hygiene

The public branch must not contain:

- generated kernels, DTBs, initrds, or root filesystems;
- UART logs or compressed boot captures;
- one-off operator scripts tied to local hostnames;
- diagnostic register scans presented as production code;
- commit messages that describe experiments as if they were upstream fixes.

Generated files and local lab scripts belong outside the public branch.

## Patch Rules

Candidate patches must:

- apply cleanly with `git am`;
- build from a clean kernel tree;
- pass `git diff --check`;
- pass relevant `scripts/checkpatch.pl` checks;
- pass `make dt_binding_check` for binding changes;
- pass `make dtbs_check` for DTS changes;
- avoid `pr_info()` trace noise and ad hoc register dumps;
- use named register macros for hardware offsets;
- use `dev_dbg()` or existing tracepoints for optional debug messages;
- include a human `Signed-off-by:` trailer only after human review.

## Subsystem Boundaries

Vendor-specific A733 behavior must stay out of generic STMMAC core files.

Do not carry candidate changes that modify generic DesignWare paths only to make
Cubie A7S probe:

- `drivers/net/ethernet/stmicro/stmmac/stmmac_main.c`
- `drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c`
- `drivers/net/ethernet/stmicro/stmmac/dwmac-generic.c`

All Allwinner-specific clock, reset, wrapper, delay, syscfg, and PHY reference
clock sequencing belongs in an Allwinner glue driver, either by extending an
accepted Allwinner STMMAC glue driver or by adding a new focused driver such as
`dwmac-sun60i.c`.

The generic STMMAC core should receive only hardware-generic changes that are
valid for all users of that Synopsys IP block.

## Devicetree Rules

Devicetree patches describe hardware, not experiments or software workarounds.

Candidate DTS/DTSI changes must:

- use only clock, reset, power-domain, and compatible identifiers that are
  defined by accepted headers and bindings;
- avoid synthetic IDs copied from vendor trees before the matching CCU or reset
  controller support exists upstream;
- introduce or update YAML bindings before DTS files use new properties or
  compatible strings;
- keep disabled hardware disabled in board DTS files until it probes cleanly.

Do not mark GMAC0 as `status = "okay"` in an upstream-facing Cubie A7S board
DTS while the DMA software reset still times out. The SoC DTSI may describe the
controller, but the board DTS must leave Ethernet disabled until clock, reset,
wrapper, PHY, and MDIO behavior are proven.

## Commit Message Rules

Kernel commit messages should:

- use imperative present tense in the subject;
- state the problem first;
- describe the exact technical change;
- avoid project history unless it is necessary for review;
- avoid "diagnostic-only", "temporary", "do not submit", and similar wording in
  candidate patches;
- keep lab conclusions in cover letters or project notes, not in production
  code commits.

## Patch Split

Expected final split for an initial non-Ethernet board milestone:

1. `dt-bindings: arm: sunxi: add Radxa Cubie A7S`
2. `dt-bindings: clock: sunxi: add Allwinner A733 CCU`
3. `clk: sunxi-ng: add Allwinner A733 CCU support`
4. `dt-bindings: pinctrl: sunxi: add Allwinner A733 pin controller`
5. `pinctrl: sunxi: add Allwinner A733 pin controller support`
6. `arm64: dts: allwinner: add Allwinner A733 SoC`
7. `arm64: dts: allwinner: add Radxa Cubie A7S`

Ethernet belongs in a later series unless it is fully proven:

1. `dt-bindings: net: stmmac: add Allwinner A733 GMAC210`
2. `net: stmmac: add Allwinner A733 GMAC210 glue support`
3. `arm64: dts: allwinner: enable GMAC0 on Radxa Cubie A7S`

Each patch must be independently reviewable and routed to the right maintainers.

## AI Assistance

Linux kernel documentation permits AI-assisted work only with human
responsibility and transparency. AI agents must not add `Signed-off-by:`.
If AI assistance contributes to a kernel patch, disclose it using the documented
trailer format:

```text
Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]
```

The human submitter remains responsible for licensing, correctness, testing,
and the DCO certification.
