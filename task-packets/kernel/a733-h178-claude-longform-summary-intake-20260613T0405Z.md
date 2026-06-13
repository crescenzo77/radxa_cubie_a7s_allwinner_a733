# A733 H178 Claude long-form summary intake

Captured: 2026-06-13T04:05Z

## Purpose

Record the durable value of the transcript-only long-form summary found in the
local Claude session cache, without making the cache itself canonical.

This note is documentation only. It does not approve sending mail, publishing
patches, kernel commits, hardware runs, service changes, cron changes, or
model-routing changes.

## Source

The source summary is embedded in the Claude transcript:

- `.claude/projects/-Users-enzo/d578de30-7622-4c6d-b0e6-87f61173238b.jsonl`
- transcript line containing title:
  `Radxa Cubie A7S Mainline Linux Patching - Long-Form Summary`
- observed size: about 20k characters

The transcript is supporting provenance only. The canonical project state
remains the homelab repo, Strix kernel worktrees/packages, and the current
task-packet queue.

## Durable points captured from the summary

### Submission scope

The intended upstream contribution remains narrow:

- `dt-bindings: arm: sunxi: add Radxa Cubie A7S`
- `dt-bindings: mmc: add Allwinner A733 compatible`
- `arm64: dts: allwinner: add Allwinner A733 SoC`
- `arm64: dts: allwinner: add Radxa Cubie A7S`

The public DTS export should claim only serial console and SD-card boot. Do not
expand the submission into Ethernet, VPU/Cedrus, display, Wi-Fi, Bluetooth,
USB-C, PCIe, or other unproven blocks.

Local A733 CCU and pinctrl work remains scaffolding or maintainer feedback
because third-party RTC, CCU/PRCM, and pinctrl RFCs are in flight.

### Series evolution

The summary reinforces the branch story already preserved in homelab:

- v6 carried the larger platform-clean scaffolding stack.
- v7 folded stale vendor-pinmux cleanup using git plumbing to avoid Mac
  APFS case-collision problems.
- v8 aligned DTSI/DTS with the prereq RFC shape and became the public export
  basis.
- the public 4-patch export is intentionally derived from, but narrower than,
  the local scaffolding branch.

The Mac `linux-a733` APFS case-collision warning remains important: do not
stage, stash, rebase, or mechanically "clean" those phantom netfilter changes.

### Runtime proof

The summary connects two runtime-proof tracks:

- Cubie3 proved the corrected-root v4 boot path.
- Cubie2 later reproduced the corrected-root proof using the same vendor-image
  PARTUUID shape, after UART mapping was confirmed.

Those proofs support the public DTS boot claim. They do not prove unrelated
peripherals and do not authorize new `/boot` writes or power actions.

### CCU/PRCM investigations

The summary usefully narrates two CCU-facing investigations that are now
covered by later H150-H177 records:

- `ahb-cpus` must remain enabled so later R-CCU/RTC register accesses do not
  stall after `clk_disable_unused()`.
- storage/MBUS/NSI fabric handling is the active SDMMC0 normal-IDMA thread:
  H149 mapped to the NSI update bit, and H151-H177 refined that into the
  current evidence-preserving CCU/NSI maintainer-feedback candidate.

The transcript predates or only partially covers the later H176/H177 send
candidate cleanup, so it must not be treated as the latest send authority.

## Current authority after intake

Use these current records instead of the transcript for operational decisions:

- `task-packets/kernel/a733-hypothesis-queue.json`
- `task-packets/kernel/a733-h176-ccu-rfc-feedback-send-candidate-20260613T0355Z.txt`
- `task-packets/kernel/a733-h177-h176-send-candidate-review-20260613T0357Z.md`
- `task-packets/kernel/a733-h175-send-now-vs-h154-proof-decision-20260613T0350Z.md`
- `task-packets/kernel/a733-h169-split-patch-readiness-review-20260613T0324Z.md`
- `task-packets/kernel/a733-h170-ccu-nsi-commit-message-draft-20260613T0329Z.md`
- `task-packets/kernel/a733-h171-nsi-update-bit-design-review-20260613T0335Z.md`

## Guardrails reinforced

- Do not use Cubie1 for proof or reproduction.
- Do not write `/boot`, reboot, power-cycle, or run UART proof sessions without
  explicit operator approval.
- Do not send H176 or publish patches without explicit operator approval.
- Do not route this kernel work through local model endpoints or OpenRouter.
- Do not treat transcript cache as canonical over the homelab repo.
