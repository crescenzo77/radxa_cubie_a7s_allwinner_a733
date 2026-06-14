# A733 Clean Prerequisite Stack Construction Plan

Status: local-only no-run construction plan
Updated: 2026-06-13

This packet records how to get from the current Mac-mini prerequisite-stack
blocker to a clean, auditable A733 kernel preparation tree. It is not a kernel
patch, not a build log, not proof that the current tree is ready, not permission
to edit kernel trees, and not permission to send or push public kernel
material.

Short rule: this packet is not permission to edit kernel trees.

## Current Blocker

The selected Mac-mini tree is clean but incomplete:

```text
path: /Users/enzo/projects/linux-a733-sparse
branch: candidate/a733-platform-clean-v4
head: abc8d07b0a63
dirty: no
audit: FAIL
```

The full Mac-mini checkout is not the selected preparation tree while its
quarantined non-A733 dirty files remain:

```text
path: /Users/enzo/projects/linux-a733
branch: candidate/a733-platform-clean-v6
head: b1f20d455a60
dirty: yes
audit: FAIL
```

The shared prerequisite audit findings are:

```text
rtc-binding-missing
rtc-clock-header-missing
rtc-ccu-driver-missing
ccu-binding-clock-inputs-mismatch
r-ccu-clock-header-missing
r-ccu-reset-header-missing
r-ccu-driver-missing
dtsi-ccu-clock-names-missing-losc-fanout
dtsi-ccu-clock-input-count
```

No DTS export should be regenerated from either Mac-mini tree until the audit
passes in a clean preparation tree.

## Known Passing Shape

The local historical audit record identifies a passing Strix scratch stack:

```text
path: /srv/projects/a733-prereq-stack-current
base: 8fde5d1d47f6
head: a1f5f546f116
audit: PASS
dirty: no
```

That passing shape included:

- A733 RTC series `1/7..7/7`.
- A733 CCU/PRCM RFC `1/8..8/8`.
- A rebased A733 pinctrl patch `1/9`.
- Pinctrl patch `2/9` intentionally skipped because the needed
  `pctl->flags` plumbing was already present after the adapted patch `1/9`.
- A local CCU Makefile fixup preserving all three A733 clock-controller object
  lines.
- A focused local MMC binding commit adding `allwinner,sun60i-a733-mmc` with
  the existing `allwinner,sun20i-d1-mmc` fallback.

Recorded validation for that shape:

```text
scripts/a733-prereq-stack-audit /srv/projects/a733-prereq-stack-current: PASS
git diff --check 8fde5d1d47f6..HEAD: PASS
targeted object build: PASS
  drivers/clk/sunxi-ng/ccu-sun60i-a733.o
  drivers/clk/sunxi-ng/ccu-sun60i-a733-r.o
  drivers/clk/sunxi-ng/ccu-sun60i-a733-rtc.o
  drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
```

Known gap from the historical record: Strix did not have `dt-doc-validate`
from `dtschema` in `PATH`, so dt-schema validation was not complete.

## Preferred Future Path

When kernel-tree mutation is explicitly allowed and resource coordination is
available, prefer this path:

1. Claim the destination proof tree path, source proof tree path if remote,
   staged artifact path, and any required host lane.
2. Re-verify the Strix passing stack from
   `/srv/projects/a733-prereq-stack-current` without mutating it.
3. Copy or recreate that stack into an isolated preparation tree whose purpose
   is A733 candidate regeneration.
4. Run the prerequisite audit against the isolated tree.
5. Run `git diff --check` from the selected base to the new head.
6. Run targeted object builds for A733 RTC CCU, main CCU, R-CCU, and pinctrl.
7. Install or select a host with `dtschema` available before treating DT
   binding validation as complete.
8. Only after all prerequisite gates pass, regenerate candidate DTS material
   from that isolated tree.

This preferred path avoids using the dirty full Mac-mini checkout and avoids
turning the sparse checkout into an untracked staging area.

## Acceptable Alternative

If the Strix passing stack is unavailable, reconstruct the stack in a new,
isolated Mac-mini or ThinkCentre worktree only after explicit kernel-tree
mutation authority exists.

The reconstruction must start from a recorded base and must apply only the
minimum prerequisite material needed for the audit:

- current or accepted A733 RTC prerequisite
- current or accepted A733 CCU/PRCM prerequisite
- A733 pinctrl prerequisite sufficient for the audit
- focused MMC binding support if absent from the chosen base

Do not use the dirty full Mac-mini checkout as the reconstruction target.
Do not mix unrelated peripheral enablement into the prerequisite stack.

## Stop Conditions

Stop and log instead of acting if any of these are true:

- Claim service is unavailable and more than one worker may touch the same
  kernel path.
- The selected source tree is dirty for unrelated files.
- The Strix passing pointer is missing, dirty, or has a different head than
  `a1f5f546f116` without a recorded explanation.
- Required prerequisite mail/archive material cannot be identified locally.
- A prerequisite series has changed enough to require maintainer judgment.
- A build, audit, or checkpatch failure requires source changes outside the
  selected contract.
- Any next step would send mail, push public kernel material, create a public
  GitHub object, mutate hardware, or rely on an unverified recovery path.

## Proof Gates Before Promotion

A future clean prerequisite stack is not promotable until all applicable gates
are recorded with commands, tree path, branch, head, dirty state, and hashes:

```text
scripts/a733-prereq-stack-audit /path/to/clean/tree
git -C /path/to/clean/tree diff --check <base>..HEAD
make -C /path/to/clean/tree ... drivers/clk/sunxi-ng/ccu-sun60i-a733.o
make -C /path/to/clean/tree ... drivers/clk/sunxi-ng/ccu-sun60i-a733-r.o
make -C /path/to/clean/tree ... drivers/clk/sunxi-ng/ccu-sun60i-a733-rtc.o
make -C /path/to/clean/tree ... drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
make -C /path/to/clean/tree ... dt_binding_check
make -C /path/to/clean/tree ... allwinner/sun60i-a733-cubie-a7s.dtb
```

The exact `make` arguments must match the chosen host, compiler, architecture,
and output directory. Do not treat this packet's command skeleton as proof.

## Next Safe Action

Until kernel-tree mutation is explicitly authorized and coordinated, the next
safe action is limited to local planning, validation, and evidence indexing.
The engineering next action remains:

```text
choose or build a clean A733 prerequisite stack before regenerating the candidate DTS export
```
