# A733 Thermal / cpufreq / Fan Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet narrows Radxa Cubie A7S / Allwinner A733 thermal sensor, CPU
frequency, OPP, cooling, PWM, and fan work to the evidence needed before
maintainer-standard kernel patchwork or runtime thermal proof. It is not a
patch plan, not DTS enablement approval, not new hardware proof, not a
workload test, and not a public communication.

## Current Boundary

- Stay local-only.
- Do not enable thermal, cpufreq, OPP, PWM, or fan nodes from this sheet.
- Do not edit kernel trees.
- Do not boot, reboot, SSH probe, UART capture, install, recover, or
  power-cycle any board.
- Do not read live board temperatures.
- Do not run workloads.
- Do not control PWM or fan hardware.
- Do not send mail, b4 submissions, list replies, GitHub comments, public
  pushes, or paid third-party calls.

## Current Status

Thermal, cpufreq, and fan support is `inventory/planning only`.

Current inventory does not establish safe thermal limits, sensor topology,
board fan wiring, PWM/tach wiring, OPP table safety, regulator coupling, or a
runtime stop threshold. Recovery is only `soft-fallback`, not drilled for burn
autonomy. The claim service is planned-not-active, so no runtime workload,
temperature, fan, or frequency proof may run.

Relevant local records:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-current-evidence-index.md`
- `task-packets/kernel/a733-peripheral-evidence-map.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`

## Read-Only Source Observations

From `/Users/enzo/projects/linux-a733`, read only:

- Existing Allwinner DTS examples use THS thermal sensor nodes, thermal zones,
  trip points, cooling maps, and CPU cooling devices.
- Existing examples use CPU OPP tables through `operating-points-v2`, with
  voltage and hardware-support metadata where required.
- Existing examples may use PWM nodes and pinctrl groups, but a PWM node does
  not prove fan presence, fan polarity, tach support, or safe fan curves on
  Cubie A7S.
- Bindings exist for thermal sensors, OPP tables, PWM providers, cooling
  devices, and thermal zones, but A733-specific compatibility and board-level
  safety facts must be established before enablement.
- The workflow identifies A733 thermal scope as sensors, OPP, regulators, fan
  PWM/tach evidence, safe thermal limits, workload proof, board role, recovery
  drill, and stop threshold requirements.

These observations are source inventory only. They do not prove A733 thermal
calibration, cpufreq safety, OPP voltage correctness, fan wiring, tach wiring,
or cooling effectiveness.

## Required Evidence Before Implementation

### Thermal Sensors And Zones

- Exact THS controller compatible, register range, clocks, resets, interrupts,
  calibration cells, and `#thermal-sensor-cells`.
- Sensor channel mapping to CPU, GPU, NPU, PMIC, board, or other zones.
- Trip point temperatures and hysteresis backed by SoC or board evidence.
- Cooling maps that match real cooling devices.
- Negative evidence for any sensor channel that is present in source but not
  safely understood.

### cpufreq And OPP

- Exact CPU clock parent, voltage regulator, supported frequency set, and
  safe voltage table.
- Whether OPPs are shared across clusters or per-cluster.
- Whether speed bins, efuse values, or `opp-supported-hw` are required.
- Thermal cooling-device linkage for CPU frequency throttling.
- Validation that each OPP is supported by the clock, regulator, and thermal
  envelope before runtime proof.

### Fan / PWM / Tach

- Whether the Cubie A7S board has a fan installed or only a fan header.
- Exact PWM controller, channel, pinctrl group, polarity, period, and power
  rail.
- Whether tachometer input exists and which GPIO/controller owns it.
- Safe fan curve or fixed-speed policy, including fail-safe behavior.
- Physical confirmation that fan control does not conflict with another pin or
  peripheral.

## Runtime Proof Requirements

Runtime proof is role-gated through:

- `A733-BATCH-011` for thermal/cpufreq/fan proof

No runtime proof class may run now. When later allowed, proof must include:

- exact source base and head
- exact Image and DTB hashes
- exact board role, UART path, power path, and recovery rung
- idle temperature baseline and ambient context
- thermal zone and trip point enumeration
- cpufreq policy, available frequencies, current frequency, and OPP evidence
- controlled workload recipe with stop threshold
- fan/PWM/tach evidence only if fan hardware is positively identified
- negative markers, including no thermal runaway, no unexpected shutdown, no
  stuck maximum frequency, no regulator errors, and no fan-control conflict
- clean restore or recovery evidence after the run

## Hard Stop Conditions

Stop local thermal/cpufreq/fan work and log the blocker if:

- THS channel mapping is guessed
- trip points or stop thresholds are copied from another SoC without evidence
- OPP frequency, voltage, regulator, or speed-bin data is incomplete
- fan presence, PWM polarity, tach wiring, or power rail is inferred
- the work requires a workload, temperature readout, PWM control, fan test,
  boot, reboot, SSH probe, or board mutation
- recovery is weaker than the test's failure mode
- board role assignment, claim service, or recovery drill is missing
- the path starts to edit DTS or driver source before evidence is complete

## Safe Next Local Items

Choose one per bounded cycle:

1. Source-only thermal checklist: list THS compatible, calibration, channels,
   trip points, cooling maps, and missing A733 facts.
2. Source-only cpufreq checklist: list clocks, regulators, OPPs, speed bins,
   cooling-device linkage, and missing safety facts.
3. Source-only fan checklist: list PWM, fan, tach, power, polarity, and pin
   conflict facts still missing.
4. Queued proof recipe skeleton: refine `A733-BATCH-011` without enabling it.
