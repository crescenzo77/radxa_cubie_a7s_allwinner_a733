# Candidate Series Audit: 2026-06-04

This note records the current upstream-readiness audit for the local A733
candidate kernel series. It does not publish patch files.

## Local Kernel Branches

Current pinctrl-only cleanup branch:

```text
sources/mainline-linux-a733-upstream
candidate/a733-pinctrl-clean
```

Current CCU-only cleanup branch:

```text
sources/mainline-linux-a733-upstream
candidate/a733-ccu-clean
```

Current board-compatible cleanup branch:

```text
sources/mainline-linux-a733-upstream
candidate/a733-board-binding-clean
```

Current MMC-compatible cleanup branch:

```text
sources/mainline-linux-a733-upstream
candidate/a733-mmc-binding-clean
```

Current integrated non-Ethernet platform branch:

```text
sources/mainline-linux-a733-upstream
candidate/a733-platform-clean
```

Current broader platform work branch:

```text
sources/mainline-linux-a733-upstream
a733-cubie-a7s-series-v1-clean
```

Baseline candidate inspected:

```text
sources/mainline-linux
a733-cubie-a7s-rfc-v7-rst41-public
```

The original lab/debug branches remain local working history. They are not
public `main` material.

## Audit Result

The non-Ethernet A733/Cubie A7S candidate series is the right near-term
upstream milestone. It avoids claiming Ethernet while GMAC0 still has an
unresolved DMA software reset timeout.

The broader platform series still needs cleanup before submission:

- DTS/driver/binding changes must be split so binding patches stand alone.
- Human `Signed-off-by:` trailers must be added only after human review.
- Commit messages need to remove lab-history prose and stay focused on the
  problem and technical change.
- Pinctrl must model the structural GPIO IRQ bank layout correctly.
- The current `fixup: align A733 pinctrl IRQ bank count` commit must be folded
  into the matching binding, driver, and DTS commits before the branch can be
  treated as a candidate patch series.

## Pinctrl Correction

The cleaned local work branch now carries a checkpoint commit:

```text
pinctrl: sunxi: account for A733 missing Port A IRQ bank
```

The change aligns the candidate with the A733/A523 GPIO IRQ layout:

- physical Port A has zero pins;
- the IRQ register layout still reserves the Port A bank slot;
- the pinctrl driver registers eleven IRQ bank slots;
- the A733 DTSI includes the structural first parent interrupt before the
  Port B through Port K parent interrupts;
- the pinctrl binding allows eleven parent interrupts for this layout.

This is still a checkpoint, not a final patch shape. The binding, driver, and
DTS changes must be split or folded into the right patches before any upstream
submission.

Public candidate branches must not contain `fixup:` commits. The fixup commit
is acceptable only as local working state.

## Pinctrl-Only Cleanup Branch

The `candidate/a733-pinctrl-clean` branch now enforces the maintainer contract
for the first pinctrl slice:

- it contains only a pinctrl binding patch and a pinctrl driver patch;
- it does not touch generic STMMAC files;
- it does not contain DTS Ethernet enablement;
- it does not contain `pr_info()`, `printk()`, register scan loops, or local
  trace strings;
- it adds a dedicated
  `Documentation/devicetree/bindings/pinctrl/allwinner,sun60i-a733-pinctrl.yaml`
  binding before the driver code;
- it keeps the A733 eleven-slot IRQ bank model in normal SoC data.

Current branch shape:

```text
dt-bindings: pinctrl: add Allwinner A733 pin controller
pinctrl: sunxi: add Allwinner A733 pin controller
```

Checks run:

```text
git diff --check
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/allwinner,sun60i-a733-pinctrl.yaml
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
```

Current checkpatch findings:

- `MISSING_SIGN_OFF`: expected until Enzo performs human DCO review;
- `FILE_PATH_CHANGES`: expected for new binding and driver files covered by
  existing Allwinner/sunxi maintainer patterns.

`make dt_binding_check` now runs using Homebrew GNU Make 4.4.1, a temporary
`dtschema` virtual environment, and a detached `/tmp` worktree because the
permanent project path contains spaces. The A733 pinctrl binding and example
validated successfully. The schema run emitted unrelated global missing type
definition warnings from other in-tree bindings, but no A733 binding error.

The pinctrl driver object now compile-tests cleanly with an arm64 cross
compiler inside a temporary Docker Linux build container on `thinkcentre`.

