# A733 SDMMC / eMMC Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet narrows Radxa Cubie A7S / Allwinner A733 SD card, SDMMC0, rootfs,
and eMMC work to the evidence needed before maintainer-standard kernel
patchwork or runtime storage proof. It is not a patch plan, not DTS enablement
approval, not new hardware proof, not a storage test, and not a public
communication.

## Current Boundary

- Stay local-only.
- Do not enable new SDMMC or eMMC nodes from this sheet.
- Do not edit kernel trees.
- Do not boot, reboot, SSH probe, UART capture, install, recover, or
  power-cycle any board.
- Do not run `mmc-utils` on a board.
- Do not write storage, remount rootfs read-write, run filesystem writes,
  repartition media, erase eMMC, touch eMMC boot partitions, or run cold boot
  tests.
- Do not send mail, b4 submissions, list replies, GitHub comments, public
  pushes, or paid third-party calls.

## Current Status

SDMMC0 is `proven narrow workaround plus open root-cause area`.

Local records show a hardware-proven narrow CCU/SDMMC0 path in H200/H201 and a
common-update-bit fallback in H247/H253. Those records are useful evidence,
but they do not by themselves close the SDMMC0 IDMAC/rootfs root cause or prove
general storage writes.

eMMC is `inventory/planning only`. Current inventory does not establish board
population, boot media, safe recovery wiring, or write/reimage recovery strong
enough for autonomous destructive storage tests. Recovery is only
`soft-fallback`, not drilled for burn autonomy. The claim service is
planned-not-active, so no runtime storage proof may run.

Relevant local records:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-current-evidence-index.md`
- `task-packets/kernel/a733-local-regeneration-checklist.md`
- `task-packets/kernel/a733-peripheral-evidence-map.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`

## Read-Only Source Observations

From `/Users/enzo/projects/linux-a733`, read only:

- Existing Allwinner DTS examples model MMC with controller nodes, pinctrl
  groups, `vmmc-supply`, optional `vqmmc-supply`, bus width, timing mode, and
  status.
- Existing examples distinguish SD-card-style MMC from eMMC-style controllers
  and may use `cap-mmc-hw-reset`, `mmc-ddr-1_8v`, `mmc-hs200-1_8v`, and data
  strobe pins where hardware supports them.
- Existing Wi-Fi SDIO examples use `mmc-pwrseq-simple`, but that is not proof
  for Cubie A7S eMMC or SD card behavior.
- The workflow identifies A733 storage scope as SDMMC0 microSD, optional eMMC
  nodes and variants, SDMMC0 IDMAC descriptor-fetch root cause, eMMC
  controller identity, bus width, reset, clocks, voltage rails, `mmc-utils`,
  filesystem writes, reboot, and cold boot.

These observations are source inventory only. They do not prove A733 eMMC
population, SDMMC0 root-cause closure, write safety, cold-boot stability, or
any eMMC boot behavior.

## Required Evidence Before Implementation

### SDMMC0 / Rootfs Stability

- Exact source base and head for the storage candidate.
- Whether the candidate is a narrow CCU/SDMMC0 keepalive, a true IDMAC root
  cause fix, or only a diagnostic experiment.
- Controller instance, clocks, resets, interrupts, DMA/IDMAC path, pinctrl,
  voltage rail, card-detect/write-protect facts, and bus width.
- Descriptor-fetch failure signature, negative controls, and why the proposed
  change addresses that path.
- Read-only boot proof with card enumeration, partition enumeration, read-only
  rootfs mount, and shell.
- Separate write/reboot/cold-boot recipe only after recovery rung and board
  role allow it.

### eMMC

- Whether Cubie A7S board under test has populated eMMC.
- Exact controller instance and whether it is shared with, independent from,
  or variant-dependent relative to SD card and SDIO paths.
- Bus width, reset line, data strobe, voltage rails, timing modes, and
  `cap-mmc-hw-reset` evidence.
- Whether eMMC boot partitions exist and whether any test might touch them.
- Non-destructive read-only proof before any write test.
- SD reimage or stronger recovery for filesystem-write, full-image, eMMC boot,
  or bootloader-adjacent experiments.

## Runtime Proof Requirements

Runtime proof is role-gated through:

- `A733-BATCH-003` for SDMMC0 IDMAC/rootfs stability proof
- `A733-BATCH-006` for eMMC proof

No runtime proof class may run now. When later allowed, proof must include:

- exact source base and head
- exact Image and DTB hashes
- exact board role, UART path, power path, boot media, and recovery rung
- boot log showing controller probe and card/eMMC enumeration
- partition table and rootfs mount evidence
- read-only proof before write proof
- explicit write/reboot/cold-boot recipe when writes are in scope
- `mmc-utils` output only when safe for the target and role
- negative markers, including no kernel panic, no I/O errors, no rootfs
  remount-rw surprise, and no unexpected media reset
- clean restore or recovery evidence after the run

## Communication Hook

`A733-COMM-006` is the held future communication hook for SDMMC0 root-cause or
diagnostic-series work.

Do not draft or send a cover letter from this sheet. If a maintainer-dependent
question becomes precise, record it in the communications ledger as a held
question with the smallest evidence bundle needed for a one-reply answer.

## Hard Stop Conditions

Stop local SD/eMMC work and log the blocker if:

- the controller, clock, reset, pinctrl, voltage, DMA/IDMAC, or bus-width facts
  are guessed
- SDMMC0 root-cause language goes beyond the recorded proof
- eMMC population or boot media is inferred instead of observed
- a test would write storage, remount rootfs read-write, reboot, cold boot, or
  touch eMMC boot partitions
- recovery is weaker than the test's failure mode
- board role assignment, claim service, or recovery drill is missing
- the path starts to edit DTS or driver source before evidence is complete

## Safe Next Local Items

Choose one per bounded cycle:

1. Source-only SDMMC0 checklist: list controller, clock, reset, pinctrl,
   regulator, IDMAC, descriptor, and rootfs facts still missing.
2. Source-only eMMC checklist: list controller, reset, bus width, data strobe,
   timing, voltage, boot-partition, and population facts still missing.
3. Proof split: separate read-only boot proof from write/reboot/cold-boot proof
   so the workflow can gate each against the correct recovery rung.
4. Queued proof recipe skeleton: refine `A733-BATCH-003` and `A733-BATCH-006`
   without enabling them.
