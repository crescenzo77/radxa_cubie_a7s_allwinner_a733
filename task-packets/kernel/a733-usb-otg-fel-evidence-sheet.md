# A733 USB / OTG / FEL Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet narrows Radxa Cubie A7S / Allwinner A733 USB, USB-C, OTG, and
FEL/BootROM recovery work to the evidence needed before maintainer-standard
kernel patchwork or autonomous recovery claims. It is not a patch plan, not a
DTS enablement approval, not new proof, not a hardware test, and not a public
communication.

## Current Boundary

- Stay local-only.
- Do not enable USB, USB-C, or OTG nodes in the Cubie A7S DTS from this sheet.
- Do not enter FEL.
- Do not run `sunxi-fel` or `xfel`.
- Do not plug, unplug, enumerate, or probe USB devices.
- Do not edit kernel trees.
- Do not boot, reboot, SSH probe, UART capture, install, recover, or
  power-cycle any board.
- Do not send mail, b4 submissions, list replies, GitHub comments, public
  pushes, or paid third-party calls.

## Current Status

USB / USB-C / OTG is `inventory/planning only`.

FEL/BootROM recovery is also `inventory/planning only`. Current inventory
records USB-OTG/FEL path as `unknown` for cubie1, cubie2, and cubie3. Recovery
is only `soft-fallback`, not drilled for burn autonomy. The claim service is
planned-not-active, so no runtime USB proof and no FEL recovery drill may run.

Relevant local records:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `runbooks/kernel-workflow-controls.md`
- `runbooks/hermes-kernel-work-prompt.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-peripheral-evidence-map.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`

## Read-Only Source Observations

From `/Users/enzo/projects/linux-a733`, read only:

- Existing Allwinner DTS examples split USB into controller nodes, PHY nodes,
  VBUS regulators, ID-detect GPIOs, and `dr_mode`/OTG policy.
- Existing examples use MUSB-style OTG nodes on older SoCs and EHCI/OHCI host
  nodes for USB2 host paths.
- Existing examples use `usb0_vbus-supply`, `usb0_id_det-gpios`,
  `usb0_vbus_det-gpios`, and board-specific fixed regulators or PMIC supplies.
- The workflow identifies A733 scope as USB2 Type-C power/OTG, USB3/DP/OTG
  Type-C, USB2 Type-A host, PHYs, role switch, and VBUS regulators.
- These examples are patterns to compare against, not proof that any A733
  controller, PHY, role switch, or Type-C block is compatible.

These observations are source inventory only. They do not prove A733 USB,
USB-C, OTG, Type-C, gadget mode, host mode, or FEL recovery.

## Required Evidence Before Implementation

### Controller Topology

- Exact USB2 controller instances and register ranges.
- Exact USB3 controller instances and register ranges, if present.
- Whether each controller is host-only, device-only, dual-role, or tied to a
  Type-C/role-switch path.
- Interrupts, clocks, resets, power domains, and PHY references for each
  controller.
- Whether existing Allwinner MUSB/EHCI/OHCI/DWC3 patterns apply or a new
  compatible/glue path is required.

### PHY And Power

- Exact USB2 PHY and USB3 PHY compatible path.
- PHY clock and reset identifiers.
- VBUS regulator or PMIC supply for each port.
- ID-detect, VBUS-detect, orientation, and over-current GPIOs, if any.
- Whether Type-C CC/orientation handling is external, PMIC-owned, or requires
  a role-switch/connector graph.

### USB-C / OTG / Role Switch

- Which physical port is USB-C and whether it exposes USB2 only, USB3, DP Alt
  Mode, OTG, or a subset.
- Whether the port needs `usb-role-switch`, extcon, connector graph, Type-C
  controller binding, or a simpler fixed host/device policy.
- Gadget-mode proof path, if device mode is claimed later.
- Host-mode proof path for storage, keyboard, serial, and Ethernet dongle.
- DP Alt Mode must stay out of USB-only patches.

### FEL / BootROM Recovery

- Which physical connector reaches the A733/SUN60IW2 BootROM USB path.
- Which controller host can see that path.
- How to enter FEL: button, strap, boot-fail fallback, or other documented
  method.
- Whether `sunxi-fel` supports this exact A733/SUN60IW2 board.
- Whether `xfel` supports this exact A733/SUN60IW2 board.
- A recovery drill record that deliberately enters the failure state covered
  by the rung, recovers the board, confirms clean boot, and records timestamped
  evidence.

Until that drill exists, `fel-bootrom` must not be counted as an available
autonomous recovery rung.

## Runtime Proof Requirements

Runtime proof is role-gated through:

- `A733-BATCH-009` for USB/USB-C host/device/gadget proof
- `A733-BATCH-012` for FEL/BootROM recovery drill

No runtime proof class may run now. When later allowed, proof must include:

- exact source base and head
- exact Image and DTB hashes
- exact board role, UART path, power path, USB cable path, and recovery rung
- boot log showing controller and PHY probe
- device enumeration for host mode
- gadget enumeration from an external host for device mode
- role-switch or fixed-role evidence matching the DTS
- negative markers, including no kernel panic and no unstable disconnect loop
- clean restore or recovery evidence after the run

## Communication Hook

`A733-COMM-009` is the held future communication hook for USB/USB-C support.

Do not draft or send a cover letter from this sheet. If a maintainer-dependent
question becomes precise, record it in the communications ledger as a held
question with the smallest evidence bundle needed for a one-reply answer.

## Hard Stop Conditions

Stop local USB/FEL work and log the blocker if:

- the controller topology is unknown
- clocks, resets, PHYs, or VBUS supplies are guessed
- Type-C role-switch or connector modeling depends on maintainer preference
- FEL support is assumed without testing `sunxi-fel` or `xfel` on the actual
  A733/SUN60IW2 board
- the work depends on plugging, unplugging, enumerating, or probing live
  hardware
- the path starts to edit DTS or driver source before evidence is complete
- DP Alt Mode starts to mix with USB-only work

## Safe Next Local Items

Choose one per bounded cycle:

1. Source-only topology checklist: identify the controller, PHY, clock, reset,
   and VBUS facts still missing for each expected USB path.
2. Binding checklist: list likely binding families and properties without
   creating a binding patch.
3. FEL readiness checklist: list physical OTG path, entry method,
   controller-host, `sunxi-fel`, and `xfel` facts needed before any drill.
4. Queued proof recipe skeleton: draft blocked `A733-BATCH-009` and
   `A733-BATCH-012` recipes that remain disabled until board roles, recovery,
   and claim service permit them.
