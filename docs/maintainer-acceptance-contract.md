# Maintainer Acceptance Contract

This project optimizes for Linux subsystem maintainer review, not local
bring-up convenience. Every public artifact must be shaped so it could become a
clean LKML patch series without first undoing lab history.

## Non-Negotiable Rules

1. Do not put board-specific behavior in generic subsystem code.
2. Do not publish DTS content that lacks matching YAML bindings and header IDs.
3. Do not enable hardware in board DTS files while probe is known to fail.
4. Do not publish diagnostic traces, printk storms, or register scan loops as
   candidate code.
5. Do not preserve trial-and-error history in public patch branches.
6. Do not add AI `Signed-off-by:` trailers.
7. Do disclose AI assistance for kernel patches when AI contributed to the
   final code, review, or commit text.

## Code-Policy Gap Rule

Documentation is not compliance. The candidate kernel code must obey this
contract before it is treated as public-ready.

If a branch contains code that violates this contract, mark the branch as
private lab state or local working state. Do not describe it as a candidate
series until the code, commit history, bindings, and checks match the policy.

The immediate enforcement path is:

1. isolate one subsystem at a time;
2. rebuild the branch from a clean kernel base;
3. copy only the final hardware description and driver logic;
4. discard trace commits, fixup commits, failed experiments, and mailbox
   failures;
5. add or update YAML bindings before DTS users;
6. run and record the required checks.

This avoids accumulating a larger cleanup debt while hardware bring-up
continues.

## Subsystem Boundaries

The generic STMMAC core is not the place for A733-specific sequencing.

Candidate Ethernet code must not modify generic files only to make Cubie A7S
probe:

```text
drivers/net/ethernet/stmicro/stmmac/stmmac_main.c
drivers/net/ethernet/stmicro/stmmac/dwmac4_lib.c
drivers/net/ethernet/stmicro/stmmac/dwmac-generic.c
```

A733-specific reset ordering, CCU gates, wrapper registers, syscfg fields,
delay-chain programming, PHY reference clocks, and power sequencing belong in
an Allwinner STMMAC glue driver. If the behavior is specific to the GMAC210
wrapper, the patch should introduce or extend an Allwinner glue layer instead
of teaching the generic Synopsys path about one SoC.

Generic code may be changed only for a hardware-generic defect that applies to
all users of that IP block and can be justified independently of Cubie A7S.

## Devicetree Acceptance

Devicetree describes hardware. It does not describe experiments, debugging
strategy, or local workarounds.

Candidate DTS/DTSI patches must use only:

- compatibles documented by YAML bindings;
- clock IDs documented by accepted clock bindings and headers;
- reset IDs documented by accepted reset bindings and headers;
- properties documented by the relevant subsystem binding.

Do not publish synthetic IDs such as local-only clock, reset, divider, or
`phy25mdivfix`-style properties. If a property or ID is needed, the binding and
driver support come first.

Ordering requirement:

1. Add or update YAML bindings.
2. Add clock/reset/pinctrl driver support and headers.
3. Add SoC DTSI nodes using those accepted interfaces.
4. Enable board DTS nodes only when the device probes cleanly.

## Broken Hardware Nodes

Upstream board DTS files must not create boot-time noise.

If a device is known to time out, wedge, report bogus IDs, or fail probe
noisily, the SoC DTSI may describe the disabled controller, but the board DTS
must not set it to `status = "okay"`.

For Radxa Cubie A7S:

```devicetree
&emac0 {
	status = "disabled";
};
```

GMAC0 can move to `status = "okay"` only after the wrapper, clocks, resets,
MDIO, PHY reset, PHY power, and link behavior are proven without the DMA
software reset timeout.

## Debug Code Policy

Diagnostic code is useful in private lab branches. It is not candidate code.

Public candidate code must not contain:

- `pr_info()` register dumps;
- reset polling print storms;
- hardcoded arrays of MMIO offsets for discovery;
- local trace labels such as board names or "A733 trace";
- temporary reset-order experiments;
- comments that say code is a hack, diagnostic, temporary, or not for
  submission.

If debug visibility is still useful after the final design is known, use normal
kernel mechanisms:

- `dev_dbg()` for optional driver-local messages;
- existing tracepoints where appropriate;
- named register macros in the relevant driver or header;
- concise comments explaining hardware behavior, not discovery history.

## Pinctrl Standard

The A733 pinctrl work must describe the hardware layout, not the debugging
path that discovered it.

The accepted shape should be:

- SoC-specific data for the new register layout;
- explicit bank sizing, including missing physical Port A;
- eleven structural IRQ bank slots where hardware reserves the Port A slot;
- no diagnostic W0C trace code;
- no GPIO output driving as a test mechanism;
- minimal comments that explain the missing-bank hardware rule.

Any write-one-to-clear or IRQ-bank behavior must become a normal SoC data
quirk or clean register-layout rule, not a trace patch.

## Ethernet Standard

Ethernet is not part of the first acceptable public board-support milestone.

The first public milestone should land A733/Cubie A7S platform support without
claiming Ethernet. Ethernet should be a later series after local testing proves
the GMAC210 programming model.

The Ethernet series must have this shape:

1. `dt-bindings: net: stmmac: add Allwinner A733 GMAC210`
2. `net: stmmac: add Allwinner A733 GMAC210 glue support`
3. `arm64: dts: allwinner: enable GMAC0 on Radxa Cubie A7S`

The glue driver must prepare the Allwinner wrapper before common STMMAC code
runs. It must use named macros for wrapper registers and fields, documented
clock/reset names, and a binding that describes the hardware resources.

## History Standard

Public patch branches must be curated.

Do not publish:

- sequences of trace-add, trace-adjust, trace-remove commits;
- mailbox files that failed `git am`;
- debug commits with "try", "test", "hack", or "diagnostic" in the subject;
- large histories that expose internal course corrections.

Use private branches for discovery. Before anything becomes public candidate
work, rebuild it into atomic subsystem patches.

Candidate branches must not contain `fixup!`, `squash!`, `WIP`, `try`, or
diagnostic commits. If such commits exist, the branch is still a work branch.

## Required Checks Before Candidate Publication

Before placing a patch series in the public repo, run the relevant checks:

```text
git diff --check
scripts/checkpatch.pl --strict
make dt_binding_check
make dtbs_check
```

For each patch, record which checks passed and which checks were not run. A
patch with known unresolved style, binding, or schema failures is not a public
candidate.

## Commit Message Standard

Kernel commit messages must be direct and technical.

Use:

```text
subsystem: area: add specific hardware support
```

Then state:

1. the hardware fact or missing support;
2. the minimal technical change;
3. any necessary compatibility or binding rationale.

Avoid:

- "This patch introduces";
- "diagnostic-only";
- "temporary";
- "do not submit";
- project-history summaries;
- long recaps of failed experiments.

## AI Assistance

AI can assist with analysis, drafting, cleanup, and review. It cannot certify
the Developer Certificate of Origin.

Kernel patches must not contain an AI `Signed-off-by:` trailer. A human adds
`Signed-off-by:` only after reviewing and accepting responsibility for the
patch.

If AI assistance contributed to a kernel patch, disclose it with the documented
`Assisted-by:` trailer in the final patch.
