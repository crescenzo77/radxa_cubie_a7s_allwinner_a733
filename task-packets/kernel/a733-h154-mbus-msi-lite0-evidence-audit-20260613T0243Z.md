# A733 H154 mbus-msi-lite0 evidence audit

Captured: 2026-06-13T02:43Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Question

Should `mbus-msi-lite0` remain in H153 patch 2, or is it an unproven extra critical clock that should be removed before upstream shaping?

## Evidence reviewed

Diagnostic commit stack on `strix:/srv/projects/a733-diag-ahbcpuscrit`:

- `027a9f9b8dda`: kept `ahb-cpus` critical for diagnosis
- `fca11ed605fd`: kept storage fabric clocks critical for diagnosis:
  - `ahb-store`
  - `mbus-msi-lite0`
  - `mbus-store`
- `b1facfb3e0ea`: pulsed the NSI update bit during CCU probe
- `8af7499f18e6`: kept NSI fabric clocks critical:
  - `nsi`
  - `bus-nsi`
- `2a9b55b6a42f`: reverted the NSI update pulse for an A/B check

UART/log evidence:

- `20260613T012948Z-a733-ahbstorecrit-fca11ed605fd-ttyUSB0.uart.log`
  - storage-fabric bundle was critical
  - `nsi` and `bus-nsi` were still disabled by the unused-clock walk
  - SDMMC0 initialized but still stopped at `Waiting for root device`
- `20260613T014946Z-a733-nsifix-b1facfb3e0ea-ttyUSB0.uart.log`
  - storage-fabric bundle plus NSI update pulse
  - `nsi` and `bus-nsi` were still disabled by the unused-clock walk
  - still stopped at `Waiting for root device`
- `20260613T015456Z-a733-nsicrit-8af7499f18e6-ttyUSB0.uart.log`
  - storage-fabric bundle plus NSI update pulse plus critical `nsi`/`bus-nsi`
  - SDMMC0 normal IDMA enumerated `mmcblk0`, saw `p1 p2 p3`, mounted root read-only, and started `/bin/sh`

Important negative evidence:

- No preserved A/B run isolates `mbus-msi-lite0` from `ahb-store` and `mbus-store`.
- The successful proof still has `mbus-msi-lite0` in the bundle, so it proves the bundle is compatible with the fix but does not prove that particular gate is necessary.
- The logs show `ahb-msi-lite0` and `bus-msi-lite0` can be disabled in the successful run; the unresolved question is only the MBUS gate `mbus-msi-lite0`.

## Recommendation

Keep H153 as the default evidence-preserving series for now:

- H153 exactly preserves the known-good diagnostic shape that reached root.
- Removing `mbus-msi-lite0` before hardware proof would create a narrower but unproven shape.
- In review/RFC text, describe `mbus-msi-lite0` honestly as part of the verified storage-fabric bundle, not as separately proven.

Use H154 as the narrowing proof candidate:

- If H154 boots to the same `mmcblk0`/root-mounted state, remove `mbus-msi-lite0` from the maintainer-facing patch 2.
- If H154 regresses to `Waiting for root device` or earlier SDMMC failure, keep `mbus-msi-lite0` and document that it was required by A/B proof.

## H154 variant artifact

Created a separate compile-checked variant that removes only `mbus-msi-lite0` from patch 2:

- Strix worktree: `/srv/projects/kernel-work/runtime/a733-ccu-nsi-no-mbus-msi-lite0-draft`
- Patch artifacts: `task-packets/kernel/a733-h154-no-mbus-msi-lite0-variant/`

Files:

- `0001-clk-sunxi-ng-a733-keep-cpus-ahb-bridge-critical.patch`
- `0002-variant-clk-sunxi-ng-a733-keep-storage-and-nsi-fabric-critical-no-mbus-msi-lite0.patch`
- `0003-clk-sunxi-ng-a733-commit-boot-programmed-nsi-state.patch`

Validation on `strix`:

- per-patch `checkpatch --strict`: pass
- final `git diff --check`: pass
- focused arm64 object build of `drivers/clk/sunxi-ng/ccu-sun60i-a733.o`: pass

H155 follow-up built this variant into a bootable, hash-validated proof package:

- readiness note: `task-packets/kernel/a733-h155-h154-proof-package-readiness-20260613T0248Z.md`
- Strix package: `/srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-d9aa2e15caae-20260613T024821Z`
- latest symlink: `/srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-latest`

## Needs approval

- Hardware proof run for H154.
- Any kernel-source commit that replaces H153 patch 2 with the H154 variant.