## CCU-Only Cleanup Branch

The `candidate/a733-ccu-clean` branch isolates the second bindings-first slice:

- it contains only the A733 CCU binding/header patch and A733 CCU driver patch;
- it does not contain DTS users;
- it does not contain Ethernet or generic STMMAC changes;
- it does not contain diagnostic traces, register scans, or board-specific
  bring-up prose in production code;
- it adds
  `Documentation/devicetree/bindings/clock/allwinner,sun60i-a733-ccu.yaml`;
- it adds clock/reset header IDs only for clocks and resets represented by the
  candidate driver.

Current branch shape:

```text
dt-bindings: clock: add Allwinner A733 CCU
clk: sunxi-ng: add Allwinner A733 CCU support
```

Checks run:

```text
git diff --check
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/clock/allwinner,sun60i-a733-ccu.yaml
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- drivers/clk/sunxi-ng/ccu-sun60i-a733.o
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 drivers/clk/sunxi-ng/ccu-sun60i-a733.o
```

Current checkpatch findings:

- `MISSING_SIGN_OFF`: expected until Enzo performs human DCO review;
- `FILE_PATH_CHANGES`: expected for new binding, header, and driver files
  covered by existing Allwinner/sunxi maintainer patterns.

`make dt_binding_check` passed for the A733 CCU binding and example using
Homebrew GNU Make 4.4.1, the temporary `/tmp/a733-dtschema-venv` environment,
and a detached `/private/tmp` worktree. The run emitted unrelated global
missing type definition warnings from other in-tree bindings, but no A733 CCU
binding error.

The CCU driver object now compile-tests cleanly with an arm64 cross compiler
inside a temporary Docker Linux build container on `thinkcentre`.

## Board-Compatible Cleanup Branch

The `candidate/a733-board-binding-clean` branch isolates the Radxa Cubie A7S
board-compatible binding change:

- it contains only the `Documentation/devicetree/bindings/arm/sunxi.yaml`
  update;
- it adds `radxa,cubie-a7s` with fallback `allwinner,sun60i-a733`;
- it does not contain DTS files, driver changes, Ethernet, or diagnostics.

Current branch shape:

```text
dt-bindings: arm: sunxi: add Radxa Cubie A7S
```

Checks run:

```text
git diff --check
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/sunxi.yaml
```

Current checkpatch findings:

- `MISSING_SIGN_OFF`: expected until Enzo performs human DCO review.

`make dt_binding_check` passed for `sunxi.yaml` using Homebrew GNU Make 4.4.1,
the temporary `/tmp/a733-dtschema-venv` environment, and a detached
`/private/tmp` worktree. The run emitted unrelated global missing type
definition warnings from other in-tree bindings, but no sunxi board-compatible
binding error.

## MMC-Compatible Cleanup Branch

The `candidate/a733-mmc-binding-clean` branch isolates the MMC compatible
binding change required before DTS users:

- it contains only the
  `Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml`
  update;
- it adds `allwinner,sun60i-a733-mmc` with fallback
  `allwinner,sun20i-d1-mmc`;
- it does not contain DTS files, driver changes, Ethernet, or diagnostics.

Current branch shape:

```text
dt-bindings: mmc: add Allwinner A733 compatible
```

Checks run:

```text
git diff --check
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml
```

Current checkpatch findings:

- `MISSING_SIGN_OFF`: expected until Enzo performs human DCO review.

`make dt_binding_check` passed for the Allwinner MMC binding and example using
Homebrew GNU Make 4.4.1, the temporary `/tmp/a733-dtschema-venv` environment,
and a detached `/private/tmp` worktree. The run emitted unrelated global
missing type definition warnings from other in-tree bindings, but no A733 MMC
binding error.

## Integrated Platform Branch

The `candidate/a733-platform-clean` branch stacks the clean non-Ethernet
candidate slices and splits DTS into SoC and board patches:

```text
dt-bindings: arm: sunxi: add Radxa Cubie A7S
dt-bindings: clock: add Allwinner A733 CCU
clk: sunxi-ng: add Allwinner A733 CCU support
dt-bindings: pinctrl: add Allwinner A733 pin controller
pinctrl: sunxi: add Allwinner A733 pin controller
dt-bindings: mmc: add Allwinner A733 compatible
arm64: dts: allwinner: add Allwinner A733 SoC
arm64: dts: allwinner: add Radxa Cubie A7S
```

Current contract status:

