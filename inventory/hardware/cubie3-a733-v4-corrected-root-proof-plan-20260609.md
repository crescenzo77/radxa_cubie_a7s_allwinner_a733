# Cubie3 A733 v4 Corrected Root Proof Plan - 2026-06-09

## Scope

- Board: Cubie3 at `192.168.50.95`
- UART host: Strix at `192.168.50.11`
- UART device:
  `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1:1.0-port0`
- Kernel candidate: `candidate/a733-platform-clean-v4`
- Kernel head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- Installed boot directory:
  `/boot/mainline-a733-v4-abc8d07b0a63`
- Current extlinux entry:
  `A733 v4 public candidate abc8d07b0a63 UART proof`

This is a private lab plan. Do not copy private paths, IPs, or raw UART logs
into an upstream kernel submission.

## Evidence Reconciled

Local token-offload review cards for the older Cubie runtime evidence still
recommend re-running the current v4 extlinux label. That recommendation is now
stale because the later UART captures and manual root attempts refined the
blocker.

Current evidence:

- Plain v4 option `50` loads the exact v4 `Image` and DTB but vendor U-Boot
  fails before Linux while mutating the mainline DTB.
- `setenv drm_debug 1` in U-Boot RAM before `run bootcmd` bypasses the vendor
  DRM/FDT mutation path and starts Linux.
- With that U-Boot RAM variable, Linux reaches:
  - `Linux version 7.1.0-rc6-gabc8d07b0a63`
  - `Machine model: Radxa Cubie A7S`
  - all 8 CPUs online
  - GICv3 redistributors
  - `sun60i-a733-pinctrl 2000000.pinctrl`
  - `2500000.serial: ttyS0 ... is a 16550A`
  - `sunxi-mmc 4020000.mmc: initialized`
- The panic happens after Linux rejects
  `root=UUID=6f750720-329a-45f0-a4b5-abc5797b040a`:
  `Disabling rootwait; root= is invalid.`
- The empty partition list in that panic is not enough to blame SDMMC0 because
  Linux disables `rootwait` immediately after rejecting the filesystem UUID.
- Manual direct-load attempts with `root=/dev/mmcblk0p3` did not prove the
  corrected-root path:
  - one attempt failed U-Boot `load mmc 0:3` with `No partition table - mmc 0`
    and then `Bad Linux ARM64 Image magic`
  - another attempt fell back through extlinux and still used the old
    `root=UUID=...` append before hitting FDT creation failure

## Current Blocker

The next blocker is a clean, repeatable boot/runtime proof for the exact v4
Image and DTB using a kernel-native root path. The evidence currently points to
a bootargs/initramfs issue, not a DTS change.

Do not change the v4 DTS before this proof. The current board DTS stays within
the first-slice guardrails: UART0 and SDMMC0 only, SD-only with `no-mmc` and
`no-sdio`, no provisional `cd-gpios`, no Ethernet, no display, and no vendor
U-Boot compatibility pollution.

## Preferred Proof Label

Add a new non-default extlinux label rather than reusing the existing option
`50`. Keep the old label for comparison.

Use `PARTUUID` first because it is kernel-native and stable across device
numbering. Use `/dev/mmcblk0p3` only as a fallback if `PARTUUID` fails but the
kernel lists `mmcblk0p3`.

Recommended append line:

```text
append console=ttyS0,115200n8 earlycon=uart8250,mmio32,0x02500000 loglevel=8 ignore_loglevel drm_debug=1 root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e rootfstype=ext4 rootwait ro rootflags=noload init=/bin/sh
```

The `drm_debug=1` token in the append line is not sufficient by itself for the
vendor bootloader problem. It remains there for log visibility. The required
bootloader step is still:

```text
setenv drm_debug 1
run bootcmd
```

Then select the new `PARTUUID ro proof` label.

## Staged Installer

The corrected-root proof installer has been staged in the Cubie3 user's home
directory only:

```text
192.168.50.95:kernel-boot-artifacts/a733-v4-corrected-root-proof-20260609
```

The staged label is:

```text
a733-v4-abc8d07b0a63-partuuid-ro-proof
```

The visible U-Boot menu label is:

```text
A733 v4 abc8d07b0a63 PARTUUID ro proof
```

The staged metadata and checksums were verified with:

```sh
scripts/cubie-boot-staging-status \
  --targets 192.168.50.95 \
  --stage kernel-boot-artifacts/a733-v4-corrected-root-proof-20260609 \
  --json
```

That status currently reports `ready_for_root_install: true`,
`root_install_complete: false`, `sha256_status: ok`, `installer_syntax: ok`,
and `sudo_status: password-required`. No `/boot` files were changed while
staging this installer.

The planned `PARTUUID` was verified read-only on Cubie3 before installing the
label:

