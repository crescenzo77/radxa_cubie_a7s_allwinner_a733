# Kernel Task Packets

Task packets are the Phase 0 patch-intent gate. Create one before asking any
model to edit kernel code.

Example:

```sh
scripts/kernel-task-packet a733-example \
  --title "Describe the narrow kernel change" \
  --board cubie3 \
  --subsystem "arm64 dts" \
  --target-file arch/arm64/boot/dts/allwinner/example.dts \
  --proof "git diff --check" \
  --proof "scripts/checkpatch.pl --strict"
```

The packet starts in `draft` status. It does not authorize candidate branch
promotion, trailers, or email submission.

## Current A733 Guardrail

Do not create a candidate submission task for A733 CCU/PRCM, pinctrl, or GMAC
until the task packet includes:

- coordination or rebase notes for Junhui Liu's A733 CCU/PRCM Linux RFC
- coordination or rebase notes for Andre Przywara's A733 pinctrl Linux RFC
- reviewed clock/reset identifiers for any GMAC work
- hardware evidence for pinctrl IRQ/bank behavior
- proof IDs from the validation harness

The current local model review consensus is `HOLD` for independent submission
work in these areas.

Before a draft is used for kernel patch work, attach local token-offload
context cards when the task involves large inputs:

```sh
scripts/kernel-research-query "TASK upstream overlap"
scripts/kernel-diff-brief --repo /path/to/kernel/tree
scripts/kernel-log-triage --proof-json tools/proof-logs/PROOF-ID.json
scripts/kernel-review-matrix --file task-packets/kernel/reviews/PAYLOAD.md
```

The 3090, 7900XT, and Strix lanes are advisory. Proof logs and human approval
remain authoritative.