- Ethernet is absent.
- Generic STMMAC files are untouched.
- PIO uses the eleven-parent-interrupt structural IRQ model.
- DTS users appear only after matching bindings and headers.
- Board DTS enables only UART0 and MMC0.
- No diagnostic trace code or register scans are present.

Checks run:

```text
git diff --check
git format-patch
git am
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
make ARCH=arm64 CROSS_COMPILE=aarch64-elf- defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-elf- DT_SCHEMA_FILES=allwinner,sun60i-a733-pinctrl.yaml:allwinner,sun60i-a733-ccu.yaml:allwinner,sun4i-a10-mmc.yaml:arm/sunxi.yaml CHECK_DTBS=y allwinner/sun60i-a733-cubie-a7s.dtb
dt-validate -u ./Documentation/devicetree/bindings -p ./Documentation/devicetree/bindings/processed-schema.json arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dtb
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- drivers/clk/sunxi-ng/ccu-sun60i-a733.o drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- W=1 drivers/clk/sunxi-ng/ccu-sun60i-a733.o drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
```

Current checkpatch findings:

- `MISSING_SIGN_OFF`: expected until Enzo performs human DCO review;
- `FILE_PATH_CHANGES`: expected for new binding, driver, DTSI, and DTS files;
- combined-mailbox `DT_SPLIT_BINDING_PATCH` warnings are expected when the whole
  stack is checked at once, while per-patch checks keep bindings split from DTS.

Direct local DT preprocessing and `dtc` produced a DTB for
`sun60i-a733-cubie-a7s.dts`; direct `dtc` reported the common `/soc`
`unit_address_vs_reg` warning seen when running outside the kernel make rules.

`git format-patch` exported the eight-patch stack to ignored local artifacts,
and `git am` applied those patches cleanly onto the mainline base in a detached
temporary worktree.

The integrated branch now also builds a default arm64 config and validates the
Cubie A7S DTB through the kernel `CHECK_DTBS=y` path on a temporary
case-sensitive APFS volume. That volume is required because the upstream Linux
tree has case-colliding files that cannot be materialized cleanly on the
default macOS case-insensitive filesystem. The generated DTB also passes direct
`dt-validate` against the processed in-tree schema.

The successful focused `CHECK_DTBS=y` run used `dtschema` 2024.11 and a
colon-separated `DT_SCHEMA_FILES` list. A previous attempt with a
space-separated list caused extra schema names to be passed as positional
`dt-validate` arguments; that command is not a valid check result even though
the kernel make rule masks validation failures with `|| true`.

Object compile validation now passes for the A733 CCU and pinctrl drivers in
the integrated branch using a temporary Docker Linux build container on
`thinkcentre`. The container installed GNU Make, flex, bison, libssl, libelf,
and `gcc-aarch64-linux-gnu`, then built arm64 `defconfig`, both A733 driver
objects, and the focused Cubie A7S `CHECK_DTBS=y` target.
Both A733 driver objects also pass the same remote build with `W=1`.

## Checkpatch Status

The checkpoint patch was checked with:

```text
perl scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
```

Remaining issues are expected for a checkpoint patch:

- `DT_SPLIT_BINDING_PATCH`: binding and DTS/driver changes must be separated;
- `MISSING_SIGN_OFF`: a human DCO signoff is intentionally absent until human
  review.

No whitespace errors were reported by `git diff --check`.

## Ethernet Boundary

Ethernet remains outside the initial upstream candidate series.

Do not enable GMAC0 in an upstream-facing Cubie A7S board DTS until:

- the GMAC210 wrapper programming model is defined with named registers;
- CCU clock and reset dependencies are represented by accepted bindings;
- common STMMAC code receives a stable, clocked DWMAC core;
- MDIO proves real external PHY communication;
- probe no longer reports the DMA software reset timeout.

## Feedback Enforcement Update

The latest technical feedback reinforces the existing policy gap: candidate
work must move from observing hardware to describing hardware. The public repo
and local flow now enforce these points:

- generic STMMAC core files are forbidden for A733-only Ethernet sequencing;
- any W0C pinctrl behavior must be represented as a normal SoC quirk, not
  diagnostic tracing;
- A733 pinctrl, CCU, board-compatible, and later EMAC schemas must precede DTS
  users;
- diagnostic patch stacks must be rebuilt into clean atomic candidate series;
- candidate code must be quiet during a normal boot.
