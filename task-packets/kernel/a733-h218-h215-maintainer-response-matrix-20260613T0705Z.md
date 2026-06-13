# A733-SDMMC-H218: H215 Maintainer Response Matrix

Captured: 2026-06-13T07:05:50Z

Updated: 2026-06-13T07:44:00Z

## Purpose

Prepare public-safe response material for the H215 RFC/RFT series after it was
sent but before it is visible in the checked public archives.

This packet is not a new mail draft, not a resend approval, and not a request
to run more hardware. Use it only if a maintainer asks a question, a public
archive entry appears, or a later reviewed follow-up becomes necessary.

## Current State

- H215 sent a five-message RFC/RFT series on the existing A733 CCU RFC patch-7
  thread.
- H226 refreshed public archive visibility and still did not find H215 markers
  in checked views; direct list-archive checks were inconclusive from this
  environment.
- H200 remains the exact-hash hardware-proven source state.
- H201 is the exact hardware proof record.
- H188 records that the no-`mbus-msi-lite0` narrowing comparison failed on
  Cubie3 immediately after the unused-clock walk.
- H211 is the public-safe UART proof excerpt.
- H205 is the patches-only share bundle.

## Evidence Anchors

Use these anchors in replies instead of lab-internal details:

- tested commit: `de486cb24c361a86cba26738f24332df780872b0`
- kernel version marker: `7.1.0-rc5-00181-gde486cb24c36`
- base: `d9aa2e15caae`
- board: Radxa Cubie A7S
- full UART log SHA256:
  `6f856491c5acd7652e9fcdad1a282819f47482f0a36fc73b046486ffe07c5914`
- public-safe excerpt SHA256:
  `fe618e48813763fd0fa197c6ae00d6a7c17e03f957c82cb48ba6d19fd578bc2d`

## Likely Questions And Safe Answers

### If Asked Whether The Stack Is Hardware Tested

```text
Yes. The exact tested commit was de486cb24c361a86cba26738f24332df780872b0.
On Radxa Cubie A7S it reached clk_disable_unused(), unused power-domain
disable, SDMMC0 host initialization, mmcblk0 card and partition discovery,
read-only ext4 root mount, and /bin/sh as init. The boot log carries kernel
version marker 7.1.0-rc5-00181-gde486cb24c36.
```

### If Asked For The Boot Excerpt

Use the H211 excerpt. Do not paste a full UART log without a fresh public
hygiene pass.

```text
The public-safe excerpt is short: it shows clk_disable_unused(), genpd unused
domain disable, SDMMC0 initialization, SD card enumeration as mmcblk0, partition
discovery, read-only ext4 root mount, and /bin/sh. The full log SHA256 is
6f856491c5acd7652e9fcdad1a282819f47482f0a36fc73b046486ffe07c5914.
```

### If Asked Why `ahb-cpus` Is Critical

```text
The CPU's register path into the R/CPUS domain depends on this AHB bridge.
When clk_disable_unused() gates it, later R-CCU/RTC register reads stall. With
the gate kept critical, the unused-clock walk completes and the later R-domain
reads complete normally on the Cubie A7S.
```

### If Asked Why The Storage/NSI Gates Are Critical

```text
Without the storage-fabric criticals, SDMMC0 reaches fatal clock-update
timeouts or the normal-IDMA path stalls before card enumeration. With the
tested storage/NSI critical set plus the NSI update-bit commit, SDMMC0
enumerates the card and mounts the read-only root filesystem.
```

### If Asked Whether `mbus-msi-lite0` Is Strictly Required

```text
The submitted stack keeps mbus-msi-lite0 because it is part of the hardware-
proven fabric set. A narrower comparison that omitted mbus-msi-lite0 was tested
on the same board and did not progress past the unused-clock walk into SDMMC0
initialization, so the current tested bundle keeps mbus-msi-lite0.
```

Do not claim that `mbus-msi-lite0` has been independently proven minimal across
all possible fabric models. The safe claim is narrower: removing it from the
tested bundle regressed the Cubie A7S proof run, so it remains in the current
hardware-proven stack unless maintainers prefer a different fabric model.

### If Asked About The NSI Update Bit

```text
The NSI clock is an MP clock with CCU_FEATURE_UPDATE_BIT. The boot-programmed
state was present in the register image, but the setting still needed the
update bit pulsed so the hardware committed it before the SDMMC0 IDMA path was
used. The submitted patch does that in A733 CCU probe code; maintainers may
prefer a common sunxi-ng registration-time treatment for update-bit clocks.
```

### If Asked For A Narrower Spin

Safe narrowing order:

1. Keep `ahb-cpus`.
2. Keep the storage/NSI critical set that is exact-hash proven.
3. Keep the NSI update-bit commit unless maintainers prefer common-framework
   handling.
4. Do not drop `mbus-msi-lite0` by default; the no-`mbus-msi-lite0`
   comparison failed on Cubie A7S.
5. Only drop `mbus-msi-lite0` if maintainers request that shape despite the
   regression evidence, or if a new fabric model/fresh proof replaces the
   current result.
6. Avoid adding unrelated peripherals or board-DTS claims.

### If Asked Why This Is Not A DTS Fix

```text
The failure is in the clock/fabric state needed for register access and
normal-IDMA operation. DTS can describe consumers, but the tested failure mode
is triggered during unused-clock handling and NSI fabric setup in the CCU
driver path. The RFC/RFT series is therefore scoped to the A733 CCU driver.
```

## Reply Discipline

- Do not resend H215 solely because H217 still cannot see it in public
  archives.
- Do not introduce local paths, hostnames, private IP addresses, model-routing
  history, or lab automation details into public replies.
- Do not say all Cubie A7S peripherals work.
- Do not say this proves Ethernet, VPU, display, USB-C, PCIe, Wi-Fi, Bluetooth,
  camera, or eMMC.
- Do not run another Cubie proof unless a fresh hardware question actually
  requires it.
- Before any reply containing excerpts or regenerated patches, re-run the
  public hygiene and trailer gates on the outgoing material.

## Next Action

Wait for one of:

- public archive visibility for H215;
- maintainer reply;
- bounce or delivery failure;
- a reviewed decision to send a clarifying follow-up after enough time has
  passed.
