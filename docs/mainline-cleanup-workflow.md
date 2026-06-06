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
- final human disclosure and trailer policy for the exact series being sent

## Preflight Gates

Run these gates before editing a candidate branch:

- search public mailing-list archives for the SoC, board, compatible strings,
  and touched driver filenames
- record any competing or prerequisite RFCs in the cover letter
- decide whether to rebase on in-flight work, coordinate with its author, or
  explicitly justify a different approach
- when in-flight CCU or pinctrl work exists, default to a board/SoC DTS series
  stacked on those prerequisites instead of carrying competing local drivers
- verify `get_maintainer.pl` coverage for every new path
- check whether new SoC names need MAINTAINERS `N:` patterns in addition to
  existing `F:` path coverage
- require a MAINTAINERS patch when a new SoC naming family is not matched by
  existing `N:` patterns
- reject binding maintainer blocks that list a third party without explicit
  consent
- reject BSP-only compatible strings such as internal `sun60iw*` names unless
  a binding maintainer explicitly asks for them
- compare GICv3 distributor and redistributor regions against the CPU count
  and the binding before exporting DTSI patches
- reject GIC nodes that carry unused child-bus properties such as
  `#address-cells`, `#size-cells`, or `ranges` when there are no child nodes
- require `capacity-dmips-mhz` for asymmetric CPU topologies unless the cover
  letter documents why scheduler capacity data is deferred
- reject deprecated kernel headers in new driver files when narrower headers
  provide the required declarations
- classify IRQ, Ethernet, and VPU work before drafting patches; each has
  subsystem-specific rules below and must not be hidden inside board DTS work

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
- Do not add or keep automatic coding-assistance trailers in candidate
  exports; make disclosure a final human review decision.
- Each patch must be independently buildable on top of the previous patch.
  Validate bisectability by applying the series to the recorded base and
  building/checking each patch step, not only the final series.

## IRQ Rules

IRQ handling must stay inside normal Linux IRQ and pinctrl infrastructure.

Do not submit:

- deferred parent IRQ registration used to avoid boot stalls
- code that bypasses the normal irq_domain hierarchy
- board-specific IRQ masking or clearing outside the SoC pinctrl/irqchip path
- register-status workarounds without a documented hardware reason

If A733 has latched status or bank-specific IRQ behavior, model it as a clean
SoC quirk in the standard initialization, mask, unmask, ack, or set-type paths.
The commit message must explain why the quirk is needed and how it preserves
the standard irqchip hierarchy.

## Ethernet Rules

Do not upstream A733 Ethernet by relying only on generic Synopsys DWMAC
fallbacks or legacy bindings.

Before any Ethernet enablement patch is a candidate, record:

- the A733/GMAC210 wrapper programming model
- the syscon or clock routing needed by GMAC0
- reset sequencing for the MAC and external PHY
- PHY power/reset GPIO behavior
- MDIO evidence from the real external PHY
- link-up evidence from the exact kernel and DTB

A proper upstream series should split binding, clock/reset, glue driver, SoC
DTS, and board DTS work as separate patches. A733-specific sequencing belongs
in Allwinner DWMAC glue, not in generic STMMAC core code.

## VPU Rules

VPU/Cedrus work must be atomic across subsystems:

- DT binding updates in their own patch
- clock/reset support in clock patches
- media/Cedrus driver support in media patches
- DTS nodes after bindings and driver dependencies
- board enablement only after runtime evidence

Do not combine DT binding, clock, media driver, and DTS changes into one
monolithic commit. Coordinate with incoming community Cedrus work before
carrying local A733 VPU patches.

## Validation Floor

Run the relevant checks on the exact branch or exported patch files:

- `git diff --check`
- `git am --check` against the recorded base
- `scripts/checkpatch.pl --strict`
- `make dt_binding_check DT_SCHEMA_FILES=<touched schemas>`
- `make ARCH=arm64 dtbs_check DT_SCHEMA_FILES=<touched schemas>`
- relevant object builds with `W=1`
- boot/runtime tests on named hardware when the patch claims runtime behavior
- per-patch bisectability checks for mixed series

Run `scripts/checkpatch.pl` from the Linux tree root and pass the exported
patch files as patch inputs, for example
`scripts/checkpatch.pl --strict --no-tree /path/to/export/patches/000[1-9]-*.patch`.
Do not substitute a generic text-file whitespace scan for `checkpatch`'s patch
parser; exported patch context lines are not source trailing whitespace.

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
- A bisectability record must show that each patch applies and builds or
  validates at the level appropriate for its subsystem.
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
- Coding-assistance disclosure must be decided by the human submitter after
  reviewing the current Linux coding-assistant documentation and the relevant
  subsystem's expectations.
- Do not let tooling add disclosure trailers automatically.
- Draft/public-preparation exports may omit coding-assistance trailers to
  avoid turning technical review prep into a policy discussion. Before any
  mailed submission, record the final disclosure decision in the cover-letter
  preparation notes.

## Stop Conditions

Stop and repair the smallest responsible slice if:

- the base commit is unclear
- the candidate branch is dirty
- a patch does not apply to the recorded base
- checkpatch, schema, dtbs, or build checks fail
- a DTS node uses an undocumented compatible, clock ID, reset ID, or property
- an asymmetric CPU topology lacks scheduler capacity data without a recorded
  reason
- a GICv3 region size is irregular for the CPU topology and lacks evidence
- a patch mixes unrelated subsystems
- a new binding volunteers another maintainer without explicit consent
- a new SoC naming family lacks explicit MAINTAINERS coverage
- an IRQ workaround bypasses irq_domain or standard irqchip/pinctrl operations
- Ethernet uses only generic DWMAC fallback behavior where SoC glue is needed
- VPU work mixes binding, clocks, media driver, and DTS in one patch
- a runtime claim lacks matching runtime evidence
- public RFCs already cover the same driver or binding and the cover letter
  does not explain the relationship
- local CCU or pinctrl patches are still present in a proposed submission when
  the intended path is to stack board support on external prerequisites
- a patch requires private lab history to make sense
- a patch contains unauthorized trailers
- a patch contains automatic coding-assistance trailers that were not reviewed
  and intentionally approved by the human submitter

## Submission Preparation

Before mailing:

1. Regenerate patches from the clean candidate branch.
2. Re-run validation on the regenerated patches.
3. Run `scripts/get_maintainer.pl` for every patch.
4. Confirm each commit message explains why the change is architecturally
   correct, especially for IRQ, GMAC, and media/VPU changes.
5. Draft a cover letter with base, scope, validation, limitations, and
   dependency notes, including any in-flight RFC relationship.
6. Record the final human decision for coding-assistance disclosure/trailers.
7. Send only after human review with the correct DCO sign-off.
