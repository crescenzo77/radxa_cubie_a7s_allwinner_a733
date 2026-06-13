# A733 H169 split patch readiness review

Captured: 2026-06-13T03:24Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Review the current H153/H154 split patch artifacts for maintainer-facing readiness without committing kernel source, running hardware, or sending mail.

This note is documentation only. It does not approve hardware runs, Cubie staging, `/boot` writes, kernel commits, patch publication, service changes, cron changes, or model-routing changes.

## Artifacts reviewed

H153 evidence-preserving split:

- `task-packets/kernel/a733-h153-split-series/0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch`
- `task-packets/kernel/a733-h153-split-series/0002-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical.patch`
- `task-packets/kernel/a733-h153-split-series/0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch`

H154 no-`mbus-msi-lite0` narrowing variant:

- `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch`
- `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/0002-variant-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical-no-mbus-msi-lite0.patch`
- `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch`

Related guidance:

- `task-packets/kernel/a733-h153-ccu-upstream-series-plan-20260613T0237Z.md`
- `task-packets/kernel/a733-h158-h153-h154-source-review-20260613T0257Z.md`
- `task-packets/kernel/a733-h159-h153-h154-static-refresh-20260613T0259Z.md`
- `task-packets/kernel/a733-h167-ccu-rfc-feedback-draft-v6-20260613T0318Z.txt`

## Current readiness state

The source deltas are small, focused, and already statically validated on Strix:

- H153 patch 1: `ahb-cpus` critical, one added line and one removed line.
- H153 patch 2: `nsi`, `bus-nsi`, `ahb-store`, `mbus-msi-lite0`, and `mbus-store` critical; seven added lines and five removed lines.
- H153 patch 3: defines `SUN60I_A733_NSI_REG` and pulses `CCU_SUNXI_UPDATE_BIT` during A733 CCU probe; nine added lines and one removed line.
- H154 patch 2 differs from H153 patch 2 only by leaving `mbus-msi-lite0` non-critical.

However, the H153/H154 artifacts are raw diffs, not maintainer-sendable patch emails:

- no `Subject:` headers;
- no commit message bodies;
- no `Signed-off-by`;
- no cover letter;
- no version notes;
- no recipients;
- no base-commit or dependency note.

That is acceptable for the current stage, but future work should not send or publish these files as-is.

## Upstream quality review

Patch 1 is the strongest standalone upstream fix:

- It addresses an independent boot hang during `clk_disable_unused()`.
- It has direct hardware evidence from the unused-clock walk completing after `ahb-cpus` stays enabled.
- It does not depend on the SDMMC0/NSI work.
- It can likely be reviewed separately from the storage-fabric discussion.

Patch 2 is evidence-preserving but still policy-sensitive:

- It keeps the known-good diagnostic bundle intact.
- The `mbus-msi-lite0` piece is explicitly not individually isolated.
- The maintainer-facing wording must avoid claiming that `mbus-msi-lite0` is independently proven required.
- H154 remains the cleaner candidate only if the approval-gated hardware proof passes.

Patch 3 is technically plausible but likely needs maintainer guidance:

- It commits the boot-programmed NSI mux/divider state with the existing update-bit mechanism.
- The evidence shows the pulse alone is not sufficient, but the pulse plus critical NSI/storage fabric reaches root.
- The open design question remains whether this belongs as an A733 probe fixup or as more general sunxi-ng handling for `CCU_FEATURE_UPDATE_BIT` MP clocks.

## Recommended commit flow when approved

When operator approval exists for kernel-source commits, use a dedicated Strix worktree and turn the raw diffs into real commits rather than mailing the raw files:

1. Commit patch 1 first with a full explanation of the CPUS/R-domain register access path.
2. Commit patch 2 using H153 by default, unless H154 passes hardware proof first.
3. Commit patch 3 after patch 2, preserving the update-bit nuance from H165/H167.
4. Use `git format-patch` from the resulting branch to generate mail-shaped artifacts.
5. Run checkpatch, diff hygiene, focused object build, public hygiene, and final b4/lore recipient checks before any send.

Use the H153 plan's draft commit-message bodies as the starting point, but revise them to avoid overclaiming:

- For H153 patch 2, say `mbus-msi-lite0` is part of the verified bundle, not individually proven.
- For H154 patch 2, only use the narrower statement if the H154 hardware proof passes.
- For patch 3, say no tested boot-path consumer commits NSI before SDMMC0 IDMA, and keep the `ccu_mp_set_rate()` update-bit nuance from H165.

## Current best next actions

Safe now:

- Human-review H167 and H169 together for technical wording.
- If no hardware proof is approved, prepare an explicit "send feedback before proof" decision note for H167.
- If kernel-source commit prep is approved, create real commits in a dedicated Strix worktree from H153, but do not send them.

Needs approval:

- H154 Cubie3 proof.
- Exact H153 hardware proof.
- Kernel-source commits in Strix worktrees.
- Any public reply or patch publication.

## Guardrails

- Do not use Cubie1.
- Do not stage to `/boot`, reboot, or power-cycle without explicit approval.
- Do not use local LLM lanes or OpenRouter for review, synthesis, or drafting.
- Do not send H167 or any generated patch series without explicit approval.
