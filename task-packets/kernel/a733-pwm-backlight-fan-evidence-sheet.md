# A733 PWM / Backlight / Fan Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet records what must be known before Radxa Cubie A7S / Allwinner A733
PWM, backlight, fan PWM, tach, buzzer, LED dimming, or header PWM work can
become maintainer-standard kernel patchwork. It is not a patch plan, not
proof, not permission to enable PWM, and not a communication draft.

## Current Boundary

- Do not enable PWM, backlight, fan PWM, tach, buzzer, LED dimming, or header
  PWM nodes from guesses.
- Do not toggle PWM outputs, drive fans, change duty cycles, probe tach lines,
  dim backlights, buzz outputs, or connect external loads.
- Do not infer PWM channel ownership, pin mux, polarity, period, voltage,
  current capacity, or external-load safety from generic A733 claims.
- Do not edit kernel trees, boot boards, change services, or send public
  communication from this sheet.
- Current inventory still has unassigned board roles, soft-fallback recovery
  only, no burn-autonomy drill, and claim service planned-not-active.

## Source Observations

Read-only source search on `/Users/enzo/projects/linux-a733` found no A733 PWM,
backlight, fan PWM, tach, buzzer, LED dimming, or header PWM nodes in
`sun60i-a733.dtsi` or the current Cubie A7S board DTS.

Generic upstream PWM, hwmon, display, and LED bindings show the usual evidence
needed for mainline PWM consumers:

- PWM controller compatible string, register range, clocks, resets, interrupts,
  and `#pwm-cells`
- pinctrl mux for each exposed PWM channel
- consumer node such as `pwm-backlight`, `gpio-fan`, panel backlight,
  LED dimmer, buzzer, or header-connected external load
- polarity, period, duty-cycle limits, cooling-state map, tach input, supply,
  enable GPIO, and safe stop behavior
- board-level proof that the channel is actually wired to the claimed consumer

Those examples are useful for shape only. They do not prove Cubie A7S PWM
population, routing, polarity, or load safety.

## Evidence Needed Before Patchwork

### PWM Controller

- Exact A733 PWM controller identity and upstream binding path.
- Register ranges, interrupts, clocks, resets, channel count, `#pwm-cells`,
  polarity support, and pin groups.
- Whether a compatible string already exists or a binding patch is required.

### Board Consumers

- Exact consumer identity: fan, tach, backlight, LED, buzzer, header PWM,
  panel, or other load.
- Pin, voltage, current, polarity, period, supply, enable GPIO, and safe duty
  cycle range for each consumer.
- For fan work: tach availability, fan-supply, speed map, thermal coupling,
  stop threshold, and safe failure behavior.
- For backlight work: panel/display dependency, brightness range, polarity,
  default brightness, and visible-output rollback path.
- For header PWM work: external device wiring, current limits, and loopback or
  measurement plan.

### Runtime Proof

- PWM proof only with a known-safe load or measurement tool.
- Fan proof only with temperature stop thresholds and rollback.
- Backlight proof only after display/panel facts are source-backed.
- Tach proof only after the input pin, polarity, and expected RPM range are
  source-backed.

## Held Communication / Queue Mapping

- Communication hook: none dedicated today. PWM questions should attach to the
  dependent subsystem communication only after a concrete source-backed
  candidate exists.
- Hardware batch queue: A733-BATCH-016 holds future PWM/backlight/fan runtime
  proof. It is a queue placeholder only and not run authority.
- If a future queue entry is refined, it must name board role, recovery rung,
  recovery drill timestamp, UART/power path, artifact path, rollback plan,
  output safety limit, thermal stop condition, and exact proof command
  boundaries.

## Safe Local Next Steps

- Search local/vendor/source references for A733 PWM controller names, clocks,
  resets, pin groups, and compatible strings.
- Search board material for fan, tach, backlight, LED, buzzer, and header PWM
  routing.
- Build a local-only PWM channel/consumer table before changing DTS.
- Refine A733-BATCH-016 only after a concrete source-backed candidate exists.

## Hard Blockers

- No A733 PWM controller source model is recorded here yet.
- No Cubie A7S fan PWM, tach, backlight, LED dimming, buzzer, or header PWM
  consumer facts are recorded here yet.
- No safe external-load, duty-cycle, polarity, thermal stop, or rollback plan
  is recorded here yet.
- No recovery rung is drilled for autonomous PWM runtime experiments.
- No claim service is active for contended board, UART, power, kernel tree, or
  proof artifact resources.
- Therefore all PWM, backlight, fan PWM, tach, buzzer, LED dimming, header PWM,
  duty-cycle, external-load, and runtime measurement work remains queued-only
  until future authority files positively permit it.
