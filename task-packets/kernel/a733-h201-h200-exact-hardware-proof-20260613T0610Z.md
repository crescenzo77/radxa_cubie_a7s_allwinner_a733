# A733 H201: H200 Exact Hardware Proof

Date: 2026-06-13T06:10:00Z

## Summary

H201 proves the exact H200 maintainer-polished commit on Cubie3. This removes
the prior caveat that H200 was only source-equivalent to the H199
hardware-proven hash.

H200 is now both:

- the clean maintainer-polished patch-text series, and
- directly hardware-proven at its exact commit hash.

## Candidate

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v4-h199-maintainer-polish
```

Branch:

```text
codex/a733-ccu-nsi-v4-h199-maintainer-polish
```

Head:

```text
de486cb24c361a86cba26738f24332df780872b0
```

Base:

```text
d9aa2e15caae arm64: dts: allwinner: add Radxa Cubie A7S
```

## Build

Build directory:

```text
/srv/projects/kernel-work/build/a733-h200-h199-maintainer-polish
```

Config source:

```text
/srv/projects/kernel-work/outgoing/a733-h199-h195-proven-clean-c5b942c818a3-20260613T055115Z/config
```

Build command:

```text
make -C /srv/projects/kernel-work/final/a733-ccu-nsi-v4-h199-maintainer-polish \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  O=/srv/projects/kernel-work/build/a733-h200-h199-maintainer-polish \
  Image allwinner/sun60i-a733-cubie-a7s.dtb -j$(nproc)
```

Result: pass.

## Boot package

Strix package:

```text
/srv/projects/kernel-work/outgoing/a733-h200-h199-maintainer-polish-de486cb24c36-20260613T060929Z
```

Hashes:

```text
8a159596dbfcd4e430aab6120e6860b0a25b617cefb8398e95318dbc05732a36  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
7c2e1b8a69f3910c512c9540eb8bd98d84da4c63a12cc39338d3572a95a39051  manifest.txt
e9e88fae8f5c064c150d2ed823266bd7347fd1d23592c79158574f93861be347  sha256sums.txt
```

The staged Cubie3 `/boot/cthu` Image, DTB, config, and manifest hashes matched
the package before direct boot.

## Hardware proof

Direct U-Boot capture:

```text
/srv/projects/cubie-uart/logs/20260613T061008Z-a733-h200-h199-maintainer-polish-ttyUSB0.uart.log
```

Local copy:

```text
/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T061008Z-a733-h200-h199-maintainer-polish-ttyUSB0.uart.log
```

Hashes:

```text
6f856491c5acd7652e9fcdad1a282819f47482f0a36fc73b046486ffe07c5914  20260613T061008Z-a733-h200-h199-maintainer-polish-ttyUSB0.uart.log
a9e3616dbfd12321710269beda6e393da5cb91543851cc295da5165f5420ada1  20260613T061008Z-a733-h200-h199-maintainer-polish-ttyUSB0.uart.log.json
```

UART device:

```text
/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1.1:1.0-port0
```

Pass markers:

```text
Linux version 7.1.0-rc5-00181-gde486cb24c36
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

H200 supersedes H199 as the current best clean hardware-proven review candidate.
H199 remains useful provenance because it was the first clean hardware-proven
materialization of the H195 source shape.

The next kernel-facing action is maintainer workflow:

- refresh the already-sent H190 feedback thread for indexing or replies,
- decide whether to send a follow-up on the existing A733 CCU RFC thread using
  the H200 exact-hash proof, and
- avoid treating H200 as a normal standalone series unless the in-flight A733
  CCU/PRCM RFC dependency is intentionally handled.
