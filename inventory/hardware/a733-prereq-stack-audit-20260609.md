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
/srv/projects/a733-prereq-stack-current
/srv/projects/cubie-a7s-armbian/sources/mainline-linux
/srv/projects/kernel-work/scratch/strix-mainline-linux
/Users/enzo/projects/linux-a733
```

This keeps Codex Desktop as the dispatcher while allowing Strix and AMD to use
their local kernel trees instead of a Mac-only path.

For the public review export, Strix now has a separate clean mirror at:

```text
/srv/projects/cubie-a7s-armbian-public
```

Do not confuse that with the older dirty Strix working checkout at
`/srv/projects/cubie-a7s-armbian`.

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

Initial result:

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

## Strix Scratch Stack Attempt

Attempted on Strix from the proven base `8fde5d1d47f6` in:

```text
/srv/projects/a733-prereq-stack-v2-20260609T183944Z
```

Local public-inbox messages were converted to mbox form and applied with
`git am`.

Result:

- A733 RTC series `1/7..7/7`: applied.
- A733 CCU/PRCM RFC `1/8..8/8`: applied after two adjacent Kconfig/Makefile
  conflict resolutions to keep all three A733 clock-controller entries:
  `SUN60I_A733_RTC_CCU`, `SUN60I_A733_CCU`, and `SUN60I_A733_R_CCU`.
- A733 pinctrl RFC: patch `1/9` can be rebased mechanically, but patch `2/9`
  fails against the 7.1-rc6-era `pinctrl-sunxi.c` / `pinctrl-sunxi.h` context.
  The pinctrl apply was aborted to leave the scratch tree clean.

Follow-up:

```text
status=PASS
git_head=a1f5f546f116
git_dirty=no
```

Interpretation:

- Andre Przywara's A733 pinctrl RFC was rebased far enough for the stack audit
  to pass. Patch `2/9` was skipped because the full `pctl->flags` plumbing was
  already present in the 7.1-rc6-era base after patch `1/9` was adapted.
- A local scratch fixup removes leftover CCU Makefile conflict markers while
  keeping all three A733 clock-controller object lines.
- A focused local MMC binding commit adds `allwinner,sun60i-a733-mmc` with the
  existing `allwinner,sun20i-d1-mmc` fallback.
- The stable Strix pointer for this passing tree is:
  `/srv/projects/a733-prereq-stack-current`.

Validation:

```text
scripts/a733-prereq-stack-audit /srv/projects/a733-prereq-stack-current: PASS
git diff --check 8fde5d1d47f6..HEAD: PASS
targeted object build: PASS
  drivers/clk/sunxi-ng/ccu-sun60i-a733.o
  drivers/clk/sunxi-ng/ccu-sun60i-a733-r.o
  drivers/clk/sunxi-ng/ccu-sun60i-a733-rtc.o
  drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
```

Known remaining validation gap:

- Strix cannot run `dt_binding_check` yet because `dt-doc-validate` from the
  `dtschema` Python package is not installed in `PATH`.
- The scratch MMC patch passes checkpatch style except for the intentionally
  missing human `Signed-off-by:` trailer. Do not add that trailer until the
  human submitter authorizes the final regenerated export.
