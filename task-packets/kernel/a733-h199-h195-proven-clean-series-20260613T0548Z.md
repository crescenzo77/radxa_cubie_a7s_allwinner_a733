# A733 H199: H195-proven clean CCU/NSI series

Date: 2026-06-13T05:48:00Z

## Summary

H199 materializes the current H195 hardware-proven source shape as a clean
four-patch review series.

H195 remains the hardware proof. H199 is the cleaner source and patch artifact:
it removes the experimental narrowing commits from the review story and keeps
only the final source state that matched H195.

## Candidate

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v3-h195-proven
```

Branch:

```text
codex/a733-ccu-nsi-v3-h195-proven
```

Head:

```text
c5b942c818a3c5027c7e2577404041569efb9e98
```

Base:

```text
d9aa2e15caae arm64: dts: allwinner: add Radxa Cubie A7S
```

## Patch series

Local copy:

```text
/Users/enzo/projects/homelab/task-packets/kernel/a733-h199-h195-proven-clean-series/
```

Strix copy:

```text
/srv/projects/kernel-work/outgoing/a733-h199-h195-proven-clean-series-c5b942c818a3-20260613T054759Z
```

Patches:

```text
0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

## Validation

- H199 final `drivers/clk/sunxi-ng/ccu-sun60i-a733.c` is source-equivalent to
  H195 for that file.
- H199 worktree status: clean.
- `git diff --check d9aa2e15caae..HEAD`: pass.
- `scripts/checkpatch.pl --strict` per generated patch: pass, 0 errors and 0
  warnings for all four patches.
- Focused arm64 object build:

```text
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  O=/srv/projects/kernel-work/build/a733-h199-proven \
  drivers/clk/sunxi-ng/ccu-sun60i-a733.o -j$(nproc)
```

Result: pass.

## Boot package

Strix package:

```text
/srv/projects/kernel-work/outgoing/a733-h199-h195-proven-clean-c5b942c818a3-20260613T055115Z
```

Hashes:

```text
8b90a489037bb531d465e39632d3a4322795d0b50849af5703f518365aab0cec  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
a718a2e9af764cc3c40e3c57fee6aa75f4816e2b5574d3b4a97bc2f71aaed8cb  manifest.txt
```

The staged Cubie3 `/boot/cthu` Image, DTB, config, and manifest hashes matched
the package.

## Hardware proof

Direct U-Boot capture:

```text
/srv/projects/cubie-uart/logs/20260613T055418Z-a733-h199-h195-proven-clean-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T055418Z-a733-h199-h195-proven-clean-ttyUSB0.uart.log
```

Hashes:

```text
5269e570c43c6c1cc7736d4a2d21faaf9071e90eb21aca421757b1c8cdf73f58  20260613T055418Z-a733-h199-h195-proven-clean-ttyUSB0.uart.log
9ef1d7c8633fdea8d7073e19b6fa47150ac124401c09da0483e5d912e3e08cf2  20260613T055418Z-a733-h199-h195-proven-clean-ttyUSB0.uart.log.json
```

Pass markers:

```text
Linux version 7.1.0-rc5-00181-gc5b942c818a3
clk: Disabling unused clocks
PM: genpd: Disabling unused power domains
sunxi-mmc 4020000.mmc: initialized, max. request size: 2048 KB, uses new timings mode
Waiting for root device PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e...
mmc0: new high speed SDXC card at address 544c
mmcblk0: mmc0:544c USD00 117 GiB
mmcblk0: p1 p2 p3
EXT4-fs (mmcblk0p3): mounted filesystem ... ro without journal
VFS: Mounted root (ext4 filesystem) readonly on device 179:3.
Run /bin/sh as init process
/bin/sh: 0: can't access tty; job control turned off
#
```

No `Kernel panic` or `Bad Linux ARM64 Image magic` marker was present.

Cubie3 was power-cycled after the proof and verified back on the vendor kernel:

```text
cubie-3
5.15.147-21-a733
```

H196-H198 remain the narrowing evidence that both `gic` and `cpu-peri` should
stay critical in this source shape.

## Decision impact

Use H199 as the current clean review/materialization artifact and current
directly hardware-proven CCU/NSI source shape.

Do not send H199 as-is without a maintainer-readiness review, dependency
thread refresh, and an explicit send decision.
