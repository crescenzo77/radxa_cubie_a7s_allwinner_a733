# A733 H184 H154 proof package freshness recheck

Captured: 2026-06-13T05:15Z

## Purpose

Refresh the H154 no-`mbus-msi-lite0` proof package state before any decision
to run the approval-gated Cubie3 hardware proof.

This note is documentation only. It does not approve hardware runs, Cubie
staging, `/boot` writes, kernel commits, patch publication, service changes,
cron changes, or model-routing changes.

## Read-only check

On the build host, the latest H154 symlink still resolves to the expected
package identity:

```text
a733-h154-no-mbus-msi-lite0-d9aa2e15caae-20260613T024821Z
```

The package directory contains:

- `Image`
- `sun60i-a733-cubie-a7s.dtb`
- `config`
- `build.log`
- `source.diff`
- `source-status.txt`
- `manifest.txt`
- `manifest.txt.sha256`

## Hash validation

The manifest hash check passed:

```text
manifest.txt: OK
```

The package file checks passed:

```text
Image: OK
sun60i-a733-cubie-a7s.dtb: OK
config: OK
build.log: OK
source.diff: OK
source-status.txt: OK
```

Observed file sizes:

```text
43309568 Image
    4705 sun60i-a733-cubie-a7s.dtb
  321548 config
  219728 build.log
    2522 source.diff
      42 source-status.txt
    1602 manifest.txt
     172 manifest.txt.sha256
```

## Worktree state

The H154 runtime worktree still reports:

```text
M  drivers/clk/sunxi-ng/ccu-sun60i-a733.c
```

This is expected for the prepared comparison artifact, but it reinforces the
H179 rule: do not reuse this runtime worktree for maintainer materialization.
Future sendable patches must be made as real commits in a fresh dedicated
worktree.

## Current decision impact

H184 does not change the H157 approval gate. It only confirms that the exact
H154 package referenced by H155 is still present and hash-valid.

If the operator chooses to run H154 before sending H176, the H157 command
sequence remains the approval-gated path. If H154 is not run first, H176 can
still be sent with the existing `mbus-msi-lite0` caveat after explicit send
approval.

## Guardrails

- Do not stage this package to Cubie3 without explicit operator approval.
- Do not run the direct U-Boot proof without explicit operator approval.
- Do not use Cubie1.
- Do not commit kernel source from the H154 runtime worktree.
- Do not send H176 based on this note alone.