```text
hostname: cubie-3
/proc/cmdline root: UUID=6f750720-329a-45f0-a4b5-abc5797b040a
findmnt /: /dev/mmcblk0p3 ext4 rw,relatime
lsblk: mmcblk0p3 ext4 rootfs UUID=6f750720-329a-45f0-a4b5-abc5797b040a PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e MOUNTPOINT=/
/dev/disk/by-partuuid/db375e07-7682-4d4e-b8bc-a923dd0b027e -> ../../mmcblk0p3
```

This closes the pre-install review risk that the corrected proof label might
point at the wrong partition.

The next operator action is:

```sh
ssh -tt -o BatchMode=no -o ConnectTimeout=8 -i /Users/enzo/.ssh/id_ed25519 \
  radxa@192.168.50.95 \
  'cd kernel-boot-artifacts/a733-v4-corrected-root-proof-20260609 && sudo ./install-extlinux-entry.sh'
```

After the install succeeds, start the UART capture before rebooting:

```sh
ssh -tt 192.168.50.11 'cd /srv/projects/homelab && git pull --ff-only mac-mini main && scripts/cubie-uart-interactive-boot-session a733-v4-abc8d07b0a63-partuuid-ro-proof'
```

Then in U-Boot, run:

```text
setenv drm_debug 1
run bootcmd
```

and select `a733-v4-abc8d07b0a63-partuuid-ro-proof`.

## Expected Pass Evidence

Capture a UART log that shows:

- the exact v4 Image and `sun60i-a733-cubie-a7s.dtb` being loaded
- U-Boot prints `drm debug mode: 1` or otherwise proceeds past the previous
  FDT creation hang
- the deterministic proof gate can see exact Image load, exact DTB load, and
  U-Boot RAM `drm_debug` workaround evidence, not only a mid-kernel log
  fragment
- `Linux version 7.1.0-rc6-gabc8d07b0a63`
- `Machine model: Radxa Cubie A7S`
- all 8 CPUs booted
- GICv3 redistributors for CPUs 0 through 7
- A733 pinctrl initialization
- `ttyS0` registration for `2500000.serial`
- `sunxi-mmc 4020000.mmc: initialized`
- `mmcblk0` and partition 3 enumeration, or equivalent kernel partition
  listing that supports the chosen root argument
- explicit read-only root intent or mount evidence (`ro` in `/proc/cmdline` or
  a read-only `/` mount)
- a shell through `init=/bin/sh` or a root mount
- no kernel panic, Oops, or new warning that undercuts the DTS claims

Inside the shell, collect:

```sh
mount -t proc proc /proc
mount -t devtmpfs devtmpfs /dev
cat /proc/cmdline
cat /proc/partitions
dmesg | grep -E 'Linux version|Machine model|GICv3|CPU[0-7]|pinctrl|ttyS0|sunxi-mmc|mmcblk|EXT4|panic|Oops|WARNING|ERROR'
mount
```

After pulling the UART log, classify the candidate log with the deterministic
corrected-root gate before claiming runtime proof:

```sh
scripts/cubie-corrected-root-proof-gate path/to/candidate.uart.log
```

Use `--strict` in automation. The gate must report `status: pass`; old logs
that still contain `root=UUID=...`, `Bad Linux ARM64 Image magic`, panic/Oops,
or vendor FDT mutation failures are not acceptable runtime proof.
The gate also surfaces `WARNING`, `ERROR`, `WARN_ON`, `BUG:`, and call-trace
markers for human review. These do not automatically fail an otherwise complete
proof, but they must be assessed before using the log as maintainer evidence.

For the standard corrected-root label, the interactive UART helper runs this
latest-log gate automatically after pulling logs:

```sh
scripts/cubie-latest-corrected-root-proof \
  --label a733-v4-abc8d07b0a63-partuuid-ro-proof
```

Power-cycle back to the vendor kernel after capture unless the board is known
to be safe to leave at the shell.

## Fallback Proof

If `PARTUUID` and `/dev/mmcblk0p3` do not give a clean read-only shell, use a
small diagnostic initramfs with the exact same v4 Image and DTB. The initramfs
should enumerate `/sys/block`, list `/proc/partitions`, and attempt:

```sh
mount -t ext4 -o ro,noload /dev/mmcblk0p3 /mnt
```

This fallback is acceptable because older RFC v7 evidence already proved
read-only `mmcblk0p3` mounting with a diagnostic initramfs. It should be used
to isolate whether the remaining problem is block enumeration, partition
selection, filesystem mount timing, or the no-initramfs root path.

## Anti-Goals

- Do not add vendor aliases, vendor path names, `arm,sun60iw2p1`, display
  nodes, or bootloader workaround nodes to upstream DTS.
- Do not expand into Ethernet, GMAC, VPU, display, Wi-Fi, Bluetooth, USB-C, or
  PCIe for this proof.
- Do not submit local CCU/PRCM or pinctrl work independently while Junhui Liu's
  and Andre Przywara's A733 RFCs remain the active external references.
- Do not claim runtime proof from a log that only reaches the old
  `root=UUID=...` panic.
