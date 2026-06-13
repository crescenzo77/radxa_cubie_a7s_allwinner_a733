# A733 H198: no-GIC/keep-CPU-peri critical split fail

Date: 2026-06-13T05:42:00Z

## Summary

H198 ran the inverse split after H197 failed. It kept `cpu-peri` critical and
dropped only `gic`.

Result: H198 failed, but later than H197.

The kernel reached:

```text
clk: Disabling unused clocks
sun60i-a733-pinctrl 2000000.pinctrl: supply vcc-pf not found, using dummy regulator
PM: genpd: Disabling unused power domains
```

and then produced no further serial output before the capture completed. It did
not reach SDMMC0 init, `mmcblk0`, root mount, or `/bin/sh`.

This means `cpu-peri` alone is not enough for the current Cubie3 SDMMC0/root
proof. H195 remains the current best hardware-proven candidate, and both `gic`
and `cpu-peri` should stay critical in the current candidate shape.

## Candidate

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v2-no-gic-keep-cpuperi-critical
```

Branch:

```text
codex/a733-ccu-nsi-v2-no-gic-keep-cpuperi-critical
```

Head:

```text
83cf8c369044ada6500234a4174842268b9ca9ab
```

Commit:

```text
83cf8c369044 clk: sunxi-ng: a733: drop GIC from critical trial
```

Validation:

- `git diff --check HEAD~1..HEAD`: pass
- `scripts/checkpatch.pl --strict <(git format-patch --stdout -1 HEAD)`: pass, 0 errors, 0 warnings
- full arm64 `Image dtbs` build: pass
- package manifest verification: pass

## Package

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-h198-no-gic-keep-cpuperi-critical-83cf8c369044-20260613T053331Z
```

Hashes:

```text
d93f76f89807672ff560d6d6d86e9a2de599104f39ed72617de14f91d0ce1607  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
cce6c71cd86753f03346d2094aa6f4d625744e5e3ac2c76968ba2f76e7ea94f2  manifest.txt
```

The staged Cubie3 `/boot/cthu` Image, DTB, config, and manifest hashes matched
the package.

## Hardware proof

Direct U-Boot capture:

```text
/srv/projects/cubie-uart/logs/20260613T053536Z-a733-h198-no-gic-keep-cpuperi-critical-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T053536Z-a733-h198-no-gic-keep-cpuperi-critical-ttyUSB0.uart.log
```

Hashes:

```text
9d4009665693c97c04b4f61f2508461b76e05e2142dcdbc9562d0996eceb516f  20260613T053536Z-a733-h198-no-gic-keep-cpuperi-critical-ttyUSB0.uart.log
3835a1edb0d4a4a5293c0e4d1a27f596e412bec4d42357986a220e6dd9571f02  20260613T053536Z-a733-h198-no-gic-keep-cpuperi-critical-ttyUSB0.uart.log.json
```

Fail boundary:

```text
Linux version 7.1.0-rc5-00184-g83cf8c369044
clk: Disabling unused clocks
sun60i-a733-pinctrl 2000000.pinctrl: supply vcc-pf not found, using dummy regulator
PM: genpd: Disabling unused power domains
```

Missing pass markers:

```text
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

The H196-H198 split sequence closes the remaining extra-clock narrowing:

- H196: dropping both `gic` and `cpu-peri` fails after unused-clock disable.
- H197: keeping `gic` but dropping `cpu-peri` fails after unused-clock disable.
- H198: keeping `cpu-peri` but dropping `gic` reaches genpd disable, then fails
  before SDMMC0.

The current best hardware-proven candidate remains H195:

- `ahb-iommu0-sys` not required
- `ahb-iommu1-sys` not required
- `pll-periph0-480M` not required
- `gic` required in the current proof shape
- `cpu-peri` required in the current proof shape

## Next recommended kernel action

Stop narrowing this critical-clock set for now. Prepare a cleaned candidate based
on H195 and focus on source shape, commit messages, and upstream explanation for
why `gic` and `cpu-peri` remain critical in this A733 proof.
