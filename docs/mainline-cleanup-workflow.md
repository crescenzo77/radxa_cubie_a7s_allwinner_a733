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
- final human trailer policy for the exact series being sent

## Preflight Gates

Run these gates before editing a candidate branch:

- search public mailing-list archives for the SoC, board, compatible strings,
  and touched driver filenames
- record any competing or prerequisite RFCs in the cover letter
- decide whether to rebase on in-flight work, coordinate with its author, or
  explicitly justify a different approach
- when in-flight CCU or pinctrl work exists, default to a board/SoC DTS series
  stacked on those prerequisites instead of carrying competing local drivers
- before claiming a series is upstream-ready, record whether the prerequisite
  CCU and pinctrl work is accepted, current RFC-only, superseded, or blocked
- if CCU or pinctrl prerequisites are not accepted yet, do not mail a final
  Cubie A7S enablement series unless the cover letter explicitly marks the
  dependency and maintainers have a reason to review it before the dependency
  lands
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
- Do not add or keep nonstandard metadata trailers in candidate exports unless
  the human submitter explicitly approves them for the exact series.
- Each patch must be independently buildable on top of the previous patch.
  Validate bisectability by applying the series to the recorded base and
  building/checking each patch step, not only the final series.
- For the expected A733 upstream path, build a submission branch that contains
  only the SoC DTSI and Cubie A7S board DTS changes on top of the accepted or
  current CCU and pinctrl prerequisite branches. Local CCU and pinctrl driver
  patches are draft evidence only unless the relevant maintainers request that
  they be carried.

## Hardware Runtime Gate

Do not describe a board DTS series as ready for upstream until a runtime proof
record exists for the exact candidate kernel and DTB.

The runtime record must include:

- board name and lab identifier, for example `cubie2` or `cubie3`
- board IP address if networking is expected to work
- kernel commit hash and branch
- kernel configuration source and checksum when available
- kernel `Image` checksum when available
- DTB path and checksum
- boot medium and command line
- bootloader environment changes or temporary bootloader-only arguments used
  during the test
- UART capture source, timestamp, and proof-log identifier
- boot log evidence showing the kernel version, machine model, command line,
  CPU bring-up, interrupt controller, pinctrl or GPIO probe status, clock
  controller status, MMC probe status, and any runtime failures
- post-boot runtime observation, such as shell access, `uname -a`, mounted root
  filesystem, or the precise reason post-boot shell access was unavailable

If the proof log cannot be shared publicly, keep the raw capture out of this
repository and publish a concise summary that includes hashes, proof IDs, and
the observations needed to support the cover-letter claims.

## Prerequisite Rebase Gate

Before preparing the real mailing-list series:

- check public archives and maintainer branches for newer A733 CCU, PRCM,
  pinctrl, RTC, or regulator prerequisites
- record the exact prerequisite source, message ID or branch, base commit, and
  status
- rebase the SoC DTSI and Cubie A7S board DTS patches on top of those
  prerequisites
- drop local duplicate CCU and pinctrl driver or binding patches unless a
  maintainer explicitly asks for them
- regenerate the patch export from that DTS-only candidate branch
- rerun schema, DTB, build, checkpatch, maintainer, bisectability, and hardware
  runtime checks on the rebased branch
- state the dependency relationship in the cover letter without implying the
  prerequisite work is already accepted unless it is present in the chosen base

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
- for DTS board enablement, a strict hardware runtime gate for the exact
  kernel image and DTB

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
known false positive before describing the series as ready. For
`FILE_PATH_CHANGES` warnings about new files and `MAINTAINERS`, the record must
show the exact new paths, the matching `MAINTAINERS` entry or pattern, and the
patch that adds or updates that coverage. Do not treat the warning as reviewed
just because the series includes a generic maintainer note.

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
- Do not use a temporary bootloader workaround as evidence for an upstream DTS
  property unless the workaround exposes a Linux-facing hardware requirement.
- Do not replace missing evidence with confidence, model output, or a summary.
- If the claim cannot be independently understood by a reviewer, narrow the
  claim.

## Trailer Rules

- `Signed-off-by:` is added only by the human submitter.
- `Reviewed-by:`, `Acked-by:`, `Tested-by:`, and similar trailers require the
  named person's explicit authorization.
- Nonstandard trailers must be decided by the human submitter after reviewing
  current kernel documentation and the relevant subsystem's expectations.
- Do not let tooling add nonstandard trailers automatically.
- Draft/public-preparation exports may omit nonstandard trailers. Before any
  mailed submission, record the final trailer decision in the cover-letter
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
- a board DTS candidate lacks a boot/runtime proof for the exact kernel image
  and DTB
- the submission branch still contains local duplicate CCU or pinctrl driver
  patches when the intended upstream path is DTS-only on prerequisites
- accepted/current CCU and pinctrl prerequisites have not been checked and
  recorded for the day the series is prepared
- public RFCs already cover the same driver or binding and the cover letter
  does not explain the relationship
- local CCU or pinctrl patches are still present in a proposed submission when
  the intended path is to stack board support on external prerequisites
- a patch requires private lab history to make sense
- a patch contains unauthorized trailers
- a patch contains nonstandard metadata trailers that were not reviewed and
  intentionally approved by the human submitter

## Submission Preparation

Before mailing:

1. Regenerate patches from the clean candidate branch.
2. Re-run validation on the regenerated patches.
3. Run `scripts/get_maintainer.pl` for every patch.
4. Confirm each commit message explains why the change is architecturally
   correct, especially for IRQ, GMAC, and media/VPU changes.
5. Draft a cover letter with base, scope, validation, limitations, and
   dependency notes, including any in-flight RFC relationship.
6. Record the final human decision for nonstandard trailers.
7. Send only after human review with the correct DCO sign-off.
