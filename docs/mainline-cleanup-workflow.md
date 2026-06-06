# Mainline Cleanup Workflow

This document describes a human workflow for turning A733/Cubie A7S bring-up
work into Linux mainline candidate patches.

It is not an instruction file for coding agents. It is a human checklist for
the maintainer of this repository. If a person uses coding assistants, scripts,
or other tools, the person still owns every decision, every technical claim,
and every trailer added to a patch.

The standing project policy remains `docs/upstream-baseline.md`. This document
is a procedure for applying that policy during cleanup work.

## Primary References

Use the current in-tree or docs.kernel.org versions of these documents while
preparing patches:

- `Documentation/process/submitting-patches.rst`
- `Documentation/process/submit-checklist.rst`
- `Documentation/process/email-clients.rst`
- `Documentation/process/coding-assistants.rst`
- `Documentation/devicetree/bindings/submitting-patches.rst`
- `Documentation/devicetree/bindings/writing-schema.rst`
- `Documentation/devicetree/bindings/ABI.rst`
- `Documentation/process/maintainer-soc.rst`
- `Documentation/process/maintainer-netdev.rst`, for networking changes
- `MAINTAINERS`

If this workflow conflicts with current subsystem maintainer instructions, use
the subsystem maintainer instructions and record the reason in the series
notes.

## Operating Principle

A candidate patch is not a patch that can be cleaned later. A candidate patch
is a patch that could be mailed as-is after final human review.

The easiest correct path is:

1. Prove the base.
2. Prove the evidence.
3. Prove the patch split.
4. Prove the branch applies.
5. Prove the build and schema results.
6. Prove the runtime claim.
7. Prove the email submission would not be mangled.

If any proof is missing, the patch is not candidate material. Do not replace a
missing proof with confidence, a summary, or a tool result that does not test
the thing being claimed.

## Required Work Products

Each submission series needs these work products before it is described as
ready:

- base record
- evidence matrix
- candidate branch
- formatted patch files
- validation logs
- runtime evidence records, if hardware behavior is claimed
- recipient matrix
- cover letter draft
- review-response log, for revisions after v1

A work product is complete only when a reviewer outside the lab could use it to
understand, reproduce, or challenge the claim. Private memory, local path
knowledge, and "this was seen earlier" do not count.

## Definitions

Use these terms strictly:

- `exploration lane`: scratch work used to answer hardware questions. It may
  contain diagnostics, experiments, failed hypotheses, and local logs.
- `mainline lane`: the clean path used to prepare upstream-facing patches.
- `candidate branch`: a topic branch in a Linux kernel tree, based on an
  official public mainline, linux-next, or subsystem maintainer branch.
- `candidate patch`: one commit from the candidate branch that is reviewable,
  bisectable, and evidence-backed.
- `submission series`: the ordered set of candidate patches, cover letter,
  base information, recipient list, validation record, and revision notes.
- `evidence`: a recorded source, log, measurement, binding, datasheet,
  commit, or runtime observation that supports a specific technical claim.
- `validation log`: output from checks run on the exact candidate branch or
  exact formatted series being evaluated.
- `clean worktree`: `git status --short` has no output in the candidate kernel
  tree and no generated files are tracked.
- `tested`: the exact patch series, kernel image, DTB, command line, and board
  identified in the runtime evidence record were exercised.
- `pass`: zero unresolved defects, zero hidden warnings, zero stale logs, and
  zero caveats affecting correctness, formatting, evidence, or reviewability.

This project repository may hold documentation and generated patch files, but
the candidate branch itself should live in a Linux kernel tree. A patch file in
this repository is not enough; it must apply cleanly to the recorded Linux
base.

## Stop Conditions

Stop candidate work immediately if any of these are true:

- the base commit is not recorded
- the base commit is not reachable from an official public tree
- the candidate kernel worktree is dirty
- a generated artifact is tracked in the candidate branch
- a patch uses a non-obvious hardware value without a strong evidence row
- a validation command failed, warned, or was skipped without being recorded as
  missing validation
