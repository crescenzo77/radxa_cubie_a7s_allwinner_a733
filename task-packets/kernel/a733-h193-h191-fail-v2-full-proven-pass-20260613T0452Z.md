# A733 H193: H191 failure and v2 full-proven critical pass

Date: 2026-06-13T04:52:00Z

## Summary

H191 was a clean materialization of the H153 three-patch CCU/NSI shape, but it failed direct Cubie3 hardware proof. The kernel started and then stopped immediately after:

```text
clk: Disabling unused clocks
```

It never reached SDMMC0 init, `Waiting for root device`, `mmcblk0`, root mount, or `/bin/sh`.

The earlier known-good diagnostic proof was not just H153. The actual passing diagnostic commit was `8af7499f18e6` in `/srv/projects/a733-diag-ahbcpuscrit`, and it carried additional critical clocks beyond H191:

- `pll-periph0-480M`
- `gic`
- `cpu-peri`
- `ahb-iommu0-sys`
- `ahb-iommu1-sys`

H193 created a v2 candidate that adds those proven critical clocks on top of H191. H193 passed the same direct Cubie3 U-Boot proof path and reached SDMMC0, root mount, and `/bin/sh`.

## H191 failure evidence

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v1-clean
```

Branch:

```text
codex/a733-ccu-nsi-v1-clean
```

Commits:

```text
3c11e16db36b clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
30fe8873a1b8 clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
7837da282ddc clk: sunxi-ng: a733: commit the boot-programmed NSI clock state
```

Cubie3 UART log:

```text
/srv/projects/cubie-uart/logs/20260613T043732Z-a733-h191-ccu-nsi-v1-clean-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T043732Z-a733-h191-ccu-nsi-v1-clean-ttyUSB0.uart.log
```

Hashes:

```text
70581931053726e80fcf47c5a8699e96209358c42203f028fcda7173e4d406c8  20260613T043732Z-a733-h191-ccu-nsi-v1-clean-ttyUSB0.uart.log
79d408e0b9d2f73d154558f755117f1f460d1a0a83a0434dbd5f0f61cc0a4b80  20260613T043732Z-a733-h191-ccu-nsi-v1-clean-ttyUSB0.uart.log.json
```

Observed markers:

- Linux version `7.1.0-rc5-00180-g7837da282ddc`
- last progress: `clk: Disabling unused clocks`
- no `sunxi-mmc 4020000.mmc`
- no `mmcblk0`
- no root shell

## H193 v2 pass evidence

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v2-full-proven-critical
```

Branch:

```text
codex/a733-ccu-nsi-v2-full-proven-critical
```

Commits:

```text
3c11e16db36b clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
30fe8873a1b8 clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
7837da282ddc clk: sunxi-ng: a733: commit the boot-programmed NSI clock state
ab8aba5af15c clk: sunxi-ng: a733: keep additional proven fabric clocks critical
```

Build package:

```text
/srv/projects/kernel-work/outgoing/a733-h193-ccu-nsi-v2-full-proven-critical-ab8aba5af15c-20260613T044534Z
```

Package hashes:

```text
8c1f712c87b2f702367e97e48a166bfa43fdb82311071c5d4d37d84680c29ec8  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
14affcda76f1c97710130b19e626a8ecb29251c739574b883d1059419e1cf84f  manifest.txt
```

Cubie3 UART log:

```text
/srv/projects/cubie-uart/logs/20260613T044739Z-a733-h193-ccu-nsi-v2-full-proven-critical-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T044739Z-a733-h193-ccu-nsi-v2-full-proven-critical-ttyUSB0.uart.log
```

Hashes:

```text
9615942d03e7b40e73f92b4d0b9ef14b9d136ee714db235ff05c05c171184d11  20260613T044739Z-a733-h193-ccu-nsi-v2-full-proven-critical-ttyUSB0.uart.log
45a5bec5eb655cd7eecdf4c5ed44d6247b7ccd1969a8d1977a3a790e690862b9  20260613T044739Z-a733-h193-ccu-nsi-v2-full-proven-critical-ttyUSB0.uart.log.json
```

Pass markers:

```text
Linux version 7.1.0-rc5-00181-gab8aba5af15c
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

H191/H153 is not a valid submission-ready shape because it fails the direct Cubie3 proof. H190 maintainer feedback was already sent and remains useful as a narrow evidence report, but it is now incomplete with respect to the real passing set.

H193 is the current best hardware-proven source shape. It preserves the evidence from H149/H151 while adding the extra critical clocks that were present in the actual known-good diagnostic commit.

## Next recommended kernel action

Do not send H191.

Use H193 as the parent for a narrowing pass:

1. Keep H193 intact as the known-good control.
2. Test grouped removals from the fourth commit:
   - IOMMU sys gates as one group: `ahb-iommu0-sys`, `ahb-iommu1-sys`
   - CPU/GIC/peripheral group: `gic`, `cpu-peri`, `pll-periph0-480M`
3. If a group removal still boots, split further.
4. If every removal fails, frame the upstream series as preserving a broader boot-proven fabric keepalive set and ask maintainers which clocks should instead acquire real consumers.

