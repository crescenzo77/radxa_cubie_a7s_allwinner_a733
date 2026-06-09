# Kernel Token Offload

Status: implemented for live testing
Operator surface: Codex Desktop only

## Purpose

This workflow makes Codex Desktop a thin dispatcher. Large logs, diffs,
mailing-list evidence, and review payloads are processed by local machines
first. Codex should read compact context cards, proof IDs, source paths, and
model disagreements instead of raw bulk text whenever possible.

Local model output is advisory. It never replaces git, proof logs, build
results, hardware logs, or human approval.

The current local lanes are compose-managed LLM containers. For the broader map
of LLM runtimes, agents, tools, hooks, gates, and skill/MCP notes, read
`inventory/models/llm-agents-tools-quick-reference.md`.

## Dispatcher Contract

Codex Desktop is the dispatcher and coordinator for kernel work. It should use
the local LLM lanes to reduce bulk context before making decisions, but it keeps
the maintainer-facing authority chain local and explicit: current git state,
proof logs, build/schema/checkpatch output, hardware UART evidence, and human
approval.

When a kernel task reaches a human or hardware gate, Codex should record the
state, commit only the relevant workflow/documentation changes, back them up to
the configured remotes or mirrors, and then take the next maintainer-safe action
that does not pretend the gate has passed.

At a stopping point, check backup posture with:

```sh
scripts/kernel-workflow-status --workflow-backup-status
```

This distinguishes a private workflow repo that is backed up only to a local
mirror from public kernel-facing material that is backed up to GitHub and the
ThinkCentre mirror. Do not invent or add a GitHub remote without explicit human
approval.

When the maintainer path is waiting on a human/hardware gate, list only safe
coordinator actions with:

```sh
scripts/kernel-workflow-status --dispatcher-waiting-actions
```

These actions may include reading the operator brief, checking backup posture,
or running advisory idle-review sweeps. They must not replace the required
runtime proof or turn the current scaffolding export into maintainer-facing
patches.

If the idle-review ledger has zero candidates, the command reports that state
instead of recommending a no-op local-model sweep.

Before declaring the persistent kernel-maintainer goal complete, run:

```sh
scripts/kernel-workflow-status --goal-completion-audit
```

This audit is stricter than a workflow-health check. It must show the exact
runtime proof, maintainer-facing patch shape, public hygiene, backups, and
dispatcher/offload requirements as complete before Codex can treat the goal as
done.

For A733/Cubie A7S work, the dispatcher must preserve the current guardrails:
do not prepare a maintainer-facing series until the exact v4 boot/runtime proof
passes, do not submit the local CCU or pinctrl scaffolding while the external
RFCs are active, do not add vendor U-Boot workarounds to upstream DTS, and do
not expand the first slice into Ethernet, display, VPU, Wi-Fi, Bluetooth,
USB-C, or PCIe.

## Live Lanes

Primary local lanes:

- AMD RTX 3090 on `192.168.50.252`, endpoint `http://127.0.0.1:8001/v1`
  - fast diff triage
  - first-pass log compression
  - quick "what command next?" suggestions
- AMD RX 7900 XT on `192.168.50.252`, endpoint `http://127.0.0.1:8092/v1`
  - research synthesis
  - LKML/linux-sunxi overlap summaries
  - secondary maintainer-risk review
- Strix on `192.168.50.11`, endpoint `http://127.0.0.1:8080/v1`
  - long-context review
  - tertiary maintainer-style rejection review
  - hardware/UART evidence review
  - current model: Qwen3.6 27B ROCmFP4-MTP headQ6 trial,
    alias `qwen3.6-27b-rocmfp4-mtp`

Storage/search lane:

- ThinkCentre `192.168.50.225`
  - Qdrant on `127.0.0.1:6333`
  - curated source text and vector evidence

## Commands

Check all local offload lanes:

```sh
scripts/kernel-token-offload status
```

Check the structured dispatcher contract for the three model lanes plus
Qdrant:

```sh
scripts/kernel-offload-status-smoke
```

Search existing evidence before planning a patch:

```sh
scripts/kernel-research-query "A733 GMAC clock reset upstream overlap"
```

Compress a long validation/proof log:

