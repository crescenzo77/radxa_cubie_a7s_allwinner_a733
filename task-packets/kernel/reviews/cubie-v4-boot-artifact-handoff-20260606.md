# Cubie V4 Boot Artifact Handoff

Generated: 2026-06-06.

## Purpose

Prepare target-hardware runtime testing for the public A733 v4 candidate
without changing any Cubie boot configuration automatically.

## Candidate

- Linux branch: `candidate/a733-platform-clean-v4`
- commit: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- public status commit: `5058155f94e404a80f111f8ae4bdbc4e66214936`

## Artifact Build

- artifact directory on AMD: `/srv/projects/kernel-work/outgoing/a733-v4-abc8d07b0a63-20260606T152409Z`
- compiler: `aarch64-linux-gnu-gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`
- `Image` SHA256: `b4584f230d436235fb3776a102546e05d8fac1d93206d25f3566aedad7e60b7d`
- `sun60i-a733-cubie-a7s.dtb` SHA256: `9ac58728715b7999bda4fe579bb00a4c9da7f123c7d0fb1bf9e4664cd85a0e44`
- `config` SHA256: `9273c649385ba95c589c9f4867a77addebb7bf39ac7a7bb3d655d4980eb7ca87`
- `manifest.txt` SHA256: `1c0ba61cc7f13ef4488cb7ede4db5d9b653b7352623d2ae29375cbee84ff7f09`

The build completed, but this is not runtime evidence.

## Driver Config Check

The built config has the minimum expected pieces for a first MMC/rootfs boot:

- `CONFIG_SERIAL_8250=y`
- `CONFIG_SERIAL_8250_DW=y`
- `CONFIG_SERIAL_OF_PLATFORM=y`
- `CONFIG_PINCTRL_SUN60I_A733=y`
- `CONFIG_SUN60I_A733_CCU=y`
- `CONFIG_MMC_BLOCK=y`
- `CONFIG_MMC_SUNXI=y`
- `CONFIG_EXT4_FS=y`
- `CONFIG_DEVTMPFS=y`

## Board Discovery

- `192.168.50.248` is `framework`, x86_64 Ubuntu. It is not a Cubie.
- `cubie2` inventory IP `192.168.50.85` is stale or currently unreachable.
- live A733 candidates found by SSH identity:
  - `192.168.50.65`, hostname `cubie-1`, model `sun60iw2`
  - `192.168.50.95`, hostname `cubie-3`, model `sun60iw2`

Do not rewrite the `cubie2` inventory entry until the human confirms whether
`cubie-1` is the renamed/readdressed Cubie2 or a separate board.

## Boot Layout Observations

Both live boards currently boot vendor kernel `5.15.147-21-a733`.

`cubie3` has many existing experimental entries under `/boot/mainline-rfc-v7`
and a long `/boot/extlinux/extlinux.conf`. It is useful for historical context
but easy to confuse with public-candidate proof.

`cubie-1` has a much cleaner boot menu:

- `/boot/extlinux/extlinux.conf`
- `/boot/uEnv.txt`
- `/boot/vmlinuz-5.15.147-18-a733`
- `/boot/vmlinuz-5.15.147-21-a733`

Neither board allows passwordless `sudo`, so no files were copied into `/boot`
and no bootloader config was changed.

## User-Space Staging

The exact v4 artifacts were staged without root privileges on both live A733
boards:

- `192.168.50.65:kernel-boot-artifacts/a733-v4-abc8d07b0a63-20260606T152409Z`
- `192.168.50.95:kernel-boot-artifacts/a733-v4-abc8d07b0a63-20260606T152409Z`

The staging helper verified `Image`, DTB, config, and manifest checksums on
each board. It also wrote `install-extlinux-entry.sh`, which requires an
explicit sudo/root run on the board and appends only a non-default extlinux
label. No `/boot` files were changed by staging.

## Next Human-Gated Action

1. Confirm which physical board should be used for the public v4 boot proof.
2. Confirm whether `192.168.50.65` / `cubie-1` is actually the missing
   `cubie2`.
3. Provide a root/sudo path for the chosen board, or perform the file staging
   manually.
4. On the chosen board, run the staged installer with sudo/root:

   ```bash
   cd kernel-boot-artifacts/a733-v4-abc8d07b0a63-20260606T152409Z
   sudo ./install-extlinux-entry.sh
   ```

5. Run `scripts/cubie-manual-boot-session 180 a733-v4-abc8d07b0a63-boot`.
6. During the capture window, choose the non-default U-Boot label
   `a733-v4-abc8d07b0a63-uart-proof` over UART and capture
   the full boot log.
7. Do not update the public repo with a runtime claim unless the UART log shows
   the exact kernel, DTB path or checksum evidence, command line, CPU bring-up,
   GIC, CCU, pinctrl, MMC/rootfs behavior, and any failures.

Suggested first-pass kernel command line for the manual boot entry:

```text
console=ttyS0,115200n8 earlycon=uart8250,mmio32,0x02500000 loglevel=8 ignore_loglevel root=UUID=6f750720-329a-45f0-a4b5-abc5797b040a rootwait rw
```
