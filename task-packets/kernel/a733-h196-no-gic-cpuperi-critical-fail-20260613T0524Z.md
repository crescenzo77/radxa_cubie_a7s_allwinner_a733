# A733 H196: no-GIC/no-CPU-peri critical narrowing fail

Date: 2026-06-13T05:24:00Z

## Summary

H196 tested whether the remaining extra H193 critical clocks can both be dropped
after the H195 no-IOMMU/no-PLL480 pass.

Result: H196 failed.

The kernel reached:

```text
clk: Disabling unused clocks
```

and then produced no further serial output before the capture completed. It did
not reach SDMMC0 init, `mmcblk0`, root mount, or `/bin/sh`.

This means `gic` and `cpu-peri` cannot both be dropped from H195 for the current
Cubie3 SDMMC0/root-shell proof.

## Candidate

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v2-no-extra-fabric-critical
```

Branch:

```text
codex/a733-ccu-nsi-v2-no-extra-fabric-critical
```

Head:

```text
398e9ffd4b0340fc9f5140cdf41e05d9a82e07d2
```

Commit:

```text
398e9ffd4b03 clk: sunxi-ng: a733: drop GIC and CPU peri from critical trial
```

Validation:

- `git diff --check HEAD~1..HEAD`: pass
- `scripts/checkpatch.pl --strict <(git format-patch --stdout -1 HEAD)`: pass, 0 errors, 0 warnings
- full arm64 `Image dtbs` build: pass
- package manifest verification: pass

## Package

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-h196-no-gic-cpuperi-critical-398e9ffd4b03-20260613T051650Z
```

Hashes:

```text
d505a397aa2629eca864639521fe347f904338c3fbc8fc64eaae7b7b5ef31b18  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
378a93d9aa900f3a669c0d7575ebd4e884b439781f691551f6a9ee1d1c26fe42  manifest.txt
```

The staged Cubie3 `/boot/cthu` Image, DTB, config, and manifest hashes matched
the package.

## Hardware proof

Direct U-Boot capture:

```text
/srv/projects/cubie-uart/logs/20260613T051850Z-a733-h196-no-gic-cpuperi-critical-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T051850Z-a733-h196-no-gic-cpuperi-critical-ttyUSB0.uart.log
```

Hashes:

```text
fdf2c32a79ee86cc6846a8786891c69ace0a18db46bc5dadee38e7184664e469  20260613T051850Z-a733-h196-no-gic-cpuperi-critical-ttyUSB0.uart.log
d2e39f39f860477caae97340d3f96aafe26f256824f4063e64a597ad836c7b8c  20260613T051850Z-a733-h196-no-gic-cpuperi-critical-ttyUSB0.uart.log.json
```

Fail markers:

```text
Linux version 7.1.0-rc5-00184-g398e9ffd4b03
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

H196 rules out dropping both remaining extra critical clocks together.

The current best hardware-proven candidate remains H195.

## Next recommended kernel action

Split the remaining pair:

- H197: keep `gic` critical, drop `cpu-peri` critical; or
- H197 alternate: keep `cpu-peri` critical, drop `gic` critical.

The lower-risk first split is to keep `gic` critical and drop `cpu-peri`,
because the failure happens at the global unused-clock disable boundary and GIC
is more plausibly system-critical.
