# A733 H188 H154 no-mbus-msi-lite0 proof result

Captured: 2026-06-13T06:20Z

## Purpose

Record the Cubie3 hardware proof result for the H154 no-`mbus-msi-lite0`
comparison package.

This note records a completed hardware proof. It does not approve sending
mail, publishing patches, creating kernel-source commits, additional hardware
runs, service changes, cron changes, or model-routing changes.

## Result

H154 failed.

The H154 kernel started, but the UART log went silent immediately after:

```text
clk: Disabling unused clocks
```

The log did not reach:

- `sunxi-mmc 4020000.mmc: initialized`
- `Waiting for root device`
- `mmc0: new high speed SDXC card`
- `mmcblk0`
- `mmcblk0: p1 p2 p3`
- read-only root mount
- `/bin/sh`

Therefore H154 does not satisfy the H157 pass criteria.

## Evidence

Copied evidence files:

- `tools/hardware-logs/cubie-uart/20260613T041101Z-a733-h154-no-mbus-msi-lite0-ttyUSB0.uart.log`
- `tools/hardware-logs/cubie-uart/`
  `20260613T041101Z-a733-h154-no-mbus-msi-lite0-ttyUSB0.uart.log.json`

Hashes:

```text
log:
  160fceef58b771d4bb9480c18fe8b8d2e1d923b8833edef7769a8550e5094bd5
metadata:
  f646ca282f5c59435c647145e3ea4dc9cac77e64a2430a2fe98caf3053c4f4f5
```

Key metadata:

```text
label: a733-h154-no-mbus-msi-lite0
device: Cubie3 UART by-path adapter resolving to ttyUSB0
capture_seconds: 180
exit_code: 0
```

The helper exit code only means the requested capture completed. It does not
mean the kernel passed.

## Proof details

Before the proof run:

- the H154 package manifest and file hashes were rechecked;
- the target board identity was checked as Cubie3;
- the H154 `Image`, DTB, config, and manifest were staged to the existing
  Cubie3 proof payload path;
- the staged `Image`, DTB, config, and manifest hashes were checked.

The first helper invocation failed before boot because its default UART path
was stale. The proof was rerun with the confirmed Cubie3 UART by-path adapter.

The proof log shows:

- U-Boot loaded the staged H154 `Image`;
- U-Boot loaded the staged H154 DTB;
- `fdt addr` succeeded;
- `booti` started the kernel;
- Linux reported version `7.1.0-rc5-00177-gd9aa2e15caae-dirty`;
- the last kernel progress marker was `clk: Disabling unused clocks`;
- no later SDMMC0 or root-device markers appeared during the capture.

## Restoration

After the proof run, Cubie3 was power-cycled and verified back on the vendor
kernel:

```text
hostname: cubie-3
kernel: 5.15.147-21-a733
```

## Interpretation

H154 differs from H153 by omitting the `mbus-msi-lite0` critical marker from
patch 2. In this tested shape, removing that marker does not merely fail later
at root-device discovery; it prevents the boot from progressing past the
unused-clock walk.

H153 therefore remains the evidence-preserving default for materialization.
Future maintainer-facing wording can now be stronger than the earlier caveat:
the no-`mbus-msi-lite0` comparison failed on Cubie3, so `mbus-msi-lite0`
should remain in the current tested bundle unless maintainers prefer a
different fabric model.

## Follow-up

- Keep H153 patch 2 as the default.
- Do not use the H154 patch-2 variant for maintainer materialization.
- Update H176 or its successor before sending so the `mbus-msi-lite0` wording
  reflects the failed H154 comparison.
- If generated commits are created later, use a fresh worktree and the H153
  patch set.

## Guardrails

- Do not run another H154 proof without a new reason.
- Do not use Cubie1.
- Do not send H176 unchanged after this result.
- Do not create kernel-source commits from the dirty runtime worktrees.
