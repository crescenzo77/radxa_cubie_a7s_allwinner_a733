# A733-SDMMC-H211: H200 Public-Safe UART Proof Excerpt

Captured: 2026-06-13T06:40Z

## Purpose

Prepare a short public-safe UART proof excerpt for the H200 A733 CCU/NSI stack.
This is meant to support maintainer discussion if someone asks for evidence
that the exact H200 commit booted far enough to prove the SDMMC0 path.

This packet is not a mail draft and does not send anything.

## Proven Candidate

- Tested commit: `de486cb24c361a86cba26738f24332df780872b0`
- Kernel version marker: `7.1.0-rc5-00181-gde486cb24c36`
- Board: Radxa Cubie A7S
- Full UART log SHA256: `6f856491c5acd7652e9fcdad1a282819f47482f0a36fc73b046486ffe07c5914`
- Public-safe excerpt SHA256: `fe618e48813763fd0fa197c6ae00d6a7c17e03f957c82cb48ba6d19fd578bc2d`

## Excerpt

The builder identity in the first line has been replaced with `builder`; the
kernel version, commit marker, timestamps, and boot markers are otherwise kept
as captured.

```text
[    0.000000] Linux version 7.1.0-rc5-00181-gde486cb24c36 (builder) (aarch64-linux-gnu-gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, GNU ld (GNU Binutils for Ubuntu) 2.46) #1 SMP PREEMPT Sat Jun 13 02:09:01 EDT 2026
[    1.306227] clk: Disabling unused clocks
[    1.318762] PM: genpd: Disabling unused power domains
[    1.340182] sunxi-mmc 4020000.mmc: initialized, max. request size: 2048 KB, uses new timings mode
[    1.349157] Waiting for root device PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e...
[    1.571197] mmc0: host does not support reading read-only switch, assuming write-enable
[    1.583577] mmc0: new high speed SDXC card at address 544c
[    1.589437] mmcblk0: mmc0:544c USD00 117 GiB
[    1.599979]  mmcblk0: p1 p2 p3
[    1.622006] EXT4-fs (mmcblk0p3): orphan cleanup on readonly fs
[    1.635386] EXT4-fs (mmcblk0p3): 1 orphan inode deleted
[    1.640761] EXT4-fs (mmcblk0p3): mounted filesystem 6f750720-329a-45f0-a4b5-abc5797b040a ro without journal. Quota mode: none.
[    1.652223] VFS: Mounted root (ext4 filesystem) readonly on device 179:3.
[    1.665948] devtmpfs: mounted
[    1.669059] VFS: Pivoted into new rootfs
[    1.674118] Freeing unused kernel memory: 3392K
[    1.678786] Run /bin/sh as init process
```

## Interpretation

The excerpt proves that the exact H200 commit reached the key checkpoints that
matter for the A733 SDMMC0 investigation:

- the kernel was built from `gde486cb24c36`;
- `clk_disable_unused()` completed;
- unused power-domain disable completed;
- SDMMC0 initialized;
- the SD card was enumerated as `mmcblk0`;
- partitions were discovered;
- the root filesystem mounted read-only;
- init reached `/bin/sh`.

The full H201 proof record also notes that no `Kernel panic` or bad-image
marker was present and that the board was restored to its vendor kernel after
the proof.

## Use Rule

Use this excerpt if maintainers ask for proof details. Do not attach or paste
the full UART log without a fresh public-hygiene review, because full boot logs
often include local build identities, paths, or lab-only operational details.
