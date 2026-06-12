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

## A733 Runtime Hypothesis Queue

Use `a733-hypothesis-queue.json` as the first stop for any Cubie A7S/A733
runtime session. It is the ordered work queue for the current SDMMC0 blocker,
including falsified tests that should not be repeated without new evidence.

Use `a733-sdmmc-register-dump-template.json` for fixed vendor-vs-mainline
register comparisons. Fill the schema before proposing another visible-register
boot variant.

End a runtime session only after these gates are closed:

- knowledge base update committed
- status doc update committed
- hypothesis queue update committed
- relevant remotes pushed or explicitly reported as missing
- Cubie3 restored to vendor kernel

The queue copy on Strix must live at
`/srv/projects/homelab/task-packets/kernel/a733-hypothesis-queue.json`.

Do not leave a session with only local notes or an uncommitted queue change.
Cold-start recovery must be: read item one in the queue, run its procedure,
record the proof, commit the docs, push the remotes, and restore Cubie3.

Public submission preparation uses the Armbian repo automation layer:
topic branches feed candidate branches, candidate branches feed generated
review branches, `scripts/kernel-validation-floor` is the validation floor, and
`b4 prep` is the mailing-list series manager. Flat patch files are snapshots,
not the final source of truth for mailout.

When a task packet graduates toward upstream submission, do not hand-edit patch
numbering, trailers, or cover-letter dependencies as the primary workflow.
Update the branch stack, regenerate the review branch, run the validation floor,
then let `b4` manage the prepared series. The PR template in the public repo is
the required stop-condition checklist before any human review or mail reflect.

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

## Workflow Controls

Use `inventory/kernel-workflow-paths.json` and `scripts/kernel-workflow-env`
before assuming host-specific paths. The current patch export location should
come from `scripts/kernel-patch-export-status`, not from thread memory.

Before Cubie runtime proof work, write an approval packet:

```sh
scripts/cubie-runtime-proof-approval-packet --board cubie2
```

Before patch prep, refresh the A733 RFC overlap packet:

```sh
scripts/a733-rfc-recheck-packet
```
