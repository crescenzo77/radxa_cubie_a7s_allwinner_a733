# A733 Hardware Lane Queue

Status: active role-gated hardware queue
Updated: 2026-06-13

This queue holds Radxa Cubie A7S / Allwinner A733 tasks that require a hardware
lane decision. Some entries may run unattended on the `burn` board after
recovery is verified. Some may run unattended on the `proving` board only after
burn-board promotion. Some remain human-gated on the `reference` board.

Queued work is not approval to execute on an arbitrary board. Before running a
batch, confirm the exact board role, UART, power path, recovery method, boot
media, artifacts, rollback path, promotion state, and stop condition.

Also confirm the recovery rung and experiment ceiling. A recovery method is
verified only after a drill that deliberately induces the covered failure,
recovers the board, confirms clean boot, and records timestamped evidence.

Any running hardware-lane batch must hold claims for the work item, board lane,
UART by-path, power outlet or power-control handle, kernel tree path, and staged
artifact path. Long burn-board experiments must heartbeat before `CLAIM_TTL`
expires. A stale burn-board claim marks that board `UNKNOWN` and forces
recovery-to-pristine before any future proof trusts it.

The claim service is planned but not active. Until it is active, keep
cross-runtime concurrency disabled and do not start destructive burn-board
autonomy.

## Board Roles

- `burn`: full autonomous discovery lane. Destructive boots, `/boot` installs,
  power cycles, and recovery reflashes are allowed only when recovery is
  verified before the experiment class.
- `proving`: controlled confirmation lane. Boots and reboots are allowed only
  for artifacts promoted from burn-board success. No raw experiments.
- `reference`: protected control lane. Passive capture and baseline
  differential reads only unless the human operator explicitly opens the gate.

## Promotion States

- `EXPERIMENT`: burn-board run in progress or ready
- `CANDIDATE`: passed on burn; awaiting proving-board confirmation
- `CONFIRMED`: passed on proving board from clean state
- `BASELINE-VERIFIED`: compared against reference baseline
- `PROVEN`: eligible for evidence packets and patch-series claims

## Recovery Rungs

- `none` or `unverified`: no autonomous state-changing hardware work
- `soft-fallback`: non-default extlinux kernel/DTB/bootargs experiments only
- `sd-reimage`: removable microSD full-image recovery through SD-Mux/SDWire or
  equivalent controller path
- `fel-bootrom`: A733/SUN60IW2 BootROM/FEL recovery drilled on the actual board
  with `sunxi-fel` or `xfel` and controller-reachable OTG/entry path

## Status Values

- `candidate`: known future hardware-lane task, not ready to run
- `staged`: artifacts and recipe exist, awaiting the required board role
- `running`: hardware-lane batch is actively in progress
- `completed`: proof captured and recorded
- `blocked`: cannot run until a named blocker is resolved
- `unknown`: burn-board state is unknown after a stale/crashed destructive
  experiment; recovery-to-pristine is required before further trust
- `obsolete`: no longer needed

## Queue

