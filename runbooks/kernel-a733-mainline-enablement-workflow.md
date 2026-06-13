# A733/Cubie A7S Mainline Enablement Workflow

Status: active project-specific durability-cycle workflow
Updated: 2026-06-13
Communication mode: local work only; do not send mail, list replies, pull
requests, issue comments, maintainer pings, or public pushes.

## Purpose

This workflow drives Radxa Cubie A7S / Allwinner A733 work toward mainline
Linux quality while communication is intentionally paused. It permits durable
local engineering, local patch preparation, evidence gathering, validation,
review-risk analysis, and documentation. It forbids public communication unless
the human operator explicitly reopens that gate.

The practical target is not "turn everything on at once." The target is to
make each hardware block boring enough that a maintainer can review it as a
small, justified, bisectable Linux change.

The continuous loop is a durability engine, not a patch-stacking engine. Its
best output is evidence, proof infrastructure, validation records, clean
integration hygiene, and DTS that mirrors already-landed sibling-SoC patterns.
It must not manufacture speculative driver logic or tall dependent stacks while
maintainer judgment is unavailable.

## Upstream Standards

Use these as the governing public standards:

- Linux patch submission process:
  <https://docs.kernel.org/process/submitting-patches.html>
- Linux patch submission checklist:
  <https://docs.kernel.org/process/submit-checklist.html>
- Devicetree binding submission rules:
  <https://docs.kernel.org/devicetree/bindings/submitting-patches.html>
- b4 contributor workflow:
  <https://b4.docs.kernel.org/en/latest/contributor/overview.html>

Local interpretation for this project:

- work from current upstream or the correct subsystem/prerequisite tree
- one logical change per patch
- every patch must build at its own position in the series
- every commit message must explain the problem, the hardware fact, and the
  exact change without relying on private links
- binding patches precede driver and DTS users
- DTS patches stay at the end of a series
- compatible strings used in DTS must already be documented by binding patches
- `scripts/checkpatch.pl` findings are either fixed or explicitly justified
- `scripts/get_maintainer.pl` output is recorded for any would-send series
- `b4 prep` owns final series metadata; flat patch files are review snapshots
- no invented trailers; `Signed-off-by`, `Tested-by`, `Reviewed-by`, and
  similar tags must reflect real authorization
- no `Fixes:`, `Cc: stable@vger.kernel.org`, or userspace ABI claims unless
  the specific criteria are met

## Communication Blackout

During this mode, do not:

- send `b4 send`
- use Gmail/Safari/Mail to reply to lists
- use `git send-email` for real delivery
- post GitHub issues, pull requests, review comments, or gist links as a
  substitute for mailing-list discussion
- ping maintainers
- push public branches or public artifacts
- add public-facing `Tested-by`, `Reported-by`, `Suggested-by`, or `Link`
  trailers that imply a communication or permission not actually present

Instead, record every communication that would normally be sent in:

```text
task-packets/kernel/a733-unsent-communications-ledger.md
```

If the correct next action depends on maintainer judgment, do not implement
past that uncertainty. Convert it to a precise held question in the ledger, add
the evidence needed for a maintainer to answer in one reply, and stop the cycle.

## Continuous Operation Model

Continuous work is allowed as repeated bounded work items:

```text
READ-STATE -> SELECT -> CONTRACT -> CLASSIFY-GATE -> CLAIM -> EXECUTE ->
PROVE -> LOG -> RELEASE -> CHECKPOINT
```

Codex Desktop may run multiple bounded work items in one invocation when each
item follows this full loop and the current disk state still permits another
safe Green item. Other agents may still run exactly one item and stop. A single
work item never carries a sprawling objective and never advances more than one
track.

Cycle commitments:

1. Select exactly one durable item.
2. Write a scope contract before touching files or running hardware-affecting
   commands.
3. Classify the item against the durability test and board-role envelope.
4. Claim the work item and every contended resource it touches.
5. Execute only the contracted work.
6. Produce the contracted proof or mark the item blocked.
7. Append one record to:

```text
task-packets/kernel/a733-cycle-ledger.md
```

8. Release claims and confirm the relevant tree state.
9. Continue only if another safe item is positively allowed by current disk
   state; otherwise stop.

The durability test is simple: only do work that remains useful regardless of a
future maintainer decision. If the right answer depends on review judgment,
maintainer preference, or an unsettled binding shape, do not build it during an
autonomous cycle.

## Interchangeable Agent Runtime

