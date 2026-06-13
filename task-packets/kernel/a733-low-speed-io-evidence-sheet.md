# A733 Low-Speed I/O Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet narrows Radxa Cubie A7S / Allwinner A733 I2C, SPI, UART, GPIO,
pinctrl, header, and connector work to the evidence needed before
maintainer-standard kernel patchwork or runtime pin proof. It is not a patch
plan, not DTS enablement approval, not new hardware proof, not an external
device test, and not a public communication.

## Current Boundary

- Stay local-only.
- Do not enable I2C, SPI, UART, GPIO, pinctrl, interrupt, or connector nodes
  from this sheet.
- Do not edit kernel trees.
- Do not boot, reboot, SSH probe, UART capture, install, recover, or
  power-cycle any board.
- Do not attach external devices.
- Do not run an I2C scan.
- Do not run a SPI transfer.
- Do not toggle GPIOs.
- Do not run loopback tests.
- Do not send mail, b4 submissions, list replies, GitHub comments, public
  pushes, or paid third-party calls.

## Current Status

Low-speed I/O is `static inventory first`.

Current inventory does not establish full header pin ownership, all connector
signals, safe pins, mux conflicts, GPIO IRQ bank mapping, pull-up/down needs,
external-device inventory, or loopback wiring. Recovery is only
`soft-fallback`, not drilled for burn autonomy. The claim service is
planned-not-active, so no runtime I2C, SPI, UART, GPIO, interrupt, or loopback
proof may run.

Relevant local records:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-current-evidence-index.md`
- `task-packets/kernel/a733-peripheral-evidence-map.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`

## Read-Only Source Observations

From `/Users/enzo/projects/linux-a733`, read only:

- Existing Allwinner DTS examples model UART, I2C, SPI, GPIO, and pinctrl as
  separate controller nodes plus per-board pin mux selections.
- Existing examples often put reusable pin groups in SoC DTSI files and board
  enablement in board DTS files.
- Existing examples use `pinctrl-names`, `pinctrl-0`, GPIO specifiers,
  interrupt-parent references, GPIO LEDs/keys, SPI NOR devices, and UART
  aliases.
- Jernej's DTS feedback for Cubie A7S specifically said the UART0 pin group
  should move to the main A733 DTSI like other SoCs.
- These source patterns do not prove any Cubie A7S header pin, connector pin,
  safe GPIO, external device, interrupt line, or pin mux conflict.

These observations are source inventory only. They do not prove A733 pinctrl
coverage, GPIO IRQ behavior, I2C device presence, SPI device presence, UART
port availability beyond already proven console scope, or header safety.

## Required Evidence Before Implementation

### Pinctrl And GPIO

- Exact A733 pinctrl compatible, register ranges, banks, interrupts, clocks,
  resets, and GPIO IRQ bank mapping.
- Which pin groups belong in `sun60i-a733.dtsi` versus the Cubie A7S board DTS.
- Header and connector pin map with signal names, voltage domains, pull states,
  mux alternatives, and conflicts.
- Safe GPIO input/output candidates that do not affect boot, power, reset,
  storage, PMIC, RF, or recovery wiring.
- GPIO IRQ proof plan with safe pins and non-destructive stimulus.

### UART

- UART controller instances, register ranges, interrupts, clocks, resets, and
  pin groups.
- Which UARTs are console, header-accessible, Bluetooth-connected, or reserved.
- Flow-control pins, voltage levels, and conflicts for any non-console UART.
- Loopback proof path only after board role and safe wiring permit it.

### I2C

- I2C controller instances, register ranges, interrupts, clocks, resets, and
  pin groups.
- Board devices on each bus, pull-up ownership, voltage domain, and safe bus
  speed.
- Whether a bus is header-exposed, PMIC-owned, display/camera-owned, or reserved.
- I2C scan policy: no blind scan on buses that may contain unsafe devices.

### SPI

- SPI controller instances, chip-select pins, clocks, resets, DMA path, and pin
  groups.
- Whether any SPI bus is tied to boot media, SPI NOR, headers, displays, or
  reserved devices.
- Safe external-device proof plan with known-voltage device and rollback.
- SPI transfer proof only after wiring and board role permit it.

## Runtime Proof Requirements

Runtime proof is role-gated through:

- `A733-BATCH-005` for pinctrl GPIO IRQ/bank proof

No runtime proof class may run now. When later allowed, proof must include:

- exact source base and head
- exact Image and DTB hashes
- exact board role, UART path, power path, pin wiring, and recovery rung
- pinctrl probe and GPIO bank enumeration
- proof that selected pins match the header/connector map
- I2C scan only for buses explicitly marked scan-safe
- SPI transfer only with known safe wiring and external device
- UART loopback only with known safe voltage and loopback wiring
- GPIO toggle only on pins explicitly marked safe
- negative markers, including no boot-pin conflict, no storage/reset/power
  disruption, no PMIC bus disturbance, and no unexpected interrupt storm
- clean restore or recovery evidence after the run

## Communication Hook

`A733-COMM-004` and `A733-COMM-005` are the held future communication hooks for
prerequisite and Tested-by context around RTC/CCU/pinctrl work.

Do not draft or send a cover letter from this sheet. If a maintainer-dependent
question becomes precise, record it in the communications ledger as a held
question with the smallest evidence bundle needed for a one-reply answer.

## Hard Stop Conditions

Stop local low-speed I/O work and log the blocker if:

- pin ownership, voltage, pull state, mux conflict, or connector mapping is
  guessed
- a bus is assumed scan-safe without board evidence
- an SPI device, I2C device, UART path, GPIO line, or interrupt source is
  inferred instead of identified
- the work requires booting, probing, I2C scan, SPI transfer, UART loopback,
  GPIO toggle, external-device attachment, or board mutation
- recovery is weaker than the test's failure mode
- board role assignment, claim service, or recovery drill is missing
- the path starts to edit DTS or driver source before evidence is complete

## Safe Next Local Items

Choose one per bounded cycle:

1. Source-only pinctrl checklist: list compatible, banks, interrupts, clocks,
   resets, GPIO IRQ mapping, and missing A733 facts.
2. Header map checklist: list all known 15-pin and 30-pin connector signals,
   voltage domains, and conflicts still missing.
3. UART checklist: separate console UART from additional UART, flow-control,
   Bluetooth, and header-exposed UART claims.
4. I2C/SPI checklist: list buses, devices, chip selects, pull-ups, scan-safe
   policy, and external-device proof needs.
5. Queued proof recipe skeleton: refine `A733-BATCH-005` without enabling it.