| ID | Track | Status | Lane | Promotion state | Required rung | Trigger | Required before run |
|---|---|---|---|---|---|---|---|
| A733-BATCH-000 | Board role and recovery-rung assignment | `candidate` | all boards | n/a | n/a | user provides wiring/recovery facts | choose burn/proving/reference roles, record recovery rung and experiment ceiling per board |
| A733-BATCH-001 | Soft-fallback recovery drill | `candidate` | future burn board | n/a | `soft-fallback` | burn board candidate chosen | induce bad non-default kernel/DTB entry, recover to known-good default, log clean boot |
| A733-BATCH-002 | Minimal DTS v2 boot proof | `candidate` | burn -> proving -> reference differential | `EXPERIMENT` | `soft-fallback` | DTS v2 local cleanup produces Image/DTB | exact artifacts, UART mapping, boot recipe, rollback card, recovery drill |
| A733-BATCH-003 | SDMMC0 IDMAC/rootfs stability proof | `candidate` | burn first; proving after candidate | `EXPERIMENT` | `soft-fallback` for kernel-only diagnostics; `sd-reimage` for rootfs-corrupting tests | diagnostic/root-cause candidate is staged | source-backed hypothesis, test rootfs, write/reboot/cold-boot recipe, recovery drill |
| A733-BATCH-004 | RTC/CCU/R-CCU/reset runtime proof | `candidate` | burn first; proving if shared infrastructure changes | `EXPERIMENT` | `soft-fallback` | prerequisite stack changes or lands | exact branch/base, clock/reset assertions, UART capture recipe |
| A733-BATCH-005 | Pinctrl GPIO IRQ/bank proof | `candidate` | burn first; proving for confirmed pin behavior | `EXPERIMENT` | `soft-fallback` | pinctrl assumptions are staged | pin map, safe pins, test wiring, rollback plan |
| A733-BATCH-006 | eMMC proof | `candidate` | burn only until non-destructive plan is proven | `EXPERIMENT` | `sd-reimage` or stronger for destructive storage; `soft-fallback` for read-only | SD card path is stable and eMMC node is staged | population check, non-destructive read-only plan before write tests |
| A733-BATCH-007 | Ethernet proof | `candidate` | burn -> proving | `EXPERIMENT` | `soft-fallback` | GMAC/PHY model is staged | PHY ID, cable/switch path, static/DHCP plan, iperf peer |
| A733-BATCH-008 | PCIe/NVMe proof | `candidate` | burn -> proving | `EXPERIMENT` | `soft-fallback` for enumeration; `sd-reimage` for storage writes | PCIe/PHY model is staged | adapter inventory, power budget, NVMe rollback, fio recipe |
| A733-BATCH-009 | USB/USB-C proof | `candidate` | burn -> proving | `EXPERIMENT` | `soft-fallback` | USB topology and role switch model are staged | device list, OTG/host plan, no-conflict power path |
| A733-BATCH-010 | Wi-Fi/Bluetooth proof | `candidate` | burn -> proving | `EXPERIMENT` | `soft-fallback` | exact module and driver/firmware path known | firmware source, AP/test device, pairing/throughput recipe |
| A733-BATCH-011 | Thermal/cpufreq/fan proof | `candidate` | burn first; proving after temperature limits are safe | `EXPERIMENT` | `soft-fallback` plus thermal stop threshold | thermal/fan/cpufreq nodes are staged | temperature limits, fan wiring, stop threshold, workload recipe |
| A733-BATCH-012 | FEL/BootROM recovery drill | `candidate` | future burn board | n/a | `fel-bootrom` | OTG path and entry method are physically wired | test `sunxi-fel` and `xfel` on actual A733/SUN60IW2 board before enabling firmware/SPI/eMMC-boot work |
| A733-BATCH-013 | Display/media/GPU proof | `candidate` | burn -> proving | `EXPERIMENT` | `soft-fallback` plus visible-console rollback path | display/media/GPU source model and board connector/sensor facts are staged | connector/panel/bridge/sensor inventory, thermal stop threshold, visible-output or capture recipe, rollback plan |
| A733-BATCH-014 | NPU/RISC-V MCU proof | `candidate` | burn only until firmware and crash recovery are proven safe | `EXPERIMENT` | `fel-bootrom` for firmware/remoteproc crash work; stronger rung if persistent firmware/storage is touched | source-backed NPU or MCU model, firmware provenance, memory map, and userspace/IPC ABI story are staged | firmware source/license, memory-region and mailbox map, crash/recovery recipe, no persistent firmware writes without sub-permission |
| A733-BATCH-015 | Audio/I2S proof | `candidate` | burn -> proving | `EXPERIMENT` | `soft-fallback` plus safe output/capture limits | source-backed audio controller, codec, DAI, routing, and board audio path are staged | volume limit, output device, capture/privacy boundary, codec/reset/regulator map, rollback plan |
| A733-BATCH-016 | PWM/backlight/fan proof | `candidate` | burn -> proving | `EXPERIMENT` | `soft-fallback` plus thermal/output stop threshold | source-backed PWM controller, channel, consumer, polarity, and safe-load model are staged | duty-cycle limit, fan/backlight/load safety, tach or measurement path, rollback plan |

