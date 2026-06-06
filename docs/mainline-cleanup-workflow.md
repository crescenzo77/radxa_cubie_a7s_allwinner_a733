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
- in-flight RFC or patch-series search results for every touched subsystem

## Preflight Gates

Run these gates before editing a candidate branch:

- search public mailing-list archives for the SoC, board, compatible strings,
  and touched driver filenames
- record any competing or prerequisite RFCs in the cover letter
- decide whether to rebase on in-flight work, coordinate with its author, or
  explicitly justify a different approach
- verify `get_maintainer.pl` coverage for every new path
- check whether new SoC names need MAINTAINERS `N:` patterns in addition to
  existing `F:` path coverage
- reject BSP-only compatible strings such as internal `sun60iw*` names unless
  a binding maintainer explicitly asks for them

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

When passing multiple schemas to this kernel tree's DT validation targets, use
a colon-separated `DT_SCHEMA_FILES` value, for example
`foo.yaml:bar.yaml`. A space-separated list can break the `dtbs_check`
wrapper.

A warning is not a pass. Either fix it or record why the specific warning is a
known false positive before describing the series as ready.

## Evidence Rules

- A validation record must name the exact commit or patch files checked.
- A runtime record must name the kernel image, DTB, command line, board, and
  observed behavior.
- A board DTS that enables UART, MMC, regulators, or other peripherals needs a
  matching boot/runtime record before the cover letter may claim the board was
  tested.
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
- public RFCs already cover the same driver or binding and the cover letter
  does not explain the relationship
- a patch requires private lab history to make sense
- a patch contains unauthorized trailers

## Submission Preparation

Before mailing:

1. Regenerate patches from the clean candidate branch.
2. Re-run validation on the regenerated patches.
3. Run `scripts/get_maintainer.pl` for every patch.
4. Draft a cover letter with base, scope, validation, limitations, and
   dependency notes, including any in-flight RFC relationship.
5. Send only after human review with the correct DCO sign-off.
