# A733 H191 CCU/NSI clean materialization

Captured: 2026-06-13T04:30Z

## Purpose

Record the first clean maintainer-shaped materialization of the H153 default
CCU/NSI source shape after the H154 no-`mbus-msi-lite0` comparison failed and
the H189 maintainer feedback was sent.

This note is documentation only. It does not send the generated patch series,
stage hardware artifacts, reboot any Cubie, or change Hermes/model routing.

## Worktree and branch

Runtime host:

- `strix`

Clean worktree:

- `/srv/projects/kernel-work/final/a733-ccu-nsi-v1-clean`

Branch:

- `codex/a733-ccu-nsi-v1-clean`

Base:

- `d9aa2e15caae5085b51a28529fc0c35d189df543`

Commits:

- `3c11e16db36b` `clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical`
- `30fe8873a1b8` `clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical`
- `7837da282ddc` `clk: sunxi-ng: a733: commit the boot-programmed NSI clock state`

The earlier sibling branch `codex/a733-ccu-nsi-v1` exists as a scratch
materialization attempt with unwrapped commit-message paragraphs. Use
`codex/a733-ccu-nsi-v1-clean` as the current review branch.

## Source shape

The clean branch uses the H153 evidence-preserving patch 2, including
`mbus-msi-lite0`, because H188 proved the H154 no-`mbus-msi-lite0` variant
failed before SDMMC0 initialization.

Patch 1 adds the short CPUS bridge source comment recommended by H187. Patch 2
does not add a broad fabric comment, leaving the evidence and policy discussion
in the commit message. Patch 3 keeps the concise NSI update-bit probe comment.

## Generated series

Strix outgoing directory:

- `/srv/projects/kernel-work/outgoing/a733-ccu-nsi-v1-clean-20260613T0430Z/`

Canonical Mac copy:

- `/Users/enzo/projects/homelab/task-packets/kernel/a733-h191-ccu-nsi-v1-clean-series/`

Files:

- `0000-cover-letter.patch`
- `0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch`
- `0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch`
- `0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch`

SHA256:

```text
2ecdf43e2beafac89bfae06061a70c89faeb42cec8d774b24a1d110079840867  0000-cover-letter.patch
30824fd98c55caf1968aa2c689f4be2dd0e4f0fd5de25e58753f3a359263d389  0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
93ae5291e0de04b875d204b154bd4d0b254d281dc58d33eafeabbdd455843162  0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
9b45c042e9845dd284f5de0948c3312ed32eb455868c34b8828e3dc657cdb654  0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
```

## Validation

Passed:

- `git diff --check HEAD~3..HEAD`
- `scripts/checkpatch.pl --strict` on all four generated patch files,
  including the cover letter
- focused arm64 object build:
  - `drivers/clk/sunxi-ng/ccu-sun60i-a733.o`
  - output object:
    `/srv/projects/kernel-work/build/a733-ccu-nsi-v1-clean/drivers/clk/sunxi-ng/ccu-sun60i-a733.o`
- `git am` apply-check of the generated patch files in a separate temp
  worktree at base `d9aa2e15caae`
- homelab public hygiene gate on the canonical Mac patch copy:
  - `status=PASS`
  - `files_scanned=4`
  - `matches=0`
- focused private/tool/model-routing grep on the generated series:
  - no hits

Not yet done:

- b4/lore refresh after H190 to check for any replies to the sent feedback
- hardware proof of the final materialized branch
- patch publication

## Next recommended action

Refresh lore for the H189/H190 feedback thread before deciding whether to wait
for maintainer response or build a hardware-test package from the clean branch.

## Guardrails

- Continue using hosted Codex Desktop for reasoning, review, synthesis, and
  drafting.
- Do not route this kernel work through local model endpoints or OpenRouter.
- Do not use Cubie1 for proof or reproduction.
- Do not publish the H191 series until the remaining apply/lore/hardware
  readiness checks are done.