## Batch Record Template

```text
### A733-BATCH-NNN

Status:
Track:
Lane:
Promotion state:
Claim IDs:
Claimed resources:
Claim heartbeat:
Board(s):
UART path(s):
Power path:
Recovery method:
Recovery check:
Recovery rung:
Recovery drill:
Experiment ceiling:
Pristine image:
Boot media:
Artifacts:
Artifact hashes:
Recipe:
Stop condition:
Rollback:
Expected proof:
Actual proof:
Logs:
Follow-up:
```

## Batch Details

### A733-BATCH-000

Status: `candidate`

Track: Board role and recovery-rung assignment.

Purpose: collect the minimum physical facts needed to choose `burn`,
`proving`, and `reference` without guessing.

Current inventory-derived snapshot, 2026-06-13:

| Board | Current role | UART mapping | Boot media | USB-OTG/FEL path | SD-Mux | Power control | Recovery rung | Recovery drill | Notes |
|---|---|---|---|---|---|---|---|---|---|
| cubie1 | `unassigned`, pending human choice | strix `192.168.50.11`, `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1.3:1.0-port0`, confirmed login prompt | `unknown` | `unknown` | not present | not present | `soft-fallback` | not drilled for burn autonomy | inventory also marks cubie1 `excluded`; resolve before assigning any A733 kernel role |
| cubie2 | `unassigned`, pending human choice | strix `192.168.50.11`, `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1.2:1.0-port0`, confirmed login prompt | `unknown` | `unknown` | not present | not present | `soft-fallback` | not drilled for burn autonomy | candidate for burn/proving/reference only after wiring and recovery facts are confirmed |
| cubie3 | `unassigned`, pending human choice | strix `192.168.50.11`, `/dev/serial/by-path/pci-0000:c3:00.4-usb-0:1.1.1:1.0-port0`, confirmed login prompt | `unknown` | `unknown` | not present | not present | `soft-fallback` | not drilled for burn autonomy | candidate for burn/proving/reference only after wiring and recovery facts are confirmed |

Current conclusion: no board is eligible for autonomous burn, proving, or
reference mutation. Role assignment still requires physical boot-media,
USB-OTG/FEL, recovery drill, and cleanest-board facts.

Inputs to collect per board:

- boot media: removable microSD, eMMC, or both
- whether the current boot path is known-good and restorable
- USB-OTG port cabled to a controller host: yes/no/unknown
- controller host and device path for OTG/FEL, if present
- FEL entry method: button, strap, boot-fail fallback, unknown, or unavailable
- `sunxi-fel` result on actual A733/SUN60IW2 board, if tested
- `xfel` result on actual A733/SUN60IW2 board, if tested
- SD-Mux/SDWire/sd-mux-ctrl path: yes/no/planned
- power-control handle: controller, outlet, and verification status
- current board cleanliness: reference-clean, previously-staged,
  heavily-experimented, or unknown
- known-good image or baseline boot entry

Decision rule:

- assign `burn` to the board with the strongest drilled recovery rung
- assign `reference` to the cleanest least-mutated board
- assign `proving` to the remaining controlled confirmation board
- if no board has a drilled recovery rung, do not enable burn autonomy

Output fields to update after collection:

- `inventory/hardware/cubie-a7s-lab.json` board `kernel_work_role`
- board `physical_wiring`
- board `recovery`
- `kernel_work_role_model.current_recovery_claim`
- this queue entry status and follow-up drill entry

### A733-BATCH-013

Status: `candidate`

Track: Display/media/GPU runtime proof.

