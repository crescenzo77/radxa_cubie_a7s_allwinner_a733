# A733-SDMMC-H207: Maintainer Response Prep After H204

Captured: 2026-06-13T06:29Z

## Purpose

Prepare a bounded response path if maintainers ask for the H200 patch text,
UART proof, or exact reproduction details after H204.

This packet is not a send approval and is not a draft email to send
immediately. Do not send another follow-up while H204 is still not visible in
the checked public views unless a maintainer reply arrives or the operator
explicitly asks for a new send.

## Current Public State

H206 refreshed the checked public views after H204:

- general search did not show H204/H200 text;
- Patchew patch-7 page did not show H204/H200 text;
- Patchew patch-7 mbox contained only the original patch-7 message;
- lore could not be confirmed from this environment because it returned
  anti-bot HTML.

## Ready Artifacts

Use these only if requested or if preparing a reviewed follow-up:

- H200 patches-only bundle:
  `/Users/enzo/projects/homelab/task-packets/kernel/a733-h200-h199-maintainer-polish-patches-only/`
- Strix mirror:
  `/srv/projects/homelab/task-packets/kernel/a733-h200-h199-maintainer-polish-patches-only/`
- H200 source worktree:
  `/srv/projects/kernel-work/final/a733-ccu-nsi-v4-h199-maintainer-polish`
- H200 commit:
  `de486cb24c361a86cba26738f24332df780872b0`
- H201 hardware proof:
  `/Users/enzo/projects/homelab/task-packets/kernel/a733-h201-h200-exact-hardware-proof-20260613T0610Z.md`
- H201 UART log copy:
  `/Users/enzo/projects/homelab/tools/hardware-logs/cubie-uart/20260613T061008Z-a733-h200-h199-maintainer-polish-ttyUSB0.uart.log`
- H205 share-bundle record:
  `/Users/enzo/projects/homelab/task-packets/kernel/a733-h205-h200-patches-only-share-bundle-20260613T0625Z.md`

## Patch Hashes

```text
241d4d8c6b1c89d7804bc1e1a1265cfaeffe49b75e0af70e3da0b83358025ee9  0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
b24712a5cd5069954d3accbf83153c49f0c9497508df39945752bc39eea36e6c  0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
b016e28834173cafcfe3231d7666a87a1eeda64cce1cb260dcbe1290ea4c7b9c  0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
a3fcbc564316c68d410af52b41db369acd7c2b55bdc68d522e9fcc3f5376a07b  0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

## If Maintainer Asks For Patch Text

Preferred response shape:

```text
Thanks, I can share the exact tested stack.

The four patches are generated from commit de486cb24c361a86cba26738f24332df780872b0
on top of d9aa2e15caae. The stack was boot-tested on Radxa Cubie A7S through
SDMMC0 enumeration, read-only root mount, and /bin/sh.

I can send these as an RFC/RFT reply to this thread, or resend them in whatever
form is easiest for the A733 CCU revision.
```

Then either attach/paste the four patch files from the H200 patches-only bundle
or generate a proper RFC/RFT series from the H200 worktree, depending on the
maintainer's requested format.

## If Maintainer Asks For UART Proof

Preferred response shape:

```text
The exact tested commit was de486cb24c361a86cba26738f24332df780872b0.
The boot log reached clk_disable_unused(), genpd unused-domain disable,
SDMMC0 host init, mmcblk0 partition discovery, read-only ext4 root mount,
and /bin/sh as init. I can provide the UART log or the relevant excerpts.
```

Before sharing excerpts, trim local host paths and lab-only operational detail.

## If Maintainer Asks About Scope

Keep the answer narrow:

- this is CCU/NSI feedback for the in-flight A733 CCU RFC;
- it is not a DTS expansion;
- it does not claim Ethernet, VPU, display, USB-C, PCIe, wireless, or camera;
- it does not require local model or lab automation context.

## Validation To Re-Run Before Any Actual Send

```sh
python3 tools/validate/public_hygiene_gate.py \
  task-packets/kernel/a733-h200-h199-maintainer-polish-patches-only

python3 tools/validate/trailer_gate.py \
  task-packets/kernel/a733-h200-h199-maintainer-polish-patches-only/*.patch
```

On Strix, re-run a temporary `git am --3way` apply-check from base
`d9aa2e15caae` if the patches are regenerated or if any patch text changes.

## Stop Conditions

- Do not send duplicate mail solely because H204 is not indexed yet.
- Do not send raw local metadata files.
- Do not include private paths, hostnames, model routing, Telegram/Hermes
  details, or lab automation internals in public mail.
- Do not run another Cubie proof just to answer a mail-thread question unless a
  fresh hardware result is explicitly needed.
