# A733 H197: keep-GIC/no-CPU-peri critical split fail

Date: 2026-06-13T05:33:00Z

## Summary

H197 split the H196 pair-drop failure by keeping `gic` critical and dropping
only `cpu-peri`.

Result: H197 failed.

The kernel reached:

```text
clk: Disabling unused clocks
```

and then produced no further serial output before the capture completed. It did
not reach SDMMC0 init, `mmcblk0`, root mount, or `/bin/sh`.

This means `cpu-peri` appears required for the current Cubie3 SDMMC0/root-shell
proof. The remaining split test is to keep `cpu-peri` critical and drop only
`gic`.

## Candidate

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v2-keep-gic-no-cpuperi-critical
```

Branch:

```text
codex/a733-ccu-nsi-v2-keep-gic-no-cpuperi-critical
```

Head:

```text
09c045cd2dc1a462301a02d4b80516de24c26ce0
```

Commit:

```text
09c045cd2dc1 clk: sunxi-ng: a733: drop CPU peri from critical trial
```

Validation:

- `git diff --check HEAD~1..HEAD`: pass
- `scripts/checkpatch.pl --strict <(git format-patch --stdout -1 HEAD)`: pass, 0 errors, 0 warnings
- full arm64 `Image dtbs` build: pass
- package manifest verification: pass

## Package

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-h197-keep-gic-no-cpuperi-critical-09c045cd2dc1-20260613T052524Z
```

Hashes:

```text
68177d0f6ac856696d60b0ed6ea17d1177935ac207b3a9a0ce7b23478dcb0b14  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
d695d3ff577f0bf2f6a15f63e3cb519ae7e20af465c68c39144f15a3d3fe9db1  manifest.txt
```

The staged Cubie3 `/boot/cthu` Image, DTB, config, and manifest hashes matched
the package.

## Hardware proof

Direct U-Boot capture:

```text
/srv/projects/cubie-uart/logs/20260613T052728Z-a733-h197-keep-gic-no-cpuperi-critical-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T052728Z-a733-h197-keep-gic-no-cpuperi-critical-ttyUSB0.uart.log
```

Hashes:

```text
203f16e10e2b61dda1dbd58e49ad8d7228b741d220e5182bb73d9b06dcb0608c  20260613T052728Z-a733-h197-keep-gic-no-cpuperi-critical-ttyUSB0.uart.log
e7e1698368653324823cd237d33e0333d47a513560e639052ddca1ae8f4221b5  20260613T052728Z-a733-h197-keep-gic-no-cpuperi-critical-ttyUSB0.uart.log.json
```

Fail markers:

```text
Linux version 7.1.0-rc5-00184-g09c045cd2dc1
sun60i-a733-pinctrl 2000000.pinctrl: supply vcc-pf not found, using dummy regulator
clk: Disabling unused clocks
```

Missing pass markers:

```text
PM: genpd: Disabling unused power domains
sunxi-mmc 4020000.mmc: initialized
Waiting for root device PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e...
mmcblk0: p1 p2 p3
VFS: Mounted root (ext4 filesystem) readonly on device 179:3.
Run /bin/sh as init process
#
```

Cubie3 was power-cycled after the proof and verified back on the vendor kernel:

```text
cubie-3
5.15.147-21-a733
```

## Decision impact

H197 shows that keeping `gic` critical is not sufficient if `cpu-peri` is
dropped.

The current best hardware-proven candidate remains H195.

## Next recommended kernel action

Run the inverse split:

- H198: keep `cpu-peri` critical, drop `gic` critical.

If H198 passes, the smallest current candidate keeps `cpu-peri` critical and
drops `gic`. If H198 fails, both `gic` and `cpu-peri` are required in the
current proof shape.
