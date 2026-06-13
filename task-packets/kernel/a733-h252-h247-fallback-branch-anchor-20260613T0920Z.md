# A733-SDMMC-H252: H247 Fallback Branch Anchor

Captured: 2026-06-13T09:20Z

## Purpose

Anchor the exact H247 hardware-proven H245 common update-bit v2 fallback head as
a named kernel branch on the build host, so the fallback is not only preserved
through loose git objects and package metadata.

This is a local source-reference action only. It is not a resend approval, not
a new public thread, and not a new hardware action.

## Branch

```text
local-prefix/a733-common-update-bit-v2-h247-proof
```

Head:

```text
e694ae3fa8477846a5a6eaf31fed4813ff991d5b
```

Base:

```text
d9aa2e15caae
```

Commit order:

```text
ab8070fb85ca clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
d9bc1f51405e clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
a6d0a4494155 clk: sunxi-ng: commit update-bit clocks during registration
e694ae3fa847 clk: sunxi-ng: a733: keep GIC and CPU peri clocks critical
```

Diffstat versus base:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c | 23 +++++++++++++++--------
drivers/clk/sunxi-ng/ccu_common.c      | 21 +++++++++++++++++++++
2 files changed, 36 insertions(+), 8 deletions(-)
```

## Verification

```text
target commit exists: PASS
branch created: PASS
branch head matches H247 proof head: PASS
git diff --check base..branch: PASS
kernel source worktree status: clean
```

## Interpretation

H247 had already proved this source shape on Cubie A7S. H252 makes the exact
proven fallback easy to check out, regenerate, or compare if maintainers ask
for the common update-bit v2 path.

This does not change the public posture:

- H215 remains the submitted narrow A733 RFC/RFT series.
- H219 still gates resend or alternate public action.
- H245/H247/H249/H251/H252 remain maintainer-requested fallback material.

## Next Action

If maintainers ask for common update-bit handling, use this branch as the
source anchor for regenerating a fresh v2 candidate, then rerun the full gates
before any public use.
