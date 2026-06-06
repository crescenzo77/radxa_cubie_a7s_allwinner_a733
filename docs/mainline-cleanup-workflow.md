# Mainline Cleanup Workflow

This is the human checklist for turning A733/Cubie A7S work into Linux kernel
candidate patches.

It is not an autonomous agent workflow. Tools may assist, but the human
submitter owns every technical claim, every patch split, every trailer, and
every email sent upstream.

## Required Inputs

Before calling a patch a candidate, record:

- Linux tree URL
- branch name
- base commit hash and subject
- candidate commit range
- touched subsystems
- relevant `MAINTAINERS` output
- validation commands and results
- runtime evidence for every runtime claim
- known limitations and deferred hardware blocks

## Candidate Branch Rules

- Start from an official public Linux tree, linux-next, or a subsystem
  maintainer branch.
- Keep the kernel worktree clean before exporting patches.
- Do not commit generated files.
- Keep diagnostic work on separate scratch branches.
- Squash out `WIP`, `fixup!`, failed experiments, print tracing, and local
  trial commits.
- Split by subsystem and dependency order.
- Put DT binding patches before driver or DTS users.
- Put DTS patches at the end of a mixed series.
- Do not enable a board peripheral until the binding, clocks, resets, pinctrl,
  power, and runtime behavior are proven.

## Validation Floor

Run the relevant checks on the exact branch or exported patch files:

- `git diff --check`
- `git am --check` against the recorded base
- `scripts/checkpatch.pl --strict`
- `make dt_binding_check DT_SCHEMA_FILES=<touched schemas>`
- `make ARCH=arm64 dtbs_check DT_SCHEMA_FILES=<touched schemas>`
- relevant object builds with `W=1`
- boot/runtime tests on named hardware when the patch claims runtime behavior

A warning is not a pass. Either fix it or record why the specific warning is a
known false positive before describing the series as ready.

## Evidence Rules

- A validation record must name the exact commit or patch files checked.
- A runtime record must name the kernel image, DTB, command line, board, and
  observed behavior.
- Do not use a log from one branch or DTB to support a different branch or DTB.
- Do not replace missing evidence with confidence, model output, or a summary.
- If the claim cannot be independently understood by a reviewer, narrow the
  claim.

## Trailer Rules

- `Signed-off-by:` is added only by the human submitter.
- `Reviewed-by:`, `Acked-by:`, `Tested-by:`, and similar trailers require the
  named person's explicit authorization.
- `Assisted-by:` records coding-assistant involvement when it contributed to
  final patch content, review, or wording.
- The documented form is `Assisted-by: AGENT_NAME:MODEL_VERSION [TOOLS]`.
- Do not let tooling add trailers automatically.

## Stop Conditions

Stop and repair the smallest responsible slice if:

- the base commit is unclear
- the candidate branch is dirty
- a patch does not apply to the recorded base
- checkpatch, schema, dtbs, or build checks fail
- a DTS node uses an undocumented compatible, clock ID, reset ID, or property
- a patch mixes unrelated subsystems
- a runtime claim lacks matching runtime evidence
- a patch requires private lab history to make sense
- a patch contains unauthorized trailers

## Submission Preparation

Before mailing:

1. Regenerate patches from the clean candidate branch.
2. Re-run validation on the regenerated patches.
3. Run `scripts/get_maintainer.pl` for every patch.
4. Draft a cover letter with base, scope, validation, limitations, and
   dependency notes.
5. Send only after human review with the correct DCO sign-off.
