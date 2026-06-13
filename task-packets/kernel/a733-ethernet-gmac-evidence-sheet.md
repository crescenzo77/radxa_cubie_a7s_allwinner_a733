# A733 Ethernet / GMAC Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet narrows the Radxa Cubie A7S / Allwinner A733 Ethernet track to the
evidence needed before any maintainer-standard kernel patchwork. It is not a
patch plan, not a DTS enablement approval, not new proof, not a hardware test,
and not a public communication.

## Current Boundary

- Stay local-only.
- Do not enable Ethernet in the Cubie A7S DTS.
- Do not invent GMAC clock or reset identifiers.
- Do not edit kernel trees.
- Do not boot, reboot, SSH probe, UART capture, cable-test, or power-cycle
  any board.
- Do not send mail, b4 submissions, list replies, GitHub comments, public
  pushes, or paid third-party calls.

## Current Status

Ethernet / GMAC is `inventory/planning only`.

The current local consensus is to keep GMAC out of the first upstream slice.
Earlier validation failed when `sun60i-a733.dtsi` referenced
`CLK_BUS_GMAC0` and `RST_BUS_GMAC0` without matching A733 dt-bindings header
definitions. A later validation slice passed the Cubie A7S DTB build only
after deferring unproven GMAC.

Relevant local records:

- `runbooks/kernel-layout.md`
- `runbooks/kernel-review-handoff.md`
- `runbooks/kernel-proof-harness.md`
- `runbooks/cubie-a7s-hardware-lab.md`
- `inventory/kernel-a733-thread-quick-reference-20260608.md`
- `task-packets/kernel/a733-gmac-clock-reset-bindings.json`
- `task-packets/kernel/a733-peripheral-evidence-map.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`

## Known Local Evidence

- Prior local notes say the GMAC0 path has evidence for address, Port H RGMII
  pins, MDIO address 1, and probe when pinctrl or PIO IRQ handling is bypassed.
- That is not full Ethernet support.
- Prior local notes also identify a recurring Port H `PH0` stall that may
  involve A733 PIO IRQ handling, pending IRQ state, or chained-handler
  behavior.
- The missing `vcc-ph` supply and zero-based IRQ-bank-map tests did not fully
  explain the Port H issue.
- The first Cubie A7S DTB validation path failed when unproven GMAC clock and
  reset IDs were referenced.
- The repaired validation path passed only after GMAC was deferred.

## Read-Only Source Observations

From `/Users/enzo/projects/linux-a733`, read only:

- STMMAC platform code parses DT MDIO, MAC mode, clocks, resets, resources,
  and IRQs in `drivers/net/ethernet/stmicro/stmmac/stmmac_platform.c`.
- Existing Allwinner DWMAC support lives in
  `drivers/net/ethernet/stmicro/stmmac/dwmac-sun8i.c`.
- The Allwinner DWMAC glue handles syscon fields, optional PHY regulators,
  internal PHY plumbing on older variants, MDIO mux registration, and runtime
  clock handling.
- Existing Allwinner DTS examples use `phy-mode`, `phy-handle`, `phy-supply`,
  MDIO child PHY nodes, and board-specific regulator nodes.
- Existing sibling DTS examples are patterns to compare against, not proof that
  the A733 GMAC210 wrapper is compatible.

These observations are source inventory only. They do not prove A733 Ethernet.

## Required Evidence Before Implementation

### Controller / Wrapper

- Exact GMAC or GMAC210 programming model.
- Whether existing `dwmac-sun8i` glue applies as-is, needs a new compatible,
  or needs a distinct wrapper.
- Syscon/register field location for interface mode, clock delay, muxing, and
  any A733-specific wrapper bits.
- Whether the wrapper overlaps CCU/PRCM or pinctrl prerequisite work.

### Clocks And Resets

- Correct A733 GMAC bus clock identifiers.
- Correct A733 GMAC reset identifiers.
- Evidence for any TX/RX, EPHY, PTP, AHB, AXI, or wrapper clocks beyond the
  simple STMMAC `stmmaceth` clock.
- Proof that identifiers are defined in bindings before DTS uses them.
- No placeholder `CLK_BUS_GMAC0` or `RST_BUS_GMAC0` unless source evidence and
  bindings support those exact names and values.

### MDIO And PHY

- Exact external PHY model or confirmed generic C22/C45 use.
- MDIO address, currently believed from local notes to involve address 1, but
  still requiring source/runtime confirmation before upstream claim.
- PHY reset GPIO, polarity, and timing.
- PHY power rail and regulator naming.
- Whether `phy-mode` is `rgmii`, `rgmii-id`, `rgmii-txid`, or another mode.
- Whether RX/TX delay is handled in PHY strap, PHY driver, or MAC wrapper.

### Pinctrl / Port H

- Port H RGMII pin group ownership.
- Interaction with the unresolved Port H `PH0` stall.
- Whether pinctrl IRQ/bank behavior must land before Ethernet proof.
- Safe pinmux definition location and naming.

### Runtime Proof

Runtime proof is role-gated through `A733-BATCH-007` and is not allowed now.
When later allowed, proof must include:

- exact source base and head
- exact Image and DTB hashes
- exact board role, UART path, power path, and recovery rung
- MDIO probe and PHY ID
- link up/down behavior
- DHCP or static IP
- ping to a controlled peer
- iperf or equivalent throughput sanity
- reboot persistence
- negative markers, including no kernel panic and no repeated PHY reset/link
  flap

## Communication Hook

`A733-COMM-007` is the held future communication hook for Ethernet/GMAC.

Do not draft or send a cover letter from this sheet. If a maintainer-dependent
question becomes precise, record it in the communications ledger as a held
question with the smallest evidence bundle needed for a one-reply answer.

## Hard Stop Conditions

Stop local Ethernet work and log the blocker if:

- the GMAC wrapper model is still unknown
- clock or reset IDs are guessed
- PHY model, reset, power, or MDIO address is inferred from a stale note only
- the work depends on live board probing
- the work depends on maintainer preference
- the path starts to edit DTS or driver source before evidence is complete
- a patch would broaden into CCU, pinctrl, or DTS changes without a clean split

## Safe Next Local Items

Choose one per bounded cycle:

1. Source-only wrapper comparison: compare `dwmac-sun8i` variants and A733
   local notes, recording only what is known and unknown.
2. Binding checklist: list the binding properties Ethernet would need, without
   creating a binding patch.
3. PHY evidence checklist: reconcile local notes about MDIO address 1, Port H
   RGMII pins, reset, and power rail into source-backed known/unknown fields.
4. Runtime proof recipe draft: write a queued A733-BATCH-007 recipe skeleton
   that remains blocked until board roles, recovery drill, and claim service
   allow it.
