# A733 Regulator / Power Domain Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet records what must be known before Radxa Cubie A7S / Allwinner A733
regulator, PMIC, OPP, or power-domain work can become maintainer-standard
kernel patchwork. It is not a patch plan, not proof, not permission to change
power rails, and not a communication draft.

## Current Boundary

- Do not add, rename, remove, or change regulator nodes from guesses.
- Do not enable power domains, OPP tables, voltage scaling, cpufreq coupling,
  GPU/NPU/media supplies, or peripheral supplies without source evidence.
- Do not toggle rails, change voltages, run workloads, or probe runtime power
  state.
- Do not infer PMIC identity, rail names, or consumer wiring from generic
  Allwinner patterns or unrelated board examples.
- Do not edit kernel trees, boot boards, change services, or send public
  communication from this sheet.
- Current inventory still has unassigned board roles, soft-fallback recovery
  only, no burn-autonomy drill, and claim service planned-not-active.

## Source Observations

Read-only source search on `/Users/enzo/projects/linux-a733` found only one
current Cubie A7S board-level regulator in the A733 DTS material:

- `reg_vcc3v3: vcc3v3`
- `compatible = "regulator-fixed"`
- `regulator-name = "vcc-3v3"`
- `regulator-min-microvolt = <3300000>`
- `regulator-max-microvolt = <3300000>`
- `regulator-always-on`
- `&mmc0` consumes it through `vmmc-supply = <&reg_vcc3v3>`

The current `sun60i-a733.dtsi` search did not show A733 power-domain nodes,
OPP tables, PMIC nodes, or additional board rail consumers. Generic upstream
binding examples show that regulator, PMIC, OPP, and power-domain work usually
needs explicit rail names, input supplies, voltage ranges, boot/always-on
policy, suspend state, consumer links, and sometimes coupled regulator or
required-OPP relationships. Those examples are useful for shape only and do
not prove Cubie A7S wiring.

## Evidence Needed Before Patchwork

### Board Regulators / PMIC

- Exact PMIC identity, bus, address, interrupt line, reset line, and compatible
  string, or evidence that a rail is a fixed regulator.
- Rail names from schematic, vendor source, or board documentation.
- Voltage ranges, boot-on / always-on status, suspend behavior, ramp delays,
  GPIO enables, parent input supplies, and regulator coupling if present.
- Consumer map for SDMMC, eMMC, USB, Ethernet PHY, PCIe/NVMe, Wi-Fi/Bluetooth,
  display/media/GPU, NPU, thermal/fan, and low-speed I/O.
- Explanation for each `regulator-always-on` or `regulator-boot-on` use so it
  is not just preserving bootloader state blindly.

### Power Domains / OPP

- Exact A733 power-domain controller model, register ranges, clocks, resets,
  domain IDs, and binding coverage.
- Consumer devices for each power domain and whether Linux may safely control
  the domain.
- OPP tables only after frequency, voltage, thermal, regulator, and binning
  evidence exists.
- Runtime proof plan for voltage/frequency changes, domain power on/off,
  suspend/resume, and thermal stop thresholds.

## Held Communication / Queue Mapping

- Communication hook: none dedicated today. Regulator and power-domain
  questions should attach to the dependent subsystem communication only after a
  concrete source-backed candidate exists.
- Hardware batch queue: no dedicated regulator/power-domain runtime-proof queue
  ID is currently defined. Runtime voltage, power-domain, OPP, or suspend
  proof must be queued explicitly before action, or folded into a dependent
  queue item such as A733-BATCH-004, A733-BATCH-011, or a future dedicated
  queue entry.
- Any future runtime queue entry must name board role, recovery rung, recovery
  drill timestamp, UART/power path, artifact path, rollback plan, thermal stop
  condition, exact rail/domain touched, and exact proof command boundaries.

## Safe Local Next Steps

- Search local/vendor/source references for PMIC identity, rail names, and
  power-domain controller details.
- Build a local-only rail/consumer table before changing DTS.
- Keep the existing `vcc-3v3` SDMMC0 regulator as the only locally recorded
  A733 board rail until stronger evidence exists.
- Add held maintainer questions only when they are precise, evidence-backed,
  and tied to a concrete dependent patch series.

## Hard Blockers

- No full Cubie A7S rail map is recorded here yet.
- No PMIC identity, bus/address, interrupt, or reset evidence is recorded here
  yet.
- No A733 power-domain controller model, OPP table, voltage-scaling model, or
  consumer-domain map is recorded here yet.
- No recovery rung is drilled for autonomous voltage, power-domain, OPP,
  suspend, or workload experiments.
- No claim service is active for contended board, UART, power, kernel tree, or
  proof artifact resources.
- Therefore all regulator changes beyond the current source-backed fixed
  `vcc-3v3` SDMMC0 supply, and all power-domain/OPP runtime work, remain
  queued-only until future authority files positively permit them.
