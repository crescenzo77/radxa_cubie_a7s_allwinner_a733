# A733 H194: no-IOMMU-critical narrowing pass

Date: 2026-06-13T05:03:00Z

## Summary

H194 tested whether the two AHB IOMMU system gates from the H193 full-proven critical set are required for the direct Cubie3 root-shell proof.

Result: H194 passed.

This means the AHB IOMMU system gates can be removed from the currently hardware-proven CCU/NSI source shape:

- `ahb-iommu0-sys`
- `ahb-iommu1-sys`

The remaining extra H193 critical clocks still needing narrowing are:

- `pll-periph0-480M`
- `gic`
- `cpu-peri`

## Candidate

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v2-no-iommu-critical
```

Branch:

```text
codex/a733-ccu-nsi-v2-no-iommu-critical
```

Head:

```text
0b00b024ac6062becbf11a701d778ee7024ddda5
```

Commit:

```text
0b00b024ac60 clk: sunxi-ng: a733: drop IOMMU sys gates from critical trial
```

Validation:

- `git diff --check HEAD~1..HEAD`: pass
- `scripts/checkpatch.pl --strict <(git format-patch --stdout -1 HEAD)`: pass, 0 errors, 0 warnings
- full arm64 `Image dtbs` build: pass
- package manifest verification: pass

## Package

Artifact:

```text
/srv/projects/kernel-work/outgoing/a733-h194-no-iommu-critical-0b00b024ac60-20260613T045620Z
```

Hashes:

```text
ab20d6da0e622be0d940c6e32f7e7fd559de86e01f0ff743dddea50400f02e99  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
7a014bc31259fe22165c5942a2d81e00604797d5a1177baec316f66d48b0b8b7  manifest.txt
```

The staged Cubie3 `/boot/cthu` Image, DTB, config, and manifest hashes matched the package.

## Hardware proof

Direct U-Boot capture:

```text
/srv/projects/cubie-uart/logs/20260613T045828Z-a733-h194-no-iommu-critical-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T045828Z-a733-h194-no-iommu-critical-ttyUSB0.uart.log
```

Hashes:

```text
dd9d042a110ff49a3681458a33faa40f288c8346a82aeb00a6b9f7ec22d4efb0  20260613T045828Z-a733-h194-no-iommu-critical-ttyUSB0.uart.log
1b774af1d82a808ca486c993a88e40de5406c6b5a61ac6a7888d026295bc6c99  20260613T045828Z-a733-h194-no-iommu-critical-ttyUSB0.uart.log.json
```

Pass markers:

```text
Linux version 7.1.0-rc5-00182-g0b00b024ac60
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

## Decision impact

H194 narrows H193. The IOMMU AHB sys gates are not required for the current SDMMC0/root-shell proof and should not remain in the minimal candidate unless later testing finds a separate need.

The current best hardware-proven candidate is H194, not H193 and not H191.

## Next recommended kernel action

Use H194 as the known-good parent for the next narrowing pass.

Next candidate should test the CPU/GIC/peripheral-parent group:

- remove `pll-periph0-480M`, `gic`, and `cpu-peri` critical flags together, or
- remove just `pll-periph0-480M` first if we want the smallest possible attribution step.

