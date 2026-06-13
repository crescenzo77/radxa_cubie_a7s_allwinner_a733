# A733 H179 CCU/NSI materialization handoff

Captured: 2026-06-13T04:15Z

## Purpose

Prepare the next maintainer-facing kernel-source step for the A733 CCU/NSI
work without creating kernel commits, running hardware, or sending mail.

This note turns the H153/H154 raw diffs and H170 commit-message draft into an
exact handoff for a future approved commit/format-patch pass.

This note is documentation only. It does not approve kernel-source commits,
hardware runs, Cubie staging, `/boot` writes, patch publication, service
changes, cron changes, or model-routing changes.

This is an internal lab handoff. It intentionally contains private Strix paths
and must not be treated as a public mailing-list artifact.

## Current evidence base

Use these records as the source of truth:

- H153 raw split series:
  `task-packets/kernel/a733-h153-split-series/`
- H154 no-`mbus-msi-lite0` variant:
  `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/`
- H158 source comparison:
  `task-packets/kernel/a733-h158-h153-h154-source-review-20260613T0257Z.md`
- H159 static validation:
  `task-packets/kernel/a733-h159-h153-h154-static-refresh-20260613T0259Z.md`
- H169 readiness review:
  `task-packets/kernel/a733-h169-split-patch-readiness-review-20260613T0324Z.md`
- H170 commit-message draft:
  `task-packets/kernel/a733-h170-ccu-nsi-commit-message-draft-20260613T0329Z.md`
- H171 NSI update-bit design review:
  `task-packets/kernel/a733-h171-nsi-update-bit-design-review-20260613T0335Z.md`
- H176 current maintainer feedback send-candidate:
  `task-packets/kernel/a733-h176-ccu-rfc-feedback-send-candidate-20260613T0355Z.txt`

## Read-only Strix state observed

Relevant Strix trees exist:

- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-upstream-shape`
- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-split-draft`
- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-no-mbus-msi-lite0-draft`
- `/srv/projects/a733-diag-ahbcpuscrit`

Important caution:

- `/srv/projects/kernel-work/runtime/a733-ccu-nsi-upstream-shape` is dirty in
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`.
- `/srv/projects/a733-diag-ahbcpuscrit` contains useful diagnostic commits, but
  it is not the maintainer materialization worktree.

Therefore, future commit prep should use a fresh dedicated worktree or clean
clone, not any existing dirty runtime tree.

## Patch selection rule

Default materialization path:

- Use H153 patch 1.
- Use H153 patch 2.
- Use H153 patch 3.

Only switch patch 2 to the H154 no-`mbus-msi-lite0` variant if the explicit
H157 one-shot Cubie3 proof passes and a follow-up result packet records that
pass. Without that proof, H153 remains the evidence-preserving default.

## Future approved command shape

Use this only after explicit approval for kernel-source commit prep.

```sh
ssh strix
cd /srv/projects/kernel-work

# Pick a clean base. The exact base must be rechecked before use.
git -C /srv/projects/kernel-work/runtime/a733-ccu-nsi-upstream-shape \
  rev-parse HEAD

# Create a fresh worktree; do not reuse dirty runtime trees.
git -C /srv/projects/kernel-work/runtime/a733-ccu-nsi-upstream-shape \
  worktree add /srv/projects/kernel-work/final/a733-ccu-nsi-v1 \
  -b codex/a733-ccu-nsi-v1 HEAD

cd /srv/projects/kernel-work/final/a733-ccu-nsi-v1
git status --short
```

Then apply the selected raw diffs one at a time, commit each with the H170
message bodies, and regenerate patches:

```sh
git apply --check /path/to/0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch
git apply /path/to/0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch
git diff --check
git commit -s

git apply --check /path/to/0002-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical.patch
git apply /path/to/0002-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical.patch
git diff --check
git commit -s

git apply --check /path/to/0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch
git apply /path/to/0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch
git diff --check
git commit -s

mkdir -p /srv/projects/kernel-work/outgoing/a733-ccu-nsi-v1-patches
git format-patch --cover-letter \
  -o /srv/projects/kernel-work/outgoing/a733-ccu-nsi-v1-patches \
  HEAD~3..HEAD
```

The `/path/to/...` values should be the synced homelab task-packet paths on
Strix, not copied from a chat transcript.

## Commit-message requirements

Patch 1:

- explain `ahb-cpus` as the CPU-visible bridge to R-CCU/RTC register access;
- avoid saying this is an SDMMC0 fix;
- include hardware-tested language from H170.

Patch 2:

- if using H153, say `mbus-msi-lite0` was part of the verified bundle, not
  independently proven required;
- if using H154, say `mbus-msi-lite0` was omitted only because the H154 proof
  passed;
- ask maintainers, in cover or reply context, whether critical clocks or a
  more explicit fabric model is preferred.

Patch 3:

- explain that the NSI update bit is self-clearing;
- state that no tested boot-path consumer committed NSI before SDMMC0 normal
  IDMA needed the fabric;
- preserve the H171 design question: A733 probe fixup versus common
  registration-time handling for `CCU_FEATURE_UPDATE_BIT` MP clocks.

## Post-materialization gates

After real commits exist, run at minimum:

```sh
git status --short
git diff --check HEAD~3..HEAD
scripts/checkpatch.pl --strict /srv/projects/kernel-work/outgoing/a733-ccu-nsi-v1-patches/*.patch
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- drivers/clk/sunxi-ng/ccu-sun60i-a733.o
```

Then copy generated patches back to the homelab repo as task-packet artifacts
and run:

```sh
scripts/kernel-public-hygiene-gate <generated-patch-directory>
```

Before any send, repeat the live b4/lore recipient and thread recheck.

## Approval boundary

Safe now:

- review this handoff;
- review H176 wording;
- run read-only status and static validation checks.

Needs explicit approval:

- creating the fresh Strix worktree branch;
- applying diffs and creating kernel commits;
- running H154 hardware proof;
- sending H176;
- sending or publishing generated patch series.

## Guardrails

- Do not use Cubie1.
- Do not reuse dirty diagnostic or runtime trees for maintainer artifacts.
- Do not stage to `/boot`, reboot, power-cycle, or open UART proof sessions
  without explicit approval.
- Do not route this work through local model endpoints or OpenRouter.
- Do not send mail or publish patches without explicit approval.
