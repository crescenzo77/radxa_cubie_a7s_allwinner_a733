# A733 H186 materialization preflight review

Captured: 2026-06-13T05:35Z

## Purpose

Review the H153/H154 CCU/NSI raw diff artifacts before any future
maintainer-materialization pass.

This note is documentation only. It does not approve kernel-source commits,
hardware runs, Cubie staging, patch publication, sending mail, service changes,
cron changes, or model-routing changes.

## Artifacts reviewed

H153 evidence-preserving split:

- `task-packets/kernel/a733-h153-split-series/`
  `0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch`
- `task-packets/kernel/a733-h153-split-series/`
  `0002-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical.patch`
- `task-packets/kernel/a733-h153-split-series/`
  `0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch`

H154 no-`mbus-msi-lite0` variant:

- `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/`
  `0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch`
- `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/`
  `0002-variant-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical-no-mbus-msi-lite0.patch`
- `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/`
  `0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch`

## Artifact-level checks

Both H153 and H154 contain exactly three raw diff files.

All six raw diffs touch only:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c
```

None of the six raw diffs has:

- a `Subject:` header;
- a `Signed-off-by:` trailer.

This matches H169: these files are source deltas, not mail-ready patches.

## Diff size summary

H153:

```text
0001: 1 insertion, 1 deletion
0002: 7 insertions, 5 deletions
0003: 11 insertions, 1 deletion
```

H154:

```text
0001: 1 insertion, 1 deletion
0002: 6 insertions, 4 deletions
0003: 11 insertions, 1 deletion
```

## Variant comparison

H153 and H154 patch 1 are byte-identical.

H153 and H154 patch 3 have the same source hunk. Their only observed
difference is the git index metadata caused by the different patch-2 parent.

Patch 2 is the only source-policy difference:

- H153 keeps `mbus-msi-lite0` in the critical bundle.
- H154 leaves `mbus-msi-lite0` non-critical.

Therefore the H179 decision rule still holds:

- default to H153;
- switch patch 2 to H154 only if the H157 hardware proof passes and a result
  packet records the pass.

## Worktree status check

A read-only status check of the existing build-host runtime trees showed that
the current upstream-shape, split-draft, and no-`mbus-msi-lite0` draft trees
all have local modifications in:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c
```

That is expected for diagnostic/runtime artifacts, but it reinforces the H179
rule: future maintainer materialization must use a fresh dedicated worktree,
not an existing dirty runtime tree.

## Materialization readiness

When explicit kernel-source commit approval exists, the future materialization
pass should:

- create a fresh dedicated worktree from a rechecked base;
- apply H153 patch 1 first;
- apply H153 patch 2 by default;
- substitute H154 patch 2 only if H154 hardware proof passes first;
- apply the matching patch 3 after the selected patch 2;
- use H170 as commit-message starting text;
- create real signed commits;
- generate patches with `git format-patch`;
- rerun diff, checkpatch, object-build, public-hygiene, and live-thread
  checks before any send.

## Guardrails

- Do not create the materialization worktree without explicit approval.
- Do not create kernel-source commits without explicit approval.
- Do not send generated patches without explicit approval.
- Do not use Cubie1.
- Do not treat H154 as the default unless the H157 proof passes.