- a runtime claim uses a log from a different image, DTB, board, branch,
  command line, or patch version
- a patch requires a later patch to repair a build break
- a DTS patch uses a compatible string, clock ID, reset ID, or binding that is
  not documented earlier in the same series or already present upstream
- a change crosses subsystem boundaries without an explicit dependency plan
- a patch contains a trailer the named person did not authorize
- the cover letter claims more than the evidence proves
- the patch would make sense only to someone who knows private lab history

When a stop condition is hit, return to the smallest slice that can repair the
defect. Do not continue to later steps to "see what else passes."

## Two Lanes

### Exploration Lane

Use this lane to answer hardware questions.

Allowed:

- scratch branches
- temporary debug patches
- UART captures
- boot artifacts outside the candidate branch
- one-off build experiments
- register trace instrumentation
- hypothesis tests
- notes about rejected approaches

Expected output:

- evidence rows
- logs
- exact observations
- rejected hypotheses
- one next question

Never move exploration commits directly into the candidate branch. Convert
exploration results into evidence, then write candidate code from that evidence.

### Mainline Lane

Use this lane to prepare upstream-facing patches.

Allowed:

- one subsystem concern per patch
- evidence-backed hardware descriptions
- clean commit messages
- clean build, schema, and apply logs
- reviewable dependency order
- narrow runtime claims

Not allowed:

- diagnostic printk output
- register scan loops
- temporary hacks
- broad board enablement without evidence
- mixed-subsystem patches
- unsupported compatibility claims
- hidden warnings
- `WIP`, `fixup!`, `squash!`, `try`, or failed-experiment commits
- generated boot artifacts, kernel images, DTBs, object files, modules, UART
  logs, compressed captures, or copied boot files

## Base Record

Before editing candidate patches, record the base.

The base record must include:

- Linux tree URL
- branch name
- base commit hash
- base commit subject
- whether the base is mainline, linux-next, or a subsystem maintainer tree
- the relevant `MAINTAINERS` `T:` tree, if one exists
- why this base is appropriate for the touched subsystem
- whether any dependency is expected to land through a different tree

The base must be reachable from an official public tree. A private branch,
local-only merge base, generated build directory, or unpublished integration
branch is not a valid base for a submission series.

If different parts of the work belong in different trees, split the work or
record the dependency explicitly. Do not hide tree dependencies in prose.

## Repo Sanitation

Before reconstructing candidate patches, inventory every dirty or untracked
path in both this repository and the candidate kernel tree.

Classify each path as one of:

- candidate source
- candidate documentation
- evidence
- generated artifact
- private lab artifact
- accidental byproduct
- unknown

Unknown paths are not harmless. Preserve them until they are understood, then
move evidence out of the candidate branch or discard accidental byproducts.

Generated artifacts include kernel images, DTBs, object files, modules, build
logs, UART captures, compressed captures, temporary scripts, copied boot files,
and sandbox output. They may be useful evidence, but they must not be committed
into the candidate branch.

The candidate kernel tree is sanitized only when:

- `git status --short` has no output
- `git log --oneline <base>..HEAD` shows only intended candidate commits
- no ignored build output is needed to apply, build, or understand the patches
- no local-only header, binding, generated include, or build directory is
  required

## Slice Size

Do not ask one pass of work to make the repo "mainline ready."

A slice is acceptable only when a human can answer all of these in one sitting:

- What changed?
- Why is it needed?
- Which subsystem owns it?
- Which patch introduces each dependency?
- What evidence supports every non-obvious value?
- Which command proves mechanical cleanliness?
- Which runtime log proves any hardware claim?
- What remains explicitly out of scope?

Good slices:

- one binding addition
- one clock/reset ID introduction
- one pinctrl SoC-data cleanup
- one DTS node kept disabled
- one board DTS first-boot enablement step
- one commit-message cleanup pass
- one validation failure type

