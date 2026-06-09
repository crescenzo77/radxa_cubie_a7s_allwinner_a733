# A733 Prerequisite Stack Audit

Date: 2026-06-09

This is a private workflow note. It documents the next maintainer-responsible
blocker before any candidate branch regeneration. It is not a patch submission
plan and does not authorize mailing patches.

## Why This Gate Exists

The public review export has the right narrow shape, but it is still tied to a
stale prerequisite API surface. The next safe kernel step is not to rewrite or
send patches. It is to choose or build the exact Linux tree that contains the
accepted or current A733 prerequisite work, then regenerate the DTS/MMC export
from that tree.

The new gate is:

```sh
scripts/a733-prereq-stack-audit /path/to/linux-tree
scripts/kernel-workflow-status --a733-prereq-stack-status
```

`KERNEL_TREE_PATH` overrides the audited tree. Without that override, the
workflow status tool chooses the first existing host-local path from:

```text
/srv/projects/cubie-a7s-armbian/sources/mainline-linux
/srv/projects/kernel-work/scratch/strix-mainline-linux
/Users/enzo/projects/linux-a733
```

This keeps Codex Desktop as the dispatcher while allowing Strix and AMD to use
their local kernel trees instead of a Mac-only path.

It checks the chosen Linux tree for:

- A733 RTC binding/header/RTC CCU driver support.
- A733 CCU/PRCM binding/headers/drivers support.
- A733 CCU four-clock API: `hosc`, `losc`, `iosc`, `losc-fanout`.
- A733 pinctrl binding and driver support.
- A733 MMC binding coverage with the `allwinner,sun20i-d1-mmc` fallback.
- If an A733 DTSI exists in the tree, the DTSI CCU node must also use the
  four-clock API.

## Current Audit Result

Mac command:

```sh
scripts/a733-prereq-stack-audit /Users/enzo/projects/linux-a733
```

Result:

```text
status=FAIL
git_head=38427a8bcfa7
git_branch=candidate/a733-platform-clean-v3
git_dirty=yes
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

Interpretation:

- The current local kernel tree is not the clean prerequisite stack to
  regenerate from.
- It has some local A733 CCU/pinctrl/MMC pieces, but it lacks the A733 RTC
  prerequisite from Junhui Liu's RTC series and the A733 R-CCU/PRCM files from
  the current CCU/PRCM RFC.
- Its A733 CCU binding and DTSI still model only three inputs instead of the
  active CCU RFC's four-input `losc-fanout` API.
- The current tree is dirty for unrelated reasons, so it must not be used as a
  maintainer-facing regeneration base.

## Maintainer-Safe Next Action

Build a separate clean worktree for A733 candidate preparation. Stack it on the
accepted or current A733 RTC, CCU/PRCM, and pinctrl prerequisite work. Then run:

```sh
KERNEL_TREE_PATH=/path/to/clean/a733-prereq-tree \
  scripts/kernel-workflow-status --a733-prereq-stack-status
```

Only after that stack audit passes should the public review export be
regenerated. If the chosen base still lacks `allwinner,sun60i-a733-mmc`, the
regenerated export may add exactly one focused MMC binding patch before the DTS
uses that compatible.

Guardrails remain unchanged: no vendor U-Boot DTS pollution, no hard-coded
memory, no local CCU/pinctrl driver submission while the RFCs are active, and no
Ethernet/VPU/display/wireless/USB-C/PCIe expansion.
