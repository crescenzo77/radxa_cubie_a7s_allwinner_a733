# A733 Prerequisite Stack Selection Note

Status: local-only read-only selection note
Updated: 2026-06-13

This note records the current Mac-mini prerequisite-stack selection for A733
DTS preparation. It is not a patch, not a build log, not proof that the
prerequisite stack is complete, not permission to edit kernel trees, and not
permission to send or push public kernel material.

Machine-check boundary: not proof that the prerequisite stack is complete.

## Current Selection

Use the clean sparse checkout for Mac-mini read-only validation and local
documentation:

```text
/Users/enzo/projects/linux-a733-sparse
```

Do not use the full checkout as the selected Mac-mini prerequisite stack while
its quarantined non-A733 dirty files remain:

```text
/Users/enzo/projects/linux-a733
```

The path registry was aligned so Mac mini now selects the sparse checkout:

```text
inventory/kernel-workflow-paths.json
```

## Read-Only Audit Results

Observed full checkout:

```text
path: /Users/enzo/projects/linux-a733
branch: candidate/a733-platform-clean-v6
head: b1f20d455a60
status: dirty
audit: FAIL
```

Dirty files are the known quarantined non-A733 files recorded in:

```text
inventory/kernel-checkout-quarantine-20260606.md
```

Observed sparse checkout:

```text
path: /Users/enzo/projects/linux-a733-sparse
branch: candidate/a733-platform-clean-v4
head: abc8d07b0a63
status: clean
audit: FAIL
```

The sparse checkout is the right local read-only validation target, but it is
not a complete A733 prerequisite stack.

## Shared Audit Findings

Both local Mac-mini trees currently fail the prerequisite-stack audit with:

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

This means the correct next engineering state is still:

```text
choose or build a clean A733 prerequisite stack before regenerating the candidate DTS export
```

## Use Rule

- Use `/Users/enzo/projects/linux-a733-sparse` for Mac-mini read-only
  validation, status checks, source inspection, and local documentation.
- Do not stage, stash, reset, clean, commit, or push
  `/Users/enzo/projects/linux-a733` as part of A733 prep.
- Do not claim the sparse checkout is maintainer-ready until the missing
  RTC/R-CCU/losc-fanout prerequisite findings are resolved by a clean stack.
- Do not run static proof from the sparse checkout if the required build,
  checkpatch, get-maintainer, or prerequisite files are absent.
- A future static proof may still prefer Strix or an isolated copied tree when
  the claim-service and tree-permission gates are satisfied.

## Commands Behind This Note

```text
git -C /Users/enzo/projects/linux-a733 status --short --branch
git -C /Users/enzo/projects/linux-a733 rev-parse --short=12 HEAD
git -C /Users/enzo/projects/linux-a733 branch --show-current
git -C /Users/enzo/projects/linux-a733-sparse status --short --branch
git -C /Users/enzo/projects/linux-a733-sparse rev-parse --short=12 HEAD
git -C /Users/enzo/projects/linux-a733-sparse branch --show-current
scripts/a733-prereq-stack-audit /Users/enzo/projects/linux-a733 --json
scripts/a733-prereq-stack-audit /Users/enzo/projects/linux-a733-sparse --json
```
