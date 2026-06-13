# A733 NPU / RISC-V MCU Boundary Sheet

Status: local-only source-backed boundary sheet
Updated: 2026-06-13

This sheet records the current boundary for Radxa Cubie A7S / Allwinner A733
NPU and RISC-V MCU work. These tracks are bucket C: possible future work, but
not ready for kernel patchwork until there is a credible upstream subsystem
path, firmware/userspace ABI story, memory map, and runtime proof plan.

It is not a patch plan, not proof, not permission to enable an NPU or remote
processor, and not a communication draft.

## Current Boundary

- Do not enable an NPU, RISC-V MCU, remoteproc, mailbox, reserved-memory,
  firmware, IOMMU, or userspace ABI node from guesses.
- Do not load firmware, start a remote processor, probe accelerators, run NPU
  workloads, run OpenAMP/RPMsg tests, or touch board runtime state.
- Do not infer hardware population or upstream support from marketing names,
  vendor claims, or generic binding examples.
- Do not edit kernel trees, boot boards, change services, or send public
  communication from this sheet.
- Current inventory still has unassigned board roles, soft-fallback recovery
  only, no burn-autonomy drill, and claim service planned-not-active.

## Source Observations

Read-only source search on `/Users/enzo/projects/linux-a733` found no A733
NPU, RISC-V MCU, remoteproc, OpenAMP/RPMsg, mailbox, firmware, reserved-memory,
or accelerator nodes in `sun60i-a733.dtsi` or the current Cubie A7S board DTS.

Generic upstream binding examples show the usual ingredients for remote
processor and firmware-controlled subsystems:

- `remoteproc` device node with compatible string, registers, interrupts, and
  reset/clock controls
- `firmware-name` or another documented firmware loading path
- `memory-region` / reserved-memory carve-outs for firmware, vrings, buffers,
  or device-private memory
- `mboxes` / mailbox channels or another IPC mechanism
- IOMMU attachment when the remote engine performs DMA through an address
  translation unit
- explicit userspace ABI or framework ownership for accelerator work

Those examples are useful for shape only. They do not prove that A733 has a
mainlineable NPU or RISC-V MCU path.

## Evidence Needed Before Patchwork

### NPU

- Exact NPU IP identification and upstream subsystem target.
- Register ranges, interrupts, clocks, resets, power domains, IOMMU stream IDs,
  SRAM/reserved-memory needs, and firmware requirements.
- Firmware license and redistribution story, including whether firmware is
  optional, required, redistributable, board-specific, or vendor-only.
- Userspace ABI plan: no private out-of-tree ABI, no opaque misc-device shortcut
  without subsystem buy-in, and no DT binding that exposes policy instead of
  hardware.
- Minimal proof plan that can demonstrate driver bind, firmware handling,
  memory isolation, and one bounded inference or self-test without overheating,
  corrupting storage, or requiring paid third-party services.

### RISC-V MCU / Remoteproc

- Exact RISC-V MCU identity, ownership, reset state, boot mode, and whether it
  is safe for Linux to control.
- Memory map, reserved-memory carve-outs, mailboxes, interrupts, reset lines,
  clocks, power domains, and any shared SRAM.
- Firmware ownership and load path: preloaded by boot firmware, Linux-loaded
  via remoteproc, or not mainlineable yet.
- IPC model: mailbox, RPMsg, OpenAMP, shared memory, vendor protocol, or none.
- Safety story for stopping, starting, crashing, and recovering the MCU without
  breaking board power, thermal, storage, or console access.

## Held Communication / Queue Mapping

- Communication hook: A733-COMM-012 for future NPU or RISC-V MCU work. It is
  `draft-needed` only and not send authority.
- Hardware batch queue: A733-BATCH-014 holds future NPU/RISC-V MCU runtime
  proof. It is a queue placeholder only and not run authority.
- If a future queue entry is added, it must name board role, recovery rung,
  recovery drill timestamp, UART/power path, artifact path, rollback plan,
  firmware provenance, thermal stop condition, and exact proof command
  boundaries.

## Safe Local Next Steps

- Search only local/vendor/source references for A733 NPU, RISC-V MCU,
  mailbox, firmware, reserved-memory, IOMMU, RPMsg, and OpenAMP naming.
- Build a local-only block map that separates SoC-level hardware facts from
  firmware ABI, userspace ABI, and board-level safety requirements.
- Refine A733-BATCH-014 only after a concrete source-backed candidate exists
  and the operator approves the firmware/runtime risk.
- Add held maintainer questions to A733-COMM-012 only if they are precise,
  evidence-backed, and still unsent.

## Hard Blockers

- No A733 NPU source model is recorded here yet.
- No A733 RISC-V MCU / remoteproc source model is recorded here yet.
- No firmware provenance, license, load path, memory-region layout, mailbox
  path, IOMMU path, OpenAMP/RPMsg path, or userspace ABI story is recorded here
  yet.
- No recovery rung is drilled for autonomous firmware, remoteproc, accelerator,
  or crash/recovery experiments.
- No claim service is active for contended board, UART, power, kernel tree,
  firmware artifact, or proof artifact resources.
- Therefore all NPU, RISC-V MCU, remoteproc, firmware loading, OpenAMP/RPMsg,
  accelerator probe, workload, and crash/recovery runtime work remains
  queued-only until future authority files positively permit it.
