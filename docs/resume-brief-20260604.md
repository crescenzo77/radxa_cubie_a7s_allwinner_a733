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
A733 pinctrl driver using an eleven-slot IRQ bank model.

Checks already run:

```text
git diff --check
scripts/checkpatch.pl --no-tree --strict --summary-file --show-types
```

Remaining expected issues:

- no human `Signed-off-by` yet;
- checkpatch new-file MAINTAINERS warnings;
- `dt_binding_check` could not run on the Mac because system GNU Make is 3.81
  and the kernel requires GNU Make 4.0 or newer.

## Technical Status

Initial upstream milestone should be non-Ethernet A733/Cubie A7S support.
Ethernet remains a later series.

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
2. Install or use a host with GNU Make 4.0+ and run DT schema validation for
   the A733 pinctrl binding.
3. Address any real schema/checkpatch findings.
4. Keep candidate branches clean: no fixup commits, traces, generic subsystem
   hacks, or broken enabled DTS nodes.
5. Only after pinctrl is clean, build the next isolated candidate slice
   (likely CCU or initial DTS), following bindings-first order.
