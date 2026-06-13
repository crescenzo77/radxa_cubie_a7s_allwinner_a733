# A733 PCIe / NVMe Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet narrows Radxa Cubie A7S / Allwinner A733 PCIe, PCIe PHY, adapter,
and NVMe work to the evidence needed before maintainer-standard kernel
patchwork or runtime link/storage proof. It is not a patch plan, not DTS
enablement approval, not new hardware proof, not a link test, and not a public
communication.

## Current Boundary

- Stay local-only.
- Do not enable PCIe, PCIe PHY, regulator, or NVMe-related DTS nodes from this
  sheet.
- Do not edit kernel trees.
- Do not boot, reboot, SSH probe, UART capture, install, recover, or
  power-cycle any board.
- Do not insert, remove, or enumerate PCIe adapters.
- Do not run `lspci`, `nvme`, `fio`, or storage-write tests on a board.
- Do not write NVMe storage or any other block device.
- Do not send mail, b4 submissions, list replies, GitHub comments, public
  pushes, or paid third-party calls.

## Current Status

PCIe/NVMe is `inventory/planning only`.

Current inventory does not establish the PCIe controller, PHY model, lane
count, reset/clock wiring, PERST GPIO, CLKREQ wiring, refclk source, power
budget, adapter inventory, or safe NVMe rollback path. Recovery is only
`soft-fallback`, not drilled for burn autonomy. The claim service is
planned-not-active, so no runtime PCIe enumeration, link training, NVMe, or
fio proof may run.

Relevant local records:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-current-evidence-index.md`
- `task-packets/kernel/a733-peripheral-evidence-map.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`

## Read-Only Source Observations

From `/Users/enzo/projects/linux-a733`, read only:

- The workflow identifies Cubie A7S scope as PCIe 3.0 x1 FPC for NVMe and
  adapters.
- Local source search found Allwinner board examples with PCIe-related power
  rail names on nearby SoCs, but that is only board-power pattern inventory.
- The scanned local Allwinner DTS paths did not establish an A733 PCIe
  controller node, A733 PCIe PHY compatible, or Cubie A7S board-level PCIe
  wiring.
- PCIe/NVMe work therefore remains blocked on controller/PHY/source evidence
  before any DTS or driver implementation.

These observations are source inventory only. They do not prove A733 PCIe
controller compatibility, PHY compatibility, link training, adapter safety,
NVMe enumeration, or storage-write safety.

## Required Evidence Before Implementation

### Controller And PHY

- Exact PCIe controller compatible, register range, interrupts, clocks,
  resets, power domains, and inbound/outbound address windows.
- Exact PCIe PHY compatible, lane mapping, refclk source, reset, and any
  calibration or efuse dependency.
- Whether the controller path is already supported by a mainline driver or
  requires new glue/binding work.
- Whether PCIe is Gen1/Gen2/Gen3 in practice and which speed is safe for first
  proof.
- Whether existing bindings cover all required properties.

### Board Wiring And Power

- Physical connector and lane routing for the Cubie A7S PCIe FPC.
- PERST, CLKREQ, wake, enable, or power GPIOs, with polarity and timing.
- 3.3 V, 1.8 V, and any auxiliary rail or switch required by adapters.
- Power budget for NVMe and representative adapters.
- Mechanical adapter inventory, including whether an FPC adapter, M.2 key,
  cable, or powered riser is required.

### NVMe And Adapter Proof

- Non-destructive enumeration proof before any storage write.
- NVMe model, firmware, power draw, namespace layout, and rollback path.
- Separate proof for representative non-storage adapters if adapters are part
  of the claim.
- Storage-write and `fio` proof only after recovery rung covers media/rootfs
  corruption and the board role permits it.

## Runtime Proof Requirements

Runtime proof is role-gated through:

- `A733-BATCH-008` for PCIe/NVMe proof

No runtime proof class may run now. When later allowed, proof must include:

- exact source base and head
- exact Image and DTB hashes
- exact board role, UART path, power path, adapter path, and recovery rung
- link training log and negotiated width/speed
- `lspci` output for endpoint enumeration
- NVMe enumeration without writes before any destructive test
- power stability evidence under idle and load
- `fio` recipe only when storage writes are explicitly in scope
- negative markers, including no AER flood, no link flap, no controller
  timeout, no rootfs corruption, and no unexpected media reset
- clean restore or recovery evidence after the run

## Communication Hook

`A733-COMM-008` is the held future communication hook for PCIe/NVMe support.

Do not draft or send a cover letter from this sheet. If a maintainer-dependent
question becomes precise, record it in the communications ledger as a held
question with the smallest evidence bundle needed for a one-reply answer.

## Hard Stop Conditions

Stop local PCIe/NVMe work and log the blocker if:

- the controller, PHY, clock, reset, PERST, CLKREQ, refclk, regulator, or
  power budget facts are guessed
- adapter wiring or power draw is inferred instead of documented
- the work requires booting, probing, enumerating PCIe, inserting adapters,
  running `lspci`, running `fio`, or writing storage
- recovery is weaker than the test's failure mode
- board role assignment, claim service, or recovery drill is missing
- the path starts to edit DTS or driver source before evidence is complete

## Safe Next Local Items

Choose one per bounded cycle:

1. Source-only controller checklist: list compatible, register, interrupt,
   clock, reset, power-domain, address-window, and binding facts still missing.
2. Source-only PHY checklist: list lane, refclk, reset, calibration, speed,
   and binding facts still missing.
3. Board adapter checklist: list FPC, M.2, PERST, CLKREQ, rail, power budget,
   and adapter-inventory facts still missing.
4. Queued proof recipe skeleton: refine `A733-BATCH-008` without enabling it.
