# A733 Peripheral Evidence Map

Status: local-only evidence map
Updated: 2026-06-13

This map classifies Radxa Cubie A7S / Allwinner A733 peripheral work by the
evidence needed before it can become maintainer-standard kernel patchwork. It
is not a patch plan, not new proof, not hardware approval, not a communication
draft, and not permission to enable peripherals speculatively.

Read first:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-current-evidence-index.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`

## Current Boundary

- Local-only work is allowed.
- Public communication is closed.
- Hardware mutation is not allowed.
- Board roles are unassigned.
- Recovery is not drilled for burn autonomy.
- Claim service is planned-not-active.

Therefore, this cycle may only prepare source-backed inventory, validation
plans, negative-evidence notes, and queue entries. It may not boot boards,
probe hardware, install kernels, edit kernel trees, send patches, or claim
runtime proof.

## Track Map

| Track | Current class | Local-only allowed now | Blocks before implementation/proof |
|---|---|---|---|
| SDMMC0 / rootfs stability | proven narrow CCU workaround plus open root-cause area | Preserve H200/H201/H247/H253 evidence; write static hypothesis notes | role assignment, recovery drill, claim service, source-backed IDMAC/root-cause plan |
| eMMC | inventory/planning only | Identify non-destructive read-only proof needs | boot media facts, recovery stronger than soft-fallback for writes, board role |
| Ethernet / GMAC | inventory/planning only | Collect source-backed wrapper/clock/reset/MDIO/PHY questions | GMAC wrapper model, clocks/resets, PHY reset/power, link proof lane |
| PCIe / NVMe | inventory/planning only | List controller/PHY/power/adapter evidence needed | controller and PHY binding shape, power budget, NVMe proof lane, recovery for writes |
| USB / USB-C / OTG | inventory/planning only | Separate host/device/role-switch/FEL evidence needs | controller/PHY/role-switch model, OTG wiring facts, safe host/device proof |
| Wi-Fi / Bluetooth | inventory/planning only | Identify exact module, bus, firmware, and power sequencing questions | module identity, mainline driver path, firmware legality, runtime association/pairing proof |
| Display / DP / GPU | inventory/planning only | Record subsystem split and dependency questions | display pipeline source model, bindings, panel/DP proof, subsystem maintainer path |
| CSI / media / VPU | inventory/planning only | Record sensor/media-block/source dependency questions | media graph, sensor identity, bindings, frame capture or decode proof |
| NPU | bucket C | Record why not yet and possible subsystem paths | credible upstream subsystem, firmware/userspace ABI, binding story |
| RISC-V MCU / remoteproc | bucket C | Record firmware/remoteproc/open-amp questions | firmware ownership, memory map, mailbox/interrupts, upstream remoteproc path |
| Thermal / cpufreq / fan | inventory/planning only | List sensors, OPP, regulator, PWM/tach evidence needs | safe thermal limits, workload proof, board role, recovery drill |
| I2C / SPI / UART / GPIO | static inventory first | Map pins, muxes, conflicts, and external-device proof needs | safe wiring, loopback/device proof, pinctrl prerequisite state |
| Audio / I2S | static inventory first | Map controller, codec, DAI, routing, jack, speaker, microphone, and HDMI-audio facts | source-backed audio path, safe playback/capture proof, board role |
| PWM / backlight / fan | static inventory first | Map controller, channels, consumers, polarity, duty-cycle limits, fan/tach, and backlight facts | safe load, thermal stop threshold, visible-output or measurement proof, board role |
| Regulators / power domains | static inventory first | Map rail names, consumers, always-on assumptions, and source evidence | board schematic/source evidence, runtime voltage/consumer proof if needed |

## Safe Local Work Items

- Create a source-backed checklist of registers, clocks, resets, pins,
  regulators, and bindings for one track at a time.
- Record negative evidence, such as "driver path not identified" or "binding
  shape unknown."
- Link each track to the relevant batch queue ID before runtime proof.
- Prepare validation commands that can be run later once a source change
  exists.
- Add held maintainer questions to the communications ledger only when the
  question is precise and evidence-backed.

## Required Runtime Proof Classes

| Track | Batch queue |
|---|---|
| SDMMC0/rootfs stability | A733-BATCH-003 |
| RTC/CCU/R-CCU/reset | A733-BATCH-004 |
| Pinctrl/GPIO IRQ/bank | A733-BATCH-005 |
| eMMC | A733-BATCH-006 |
| Ethernet | A733-BATCH-007 |
| PCIe/NVMe | A733-BATCH-008 |
| USB/USB-C | A733-BATCH-009 |
| Wi-Fi/Bluetooth | A733-BATCH-010 |
| Thermal/cpufreq/fan | A733-BATCH-011 |
| FEL/BootROM recovery | A733-BATCH-012 |
| Display/media/GPU | A733-BATCH-013 |
| NPU/RISC-V MCU | A733-BATCH-014 |
| Audio/I2S | A733-BATCH-015 |
| PWM/backlight/fan | A733-BATCH-016 |

No runtime proof class may run until the queue, inventory, recovery rung, role
assignment, and claim-service state positively allow it.

## Communication Ledger Hooks

| Track | Ledger hook |
|---|---|
| SDMMC0 root-cause or diagnostic series | A733-COMM-006 |
| Ethernet / GMAC | A733-COMM-007 |
| PCIe / NVMe | A733-COMM-008 |
| USB / USB-C | A733-COMM-009 |
| Wi-Fi / Bluetooth | A733-COMM-010 |
| Display / DP / media | A733-COMM-011 |
| NPU / RISC-V MCU | A733-COMM-012 |

These are held future communication hooks only. They are not send authority.

## Anti-Overclaim Rules

- Do not enable a DTS node because the vendor tree has one.
- Do not claim a peripheral works from boot logs that only show unrelated
  clocks, SD card enumeration, or rootfs mount.
- Do not treat Cubie3 proof as board-family proof unless a reference/proving
  policy explicitly says so.
- Do not infer eMMC, Wi-Fi, Bluetooth, PCIe, USB-C, display, or NPU population
  without physical/source evidence.
- Do not conflate "safe to inspect source" with "safe to boot hardware."

## Next Local Inventory Candidates

Choose one track per bounded cycle:

1. Ethernet source-backed evidence sheet: GMAC wrapper, clocks, resets, MDIO,
   PHY reset, PHY power, and link-proof needs.
2. USB/OTG/FEL evidence sheet: controller/PHY/role-switch split plus physical
   OTG/FEL wiring facts still needed.
3. eMMC/SDMMC evidence sheet: non-destructive read-only proof plan versus
   storage-write proof requiring stronger recovery.
4. Thermal/cpufreq/fan evidence sheet: sensor, OPP, regulator, fan PWM/tach,
   and stop-threshold requirements.
5. Low-speed I/O evidence sheet: I2C/SPI/UART/GPIO pin ownership, conflicts,
   and loopback/external-device proof requirements.
6. Display/media/GPU queue refinement only after a source-backed block map
   and board connector/sensor facts exist.
7. NPU/RISC-V MCU queue refinement only after firmware provenance, memory map,
   upstream subsystem path, and crash/recovery boundaries exist.
8. Audio/I2S queue refinement only after controller, codec, DAI, routing,
   speaker/microphone/jack, and safe playback/capture facts exist.
9. PWM/backlight/fan queue refinement only after controller, channel,
   consumer, polarity, duty-cycle, load-safety, and thermal-stop facts exist.
