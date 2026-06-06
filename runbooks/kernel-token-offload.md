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
- Strix on `192.168.50.11`, endpoint `http://127.0.0.1:8082/v1`
  - long-context review
  - tertiary maintainer-style rejection review
  - hardware/UART evidence review

Storage/search lane:

- ThinkCentre `192.168.50.225`
  - Qdrant on `127.0.0.1:6333`
  - curated source text and vector evidence

## Commands

Check all local offload lanes:

```sh
scripts/kernel-token-offload status
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
