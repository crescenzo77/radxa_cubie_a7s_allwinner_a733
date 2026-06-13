# A733 H255 - Source Anchor Integrity Refresh

Captured UTC: 2026-06-13T09:10Z

## Purpose

Verify that the recorded source anchors for the submitted narrow H215 line and
the maintainer-directed H253 fallback line still exist, are based on the
recorded base, and remain mechanically reproducible from the stored patch
bundle.

This packet is documentation only. It is not a resend approval, not a new public
thread, not a source change, not a hardware action, and not a service, cron, or
model-routing change.

## Source Anchors Checked

Base:

```text
d9aa2e15caae5085b51a28529fc0c35d189df543
```

Submitted narrow H215/H200 source anchor:

```text
local-prefix/a733-ccu-nsi-v4-h199-maintainer-polish
de486cb24c361a86cba26738f24332df780872b0
```

Maintainer-directed H253/H247 common update-bit fallback source anchor:

```text
local-prefix/a733-common-update-bit-v2-h247-proof
e694ae3fa8477846a5a6eaf31fed4813ff991d5b
```

## Results

- H200 source worktree status: clean
- H200 branch head: matches `de486cb24c361a86cba26738f24332df780872b0`
- H253 fallback branch head: matches `e694ae3fa8477846a5a6eaf31fed4813ff991d5b`
- H200 merge-base with recorded base: matches `d9aa2e15caae5085b51a28529fc0c35d189df543`
- H253 fallback merge-base with recorded base: matches `d9aa2e15caae5085b51a28529fc0c35d189df543`
- H200 `git diff --check` against base: pass
- H253 fallback `git diff --check` against base: pass
- H253 patch bundle `git am --3way` from base: pass
- Applied H253 bundle `git diff --check`: pass
- Applied H253 bundle source equivalence against the H253 fallback anchor for
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.c` and
  `drivers/clk/sunxi-ng/ccu_common.c`: pass

H200 diffstat against base:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c | 35 +++++++++++++++++++++++++---------
1 file changed, 26 insertions(+), 9 deletions(-)
```

H253 fallback diffstat against base:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c | 23 +++++++++++++++--------
drivers/clk/sunxi-ng/ccu_common.c      | 21 +++++++++++++++++++++
2 files changed, 36 insertions(+), 8 deletions(-)
```

## Interpretation

The current source anchors match the recorded packet state:

- H215/H200 remains the submitted narrow, exact hardware-proven line.
- H253 remains a mechanically reproducible no-send fallback for common
  `CCU_FEATURE_UPDATE_BIT` registration-time handling.
- H219 still controls any duplicate resend or alternate public action.

The temporary apply worktree used for this check was removed after validation.