Bad slices:

- "make A733 mainline ready"
- "fix all DTS warnings"
- "enable the board"
- "clean up Ethernet"
- "make the patch acceptable"

## Cleanup Order

Use this order:

1. Sanitize the repo state.
2. Record the public base.
3. Reconstruct the clean candidate branch from the intended patch series.
4. Build the evidence matrix.
5. Audit patch split and dependency order.
6. Perform semantic review before running mechanical tools.
7. Run binding validation and fix only binding issues.
8. Run DTB validation and fix only DTS/schema issues.
9. Audit C driver architecture and subsystem placement.
10. Audit CCU, reset, and pinctrl evidence.
11. Audit MMC and first-boot support.
12. Keep Ethernet disabled unless reset, clock, wrapper, MDIO, PHY, and link
    behavior are proven.
13. Minimize DTS to the supported scope.
14. Rewrite commit messages.
15. Run apply, build, schema, and static-analysis checks.
16. Bind hardware logs to the exact series.
17. Draft the cover letter.
18. Build the recipient matrix.
19. Run the email self-test.
20. Perform the final rejection review.

If a later step exposes a real defect, return to the smallest earlier slice
that can fix it. Do not skip ahead because a later stage is more interesting.

## Evidence Matrix

Every non-obvious hardware value needs an evidence row before it enters a
candidate patch.

Track at least:

- register address
- register bit
- reset ID
- clock ID
- IRQ number
- compatible string
- pin name
- pinmux value
- GPIO number
- DMA channel
- regulator name or voltage
- bus width
- PHY interface mode
- binding choice
- runtime behavior claim

Each row must include:

- claim ID
- claim being supported
- value used in the patch
- patch subject and file path
- file and line where the value appears
- source type
- exact source path, URL, datasheet page, commit, symbol, offset, or log line
- source license, for vendor or reference code
- mainline precedent, if any
- runtime proof, if runtime behavior is claimed
- conflicting evidence, if any
- confidence level
- decision

Confidence levels are strict:

- `strong`: authoritative source or mainline precedent, no unresolved conflict,
  and runtime evidence where runtime behavior is claimed
- `medium`: vendor/reference evidence or plausible inference, but missing an
  authoritative source, independent precedent, or matching runtime proof
- `weak`: plausible but not safe for candidate code
- `unknown`: not usable

Final candidate patches may use only `strong` evidence for non-obvious values.
`medium` evidence may appear only in an RFC with an explicit review question.
`weak` and `unknown` evidence must not enter candidate code.

If two sources disagree, record the conflict and stop. Do not choose the source
that makes the patch easier unless there is a technical reason that would
persuade a subsystem maintainer.

Vendor or reference code can support facts. It does not automatically justify
copying implementation code. If the evidence source is vendor code, record the
license, repository, branch, commit, and exact file path before relying on it.

## Semantic Review Before Tools

Run this review before `checkpatch.pl`, `dtbs_check`, or build testing. Tools
can show that a patch is malformed, but they cannot prove that it is a good
kernel patch.

For every patch, answer:

- Does this patch have exactly one purpose?
- Is this the subsystem that should own the change?
- Is the change modeled as hardware description, SoC data, or framework logic
  in the right place?
- Is any generic driver code carrying A733-only behavior?
- Is every magic value named, sourced, and justified?
- Is every fallback compatible actually supported by the driver?
- Is the patch bisectable at its position in the series?
- Would this patch still make sense if the reviewer never saw the lab notes?
- Would a maintainer be able to reject one patch without making the rest
  incoherent?
- Does the commit message explain why the change exists, not just what changed?

For C driver or subsystem code, also answer:

- Are error paths, probe deferral, cleanup, and resource lifetime correct?
- Are includes direct, not accidentally inherited?
- Are locking, ordering, reset sequencing, and clock enablement defensible?
- Are Kconfig dependencies and build combinations considered?
- Are new abstractions justified by more than this one board?
- Is runtime logging quiet on success paths?
- Are debug traces and discovery logic removed?

