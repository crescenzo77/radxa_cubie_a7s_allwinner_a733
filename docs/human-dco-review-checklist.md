# Human DCO Review Checklist

This checklist is for Enzo's human review before any A733/Cubie A7S candidate
patch receives a `Signed-off-by:` trailer or is exported to `patches/`.

## Scope

Current clean public Linux branches:

```text
https://github.com/crescenzo77/linux.git
candidate/a733-pinctrl-clean
candidate/a733-ccu-clean
candidate/a733-board-binding-clean
candidate/a733-mmc-binding-clean
candidate/a733-platform-clean
```

The documentation repository's `patches/` directory is still an intentionally
empty baseline. Do not add mailbox patches there until the human review below
is complete.

## Required Human Review

Before adding a human `Signed-off-by:` trailer, verify:

- the patch was authored or reviewed sufficiently for DCO responsibility;
- no vendor BSP code was copied into the candidate;
- any vendor DT or BSP material was used only as evidence;
- AI assistance is disclosed with `Assisted-by:` and never `Signed-off-by:`;
- the commit message is technical and does not preserve lab history;
- the patch does not contain WIP, fixup, diagnostic, trace, printk, or register
  scan content;
- DTS users do not precede their bindings or clock/reset header definitions;
- Ethernet remains omitted or disabled in the current candidate layer.

## Current Known Non-Code Blockers

- Human DCO review has not been performed.
- Human `Signed-off-by:` trailers have not been added.
- Mailbox patches have not been generated into `patches/`.

## Validation Baseline

Recorded validation includes:

- per-branch `git diff --check`;
- per-patch `checkpatch.pl --no-tree --strict --show-types`;
- binding checks for pinctrl, CCU, board compatible, and MMC;
- focused DTB validation for the integrated platform branch;
- native `strix` arm64 `W=1` object build for the A733 CCU and pinctrl drivers;
- native `strix` full arm64 defconfig `Image` build for the integrated branch.
