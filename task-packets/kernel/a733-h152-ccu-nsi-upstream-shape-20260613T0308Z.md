# A733 H152 CCU NSI upstream-shape candidate

Captured: 2026-06-13T03:08Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Convert the H149/H151 NSI root-cause evidence into a small upstream-facing CCU patch candidate without touching Cubie hardware and without committing kernel source.

## Kernel worktree

- Host: `strix`
- Source worktree: `/srv/projects/kernel-work/runtime/a733-ccu-nsi-upstream-shape`
- Branch: `codex/a733-ccu-nsi-upstream-shape`
- Base: `d9aa2e15caae arm64: dts: allwinner: add Radxa Cubie A7S`
- Status: one uncommitted source edit in `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`

## Patch artifact

- Homelab patch: `task-packets/kernel/a733-h152-ccu-nsi-upstream-shape.patch`
- Strix temporary copy: `/tmp/a733-h152-ccu-nsi-upstream-shape.patch`

The candidate:

- adds `SUN60I_A733_NSI_REG` for the NSI clock register at `0x580`
- marks `nsi` critical
- marks `bus-nsi` critical
- marks storage/fabric gates `ahb-store`, `ahb-cpus`, `mbus-msi-lite0`, and `mbus-store` critical
- pulses `CCU_SUNXI_UPDATE_BIT` for NSI during CCU probe so boot-firmware NSI mux/divider state is committed before fabric consumers probe

## Validation

On `strix`:

```sh
cd /srv/projects/kernel-work/runtime/a733-ccu-nsi-upstream-shape
git diff --check
scripts/checkpatch.pl --strict /tmp/a733-h152-ccu-nsi-upstream-shape.patch
make O=/srv/projects/kernel-work/build/a733-ccu-nsi-upstream-shape \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  -j$(nproc) drivers/clk/sunxi-ng/ccu-sun60i-a733.o
```

Results:

- `git diff --check`: pass
- `checkpatch --strict`: pass, no errors/warnings/checks
- focused arm64 object build: pass

## Remaining decisions

- Decide whether the upstreamable submission should be one patch or split into:
  - critical fabric/storage clocks
  - NSI update pulse
- Decide whether to test this exact H152 candidate on hardware before committing.
- Draft a commit message that ties the change to the observed failure mode without referencing private lab-only filenames as required evidence.
- Do not commit, push, or run hardware proof until explicitly approved.
