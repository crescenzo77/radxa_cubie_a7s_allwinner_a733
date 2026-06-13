# A733 H262 - DTS Public-Ready Branch Send-Preview Pass

Captured UTC: 2026-06-13T09:31Z

## Purpose

Resolve the H261 b4 send-preview blocker for the A733/Cubie A7S DTS series and
replace the stale final DTS branch with a public-identity, send-preview-clean
branch.

This packet is documentation only. It is not a `b4 send`, not a `b4 send
--reflect`, not a public push, and not a hardware, service, cron, or
model-routing action.

## Changes Made

- Created a local patatt ed25519 key for the A733/Cubie A7S send path.
- Configured the final DTS repo with:
  - `patatt.signingkey = ed25519:a733-cubie-a7s`
  - `patatt.selector = a733-cubie-a7s`
- Created a new prep-managed final branch:
  - branch: `a733-dts-v1-public-ready`
  - base: `1626ce5bc85bd3faaa92877d1b65c924d86a9546`
  - head: `0356b43f505bbb3ec6a7679a49748750b37fe099`
- Preserved the previous final branch head under a local backup branch.
- Rebuilt the cover commit with the public author identity:
  `Enzo Adriano <enzo.adriano.code@gmail.com>`.
- Removed stale cover-letter wording that still described pre-mailing open
  work.
- Replaced the old b4 change-id with:
  `20260613-a733-dts-v1-public-ready-8cbb37133b64`.
- Cherry-picked the four DTS patch commits on top of the new cover commit.

The final source tree matches the previous final DTS branch exactly.

## Final Branch

```text
branch: a733-dts-v1-public-ready
base:   1626ce5bc85bd3faaa92877d1b65c924d86a9546
head:   0356b43f505bbb3ec6a7679a49748750b37fe099
```

Commit order:

```text
37bba45d5e14 arm64: dts: allwinner: add A733/Cubie A7S DTS support
ec4971061d6f dt-bindings: arm: sunxi: add Radxa Cubie A7S
5d2bcd9aae3 dt-bindings: mmc: add Allwinner A733 compatible
5f0d6a135f21 arm64: dts: allwinner: add Allwinner A733 SoC
0356b43f505b arm64: dts: allwinner: add Radxa Cubie A7S
```

## Gate Update

Updated `scripts/kernel-b4-final-gate` again so the no-send gate checks the
rendered `.eml` messages for local lab/provider markers after `b4 send -o`
successfully writes them.

The final gate now checks:

- b4 metadata gates;
- b4 dependency check;
- b4 series check;
- send-preview rendering with `b4 send -o`;
- rendered-message marker scan.

## Validation

Rerun on the public-ready branch:

```text
scripts/kernel-b4-final-gate --repo FINAL_DTS_WORKTREE
```

Result:

```text
kernel-b4-final-gate: PASS
```

Observed b4 metadata:

```text
needs-editing: False
needs-recipients: False
has-prerequisites: True
needs-auto-to-cc: False
needs-checking: False
needs-checking-deps: False
preflight-checks-failing: False
```

Send-preview header shape:

```text
From: Enzo Adriano <enzo.adriano.code@gmail.com>
Message-Id: <20260613-a733-dts-v1-public-ready-v1-0-...@gmail.com>
X-Developer-Key: i=enzo.adriano.code@gmail.com; a=ed25519;
```

Rendered-message marker scan: pass.

Source-tree equivalence against the previous final DTS branch: pass.

## Interpretation

The H261 signing blocker is resolved for no-send final-gate purposes. Gate 07
can be closed again against the new public-ready final branch. Gate 08 remains
open: no reflect copy or real send has been run.