Agents are interchangeable only when state is on disk. At cycle start, the
agent must read this workflow, inventory, the hardware lane queue, the cycle
ledger, the communication ledger, and active claims. Conversation history and
prior-session memory are not authority.

Harness-provided context:

- `AGENT_ID`: stable worker identity, such as `codex-desktop` or `qwen-strix`
- `OPERATOR_PRESENT`: `true` only when a human is live for per-operation
  approval
- `APPROVAL_TIMEOUT`: default `120s` if unset; if approval is not received
  within this timeout, log and stop
- `REPO_ROOT`: homelab coordination repo path on the current host
- `INVENTORY`: `inventory/hardware/cubie-a7s-lab.json`
- `WORKFLOW`: this file
- `COMMS_LEDGER`: `task-packets/kernel/a733-unsent-communications-ledger.md`
- `CYCLE_LOG`: `task-packets/kernel/a733-cycle-ledger.md` or the matching
  SQLite-WAL record, once enabled
- `HARDWARE_QUEUE`: `task-packets/kernel/a733-supervised-batch-queue.md`

`AGENT_TIER` must not be self-declared by the model. The authoritative tier is
held by the claim service as an `AGENT_ID -> AGENT_TIER` registry and stamped on
claims server-side. A prompt or harness may display a tier for readability, but
the claim service is the authority.

Tier meanings:

- `local`: mechanical, pattern-following, verifiable work only. Route subtle
  driver root-cause, unclear binding shape, ambiguous register semantics, and
  maintainer-judgment work to the frontier queue or communication ledger.
- `frontier`: reasoning-heavy local work is allowed, still under the
  durability test, blackout, and board-role envelope.

Operating mode:

- Run one live agent at a time.
- That single agent may pipeline work across lanes, such as keeping a long
  burn-board experiment alive with heartbeat while doing software-only cycles.
- Do not enable true cross-runtime concurrency until the central claim service
  is active and verified.

## Claim Service

Do not build a new per-host claim system. The intended backend is the existing
ThinkCentre Fault Ledger/FastMCP SQLite-WAL pattern: SQLite stays local to
ThinkCentre, and agents use a narrow claim/release/heartbeat interface by
SSH-exec or the existing FastMCP surface.

Until that claim service exists and is verified, only one live agent may run
and destructive burn-board autonomy remains blocked.

Every EXECUTE step must first atomically claim each contended resource it
touches:

- work item ID
- board role or board lane
- UART by-path device
- power outlet or power-control handle, not the whole strip unless unavoidable
- kernel tree path
- staged artifact path when relevant

Claim rows must include:

- `AGENT_ID`
- server-stamped `AGENT_TIER`
- timestamp
- heartbeat timestamp
- item ID
- claimed resources
- cycle ID
- promotion state, when hardware is involved

If a non-stale claim exists, reselect a different item. A claim is stale only
after `CLAIM_TTL`, default `30m`, without heartbeat.

Stale-claim takeover rules:

- software, proving, and reference claims: log the stale claim before takeover.
- burn claims: log the stale claim, mark the burn board state `UNKNOWN`, and
  force recovery-to-pristine before any new burn, proving, reference, or proof
  work trusts that board.

Release all claims at the end of the cycle. If release fails, log it and stop;
do not begin another item.

## Tree State Rules

Coordination repo:

- leave no uncommitted changes outside the cycle's own scope
- either commit cycle-owned changes when explicitly requested, or log them as
  pending review in the cycle ledger
- tolerate pre-existing unrelated dirty files, but do not claim a globally
  clean repo when they exist

Kernel trees:

- any kernel tree touched by a cycle must still build for the relevant target,
  or the failure must be committed to a diagnostic branch with the exact
  build-state recorded
- do not leave half-edited kernel source outside a named diagnostic or
  integration branch
- public pushes remain forbidden during blackout

## Board-Role Envelope

Hardware autonomy is controlled by board role, not by a single global rule. The
role assignment must be read from inventory and must never be guessed from IP,
UART order, or convenience.

Required inventory fields for any state-changing hardware cycle:

- board name
- role: `burn`, `proving`, or `reference`
- UART by-path device and mapping status
- power-control handle, if any
- recovery rung, method, experiment ceiling, and drill status
- pristine image or known-good baseline
- current promotion state, if running a candidate artifact

`burn` board: full autonomous discovery lane. It may run the normal Green work
plus experimental boots, reboots, power-cycles, `/boot` installs, raw
experimental kernels, reversible register pokes, recovery-mode reflash, and
documented restore steps. Before each destructive experiment class, it must
verify that the recovery path is reachable. If recovery is not verified, the
same work downgrades to human-present. Reset the burn board to a pristine image
between hypothesis families so accumulated state does not contaminate results.
An unrecoverable brick is logged and escalated; the loop continues only on
software and non-burn lanes until the board is restored.