For DTS and bindings, also answer:

- Is the DTS describing hardware, not Linux driver policy?
- Are disabled nodes described without implying working support?
- Are required regulators, clocks, resets, interrupts, and pinctrl states real?
- Are compatible strings specific enough for future hardware differences?
- Does adding a property preserve the existing Devicetree ABI?

If any answer is uncertain, the patch is not ready for mechanical validation.

## Patch Admission Rules

A patch may enter the candidate branch only when all are true:

- It has one clear purpose.
- It is in the correct subsystem bucket.
- It has no diagnostic code or local lab prose.
- It uses only acceptable evidence.
- It does not claim more hardware support than was tested.
- It has a maintainer-style commit message.
- It has a human-reviewed sign-off decision.
- It has passed relevant mechanical checks.
- It has no open caveats affecting correctness, formatting, reviewability, or
  evidence.
- The kernel builds at that patch's position in the series.
- No later patch is required to fix a build break introduced by this patch.
- Validation logs come from the exact candidate branch or exact formatted
  series being evaluated.

Warnings count as defects unless a human records why they are false positives.
"False positive" means the warning is wrong for a specific technical reason,
not merely inconvenient.

Do not use shell constructs that hide failure, such as `|| true`, when
producing candidate validation logs. If a command is expected to fail during
exploration, keep that log in the exploration lane and label it as a failure.

If a check is skipped because the relevant tool is unavailable, record that as
missing validation. Do not describe the patch as checked.

## Validation Logs

Each validation log must begin with:

- date and time
- host
- Linux tree URL
- branch
- base commit
- candidate commit or patch range
- exact command
- environment variables that affect the result
- compiler and tool versions when relevant
- result: `PASS`, `FAIL`, or `MISSING`

`PASS` means no unresolved warnings, no unresolved errors, and no caveats that
affect the claim. A log with caveats is not a pass.

Required checks depend on the slice, but normally include:

- `git diff --check <base>..HEAD`
- `scripts/checkpatch.pl --strict` on the formatted patches
- `git am` of the formatted series onto a fresh branch at the recorded base
- relevant object builds
- relevant `ARCH=arm64` image or DTB build
- `dt_binding_check` for changed bindings
- `dtbs_check` for affected DTS/DTB files
- `W=1` builds for new or changed C code
- sparse or other static analysis where practical for new C code
- Kconfig `=y`, `=m`, and `=n` combinations when a configurable feature is
  introduced or changed

Use an out-of-tree build directory for builds. The build directory must not be
part of the candidate branch.

## Tool Limitations

Mechanical tools are gates, not proof of correctness.

`checkpatch.pl` can catch style and some process issues. It does not prove that
registers, clocks, resets, IRQs, pinctrl data, compatible strings, driver
architecture, patch split, or evidence are correct.

`dt_binding_check` can prove that a schema is structurally valid. It does not
prove that the binding is the right hardware contract, that the compatible
fallback is appropriate, or that the binding avoids Linux-driver-specific
design.

`dtbs_check` can prove that a DTB matches schemas. It does not prove that the
board boots, that an interrupt is wired correctly, that a reset bit works, that
a pinmux value is correct, that a regulator is real, or that a disabled node is
usable.

A successful build proves compilation only. It does not prove probe order,
runtime reset sequencing, interrupt behavior, storage reliability, PHY access,
power behavior, or ABI quality.

UART logs prove only the exact event captured in that log. They do not prove a
different patch version, DTB, kernel image, board, boot command, or hardware
configuration.

Patch application proves only that `git am` can apply the series. It does not
prove patch ordering, subsystem ownership, or reviewability.

## Devicetree Rules

Devicetree is a hardware ABI. Treat binding mistakes as long-lived mistakes.

Binding patches:

- must be separate from driver and DTS patches
- must appear before code or DTS users in the series
- must use the expected subject prefix, usually `dt-bindings: <dir>: ...`
- should use SPDX `(GPL-2.0-only OR BSD-2-Clause)` unless the subsystem has a
  better reason
- must be sent to the Devicetree list and maintainers
- must pass `dt_binding_check`
- must constrain compatible-specific differences instead of using loose schemas
- must avoid properties that merely configure Linux driver behavior
- must document any compatible string before DTS uses it

DTS patches:

- should appear at the end of a mixed series
- should be routed through the platform or SoC path, not a driver tree, unless
  maintainers explicitly direct otherwise
- must not enable untested hardware
- must not imply support for disabled nodes
- must not use local-only IDs, local-only compatibles, or unpublished bindings
- must keep board enablement narrower than or equal to the tested scope

Compatible strings:

- should be specific enough to preserve future options
- may use fallback compatibles only when the fallback behavior is actually
  supported
- must not change the meaning of an existing binding

Run `dt_binding_check` before `dtbs_check`. A broken binding can cause DTB
validation to skip the schema that should have caught the real problem.

## SoC and Board Support Rules

For A733/Cubie A7S work:

- keep SoC description separate from board enablement
- land binding/header support before DTS users
- keep DTS changes narrow and ordered after dependencies
- keep disabled hardware disabled until it is evidenced and tested
- describe only the first-boot path if that is all that was tested
- do not claim full board support from initramfs boot alone

Driver, defconfig, and Devicetree changes may need different maintainer trees.
Each branch or patch group should be useful by itself and should avoid
regressions caused by hidden dependencies on another branch.

## Clock, Reset, and Pinctrl Rules

For clock, reset, and pinctrl support:

- justify every register offset, bit, ID, and parent relationship
- avoid fake parents, placeholder IDs, and local-only names
- model SoC quirks as SoC data or reviewed framework hooks
- keep A733 structural quirks out of generic code unless they are genuinely
  generic
- avoid discovery traces, printk dumps, and register scan loops
- prove that any pinctrl IRQ-bank layout matches hardware and mainline design

Do not rely on a successful boot to prove clock, reset, or pinmux correctness.
Boot can succeed while a value is wrong, unused, masked by firmware, or hidden
behind a disabled node.

## Ethernet and Netdev Rules

No Ethernet support is claimed for this repository unless reset, clock,
wrapper, MDIO, PHY, carrier, and link behavior are all proven by exact runtime
evidence.

For netdev work:

- decide whether the target tree is `net` or `net-next`
- do not send new `net-next` content while `net-next` is closed
- use the expected subject prefix, such as `[PATCH net-next ...]`
- keep series small; avoid more than about 15 patches outstanding for one tree
- use patchwork and lore to track status
- resend the whole series for a new version, not only changed patches
- do not send emails whose only purpose is "ping" or "bump"
- if status is unclear, describe the specific uncertainty and ask for the next
  step

A733-specific Ethernet sequencing belongs in the appropriate Allwinner glue
path, not in generic STMMAC core code, unless the change is genuinely generic
and justified by existing mainline precedent.

## Commit Message Rules

Commit messages should be self-contained. Reviewers should not need to read
old versions, private notes, or external lab history to understand the patch.

Use imperative mood in the subject and describe:

- what changes
- why it is needed
- why this subsystem owns the change
- what evidence supports non-obvious hardware values
- what was tested, if runtime behavior is mentioned
- what is intentionally out of scope

Avoid:

- "likely"
- "probably"
- "validated" without scope
- "working" without an exact test
- "full support"
- "mainline ready"
- "minor issue" for anything a reviewer would ask about
- vague references to vendor behavior
- unsupported references to public RFCs, vendor trees, or hardware behavior
  without path, commit, log, or citation

Prefer exact claims:

