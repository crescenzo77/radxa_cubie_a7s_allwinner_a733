# A733 Display / Media Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet records what must be known before Radxa Cubie A7S / Allwinner A733
display, DP/eDP/HDMI/MIPI DSI, CSI, media, VPU, or GPU work can become
maintainer-standard kernel patchwork. It is not a patch plan, not proof, not
permission to enable display, and not a communication draft.

## Current Boundary

- Do not enable display, GPU, CSI, media, or VPU nodes from guesses.
- Do not run display tests, frame capture, decode tests, GPU workloads, or
  connector probing.
- Do not infer a panel, DP/eDP bridge, HDMI connector, MIPI DSI panel, CSI
  sensor, camera module, or media codec capability from generic A733 claims.
- Do not edit kernel trees, boot boards, change services, or send public
  communication from this sheet.
- Current inventory still has unassigned board roles, soft-fallback recovery
  only, no burn-autonomy drill, and claim service planned-not-active.

## Source Observations

Read-only source search on `/Users/enzo/projects/linux-a733` found no A733
display, GPU, CSI, media, VPU, HDMI, eDP, DP, MIPI DSI, TCON, DE, mixer, bridge,
panel, connector, ISP, or video-engine nodes in `sun60i-a733.dtsi` or the
current Cubie A7S board DTS.

Comparable older Allwinner SoCs show the expected subsystem split rather than
a single board-only enablement:

- display-engine / DE pipeline nodes
- mixer nodes
- TCON LCD / TCON TV nodes
- HDMI or MIPI DSI controller and PHY nodes
- connector or panel graph endpoints
- GPU node with clocks, resets, interrupts, OPPs, and regulator supply
- CSI and media graph nodes when a camera path exists
- video codec / VE nodes with SRAM, clocks, resets, and media bindings

Those older examples are useful for shape, but not evidence that A733 has the
same register layout, compatible strings, clocks, reset lines, PHYs, endpoints,
or board wiring.

## Evidence Needed Before Patchwork

### Display / DP / eDP / HDMI / MIPI DSI

- SoC source model for the A733 display pipeline: DE/mixer/TCON/PHY blocks,
  register ranges, clocks, resets, interrupts, SRAM, and compatible strings.
- Exact board connector path: DP, eDP, HDMI, MIPI DSI, bridge chip, panel, or
  no populated display output.
- Graph endpoints from pipeline to connector or panel.
- Regulator and GPIO evidence for panel power, bridge reset, hotplug, backlight,
  or connector power.
- Binding coverage or new binding requirements for any A733-specific block.
- Runtime proof plan for mode set, connector detection, panel bring-up, frame
  visibility, and rollback if a bad display experiment wedges console access.

### CSI / Media / VPU

- Exact CSI, ISP, video-engine, and media-block source model for A733.
- Sensor or connector identity, lane count, clocks, regulators, reset GPIOs,
  power-down GPIOs, and media graph topology.
- Binding coverage for each media block and sensor/connector.
- Runtime proof plan for frame capture or decode that avoids storage-write or
  thermal-risk assumptions unless the board role and recovery rung permit them.

### GPU

- Exact GPU IP identification and upstream driver path.
- Clocks, resets, interrupts, power domains, OPPs, regulators, thermal coupling,
  and firmware/userspace requirements if any.
- Runtime proof plan for basic DRM/render-node availability or a minimal GPU
  workload after display-independent enablement is source-backed.

## Held Communication / Queue Mapping

- Communication hook: A733-COMM-011 for future display/DP/media work. It is
  `draft-needed` only and not send authority.
- Hardware batch queue: A733-BATCH-013 holds future display/media/GPU runtime
  proof. It is a queue placeholder only and not run authority.
- If a future queue entry is added, it must name board role, recovery rung,
  recovery drill timestamp, UART/power path, artifact path, rollback plan,
  thermal stop condition, and exact proof command boundaries.

## Safe Local Next Steps

- Search vendor/source references for A733 display, DP/eDP/HDMI/MIPI DSI,
  CSI/media/VPU, and GPU register/block naming.
- Build a local-only block map that separates SoC-level nodes from Cubie A7S
  board-level connector, bridge, panel, sensor, and regulator facts.
- Refine A733-BATCH-013 only after a concrete source-backed display/media/GPU
  candidate exists.
- Add held maintainer questions to A733-COMM-011 only if they are precise,
  evidence-backed, and still unsent.

## Hard Blockers

- No A733 display/media/GPU source model is recorded here yet.
- No Cubie A7S display connector, panel, bridge, CSI sensor, camera module, GPU
  proof path, or media proof path is recorded here yet.
- No recovery rung is drilled for autonomous display/media experiments.
- No claim service is active for contended board, UART, power, kernel tree, or
  artifact resources.
- Therefore all display, DP/eDP/HDMI/MIPI DSI, CSI, media, VPU, frame capture,
  decode, and GPU runtime work remains queued-only until future authority files
  positively permit it.
