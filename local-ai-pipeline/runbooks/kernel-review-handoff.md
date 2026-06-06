# Kernel Review Handoff

Status: payload generator and Strix review handoff smoke-tested
Operator surface: Codex Desktop only

## Purpose

This layer packages a validated kernel diff for maintainer-risk review. It does
not apply patches, promote branches, add trailers, or send mail.

The reviewer prompt is fixed:

```text
Find three reasons a Linux kernel maintainer would reject this code.
```

## Location

- Wrapper: `scripts/kernel-maintainer-review`
- Tool: `tools/review/kernel_review_handoff.py`
- Output directory: `task-packets/kernel/reviews`
- Tree host: `192.168.50.252`
- Review host: `192.168.50.11`

## Commands

Create a payload only:

```sh
scripts/kernel-maintainer-review payload \
  --task-id TASK-ID \
  --proof-id PROOF-ID
```

Create a payload and ask Strix for rejection risks:

```sh
scripts/kernel-maintainer-review review \
  --task-id TASK-ID \
  --proof-id PROOF-ID
```

## Smoke-Test Result

The first handoff used:

- Proof ID:
  `synced-strix-mainline-git-diff-check-584ac4f56f72`
- Payload:
  `task-packets/kernel/reviews/synced-strix-mainline-024943eb73c30b5b.md`
- Manifest:
  `task-packets/kernel/reviews/synced-strix-mainline-024943eb73c30b5b.json`
- Payload SHA256:
  `024943eb73c30b5b4b9b13c0f46f0624934eacd27428fb1ee42b9064fd4be0b6`
- Review notes:
  `task-packets/kernel/reviews/synced-strix-mainline-024943eb73c30b5b.strix-review.txt`

The refreshed payload included two proof logs:

- `synced-strix-mainline-git-diff-check-584ac4f56f72`: `PASS`
- `synced-strix-mainline-checkpatch-current-diff-strict-4c6a137383fe`: `FAIL`

The GMAC blocker handoff used:

- Task packet:
  `task-packets/kernel/a733-gmac-clock-reset-bindings.json`
- Payload:
  `task-packets/kernel/reviews/a733-gmac-clock-reset-bindings-9b373d6a0c4b4ba6.md`
- Payload SHA256:
  `9b373d6a0c4b4ba61894ad1d79bf6893276207fa9e5fc9f27c9ff6eb0314d673`
- Proofs:
  `git diff --check` `PASS`, strict checkpatch `FAIL`, A733 CCU binding
  `PASS`, Cubie A7S DTB build `FAIL`

The repaired validation-slice handoff used:

- Payload:
  `task-packets/kernel/reviews/a733-defer-unproven-gmac-962ab817120d7d9b.md`
- Payload SHA256:
  `962ab817120d7d9b45eb007c40d2c8003e52cd70351e7e80e6aeff91ff209f1b`
- Proofs:
  `a733-defer-unproven-gmac-git-diff-check-f18025f8bc9f` `PASS`,
  `a733-mmc-compatible-binding-dt-binding-check-562c5187dab1` `PASS`,
  `a733-defer-unproven-gmac-cubie-a7s-dtbs-check-94d5f0714c56` `PASS`,
  `a733-defer-unproven-gmac-checkpatch-current-diff-strict-d61c953b97c1`
  `FAIL`

The tool printed `halted_for_human_gate=1` after the review.

## First Reviewer Risks

Strix identified these maintainer rejection risks for the current synced WIP:

- The A733 CCU driver is explicitly minimal rather than complete.
- A733-specific IRQ-clearing logic is added in the shared sunxi pinctrl core.
- The patch fails strict checkpatch.
- The Cubie A7S DTB does not build because GMAC clock/reset identifiers are
  referenced without definitions.
- After the repair, Strix still flagged the minimal CCU driver and the A733
  pinctrl workaround in shared core code as maintainer rejection risks.

These notes are review input only. They are not validation proof. The Strix
review sometimes infers broader board-support expectations, so raw proof logs
and subsystem evidence remain the authority for exact diagnostics.

## Gate

After review output is written, the pipeline stops. A human must explicitly
approve any next step that would create a candidate branch, add
`Signed-off-by`, or prepare a submission series.