- "boot-tested to initramfs"
- "UART0 console observed"
- "MMC0 enumerated SD card"
- "root partition mounted read-only"
- "Ethernet intentionally left disabled"
- "limited to the first-boot path"

If a statement cannot be tied to a build log, UART log, source file, binding,
datasheet, or reviewed code path, rewrite it as a question or remove it.

## Trailer Handling

Use trailers carefully.

- `Signed-off-by:` means the named human certifies the Developer Certificate of
  Origin and takes responsibility for the contribution.
- AI tools must not add `Signed-off-by:` trailers.
- `Assisted-by:` records AI assistance when it contributed to final patch
  content, review, or commit text.
- `Reviewed-by:`, `Acked-by:`, and `Tested-by:` may be carried forward only if
  the patch has not changed in a way that invalidates the review, ack, or test.
- `Fixes:` is for bug fixes and must name the fixed commit with at least 12
  characters of hash plus the commit subject.
- `Link:` should point to relevant public discussion or prior versions,
  usually via lore.kernel.org.
- `Cc: stable@vger.kernel.org` belongs in the sign-off area only for patches
  that meet stable-kernel criteria.

Do not invent trailers. Do not keep trailers from older revisions without
checking that they still apply.

## Runtime Evidence Binding

Every hardware behavior claim needs a runtime evidence record.

For each claim, record:

- board name and board identifier
- host used for the test
- Linux tree URL and commit
- submission series version or branch
- patch range
- kernel `Image` hash
- DTB hash
- initramfs hash, if used
- boot command or extlinux entry
- kernel command line
- UART log path
- exact observed result
- known failures in the same log

Do not reuse an old boot log as proof for a new patch version unless the image,
DTB, command line, board, and patch series match.

Do not write "tested" if only part of the path was observed. Name the endpoint:
for example, "booted to initramfs", "mounted root read-only", or "observed
link-up with DHCP lease".

## Cover Letter Rules

The cover letter should be honest, narrow, and useful to a maintainer deciding
whether to spend time on the series.

It should state:

- target tree and base commit
- series scope
- patch ordering and dependency plan
- what is newly added
- what was build-tested
- what was hardware-tested
- where logs or evidence are recorded
- what remains disabled
- what is intentionally not claimed
- review questions, if any
- changes since the previous version, for v2 and later

Do not hide uncertainty inside individual patches. Put unresolved design
questions in the cover letter or keep the patch out of the series.

The cover letter should not compensate for weak patches. If the cover letter
needs to apologize for a patch, the patch needs another cleanup pass.

## Patch Formatting

Generate patches from the clean candidate branch.

Use:

```sh
git format-patch --base=auto --cover-letter -o outgoing/ <base>..HEAD
```

The generated cover letter or first patch should include a `base-commit:`
trailer that points to an official public tree. If `--base=auto` cannot produce
the right base, record the base manually and explain why.

Before sending:

- apply the generated series to a fresh branch with `git am`
- confirm the fresh branch matches the candidate branch
- inspect patch subjects, numbering, and diffstats
- send a test email to yourself
- save the received email as raw text
- apply the received raw email with `git am`
- inspect the received email for mangled whitespace, wrapped lines, HTML,
  MIME attachments, missing patches, broken threading, or charset changes

Use plain-text inline email. `git send-email` is the normal tool. Do not send
HTML mail, compressed patches, MIME attachments, `format=flowed` mail, or
PGP/GPG-signed patch mail unless a maintainer explicitly asks for a resend in a
different form.

Copy-and-paste is not a patch delivery method unless the received mail has been
proved to apply cleanly.

## Maintainer Routing

Run maintainer routing per patch, not only for the whole series.

For each patch:

- run `scripts/get_maintainer.pl` on the patch or touched files
- inspect `MAINTAINERS` manually
- inspect recent git history for active reviewers
- check whether the subsystem has its own maintainer handbook
- identify the correct maintainer tree from `MAINTAINERS` `T:` entries, if any
- avoid unrelated lists and unrelated people
- preserve reviewers and commenters on Cc for later revisions

