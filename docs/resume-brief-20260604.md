# Resume Brief: 2026-06-04

Use this file to resume the Radxa Cubie A7S / Allwinner A733 mainline Linux
bring-up in a new Codex Desktop chat.

## Workspace

Permanent project path:

```text
/Users/enzo/projects/Home Lab/cubie-a7s-armbian
```

Do not use or recreate the old iCloud path under
`/Users/enzo/Documents/Home Lab`.

## Standing Constraints

- Mainline Linux compatibility is the goal.
- Vendor BSPs and vendor DTBs are evidence only.
- Mainline board tests use extlinux option 5 only.
- Do not save U-Boot environment.
- Do not change vendor boot defaults.
- Do not use tmux.
- Do not drive arbitrary GPIO outputs.
- Both Cubies have fan power on physical pin 4 and ground on physical pin 9.

## Public Repository State

Public GitHub:

```text
https://github.com/crescenzo77/radxa_cubie_a7s_allwinner_a733
```

Current public `main` is documentation-only and upstream-facing. It must stay
free of generated artifacts, diagnostic patches, logs, vendor source dumps,
and WIP patch history.

Key docs:

- `docs/maintainer-acceptance-contract.md`
- `docs/project-flow.md`
- `docs/public-repo-expectations.md`
- `docs/upstream-discipline.md`
- `docs/status.md`
- `docs/evidence.md`
- `docs/candidate-series-audit-20260604.md`

## Kernel Worktrees

Original active lab tree:

```text
sources/mainline-linux
```

This tree contains many private diagnostic branches and may be dirty. Treat it
as lab state, not candidate state.

Clean candidate worktree:

```text
sources/mainline-linux-a733-upstream
```

Important branch:

```text
candidate/a733-pinctrl-clean
```

This branch currently contains a pinctrl-only cleanup series:

```text
dt-bindings: pinctrl: add Allwinner A733 pin controller
pinctrl: sunxi: add Allwinner A733 pin controller
```

It avoids Ethernet, generic STMMAC edits, diagnostic traces, register scan
loops, and DTS enablement. It adds a dedicated A733 pinctrl YAML binding and an
A733 pinctrl driver using an eleven-slot IRQ bank model. The driver object now
compile-tests cleanly with `W=1` in a Linux Docker build container on
`thinkcentre`.

Second clean branch:

```text
candidate/a733-ccu-clean
```

This branch currently contains a CCU-only cleanup series:

```text
dt-bindings: clock: add Allwinner A733 CCU
clk: sunxi-ng: add Allwinner A733 CCU support
```

It avoids DTS users, Ethernet, generic STMMAC edits, diagnostics, and
board-specific bring-up prose in production code. It adds a dedicated A733 CCU
YAML binding, clock/reset header IDs, and an A733 CCU driver slice. The driver
object now compile-tests cleanly with `W=1` in a Linux Docker build container on
`thinkcentre`.

Third clean branch:

```text
candidate/a733-board-binding-clean
```

This branch contains only the Radxa Cubie A7S board-compatible binding update:

```text
dt-bindings: arm: sunxi: add Radxa Cubie A7S
```

It adds `radxa,cubie-a7s` with fallback `allwinner,sun60i-a733` and passed
schema validation for `Documentation/devicetree/bindings/arm/sunxi.yaml`.

Fourth clean branch:

```text
candidate/a733-mmc-binding-clean
```

This branch contains only the MMC compatible binding update:

```text
dt-bindings: mmc: add Allwinner A733 compatible
```

It adds `allwinner,sun60i-a733-mmc` with fallback
`allwinner,sun20i-d1-mmc` and passed schema validation for the Allwinner MMC
binding.

Integrated non-Ethernet platform branch:

```text
candidate/a733-platform-clean
```

This branch stacks the clean binding/driver slices and splits DTS into:

```text
arm64: dts: allwinner: add Allwinner A733 SoC
arm64: dts: allwinner: add Radxa Cubie A7S
```

It keeps Ethernet absent, uses the eleven-parent-interrupt A733 PIO layout, and
enables only UART0 and MMC0 in the board DTS. `git diff --check` and per-patch
checkpatch have been run. `git format-patch` output applies cleanly with
`git am`. The branch now builds `defconfig` and validates the Cubie A7S DTB
through the kernel `CHECK_DTBS=y` path on a temporary case-sensitive APFS
volume. The generated DTB also passes direct `dt-validate` against the
processed in-tree schema. The integrated branch also compile-tests both A733
driver objects cleanly with `W=1` in the remote Linux Docker build flow. The
four binding checks also pass in that remote Linux flow, and the integrated
branch builds a full arm64 defconfig `Image`.

Checks already run:

```text
git diff --check
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/allwinner,sun60i-a733-pinctrl.yaml
```

Remaining expected issues:

- no human `Signed-off-by` yet;
- checkpatch new-file MAINTAINERS warnings;

Validation note:

- Homebrew GNU Make 4.4.1 was installed as `gmake`;
- `dt_binding_check` was run from a detached `/tmp` worktree because the
  permanent project path contains spaces;
- a temporary `/tmp/a733-dtschema-venv` Python environment supplied `dtschema`
  and `yamllint`;
- the A733 pinctrl binding and example passed schema validation.
- full Linux-tree materialization on macOS requires a temporary case-sensitive
  APFS volume because the upstream kernel contains case-colliding paths;
- focused kernel `CHECK_DTBS=y` passed with `dtschema` 2024.11 and a
  colon-separated `DT_SCHEMA_FILES` list;
- macOS object compilation is blocked at host `scripts/sorttable.o` because the
  host lacks a Linux-compatible `elf.h`;
- remote `thinkcentre` Docker provides the current compile path with
  `python:3.11-slim`, `gcc-aarch64-linux-gnu`, GNU Make, flex, bison, libssl,
  and libelf.

## Technical Status

Initial upstream milestone should be non-Ethernet A733/Cubie A7S support.
Ethernet remains a later series.

Binding inventory:

- A733 pinctrl binding exists in the clean candidate branch and passed schema
  validation.
- A733 CCU binding/header/driver work now exists in
  `candidate/a733-ccu-clean` and has passed schema and object-build
  validation.
- Radxa Cubie A7S board compatible binding now exists in
  `candidate/a733-board-binding-clean` and has passed schema validation.
- A733 MMC compatible binding now exists in `candidate/a733-mmc-binding-clean`
  and has passed schema validation.
- A733 GMAC210/EMAC binding is deferred until Ethernet is proven.

Known GMAC0 facts:

- base `0x04500000`;
- wrapper `0x04508000`;
- vendor evidence: `allwinner,sunxi-gmac-210`, `snps,dwmac-5.20`;
- DMA software reset remains stuck in local tests;
- MDIO has not proven real external PHY communication.

Do not enable GMAC0 in upstream-facing Cubie A7S DTS until the Allwinner
GMAC210 wrapper, CCU clocks, reset ordering, MDIO, PHY reset, PHY power, and
link behavior are proven. A733-specific Ethernet logic belongs in Allwinner
STMMAC glue code, not generic STMMAC core files.

## Next Best Actions

1. Continue from `sources/mainline-linux-a733-upstream` on
   `candidate/a733-pinctrl-clean`.
2. Add human review and DCO signoff when Enzo accepts responsibility for the
   pinctrl patches.
3. Keep candidate branches clean: no fixup commits, traces, generic subsystem
   hacks, or broken enabled DTS nodes.
4. After validation remains clean, prepare the non-Ethernet platform stack
   for human DCO review and eventual patch-series export.
