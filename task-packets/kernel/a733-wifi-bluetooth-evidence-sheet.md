# A733 Wi-Fi / Bluetooth Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet narrows Radxa Cubie A7S / Allwinner A733 Wi-Fi, Bluetooth, SDIO,
UART, firmware, and power-sequencing work to the evidence needed before
maintainer-standard kernel patchwork or runtime radio proof. It is not a patch
plan, not DTS enablement approval, not new hardware proof, not a radio test,
and not a public communication.

## Current Boundary

- Stay local-only.
- Do not enable Wi-Fi, Bluetooth, SDIO, UART, regulator, pwrseq, wake GPIO, or
  firmware-related DTS nodes from this sheet.
- Do not edit kernel trees.
- Do not boot, reboot, SSH probe, UART capture, install, recover, or
  power-cycle any board.
- Do not load firmware.
- Do not run a Wi-Fi scan.
- Do not associate to an AP or run throughput tests.
- Do not pair Bluetooth devices.
- Do not send mail, b4 submissions, list replies, GitHub comments, public
  pushes, or paid third-party calls.

## Current Status

Wi-Fi/Bluetooth is `inventory/planning only`.

Current inventory does not establish exact module identity, SDIO bus, Bluetooth
UART path, firmware files, firmware license, power rails, pwrseq reset line,
wake GPIOs, shutdown GPIO, antenna path, or runtime proof plan. Recovery is
only `soft-fallback`, not drilled for burn autonomy. The claim service is
planned-not-active, so no radio scan, AP association, throughput, pairing, or
firmware-loading proof may run.

Relevant local records:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-current-evidence-index.md`
- `task-packets/kernel/a733-peripheral-evidence-map.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`

## Read-Only Source Observations

From `/Users/enzo/projects/linux-a733`, read only:

- Existing Allwinner DTS examples model Wi-Fi as SDIO child nodes under an MMC
  controller, often with `mmc-pwrseq-simple`, `vmmc-supply`, `vqmmc-supply`,
  and Wi-Fi-specific regulators.
- Existing examples model Bluetooth as a child of a UART node with
  `uart-has-rtscts`, compatible strings, clocks, device-wakeup GPIOs,
  host-wakeup GPIOs, and shutdown GPIOs.
- Existing examples include Broadcom and Realtek module patterns, but sibling
  board examples do not prove the Cubie A7S module identity.
- The workflow identifies A733 scope as onboard Wi-Fi 6, Bluetooth 5.4,
  firmware loading, module identification, firmware licensing, mainline driver
  availability, Wi-Fi scan/association/throughput, Bluetooth pairing/audio,
  and suspend/reconnect proof.

These observations are source inventory only. They do not prove Cubie A7S
module identity, firmware availability, firmware license, SDIO wiring,
Bluetooth UART wiring, power sequencing, wake GPIO polarity, or radio runtime
behavior.

## Required Evidence Before Implementation

### Module Identity

- Exact Wi-Fi/Bluetooth module vendor and part number.
- Whether Wi-Fi and Bluetooth are a combo module or separate devices.
- Exact chip IDs, compatible strings, firmware filenames, and calibration data
  needs.
- Whether firmware is redistributable, already in `linux-firmware`, or requires
  a separate licensing path.

### Wi-Fi / SDIO

- Exact SDIO/MMC controller instance, pin group, voltage rails, bus width,
  `vmmc-supply`, `vqmmc-supply`, and pwrseq reset GPIO.
- Whether SDIO IRQ is used and which line owns it.
- Mainline driver path and binding compatibility.
- Scan-safe, association-safe, throughput-safe, and suspend/reconnect proof
  plan.

### Bluetooth / UART

- Exact UART controller, pin group, flow-control pins, baud rate, and voltage
  domain.
- Compatible string and whether a clock, regulator, enable GPIO, shutdown GPIO,
  host-wakeup GPIO, or device-wakeup GPIO is required.
- Firmware or patchram loading path.
- Pairing, audio, reconnect, and suspend/resume proof plan.

## Runtime Proof Requirements

Runtime proof is role-gated through:

- `A733-BATCH-010` for Wi-Fi/Bluetooth proof

No runtime proof class may run now. When later allowed, proof must include:

- exact source base and head
- exact Image and DTB hashes
- exact board role, UART path, power path, RF environment, and recovery rung
- module/chip detection logs
- firmware filenames, versions, and license/source notes
- Wi-Fi scan, association, IP acquisition, throughput, and reconnect evidence
- Bluetooth controller bring-up, pairing, basic data/audio path as applicable,
  and reconnect evidence
- negative markers, including no firmware-load failure, no SDIO timeout, no
  UART flow-control failure, no RF-kill surprise, and no unstable reconnect loop
- clean restore or recovery evidence after the run

## Communication Hook

`A733-COMM-010` is the held future communication hook for Wi-Fi/Bluetooth
enablement.

Do not draft or send a cover letter from this sheet. If a maintainer-dependent
question becomes precise, record it in the communications ledger as a held
question with the smallest evidence bundle needed for a one-reply answer.

## Hard Stop Conditions

Stop local Wi-Fi/Bluetooth work and log the blocker if:

- module identity is guessed
- firmware filename, license, calibration, or mainline driver path is unknown
- SDIO bus, UART path, regulator, pwrseq, wake GPIO, or shutdown GPIO facts are
  inferred from another board
- the work requires booting, probing, firmware loading, Wi-Fi scan, AP
  association, throughput, Bluetooth pairing, or board mutation
- recovery is weaker than the test's failure mode
- board role assignment, claim service, or recovery drill is missing
- the path starts to edit DTS or driver source before evidence is complete

## Safe Next Local Items

Choose one per bounded cycle:

1. Source-only module checklist: list module identity, chip ID, compatible,
   firmware, calibration, and license facts still missing.
2. Source-only Wi-Fi checklist: list SDIO bus, rails, pwrseq, IRQ, scan,
   association, throughput, and reconnect facts still missing.
3. Source-only Bluetooth checklist: list UART, flow-control, wake/shutdown
   GPIO, firmware, pairing, audio, and reconnect facts still missing.
4. Queued proof recipe skeleton: refine `A733-BATCH-010` without enabling it.