The burn role does not automatically enable firmware/SPI/eMMC bootloader
writes, fuses, or other unrecoverable persistent state. Those require explicit
burn-board sub-permissions in inventory.

`proving` board: controlled confirmation lane. It may run software staging,
passive capture, boots, and reboots only for artifacts that have already passed
on the burn board and are marked `CANDIDATE`. No raw experiments, no recovery
flashing, and no destructive storage or firmware work. A failure here means the
promotion gate is wrong and must be escalated.

`reference` board: protected control lane. It stays pinned to a known-good
vendor or last-fully-proven baseline. Unattended work is limited to passive
read-only capture and differential reads against baseline. Any non-baseline
boot, install, reboot for test purposes, or persistent mutation is human-gated.

Until roles and recovery are recorded in inventory, runtime-mutating work
remains queued. The current `power_switch: null` state means autonomous power
recovery is not available unless another documented recovery method is added.

## Recovery Ladder

Verified recovery-to-pristine is a ladder, not a boolean. The highest drilled
rung controls which burn-board experiment classes may run autonomously.

`none` or `unverified`: no autonomous state-changing hardware work. Build and
stage artifacts only.

`soft-fallback`: experimental kernels and DTBs are installed only as
non-default extlinux entries while a known-good default remains intact. This
recovers bad-kernel, bad-DTB, and bad-bootargs experiments when the board can be
rebooted or power-cycled back to the default. It does not recover bootloader,
SPI, eMMC-boot, firmware, rootfs-corrupting, or full-image corruption.

`sd-reimage`: a controller can take the removable microSD card, write a
pristine image, and hand it back without human card swapping. This requires an
SD-Mux/SDWire/sd-mux-ctrl-style path or equivalent. In-place reimage while the
board is still running is useful maintenance, but it is not recovery from a
board that can no longer boot.

`fel-bootrom`: Allwinner BootROM/FEL or equivalent can recover corrupted boot
media and rewrite firmware/SPI/eMMC where appropriate. For A733/SUN60IW2 this
must be drilled on the actual board with `sunxi-fel` or `xfel`; do not assume
support exists because older sunxi SoCs support FEL. Autonomous FEL also
requires a controller-reachable USB-OTG path and a documented way to enter FEL,
such as an assertable strap/button or proven boot-fail fallback.

Verification means a drill, not a declaration:

1. Deliberately induce the failure class the rung is meant to recover.
2. Run the recovery path without relying on undocumented manual steps.
3. Confirm a clean boot to the pristine image or known-good baseline.
4. Log the timestamp, board, rung, induced failure, recovery commands,
   artifacts, and proof result.

Role assignment should follow recovery capability. The burn board should be the
board with the strongest drilled recovery path. The reference board should be
the cleanest and least-mutated board. The proving board is the remaining
controlled confirmation lane.

## Promotion State Machine

Runtime promotion is separate from work-track state. Runtime results move
through the hardware lanes in this order:

```text
EXPERIMENT(burn) -> CANDIDATE -> CONFIRMED(proving, clean state) ->
BASELINE-VERIFIED(differential vs reference) -> PROVEN
```

Only `PROVEN` results may feed evidence packets or patch-series claims. A
burn-only pass is a candidate, never proof, because the burn board is allowed
to be dirty by design.

Selection must drain the promotion pipeline before generating new candidates.
A pending `CANDIDATE` awaiting proving-board confirmation outranks a fresh burn
experiment.

## Permission Envelope

Green work may run continuously on any role:

- read-only source, log, and artifact analysis
- local-only commits to diagnostic or integration branches
- cross-compile builds
- passive UART capture that does not reboot or power-cycle a board
- `checkpatch`, `dt_binding_check`, `dtbs_check`, `dt-validate`, sparse, smatch,
  and similar validation
- documentation, evidence packet, cycle ledger, and communication ledger writes
- staging artifacts to a local holding directory with hashes

Role-gated work may run only when the selected board role permits it:

- board boot, reboot, shutdown, power-cycle, or serial break
- installing or replacing `/boot` files
- changing U-Boot environment, SPI flash, eMMC boot partitions, firmware,
  EEPROM, fuses, or persistent board configuration
- active tests that may wedge networking, storage, power, clocks, thermal
  behavior, or rootfs state
- multi-board reproduction passes that require physical cable/power decisions