Purpose: hold future display, DP/eDP/HDMI/MIPI DSI, CSI, media, VPU, GPU,
connector, panel, bridge, frame-capture, decode, or render proof until the
source model, board wiring, rollback path, thermal stop condition, and board
role envelope are explicit.

Current blockers:

- no A733 display/media/GPU source model is staged
- no Cubie A7S connector, panel, bridge, CSI sensor, or camera module facts are
  staged
- no board is assigned `burn`, `proving`, or `reference`
- no recovery rung is drilled for display/media/GPU experiments
- claim service is planned-not-active

Run ceiling until blockers clear: queue-only. Do not run display tests,
connector probes, frame capture, decode, render, GPU workloads, board boots,
or kernel installs from this entry.

### A733-BATCH-014

Status: `candidate`

Track: NPU / RISC-V MCU runtime proof.

Purpose: hold future NPU, RISC-V MCU, remoteproc, firmware loading,
reserved-memory, mailbox, IOMMU, OpenAMP/RPMsg, accelerator, userspace ABI,
workload, or crash/recovery proof until firmware provenance, memory map,
subsystem path, crash recovery, and board-role envelope are explicit.

Current blockers:

- no A733 NPU source model is staged
- no A733 RISC-V MCU / remoteproc source model is staged
- no firmware provenance, license, load path, memory-region layout, mailbox
  path, IOMMU path, OpenAMP/RPMsg path, or userspace ABI story is staged
- no board is assigned `burn`, `proving`, or `reference`
- no FEL/BootROM recovery rung is drilled for firmware or crash/recovery work
- claim service is planned-not-active

Run ceiling until blockers clear: queue-only. Do not load firmware, start or
stop remote processors, run OpenAMP/RPMsg tests, probe accelerators, run NPU
workloads, trigger crash/recovery tests, boot boards, or install kernels from
this entry.

### A733-BATCH-015

Status: `candidate`

Track: Audio / I2S runtime proof.

Purpose: hold future audio, I2S, codec, DMIC, SPDIF, HDMI-audio, amplifier,
jack, speaker, microphone, playback, capture, loopback, mixer, DAI-link, or
audio-routing proof until the SoC controller model, board audio path, safe
output/capture limits, and board-role envelope are explicit.

Current blockers:

- no A733 audio/I2S source model is staged
- no Cubie A7S codec, amplifier, speaker, microphone, jack, HDMI-audio, DAI
  link, or audio-routing facts are staged
- no safe playback volume, output-device, capture/privacy, or loopback wiring
  boundary is staged
- no board is assigned `burn`, `proving`, or `reference`
- no recovery rung is drilled for audio runtime experiments
- claim service is planned-not-active

Run ceiling until blockers clear: queue-only. Do not run playback, capture,
loopback, mixer, ALSA, jack-detect, HDMI-audio, speaker, microphone, board
boot, or kernel install work from this entry.

### A733-BATCH-016

Status: `candidate`

Track: PWM / backlight / fan runtime proof.

Purpose: hold future PWM, backlight, fan PWM, tach, buzzer, LED dimming, header
PWM, duty-cycle, external-load, cooling-state, brightness, or measurement proof
until the controller model, channel routing, consumer facts, safe-load limits,
thermal stop condition, and board-role envelope are explicit.

Current blockers:

- no A733 PWM controller source model is staged
- no Cubie A7S fan PWM, tach, backlight, LED dimming, buzzer, or header PWM
  consumer facts are staged
- no safe duty-cycle, polarity, load, brightness, thermal stop, or measurement
  boundary is staged
- no board is assigned `burn`, `proving`, or `reference`
- no recovery rung is drilled for PWM runtime experiments
- claim service is planned-not-active

Run ceiling until blockers clear: queue-only. Do not toggle PWM outputs, drive
fans, change duty cycles, probe tach lines, dim backlights, buzz outputs,
connect external loads, boot boards, or install kernels from this entry.
