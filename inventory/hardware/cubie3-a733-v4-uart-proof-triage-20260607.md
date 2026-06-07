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

## Next Action

Triage why vendor U-Boot treats the staged mainline DTB as invalid during its
FDT mutation path before repeating runtime proof. Do not claim mainline boot or
runtime success from this capture.
