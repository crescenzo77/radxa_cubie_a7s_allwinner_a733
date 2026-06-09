# A733 / Cubie A7S Thread Quick Reference - 2026-06-08

Purpose: compact restart context for continuing Radxa Cubie A7S / Allwinner
A733 kernel patch work in this Codex thread. This is a private lab reference,
not a public submission artifact.

## Current Repositories

- Private workflow repo: `/Users/enzo/projects/homelab`
- Public-facing repo: `/Users/enzo/projects/Home Lab/cubie-a7s-armbian`
- Public GitHub record: `https://github.com/crescenzo77/radxa_cubie_a7s_allwinner_a733`
- Candidate Linux fork/branch referenced by public docs:
  - fork: `https://github.com/crescenzo77/linux.git`
  - branch: `candidate/a733-platform-clean-v4`
  - head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- Public repo is documentation/patch-export facing. Keep raw UART logs, model
  reviews, private topology, generated images, DTBs, and scratch notes out of
  it.

## Hardware Map

- Cubie2: `192.168.50.85`
  - A733 target, staged artifacts present, `/boot` entry not installed in the
    latest gate output.
  - Kasa wrapper on Strix: `~/.local/bin/cubie2-power`
  - Kasa plug IP: `192.168.50.74`
- Cubie3: `192.168.50.95`
  - Active proof target.
  - Exact A733 v4 boot entry installed.
  - Extlinux test entry is menu choice `50`.
  - Kasa wrapper on Strix: `~/.local/bin/cubie3-power`
  - Kasa plug IP: `192.168.50.104`
- Excluded target: `192.168.50.65`
  - Do not use for kernel work. It is reserved for Wyze/object detection.
- UART host: Strix `192.168.50.11`
  - Cubie3 UART: `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1:1.0-port0`
    -> `/dev/ttyUSB0`
  - The other CP2102 path exists at `...usb-0:1.2...` -> `/dev/ttyUSB1`, but
    Cubie2 UART proof remains weaker.

## Current Boot Artifact

AMD artifact directory:

```text
/srv/projects/kernel-work/outgoing/a733-v4-abc8d07b0a63-20260606T152409Z
```

Manifest essentials:

```text
kernel_head=abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e
Image sha256=b4584f230d436235fb3776a102546e05d8fac1d93206d25f3566aedad7e60b7d
DTB sha256=9ac58728715b7999bda4fe579bb00a4c9da7f123c7d0fb1bf9e4664cd85a0e44
config sha256=9273c649385ba95c589c9f4867a77addebb7bf39ac7a7bb3d655d4980eb7ca87
DTB size=4165 bytes
```

Cubie3 extlinux entry:

```text
50: A733 v4 public candidate abc8d07b0a63 UART proof
```

## Most Recent Hardware Result

Tracked note:

```text
inventory/hardware/cubie3-a733-v4-uart-proof-triage-20260607.md
```

Summary:

- Plain extlinux option `50` loads Image/DTB but vendor U-Boot fails before
  Linux with FDT mutation errors:
  - `sunxi_update_fdt_para_for_kernel : FDT_ERR_BADPATH`
  - `sunxi_drm_kernel_para_flush for fdt_add_subnode fail`
  - `/chosen node create failed`
- Retesting option `50` after interrupting U-Boot and running:

```text
setenv drm_debug 1
run bootcmd
```

  bypasses the vendor DRM/FDT mutation failure.
- With that temporary U-Boot env var, Linux starts, brings up 8 CPUs,
  initializes `ttyS0`, and initializes `sunxi-mmc 4020000.mmc`.
- It then panics because the extlinux entry uses filesystem `UUID=...` without
  an initramfs:

```text
Disabling rootwait; root= is invalid.
/dev/root: Can't open blockdev
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```

Practical next proof action: repeat the successful U-Boot-env boot with a
kernel-native root argument such as `/dev/mmcblk0p3` or `PARTUUID=...`.

Important nuance: `drm_debug=1` must be set in U-Boot RAM. Putting it only in
Linux bootargs is not enough to bypass the vendor U-Boot DRM/FDT path.

## Historical Boot Lessons From Strix

High-value Strix source:

```text
192.168.50.11:/srv/projects/cubie-a7s-local-agent
```

Key files:

- `A733_UNCERTAINTY_REGISTER_20260530.md`
- `MAINLINE_RFC_V7_BOOT_STAGING_20260530.md`
- `VENDOR_UBOOT_DTB_HANDOFF_ANALYSIS_20260531.md`
- `VENDOR_UBOOT_SOURCE_INSPECTION_20260601.md`
- `artifacts/uart/README.md`
- `artifacts/test-dtb/README.md`

Useful conclusions:

- Vendor RadxaOS baseline boots through BOOT0 -> BL31 -> U-Boot 2018.07 ->
  extlinux -> Linux.
- Vendor console is `ttyAS0`; mainline UART0 should appear as `ttyS0`.
- Clean mainline DTB handoff under vendor U-Boot is sensitive to vendor FDT
  mutation paths.
- `dtc -R 64` reserve-map padding removes one bogus reserve-map cascade but
  does not by itself solve the `/chosen` failure.
- `setenv fdt_high 0xffffffffffffffff` did not solve the failure.
- U-Boot source inspection tied the fatal path to vendor DRM/display fixups.
- Temporary `setenv drm_debug 1` in U-Boot RAM skips that vendor DRM path and
  previously allowed clean DTBs to reach Linux.
