# A733-SDMMC-H247: H245 Common Update-Bit V2 Hardware Proof

Captured: 2026-06-13T08:45Z

## Purpose

Run a controlled Cubie A7S hardware proof for the H245 common update-bit
v2-series option. H245 is the maintainer-directed fallback that moves the NSI
update-bit write into common sunxi-ng registration handling instead of keeping
an A733-only probe-time write.

This packet records a local proof result only. It is not a resend approval, not
a new public thread, and not a service, cron, mail-routing, or model-routing
change.

## Inputs

- Series artifact: `a733-h245-common-update-bit-v2-series-option`
- Base: `d9aa2e15caae`
- Applied proof head: `e694ae3fa8477846a5a6eaf31fed4813ff991d5b`
- Commit order:

```text
ab8070fb85ca clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
d9bc1f51405e clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
a6d0a4494155 clk: sunxi-ng: commit update-bit clocks during registration
e694ae3fa847 clk: sunxi-ng: a733: keep GIC and CPU peri clocks critical
```

## Built Artifact

The proof package was rebuilt from the recorded base and H245 patches with the
recorded H201/H200 configuration.

```text
Image SHA256:  ae7e03824e3d384ff5467fd1fa6eafa109beb620f60401eec3870f2f71c754bb
DTB SHA256:    6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
Config SHA256: dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202
Image size:    43244032 bytes
DTB size:      4705 bytes
```

Build result:

```text
git am --3way patches 1-4: PASS
olddefconfig: PASS
Image/DTB build: PASS
build warning/error grep: clean
```

The DTB and config hashes match the H201 exact hardware-proof hashes.

## Hardware Proof

The proof boot used the confirmed Cubie3 UART path and direct U-Boot load from
the proof staging area. The staged Image, DTB, config, and manifest hashes
matched the package before boot.

UART log basename:

```text
20260613T083956Z-a733-h247-h245-common-update-bit-v2-proof-ttyUSB0.uart.log
```

UART log SHA256:

```text
ab8df24ff27ca7ed8ef97cfe571faf640cb209934424f56a6845e23f9e38f05f
```

Pass markers observed:

```text
Linux version 7.1.0-rc5-00181-ge694ae3fa847
clk: Disabling unused clocks
PM: genpd: Disabling unused power domains
sunxi-mmc 4020000.mmc: initialized
mmc0: new high speed SDXC card
mmcblk0: p1 p2 p3
EXT4-fs (mmcblk0p3): mounted filesystem
VFS: Mounted root (ext4 filesystem) readonly on device 179:3.
Run /bin/sh as init process
/bin/sh: 0: can't access tty; job control turned off
# 
```

Negative markers:

```text
Kernel panic: absent
Bad Linux ARM64 Image magic: absent
fatal err update clk timeout: absent
```

`Waiting for root device` appeared once before normal card enumeration, then
the card enumerated and root mounted read-only. Treat this as a pass, not the
old IDMAC stall.

## Restore State

After capture, Cubie3 was power-cycled back to the vendor kernel and checked by
SSH:

```text
hostname: cubie-3
kernel: 5.15.147-21-a733
```

The proof staging area was restored to its pre-H247 H200 payload:

```text
Image SHA256:    8a159596dbfcd4e430aab6120e6860b0a25b617cefb8398e95318dbc05732a36
DTB SHA256:      6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a
Config SHA256:   dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202
Manifest SHA256: 7c2e1b8a69f3910c512c9540eb8bd98d84da4c63a12cc39338d3572a95a39051
```

An initial broad backup attempt was stopped before staging because it copied
the backup tree itself. The active proof payload was unchanged during that
attempt; cleanup removed the incomplete backup directory. The successful retry
used a bounded backup of only the active payload files.

## Interpretation

H247 proves that the H245 common update-bit v2-series option boots the Cubie
A7S through the same success boundary as H201/H200: unused-clock cleanup,
power-domain cleanup, SDMMC0 host init, SD card enumeration, read-only root
mount, and `/bin/sh`.

This does not make H245 the default resend path. H215 remains the currently
submitted narrow A733 series unless maintainers ask for common update-bit
handling. If they do, H245 now has apply, checkpatch, focused build/sparse,
full Image/DTB build, and hardware-proof coverage.

## Next Action

Keep waiting under the H219 resend gate unless sender-mailbox evidence,
confirmed delivery failure, or maintainer request changes the public-mail
decision. Technically, the maintainer-directed common-helper fallback is now
ready for a v2 prep branch if requested.