Record role-gated work, queued work, and promotion work in:

```text
task-packets/kernel/a733-supervised-batch-queue.md
```

Red work is never allowed in this mode:

- public communication
- public sends
- `b4 send`
- `git send-email` delivery
- list replies
- GitHub comments, pull requests, issues, or public gists
- public pushes
- agent-initiated paid or third-party API calls beyond the agent's own
  inference/runtime

Hardware destructiveness is not Red by itself. Hardware risk is governed by the
board-role envelope. A destructive action on the burn board may be allowed when
the burn role, recovery method, pristine image, and claims all permit it. The
same action on proving or reference is blocked by role, not by the Red boundary.

## Selection Function

Pick the single highest-value item by this deterministic order:

1. unblocks the most downstream durable work
2. most likely to remain valid after review
3. most mechanical, pattern-following, and verifiable
4. has a clear proof definition
5. can finish in one bounded cycle
6. drains an existing promotion candidate before opening a new experiment

Hard exclusions for autonomous cycles:

- NPU, PowerVR GPU, RISC-V MCU, DisplayPort Alt Mode, or other long-horizon
  tracks beyond a one-page "why not yet" assessment
- subtle driver root-cause work that requires novel reasoning
- any new binding shape that is not mirrored from landed sibling-SoC precedent
- any item that requires a maintainer answer before the next technical step
- any role-gated action whose board role, UART mapping, and recovery state are
  not recorded
- any Red action

## Work-Track State Model

Each peripheral or patch track moves through these states:

1. `inventory-only`: hardware exists or is claimed, but no source-backed Linux
   model exists yet.
2. `evidence`: vendor docs, schematics, DTS, driver source, public patches, or
   measured registers identify a plausible Linux representation.
3. `lab-diagnostic`: local patch or boot artifact used only to learn behavior.
4. `local-candidate`: patch is shaped like upstream work, but still lacks one
   or more proof or dependency gates.
5. `sendable-held`: patch has passed local gates, but communication blackout or
   dependency timing prevents public send.
6. `question-held`: progress depends on a maintainer/subsystem decision; the
   precise question and evidence are in the unsent communications ledger.
7. `role-gated`: next useful action requires a board role, recovery rung,
   recovery drill, claim service, or human-present condition not currently
   satisfied.
8. `obsolete`: superseded by better evidence, upstream work, or a failed
   falsifier.

Hardware runtime promotion uses `EXPERIMENT`, `CANDIDATE`, `CONFIRMED`,
`BASELINE-VERIFIED`, and `PROVEN`. Those are promotion states, not work-track
states.

Recovery uses `none`, `unverified`, `soft-fallback`, `sd-reimage`, and
`fel-bootrom`. Those are recovery rungs, not work-track states.

Never skip from `inventory-only` or `evidence` straight to `sendable-held`.
Never let an autonomous cycle move a work track past `question-held` or
`role-gated`.

## Bounded Work Item

A bounded work item is the only unit of autonomous work.

1. SELECT: read this workflow, the track matrix, the cycle ledger, the
   hardware lane queue, and active task packets. Choose one item using the
   selection function. Drain existing promotion candidates before starting new
   burn experiments.
2. CONTRACT: write a short scope contract in the cycle ledger before action.
   It must name the exact change or analysis, files in scope, proof definition,
   and explicit non-goals.
3. CLASSIFY-GATE: confirm the item is durable and allowed by the selected board
   role. If it is maintainer dependent, write a held question in the
   communication ledger and end. If the required board role, recovery path, or
   human-present condition is missing, queue it in the hardware lane queue and
   end. If it is Red, reject it and end.
4. CLAIM: atomically claim the work item and all contended resources. If a
   non-stale claim exists, reselect once. If the stale claim is on the burn
   board, mark that board `UNKNOWN` and queue recovery-to-pristine before
   trusting it.
5. EXECUTE: do only the contracted work. For long burn experiments, heartbeat
   the claim before `CLAIM_TTL` expires.
6. PROVE: produce the contract's proof. If proof fails, mark the item blocked
   with the reason and at most one safe reselection. Do not half-finish.
7. LOG: append commands, artifacts, hashes, proof result, promotion state,
   tree state, claim state, and the next-selection pointer to the cycle ledger.
8. RELEASE: release all claims. If release fails, log it and stop.
9. CHECKPOINT: confirm the tree state relevant to the item. Codex Desktop may
   continue to another safe item after rereading relevant authority files.
   Single-cycle agents stop here.

For each hardware block, the human-facing engineering path remains:

1. Define the smallest upstreamable claim.
2. Identify the correct subsystem and existing driver model.
3. Gather source-backed evidence.
4. Draft the binding change, if any, only when the binding shape is already
   supported by precedent or is explicitly approved for human/frontier work.
5. Draft the driver change, if any, only when the model is source-backed and
   not speculative.
6. Draft the SoC DTSI node disabled by default.
7. Draft the board DTS enablement only after board-level proof exists.
8. Run static validation.
9. Queue runtime proof if it needs boot, reboot, install, or power action.
10. Reproduce on a second Cubie when the change affects boot, storage,
    networking, clocks, resets, power, or shared infrastructure.
11. Run maintainer-risk review with the prompt:
    `Find three reasons a Linux kernel maintainer would reject this code.`
12. Record any would-send cover letter, reply, or `Tested-by` note in the
    unsent communications ledger.
13. Mark the track state.

## Required Evidence Packet

Every local-candidate track needs a packet under `task-packets/kernel/` with:

- task ID
- source branch and base commit
- cycle ledger ID
- agent ID and server-stamped agent tier
- claim IDs and claimed resources
- operator-present flag and approval timeout, when relevant
- scope contract
- classification gate result
- touched files
- hardware board and revision if known
- board role, recovery rung, experiment ceiling, and recovery drill status
- exact boot artifacts, if runtime-tested
- exact kernel config or defconfig target
- proof commands
- proof result
- artifact paths and hashes
- UART/dmesg/log artifact paths
- expected maintainer objection list
- rollback path
- clean-tree or dirty-tree explanation
- whether communication would normally be sent
- ledger entry ID for any withheld communication
- hardware lane queue IDs for role-gated or promotion work

## Validation Floor

Use the strongest relevant subset. Do not claim a pass that was not run.

Coordination-file changes:

```sh
python3 tools/validate/a733_authority_check.py
python3 -m json.tool inventory/hardware/cubie-a7s-lab.json >/dev/null
git diff --check -- runbooks/kernel-a733-mainline-enablement-workflow.md task-packets/kernel/a733-cycle-ledger.md task-packets/kernel/a733-unsent-communications-ledger.md task-packets/kernel/a733-supervised-batch-queue.md inventory/hardware/cubie-a7s-lab.json
```

Baseline for any patch:

```sh
git diff --check
scripts/checkpatch.pl --strict --no-tree --git <range>
scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats <patches>
```

Devicetree:

```sh
make dt_binding_check
make CHECK_DTBS=y ARCH=arm64 <target-dtb>
dt-validate <built-dtb>
```

Driver code:

```sh
make ARCH=arm64 <relevant-target>
make C=1 ARCH=arm64 <relevant-target>
```

When practical:

```sh
make W=1 ARCH=arm64 <relevant-target>
sparse or smatch for touched driver areas
clang build for touched subsystem
```

Runtime proof:

- exact git commit
- exact Image/DTB
- exact bootargs
- UART capture
- dmesg excerpt
- one command proving the feature works
- one falsifier or negative observation
- no raw private lab logs in public-facing docs

## Series Discipline

Expected ordering for multi-part A733 work:

1. dt-bindings
2. dt-bindings headers
3. core driver or subsystem support
4. SoC DTSI, usually disabled by default
5. board DTS enablement
6. defconfig only if the subsystem normally accepts it and the reason is clear

Do not mix these in one patch:

- binding plus driver
- driver plus board DTS enablement
- unrelated peripherals
- vendor workaround plus upstream model
- diagnostic logging plus behavior change
- code movement plus semantic edits

Large work should be split into separate series by subsystem even if the local
goal is full board enablement.

## Board Source Scope

Public board capabilities to track for Cubie A7S:

- Allwinner A733
- 2 Cortex-A76 plus 6 Cortex-A55 CPUs
- RISC-V E902 MCU
- LPDDR5
- optional eMMC
- microSD
- Gigabit Ethernet
- Wi-Fi 6
- Bluetooth 5.4
- PCIe 3.0 x1 FPC for NVMe/adapters
- USB-C USB 2.0 power/OTG
- USB-C USB 3.2 with DisplayPort Alt Mode and OTG
- USB 2.0 Type-A host
- MIPI CSI 4-lane camera connector
- fan header
- 15-pin and 30-pin GPIO headers with UART, I2C, I2S, PWM, GPIO, and related
  low-speed functions
- 3 TOPS NPU
- PowerVR BXM-4-64 MC1 GPU
- video encode/decode blocks

