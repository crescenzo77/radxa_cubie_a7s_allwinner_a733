# A733 Audio / I2S Evidence Sheet

Status: local-only source-backed evidence sheet
Updated: 2026-06-13

This sheet records what must be known before Radxa Cubie A7S / Allwinner A733
audio, I2S, codec, DMIC, SPDIF, amplifier, jack, speaker, microphone, or HDMI
audio work can become maintainer-standard kernel patchwork. It is not a patch
plan, not proof, not permission to enable audio, and not a communication draft.

## Current Boundary

- Do not enable audio, I2S, codec, DMIC, SPDIF, HDMI-audio, amplifier, jack,
  speaker, or microphone nodes from guesses.
- Do not run playback, capture, loopback, mixer, ALSA, jack-detect, speaker, or
  microphone tests.
- Do not infer codec identity, audio routing, DAI links, jack wiring, speaker
  amplifier presence, microphone presence, or HDMI-audio support from generic
  A733 claims.
- Do not edit kernel trees, boot boards, change services, or send public
  communication from this sheet.
- Current inventory still has unassigned board roles, soft-fallback recovery
  only, no burn-autonomy drill, and claim service planned-not-active.

## Source Observations

Read-only source search on `/Users/enzo/projects/linux-a733` found no A733
audio, I2S, codec, sound-card, DMIC, SPDIF, DAI, jack, speaker, amplifier, or
microphone nodes in `sun60i-a733.dtsi` or the current Cubie A7S board DTS.

Generic upstream sound bindings show the usual ingredients for mainline audio
work:

- SoC audio controller node with compatible string, registers, clocks, resets,
  interrupts, DMA, and `#sound-dai-cells`
- codec, amplifier, DMIC, or HDMI-audio endpoint binding
- board-level sound card or audio graph describing DAI links
- audio-routing or graph endpoints for jacks, speakers, microphones, and
  external codecs
- regulator, GPIO, reset, master-clock, and pinctrl facts for every external
  audio component

Those examples are useful for shape only. They do not prove Cubie A7S audio
population, routing, or driver compatibility.

## Evidence Needed Before Patchwork

### SoC Audio Controller

- Exact A733 audio block identity: I2S, TDM, PCM, DMIC, SPDIF, HDMI-audio, or
  other controller type.
- Register ranges, interrupts, clocks, resets, DMA channels, pin groups,
  master-clock source, and binding coverage.
- Whether a compatible string already exists or a binding patch is required.

### Board-Level Audio Path

- Exact codec, amplifier, microphone, speaker, jack, or HDMI-audio endpoint
  identity.
- Bus and address for external codecs or amplifiers, including I2C/SPI path if
  present.
- Regulators, GPIO enables, reset lines, jack-detect pins, microphone bias,
  speaker supply, and pin mux.
- DAI link topology and audio-routing or audio-graph shape.

### Runtime Proof

- Playback proof with a bounded test tone or known sample only after safe
  output device and volume limits are known.
- Capture proof only after microphone path, gain, privacy, and storage-write
  boundaries are explicit.
- Loopback proof only with known-safe physical wiring.
- HDMI-audio proof only after the display/HDMI path is source-backed and gated.

## Held Communication / Queue Mapping

- Communication hook: none dedicated today. Audio questions should attach to a
  future dependent subsystem communication only after a concrete source-backed
  candidate exists.
- Hardware batch queue: A733-BATCH-015 holds future audio/I2S runtime proof. It
  is a queue placeholder only and not run authority.
- If a future queue entry is refined, it must name board role, recovery rung,
  recovery drill timestamp, UART/power path, artifact path, rollback plan,
  volume/speaker safety limit, privacy boundary for capture, and exact proof
  command boundaries.

## Safe Local Next Steps

- Search local/vendor/source references for A733 audio controller names,
  clocks, resets, DMA, pin groups, and compatible strings.
- Search board material for codec, amplifier, speaker, microphone, jack, and
  HDMI-audio population.
- Build a local-only audio block/route table before changing DTS.
- Refine A733-BATCH-015 only after a concrete source-backed candidate exists.

## Hard Blockers

- No A733 audio/I2S source model is recorded here yet.
- No Cubie A7S codec, amplifier, speaker, microphone, jack, HDMI-audio, DAI
  link, or audio-routing facts are recorded here yet.
- No recovery rung is drilled for autonomous audio runtime experiments.
- No claim service is active for contended board, UART, power, kernel tree, or
  proof artifact resources.
- Therefore all audio, I2S, codec, DMIC, SPDIF, HDMI-audio, amplifier, jack,
  speaker, microphone, playback, capture, loopback, and mixer runtime work
  remains queued-only until future authority files positively permit it.
