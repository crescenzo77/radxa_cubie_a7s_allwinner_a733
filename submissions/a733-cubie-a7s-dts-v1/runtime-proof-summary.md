# Runtime Proof Summary

Private runtime logs were collected for the exact v4 Image and DTB used during
bring-up validation. Raw logs are intentionally not included here because they
contain local lab details that are not useful to kernel review.

Public-safe observations from the runtime proof:

- the v4 Image and DTB loaded
- Linux reported `7.1.0-rc6-gabc8d07b0a63`
- the machine model was `Radxa Cubie A7S`
- 8 CPUs were visible
- GICv3 redistributors were initialized
- A733 pinctrl and UART0 were active enough for serial console proof
- SDMMC0 enumerated storage
- `mmcblk0` partitions were discovered
- a read-only `mmcblk0p3` root mount succeeded via the corrected PARTUUID path

This proof supports the narrow claim made by the v1 series: initial serial
console and SD-card boot storage enablement. It does not claim Ethernet,
VPU/Cedrus, display, wireless, USB-C, PCIe, or other board peripherals.
