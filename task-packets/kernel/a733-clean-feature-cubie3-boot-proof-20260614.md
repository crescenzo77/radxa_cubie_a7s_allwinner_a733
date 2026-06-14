# A733 Clean Feature Kernel Cubie3 Boot Proof

Status: local hardware proof; direct U-Boot load passes, extlinux menu path held
Date: 2026-06-14

## Scope

This packet records the first Cubie3 runtime proof for the clean broad-feature
A733 kernel build.

Target:

```text
board=cubie3
ip=192.168.50.95
uart_host=strix
uart_device=/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1.1:1.0-port0
```

Artifacts:

```text
source=/srv/projects/kernel-work/outgoing/a733-clean-feature-20260614
installed_boot_dir=/boot/mainline-a733-clean-feature-20260614
installed_modules=/lib/modules/7.1.0-rc5-a733-clean-feature-00177-g68d5a36e1dc5
```

Hashes:

```text
64d2cd3c28ff2ef4a3c3086b9d5a52a867e84a481161e374dbb8ae31f3b00152  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
a08a82ddfc83d5860420899797ef0baf3376addcae802939dc978190e4c5eb08  config
```

## Result

Direct U-Boot load succeeded with the clean kernel and DTB:

```text
Linux version 7.1.0-rc5-a733-clean-feature-00177-g68d5a36e1dc5
Machine model: Radxa Cubie A7S
root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e
VFS: Mounted root (ext4 filesystem) on device 179:3.
Debian GNU/Linux 11 cubie-3 ttyS0
cubie-3 login:
```

Proof log:

```text
/srv/projects/cubie-uart/logs/20260614T043552Z-a733-clean-feature-20260614-partuuid-rw-ttyUSB0.uart.log
sha256=2c3653dc14be90348b6efdf347bb43d47a69448b0b96cab21c2acb5daa54b004
```

Direct-load command shape:

```text
ext4load mmc 0:3 0x40080000 /boot/mainline-a733-clean-feature-20260614/Image
ext4load mmc 0:3 0x4fa00000 /boot/mainline-a733-clean-feature-20260614/sun60i-a733-cubie-a7s.dtb
fdt addr 0x4fa00000
setenv bootargs console=ttyS0,115200n8 earlycon=uart8250,mmio32,0x02500000 loglevel=8 ignore_loglevel clk_ignore_unused root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e rootfstype=ext4 rootwait rw
booti 0x40080000 - 0x4fa00000
```

## Negative Findings

The first direct-load attempt used the vendor-root UUID form and failed:

```text
root=UUID=6f750720-329a-45f0-a4b5-abc5797b040a
VFS: Cannot open root device "UUID=6f750720-329a-45f0-a4b5-abc5797b040a"
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

Failed log:

```text
/srv/projects/cubie-uart/logs/20260614T043227Z-a733-clean-feature-20260614-direct-ttyUSB0.uart.log
sha256=7693d053afcbe96deb65593dbf17d816b55519f153cdb8439bc8cf5be061884a
```

The extlinux menu path is held. Selecting the clean feature entry through
U-Boot extlinux caused U-Boot FDT handling errors and a hang before Linux:

```text
FDT creation failed! hanging...### ERROR ### Please RESET the board ###
```

Extlinux failure log:

```text
/srv/projects/cubie-uart/logs/20260614T044124Z-a733-clean-feature-20260614-extlinux-item4-ttyUSB0.uart.log
sha256=4b1313452ac4fab79673f7a85b898d3e7a23ea29167e64a7f96165ebf20c896b
```

The unsafe clean-feature extlinux label was removed after this test. The
installed files and modules remain for direct-load testing.

## Recovery State

Cubie3 was power-cycled back to the vendor default after proof and after the
extlinux failure:

```text
hostname=cubie-3
kernel=5.15.147-21-a733
default_extlinux=vendor
```

Current `/boot/extlinux/extlinux.conf` no longer contains
`a733-clean-feature-20260614`.

## Feature Boundary

This proof establishes mainline kernel boot to userspace on Cubie3 with serial
console, SD root, RTC registration, pinctrl initialization, MMC root mount, and
matching staged modules. It does not prove Ethernet, Wi-Fi, Bluetooth, PCIe,
NVMe, display, media, NPU, RISC-V MCU, or other peripheral enablement. Those
remain separate DTS/driver/proof tasks.
