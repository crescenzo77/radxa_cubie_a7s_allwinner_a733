# Cubie Corrected-Root Operator Handoff - 2026-06-09

This is a private operator handoff snapshot. Do not copy private paths, IP
addresses, or local workflow notes into upstream kernel submission material.

## Current Maintainer-Path Next Action

```sh
ssh -tt 192.168.50.11 'cd /srv/projects/homelab && git pull --ff-only mac-mini main && scripts/cubie-interactive-root-install-session --confirm-target-ip 192.168.50.95'
```

Codex Desktop on the Mac is only the dispatcher. The live root-install, UART,
and U-Boot-selection session runs on Strix because Strix owns the Cubie serial
adapters.

## Current Blockers

```text
private workflow repo is dirty
cubie runtime proof is root-install-required
A733 export shape is not maintainer-ready: too-many-patches, local-ccu-binding, local-ccu-driver, local-pinctrl-binding, local-pinctrl-driver, standalone-mmc-compatible, maintainers-sun60i-pattern, missing-depends-on, missing-depends-on
```

The private workflow dirty state includes unrelated knowledge/model files and
should not be mass-staged for this kernel proof. Commit only scoped workflow or
proof artifacts.

## Backup Posture

```text
private_origin_backed=yes
private_github_backed=no
private_remote_url=/Users/enzo/git-mirrors/homelab.git
public_github_backed=yes
public_mirror_backed=yes
```

Do not add or guess a private GitHub remote. Human approval is required for the
destination URL and visibility before pushing private workflow material to
GitHub.

## Read-Only Preflight State

```text
target=cubie-3 ip=192.168.50.95
stage=kernel-boot-artifacts/a733-v4-corrected-root-proof-20260609
extlinux_label=a733-v4-abc8d07b0a63-partuuid-ro-proof
extlinux_menu_label=A733 v4 abc8d07b0a63 PARTUUID ro proof
sudo_status=password-required
uart_preflight_status=ok
uart_preflight_host=192.168.50.11
status=root-install-required
required_confirmation=--confirm-target-ip 192.168.50.95
```

The corrected-root proof label append line is:

```text
console=ttyS0,115200n8 earlycon=uart8250,mmio32,0x02500000 loglevel=8 ignore_loglevel drm_debug=1 root=PARTUUID=db375e07-7682-4d4e-b8bc-a923dd0b027e rootfstype=ext4 rootwait ro rootflags=noload init=/bin/sh
```

## Live U-Boot Step

The vendor U-Boot workaround is RAM-only:

```text
setenv drm_debug 1
run bootcmd
```

Then select the non-default U-Boot menu label:

```text
A733 v4 abc8d07b0a63 PARTUUID ro proof
```

Do not encode this vendor U-Boot workaround into upstream DTS.

## Proof Gates After UART Capture

```sh
scripts/cubie-corrected-root-proof-gate-selftest
scripts/cubie-latest-corrected-root-proof --strict
scripts/kernel-workflow-status --maintainer-ready-blockers
scripts/a733-patch-prep-checklist --run
```

The captured-log proof gate must pass before claiming exact-v4 runtime proof,
reshaping the patch export, preparing a maintainer-facing branch, or drafting
submission mail.

## Maintainer Guardrails

- Do not send the current 9-patch public export.
- Do not submit local A733 CCU/PRCM or pinctrl patches independently while the
  Junhui Liu and Andre Przywara RFCs remain the active references.
- Do not add vendor U-Boot aliases, `arm,sun60iw2p1`, `fdt_high`, display
  workaround nodes, or bootargs policy to DTS.
- Do not expand the first slice into Ethernet/GMAC, VPU, display, Wi-Fi,
  Bluetooth, USB-C, PCIe, or other unproven hardware blocks.
- After proof passes, the likely maintainer-facing direction remains a narrow
  board-compatible binding plus SoC DTSI plus Radxa Cubie A7S board DTS slice
  with explicit `Depends-on:` references for the active A733 CCU/PRCM and
  pinctrl prerequisites.

## Safe Waiting Command

```sh
scripts/a733-patch-prep-checklist --preflight
```