`get_maintainer.pl` is a starting point, not a substitute for judgment. If it
returns a broad or surprising list, inspect why before sending.

Do not send directly to Linus for normal subsystem work. Do not send private
mail to maintainers for public review questions that belong on-list.

## Patch Versioning and Review Etiquette

Each posting needs clear versioning.

Use subject prefixes such as:

- `[RFC PATCH v1 0/N]`
- `[PATCH v2 0/N]`
- `[PATCH net-next v3 0/N]`

Use `RFC` when the design is intentionally being reviewed before it is ready to
merge. Do not use `RFC` to disguise avoidable missing validation.

Use `RESEND` only when the patch content is unchanged and the previous posting
was missed or mangled. If the patch changed, increment the version instead.

For revisions:

- resend the entire series
- keep each commit message self-contained
- include the changelog after the `---` separator so it is not committed
- link earlier versions on lore.kernel.org when available
- answer review questions in the commit message or cover letter when future
  reviewers need that context
- use `git range-diff` against the previous version before sending
- keep reviewers and commenters on Cc

Do not top-post in review discussions. Reply inline, trim quoted text, answer
the technical point, and be specific about what will change in the next
revision.

Do not repost quickly because silence is uncomfortable. Check patchwork, lore,
and subsystem timing first. During merge windows or closed subsystem trees, a
technically good patch can still be mistimed.

## Common Failure Modes

Any of these mistakes is enough to stop candidate work:

- A patch builds but uses an unsupported clock, reset, IRQ, or pin value.
- A binding passes syntax checks but describes the wrong hardware contract.
- A DTS node validates because it is disabled, but the commit message implies
  working hardware.
- A boot log proves initramfs only, but the patch claims board support.
- A root filesystem mounted read-only, but the text says storage works.
- Ethernet creates `eth0`, but reset, MDIO, PHY, carrier, or link-up is still
  unproven.
- A debug patch becomes the basis for candidate code.
- A patch applies cleanly but has mixed concerns.
- A series depends on local-only header IDs, bindings, or unmerged patches.
- A commit message cites vendor behavior without a recorded source.
- A validation result says `PASS` while listing caveats.
- A new patch version reuses old validation logs from a different build.
- A series is reviewable only if the reader knows private lab history.
- A cover letter claims a subsystem is supported because the relevant node is
  present but disabled.
- A maintainer comment is "addressed" by changing code without answering the
  underlying design objection.

## Public Branch Check

Before publishing or sending patches, inspect the branch as an outsider would:

- `git status --short` is clean.
- No build output or boot artifact is tracked.
- No private host paths are required.
- No lab-only scripts are part of candidate history.
- Patch files apply with `git am` to the stated base.
- The base commit is recorded.
- The evidence matrix matches the exact patch series.
- Validation logs match the exact patch series.
- Runtime logs match the exact image, DTB, command line, board, and series.
- The cover letter scope matches the tested scope.
- Every patch builds at its position in the series.
- Recipient lists were checked per patch.
- Prior review comments were addressed or explicitly answered.
- The email self-test applied from the received raw message.

If the branch requires private context to look credible, it is not ready.

## Final Rejection Review

Before sending anything, try to reject the series.

Ask:

- What would a maintainer object to first?
- Is that objection answered by evidence or only by confidence?
- Which patch is least reviewable?
- Which claim is broadest?
- Which value has the weakest source?
- Which tool passed without checking the real risk?
- Which dependency would break if another maintainer took only part of the
  series?
- Would the same patch look clean if the lab history were invisible?
- Is the claimed support narrower than the tested support, equal to it, or
  broader than it?

Only two answers are acceptable for the final question: narrower than tested,
or exactly equal to tested. Broader than tested is not candidate material.

If the series survives this review, it is ready for final human sign-off review.
If it does not, return to the smallest slice that failed.