```sh
scripts/kernel-log-triage \
  --proof-json tools/proof-logs/PROOF-ID.json
```

Brief a diff before Codex reads it:

```sh
scripts/kernel-diff-brief --repo /path/to/kernel/tree
```

Ask one local reviewer:

```sh
scripts/kernel-review-local --file task-packets/kernel/reviews/PAYLOAD.md
```

Use all review lanes together:

```sh
scripts/kernel-review-matrix --file task-packets/kernel/reviews/PAYLOAD.md
```

List pending review/research artifacts that do not yet have a matrix card:

```sh
scripts/kernel-idle-review-sweep --limit 3
```

Review the next due artifact only:

```sh
scripts/kernel-idle-review-sweep --next --run --allow-unavailable
```

Spend idle local hardware on secondary/tertiary review cards:

```sh
scripts/kernel-idle-review-sweep --limit 1 --run --allow-unavailable
```

Run a bounded continuous sweep:

```sh
scripts/kernel-idle-review-sweep \
  --loop \
  --max-runs 3 \
  --run \
  --allow-unavailable
```

All commands write Markdown and JSON cards under:

```text
task-packets/kernel/context-cards/
```

## Mandatory Offload Gates

Before Codex reads a large artifact directly, run local offload first:

- logs over about 100 lines: `kernel-log-triage`
- diffs over about 200 lines: `kernel-diff-brief`
- patch-review payloads: `kernel-review-matrix`
- mailing-list or datasheet questions: `kernel-research-query`

Codex should receive:

- context-card path
- source path or public URL
- proof ID, commit ID, or message ID
- concise model summary
- disagreements between local lanes

Codex should avoid receiving:

- full logs unless the local triage card is insufficient
- full mailing-list threads unless exact wording is needed
- full diffs before a diff brief exists
- repeated cascades of the same validation failure

## Idle Hardware Policy

When one lane is busy and another is idle:

- RTX 3090 should do fast first-pass triage.
- RX 7900 XT should do secondary research or overlap review.
- Strix should do tertiary maintainer skepticism.

When all lanes are available, use `kernel-review-matrix`. The expected output
is not one model consensus. The useful signal is disagreement:

- 3090 flags obvious build or patch-shape failures.
- 7900XT flags process, prior-art, and evidence gaps.
- Strix flags maintainer rejection risks.

If any lane is unavailable, run with:

```sh
scripts/kernel-review-matrix --allow-unavailable ...
```

The missing lane is recorded in the context card instead of silently ignored.

For background-style manual use, run:

```sh
scripts/kernel-idle-review-sweep --limit 1 --run --allow-unavailable
```

This is deliberately not a daemon. Codex Desktop or the human operator starts
it, and every output remains a review card behind the human gate.

The sweep keeps a persistent ledger at:

```text
task-packets/kernel/context-cards/idle-review-ledger.json
```

The ledger records the artifact path, content hash, review status, card path,
lane metadata, and any unavailable-lane errors. If an artifact changes, its
hash changes and it becomes reviewable again.

Inspect the ledger:

```sh
scripts/kernel-idle-ledger status
```

Backfill the ledger from existing review-matrix cards:

```sh
scripts/kernel-idle-ledger backfill
```

Show the next reviewed card that Codex has not consumed:

```sh
scripts/kernel-idle-ledger next-unconsumed
```

Mark a card or source artifact as consumed after Codex has used it:

```sh
scripts/kernel-idle-ledger mark-consumed task-packets/kernel/reviews/PAYLOAD.md
```

## Authority Boundaries

Models may say:

- "likely cause"
- "probable maintainer risk"
- "next command to run"
- "source IDs to inspect"

Models must not say:

- "validation passed" without proof ID
- "submit this"
- "add Signed-off-by"
- "promote candidate branch"
- "send mail"

The authority chain remains:

1. exact command output in proof logs
2. git diff and commit history
3. DT schema/build/checkpatch results
4. hardware UART/power evidence
5. human approval

## Long-Term Measurement

For each context card, record:

- source character count
- context-card character count
- approximate compression ratio
- model lane used
- unavailable lanes
- whether Codex had to open the raw source afterward

This lets the workflow measure how much the local machines are reducing Codex
context load over time.