Treat marketing and product-page claims as inventory only. Upstreamable Linux
claims require driver, binding, DTS, and runtime evidence.

## Track Matrix

Autonomous cycle bucket meanings:

- Bucket A: durable Green work suitable for bounded autonomous cycles.
- Bucket B: useful runtime work that must follow the board-role envelope and
  promotion state machine before it can become proof.
- Bucket C: inventory/evidence only during blackout; no implementation beyond
  "why not yet" notes.

### Current Local Track Snapshot

Updated: 2026-06-13 from local task-packet records only. This snapshot is an
orientation layer, not a substitute for the detailed packets.

Current evidence index:

```text
task-packets/kernel/a733-current-evidence-index.md
```

Use this index to find the active local proof and fallback packets before
preparing any response draft, regeneration, or proof bundle. It is a pointer,
not a communication approval and not a substitute for the five authority files.

| Track | Current state | Key local records | Local-only next action |
|---|---|---|---|
| Cubie A7S DTS v1 | `sent-before-blackout`; public v1 is recorded as sent and indexed | H261-H265, A733-COMM-016 | Do not resend. Prepare v2 only if maintainer feedback, prerequisite landing, or a concrete correction requires it. |
| Cubie A7S DTS v2 | `question-held` / `sendable-held` candidate | A733-COMM-002, A733-COMM-003, H260-H265 | Keep local cleanup aligned with Jernej's feedback: SoC pin group in DTSI, no Ethernet, and clock/prerequisite timing respected. |
| A733 CCU/SDMMC0 keepalive | `sent-before-blackout`; local proof exists but public visibility was mixed in earlier records | H200-H247, A733-COMM-013 through A733-COMM-015 | Do not resend. Preserve H200/H201/H211/H247 evidence and prepare only local response notes until communication reopens. |
| Common update-bit helper option | `local-candidate` / fallback candidate | H242-H253 | Keep as a local alternative only. Do not promote without maintainer feedback or a source-backed reason to replace the sent H215 shape. |
| Hardware role model | `role-gated` | A733-BATCH-000, inventory `kernel_work_role_model` | Collect physical boot-media, USB-OTG/FEL, power-control, recovery-drill, and cleanest-board facts before assigning burn/proving/reference. |
| Runtime proof lanes | `role-gated` | A733-BATCH-001 through A733-BATCH-012 | Queue work only. Do not boot, reboot, install, power-cycle, or mutate boards until roles, recovery rung, drill, and claim service permit it. |
| Ethernet/PCIe/USB/Wi-Fi/Bluetooth/media/NPU/RISC-V | `inventory-only` or `evidence` depending on block | Track matrix sections E-L and hardware queue | Continue source-backed inventory and validation planning. Avoid implementation until dependencies, bindings, and runtime proof lanes are ready. |

### A. Minimal DTS v2

Scope:

- A733 SoC DTSI
- Cubie A7S board DTS
- UART0 console
- SD-card boot storage only

Required local work:

- move `uart0_pb9_pb10_pins` into `sun60i-a733.dtsi`
- keep board DTS referencing the SoC pin group
- fix sashiko-bot findings
- rebase on current prerequisite stack
- rebuild and boot exact Image/DTB

State target: `sendable-held`.
Autonomous bucket: A for static cleanup and validation; B for boot proof.

Would-send item:

- v2 cover letter and changelog, withheld until communication opens and clock
  prerequisites are in a maintainer-acceptable state.

### B. RTC, CCU, R-CCU, Resets

Scope:

- RTC oscillator providers
- main CCU
- PRCM/R-CCU
- reset IDs
- storage and fabric clocks

Required local work:

- track in-flight A733 RTC and CCU/PRCM series
- compare local assumptions against current public patch IDs
- prove every clock and reset ID used by DTS
- avoid duplicate standalone submissions while overlapping work exists
- produce local integration branch that can be dropped if upstream lands first

State target: `local-candidate` or `sendable-held`, depending on overlap.
Autonomous bucket: A for tracking, integration hygiene, and validation; B for
runtime clock/reset proof.

### C. Pinctrl and GPIO IRQs

Scope:

- A733 pin banks
- mux functions
- bias and drive strength
- GPIO IRQ banks
- pin groups reused by board DTS

Required local work:

- track in-flight A733 pinctrl series
- test IRQ bank behavior on hardware
- add SoC-level pin groups for common controller pins
- avoid shared-core hacks unless a subsystem maintainer would accept the design

State target: `local-candidate`.
Autonomous bucket: A for landed-pattern comparison and static pin group work;
B for hardware IRQ proof.