- Older RFC v7 work already proved UART, GIC routing, SDMMC0 enumeration, and
  read-only `mmcblk0p3` rootfs mount when using a diagnostic initramfs/path.
- Do not use these vendor-boot constraints as justification for upstream DTS
  vendor-only names or display/policy nodes.

## Current Upstream Strategy

Public docs say the current v4 patch export is a review snapshot, not a
sendable series.

Current v4 scope:

- Radxa Cubie A7S board compatible
- A733 CCU binding and initial driver support
- A733 pinctrl binding and driver support
- A733 MMC compatible
- initial A733 SoC DTSI
- Cubie A7S DTS with UART0 console and MMC0 storage
- Allwinner `sun60i` MAINTAINERS pattern

Cleanup already applied:

- no nonstandard AI trailers
- no deferred parent IRQ registration workaround
- no Ethernet node or generic DWMAC fallback enablement
- no VPU/Cedrus/media patches
- maintainer blocks use `Enzo Adriano <enzo.adriano.code@gmail.com>`
- GIC redistributor size fixed to `0x100000`
- asymmetric CPU capacities present
- unused GIC child-bus properties removed
- deprecated `linux/of_device.h` removed from the draft pinctrl driver

## External Work To Coordinate

ThinkCentre research packets:

```text
192.168.50.225:/srv/projects/kernel-services/cortex/ingest
```

Key files:

- `a733-overlap-scan-20260606.md`
- `a733-inflight-ccu-pinctrl-state-20260606.md`
- `a733-rfc-recheck-20260606.md`

Current coordination state:

- Junhui Liu has an in-flight A733 CCU/PRCM RFC:
  `20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech`
- Andre Przywara has an in-flight A733 pinctrl RFC:
  `20250821004232.8134-1-andre.przywara@arm.com`
- No newer A733-specific Linux CCU/pinctrl v2 was found in the local
  public-inbox cache through 2026-06-06.
- Yixun Lan's A733 pinctrl work found in the scan is U-Boot-facing, not the
  Linux pinctrl series.

Policy:

- Do not submit local CCU/PRCM as an independent upstream series while Junhui's
  RFC remains the active reference.
- Do not submit local pinctrl as an independent upstream series while Andre's
  RFC remains the active reference.
- Expected sendable direction is a smaller DTS/board enablement series stacked
  on accepted or current CCU/PRCM and pinctrl prerequisites, unless maintainers
  request a different dependency plan.
- Current private strategy note:
  `inventory/hardware/a733-upstream-minimal-series-strategy-20260609.md`.
  It records that the local 9-patch v4 export should not be sent as-is; the
  expected sendable shape after runtime proof is a smaller SoC DTSI plus Cubie
  A7S board DTS series with explicit dependency handling for Junhui Liu's
  CCU/PRCM RFC and Andre Przywara's pinctrl RFC.

## Subsystem Guardrails

- IRQ: no workaround that bypasses irq_domain/chained irqchip expectations.
  Any A733 IRQ quirk must be modeled in normal irqchip/pinctrl paths.
- Ethernet: keep GMAC out of the first upstream slice. Need proper
  Allwinner/STMMAC glue, GMAC210 wrapper, clock/reset, MDIO, PHY reset, PHY
  power, and link evidence before enabling it.
- VPU/Cedrus: split by subsystem. Do not mix binding, clock/reset, media driver,
  and DTS in one patch.
- MMC: current evidence favors SD-only description for SDMMC0 with `no-mmc` and
  `no-sdio`; provisional `cd-gpios` should stay out until focused card-detect
  evidence exists.
- Memory: do not hard-code RAM size in DTS; rely on bootloader fixup.
- Vendor sources and Orange Pi BSP are evidence only, not implementation bases.

## Commands To Resume

Status gate:

```sh
cd /Users/enzo/projects/homelab
scripts/kernel-workflow-status --strict
```

Pull UART logs and inspect gate:

```sh
scripts/cubie-uart pull-logs
scripts/cubie-runtime-gate
```

Cubie3 Kasa state and cycle:

```sh
ssh enzo@192.168.50.11 '~/.local/bin/cubie3-power state'
ssh enzo@192.168.50.11 '~/.local/bin/cubie3-power cycle 5'
```

Check UART is free:

```sh
ssh enzo@192.168.50.11 'fuser -v /dev/ttyUSB0 2>&1 || true; test ! -e /tmp/cubie-uart-capture.lock || ls -ld /tmp/cubie-uart-capture.lock'
```

Known-good bootloader workaround shape:

```text
interrupt U-Boot
setenv drm_debug 1
run bootcmd
select extlinux option 50
```

Next likely test: same as above, but with a corrected root argument. If editing
the installed extlinux entry is needed, remember Cubie3 sudo is password-gated.

## Things Not To Do

- Do not use `192.168.50.65`.
- Do not install Docker Desktop or sustained model/container services on the
  Mac.
- Do not run models on the Mac.
- Do not put private lab paths, raw logs, AI/model notes, or topology into the
  public GitHub repo.
- Do not claim runtime success from the current A733 v4 capture; it reached
  Linux and initialized UART/MMC, but rootfs did not mount.
- Do not turn temporary `drm_debug=1` U-Boot env handling into an upstream DTS
  or Linux patch claim.
