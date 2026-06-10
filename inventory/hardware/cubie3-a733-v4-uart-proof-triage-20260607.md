# Cubie3 A733 v4 UART Proof Triage - 2026-06-07

## Scope

- Board: Cubie3 at `192.168.50.95`
- UART host: Strix at `192.168.50.11`
- UART device: `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1:1.0-port0`
- Power control: Strix `~/.local/bin/cubie3-power`, Kasa HS103 at `192.168.50.104`
- Extlinux target: `50`, `A733 v4 public candidate abc8d07b0a63 UART proof`
- Raw logs: local ignored path `tools/hardware-logs/cubie-uart/`

## Result

The automated Kasa/UART flow successfully selected extlinux option `50`, loaded
the staged A733 v4 `Image` and DTB, and captured the bootloader failure.

The kernel did not start. Vendor U-Boot failed while mutating or preparing the
mainline DTB:

```text
Retrieving file: /boot/mainline-a733-v4-abc8d07b0a63/Image
Retrieving file: /boot/mainline-a733-v4-abc8d07b0a63/sun60i-a733-cubie-a7s.dtb
## error: sunxi_update_fdt_para_for_kernel : FDT_ERR_BADPATH
sunxi_drm_kernel_para_flush for fdt_add_subnode fail
ERROR: /chosen node create failed
FDT creation failed! hanging...### ERROR ### Please RESET the board ###
```

This is not Linux runtime proof. It is bootloader/DTB handoff evidence.

## Recovery

Cubie3 was power-cycled again through the same Kasa wrapper and extlinux option
`1` was selected to return to the vendor kernel path.

## Follow-Up U-Boot Env Test

The same option `50` was tested again with `drm_debug` set as a temporary
U-Boot environment variable before running `bootcmd`:

```text
setenv drm_debug 1
run bootcmd
```

That bypassed the vendor U-Boot FDT creation hang. Linux started, brought up all
8 CPUs, initialized `ttyS0`, and initialized `sunxi-mmc 4020000.mmc`.

The next failure was later and different:

```text
Disabling rootwait; root= is invalid.
/dev/root: Can't open blockdev
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

This is meaningful runtime evidence for kernel handoff, UART, CPU topology, and
MMC controller initialization. It is still not a full boot proof because the
root filesystem was not mounted.

## Next Action

Repeat the U-Boot-env boot with a kernel-native root argument such as a concrete
block device or `PARTUUID`, instead of relying on filesystem `UUID=` without an
initramfs. Keep `drm_debug=1` as a temporary bootloader test constraint, not as
an upstream DTS or kernel patch claim.

## 2026-06-10 Follow-Up Status

This root-argument blocker is superseded. Later Cubie3 runs using Strix proved
SD card init, partition discovery, read-only EXT4 root mount to `init=/bin/sh`
when IDMA is bypassed, and several PIO enumeration rails. The active blocker is
now SDMMC0 IDMAC descriptor-fetch progress on normal block I/O.

Current work is tracked in
`task-packets/kernel/a733-hypothesis-queue.json`. As of H017, the next
responsible test is H018: replay the H016 descriptor-stamp proof without the
forced A733 64-bit DMA-mask diagnostic path. Keep `drm_debug=1` as a RAM-only
vendor U-Boot workaround and keep it out of upstream DTS.