### D. SD Card and eMMC

Scope:

- SDMMC0 microSD
- optional eMMC nodes and variants
- normal IDMAC data path
- tuning, voltage, and high-speed modes only after base stability

Required local work:

- finish SDMMC0 IDMAC descriptor-fetch root cause
- separate diagnostic patches from behavior patches
- prove read/write rootfs stability
- add eMMC only after identifying exact controller, bus width, reset, clock,
  power rail, and board population behavior
- test `mmc-utils`, filesystem write, reboot, and cold boot

State target: `local-candidate` first, then `sendable-held`.
Autonomous bucket: A for evidence, builds, diagnostic analysis, and staged test
artifacts; B for boot/rootfs/write/reboot proof.

### E. Ethernet

Scope:

- A733 GMAC wrapper
- STMMAC glue, if required
- MDIO bus
- PHY reset and power
- board DTS Ethernet enablement

Required local work:

- identify exact GMAC/GMAC210 programming model
- prove clocks and resets
- prove wrapper/syscon routing
- identify PHY model, reset GPIO, power rail, and MDIO behavior
- validate link, DHCP/static IP, ping, iperf, and reboot persistence
- keep DTS disabled until driver and hardware proof are ready

State target: `local-candidate`.
Autonomous bucket: A for source-backed evidence and staged DTS/driver review
snapshots; B for link/DHCP/iperf proof.

### F. PCIe and NVMe

Scope:

- PCIe controller
- PCIe PHY
- reset, clock, regulator, PERST#, wake
- FPC connector
- NVMe and adapter proof

Required local work:

- identify controller IP and existing Linux driver match
- add binding only if a new compatible is required
- prove link training, lane width, and speed
- test NVMe enumeration and fio
- test representative adapters separately from NVMe storage

State target: `local-candidate`.
Autonomous bucket: A for controller/PHY evidence and static validation; B for
link training and NVMe proof.

### G. USB and USB-C

Scope:

- USB2 power/OTG Type-C
- USB3/DP/OTG Type-C
- USB2 Type-A host
- PHYs
- role switch
- VBUS regulators

Required local work:

- identify controller and PHY topology
- prove host and device modes independently
- add Type-C/role-switch support only with source-backed controller evidence
- test storage, keyboard, serial, Ethernet dongle, and gadget mode
- keep DP Alt Mode out of USB-only patches

State target: `local-candidate`.
Autonomous bucket: A for topology evidence and static validation; B for
host/device/gadget runtime proof.

### H. Wi-Fi and Bluetooth

Scope:

- onboard Wi-Fi 6 module
- Bluetooth 5.4 side
- firmware loading
- power, reset, wake, and transport buses

Required local work:

- identify exact module and transport
- identify firmware licensing and mainline driver availability
- prove scan, association, throughput, and suspend/reconnect for Wi-Fi
- prove controller init, scan, pair, and basic input/audio behavior for
  Bluetooth
- split Wi-Fi and Bluetooth unless the binding genuinely requires a shared
  power-sequence node

State target: `evidence` until driver path is clear.
Autonomous bucket: A for module identification and firmware/license inventory;
B for association/pairing runtime proof.

### I. Display, GPU, and DP Alt Mode

Scope:

- display engine
- USB-C DisplayPort Alt Mode
- DRM pipeline
- PowerVR BXM GPU

Required local work:

- identify display pipeline blocks and clocks
- prove EDID, modeset, hotplug, and 4K mode claims separately
- treat GPU acceleration as separate from basic display output
- do not claim PowerVR acceleration unless a mainline driver path exists

State target: `evidence` for GPU, `local-candidate` only for display pieces
with existing subsystem support.
Autonomous bucket: C for GPU and DP Alt Mode; A only for source-backed display
inventory against existing subsystem support.

### J. Video, Camera, and Media

Scope:

- MIPI CSI 4-lane connector
- camera receiver
- VPU/Cedrus-style decode/encode
- media IOMMU paths

Required local work:

- split binding, clock/reset, media driver, and DTS changes
- validate with `v4l2-compliance` where applicable
- capture a frame for CSI proof
- decode/encode media samples only after the driver and memory path are known

State target: `evidence` until source-backed block model is solid.
Autonomous bucket: C for implementation; A only for inventory and existing
driver-path evidence.

### K. NPU

Scope:

- 3 TOPS NPU
- firmware/runtime ABI
- IOMMU or reserved memory, if any

Required local work:

- identify exact IP block and mainline subsystem path
- audit vendor runtime and firmware requirements
- avoid DTS enablement without a mainline driver and acceptable userspace ABI
- document local-only runtime experiments separately

State target: `inventory-only` or `evidence`.
Autonomous bucket: C.

### L. RISC-V E902 MCU / ARISC / Firmware

Scope:

- RISC-V E902 real-time core
- firmware loading
- mailboxes
- SRAM/reserved memory
- remoteproc or firmware interface

Required local work:

- identify whether Linux directly controls this core
- map firmware handoff and secure-world boundaries
- test only with recoverable firmware artifacts
- do not write SPI/eMMC boot firmware without explicit separate approval

State target: `evidence`.
Autonomous bucket: C.

### M. Low-Speed I/O, Audio, Fan, Thermal, Power

Scope:

- additional UARTs
- I2C
- SPI
- PWM
- I2S/audio
- fan header
- thermal sensor
- CPU OPP/DVFS/cpufreq
- regulators and power domains

Required local work:

- test each bus with an external device or loopback proof
- identify header pin ownership and pinmux conflicts
- validate thermal readings under load
- validate fan PWM or tach behavior if exposed
- validate cpufreq transitions, stability, and thermals
- document regulator names and consumers

State target: `local-candidate` per bus or feature.
Autonomous bucket: A for static/header/pin inventory and validation; B for
external-device, fan, thermal-load, or cpufreq runtime proof.

## Seed Queue And Work Order

The first autonomous seed queue is:

1. Maintain a clean integration view of in-flight A733 RTC, CCU, PRCM, reset,
   and pinctrl prerequisites.
2. Keep minimal DTS v2 cleanup aligned with landed or clearly prerequisite
   sibling-SoC patterns.
3. Deepen hardware evidence for Bucket A/B blocks: SDMMC/eMMC, GMAC, UART,
   I2C, SPI, thermal, regulators, and fan.
4. Build and harden validation/proof infrastructure.
5. Reconcile hardware facts against vendor source: exact PHY, Wi-Fi module and
   transport, GPIO maps, power rails, register offsets, and reset lines.
6. Catalog negative results that narrow the search space.
7. Keep validation floor results current as local and upstream trees move.

The hardware-lane work order is:

1. Record physical wiring facts and assign burn/proving/reference roles.
2. Drill the burn board's highest claimed recovery rung.
3. Minimal DTS v2 boot proof.
4. SDMMC0 IDMAC/rootfs stability proof.
5. RTC/CCU/R-CCU/reset runtime proof.
6. Pinctrl hardware IRQ/bank proof.
7. eMMC proof after SD card is stable.
8. Ethernet link/DHCP/iperf proof.
9. PCIe/NVMe link and storage proof.
10. USB/USB-C host/device/gadget proof.
11. Wi-Fi/Bluetooth runtime proof.
12. Thermal/cpufreq/fan proof.
13. Display/DP proof only when source-backed prerequisites exist.
14. CSI/media/VPU proof only when source-backed prerequisites exist.
15. GPU, NPU, and RISC-V MCU remain Bucket C unless a credible mainline path
    is established.

This order can change when evidence changes, but the reason must be recorded
in the relevant task packet or cycle ledger.

## Communication Ledger Protocol

Any time a normal upstream workflow would call for a message, create or update
an entry in:

```text
task-packets/kernel/a733-unsent-communications-ledger.md
```

Required fields:

- ID
- date
- communication type
- target thread or subsystem
- intended recipients
- trigger
- precise question, when diverted by CLASSIFY-GATE
- evidence needed for a maintainer to answer in one reply
- draft location
- current status
- send blocker
- reopen condition

Allowed statuses:

- `draft-needed`
- `drafted-not-reviewed`
- `ready-held`
- `question-held`
- `obsolete-unsent`
- `sent-before-blackout`

The ledger is not a queue to drain automatically. When communication reopens,
each item must be reviewed against current source, current public threads, and
current maintainer feedback before it can be sent.

## Completion Definition

This workflow is succeeding when:

- every hardware block has a state and next action
- every bounded work item has exactly one cycle ledger record
- every cycle has a scope contract before execution
- every role-gated item is queued or run only inside the allowed board role
- no burn-only result is treated as proof
- every maintainer-dependent decision becomes a held question
- every local patch has a proof packet
- every communication that would normally happen is captured as either held
  unsent work or a historical no-resend record
- every sendable-held series can be regenerated from a clean branch
- no public mail or public comment occurs during the communication blackout
- future maintainers would see small, evidence-backed, subsystem-shaped work
