# A733 Gated Transition Approval Packet

Status: local-only approval packet
Updated: 2026-06-14

This packet records high-value gates that cannot be crossed under the current
local-work-only mode without explicit human approval. It is
not approval to act, not a public communication, not a kernel patch plan, not a
build log, and not permission to mutate kernel trees, hardware, remotes, or
services.

## Current State

Private homelab coordination repo:

```text
private_origin_backed=yes
private_github_backed=yes
```

Public-facing Cubie A7S repo:

```text
path: /Users/enzo/projects/Home Lab/cubie-a7s-armbian
local branch: main
public hygiene: PASS, match_count=0
private ThinkCentre mirror: backed
public GitHub remote: not backed
local/public divergence: ahead of public/main and behind public/main
```

Selected Mac-mini A733 prerequisite tree:

```text
path: /Users/enzo/projects/a733-prereq-stack-clean/linux
branch: local/a733-prereq-stack-clean-20260614
head: 5ea091fd44b3
dirty: no
audit: PASS
```

Build artifact staging:

```text
/srv/projects/kernel-work/outgoing/a733-clean-feature-20260614
```

## Gate 1: Public GitHub Backup

Current blocker:

```text
public kernel repo is not backed up to its public remote
```

This is a public-push gate because the destination is:

```text
https://github.com/crescenzo77/radxa_cubie_a7s_allwinner_a733.git
```

Approval question:

```text
May Codex push /Users/enzo/projects/Home Lab/cubie-a7s-armbian branch main to
the public GitHub remote named public, despite the active local-work-only
public-push restriction?
```

Required before approval can be used:

- Public hygiene gate still passes with zero matches.
- Public repo is clean.
- Human accepts that the local branch is ahead of and behind public/main, and
  either approves the exact push strategy or asks for a reconciliation plan
  first.
- No public issue, pull request, comment, gist, or mailing-list communication
  is bundled into the action.

Allowed command shape only after explicit approval:

```text
git -C "/Users/enzo/projects/Home Lab/cubie-a7s-armbian" status --short --branch
git -C "/Users/enzo/projects/Home Lab/cubie-a7s-armbian" log --oneline --left-right --graph public/main...main
git -C "/Users/enzo/projects/Home Lab/cubie-a7s-armbian" push public main
```

Stop conditions:

- Public hygiene fails.
- The push is non-fast-forward and no explicit reconciliation strategy exists.
- The remote URL differs from the expected public GitHub URL.
- Any step would create a GitHub issue, pull request, comment, release, tag, or
  other public object beyond the branch push.

Proof after action:

```text
scripts/kernel-workflow-status --workflow-backup-status
git -C "/Users/enzo/projects/Home Lab/cubie-a7s-armbian" ls-remote public refs/heads/main
```

## Gate 2: Clean A733 Prerequisite Stack

Status:

```text
completed locally; no hardware install or DTS regeneration performed
```

This gate was reopened by operator approval and completed locally. The selected
tree now passes the prerequisite-stack audit. This completion does not approve
DTS regeneration, kernel installation, board boot tests, public pushes, or
maintainer communication.

Historical approval question, now consumed:

```text
May Codex create or update an isolated A733 prerequisite preparation tree,
using the local no-run construction plan, for the sole purpose of producing a
clean prerequisite-stack audit before any DTS regeneration?
```

Required before approval can be used:

- Choose the destination tree path explicitly.
- Confirm no other live worker is using that path.
- Confirm whether Strix's historical passing tree
  `/srv/projects/a733-prereq-stack-current` is reachable and should be used as
  source evidence.
- Keep `/Users/enzo/projects/linux-a733` quarantined and avoid using it as the
  construction target.
- Do not regenerate DTS exports until the prerequisite audit passes.

Preferred command envelope only after explicit approval:

```text
scripts/a733-prereq-stack-audit /path/to/isolated/tree
git -C /path/to/isolated/tree status --short --branch
git -C /path/to/isolated/tree diff --check <base>..HEAD
```

Additional proof gates before promotion:

```text
make -C /path/to/isolated/tree ... drivers/clk/sunxi-ng/ccu-sun60i-a733.o
make -C /path/to/isolated/tree ... drivers/clk/sunxi-ng/ccu-sun60i-a733-r.o
make -C /path/to/isolated/tree ... drivers/clk/sunxi-ng/ccu-sun60i-a733-rtc.o
make -C /path/to/isolated/tree ... drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o
make -C /path/to/isolated/tree ... dt_binding_check
make -C /path/to/isolated/tree ... allwinner/sun60i-a733-cubie-a7s.dtb
```

Stop conditions:

- The selected destination tree is dirty or shared.
- The source prerequisite stack head does not match the recorded passing shape
  and no explanation exists.
- Any prerequisite series changed enough to require maintainer judgment.
- A command would alter the dirty full Mac-mini checkout.
- A command would send mail, push public material, boot a board, or touch
  hardware.

Proof after action:

```text
scripts/kernel-workflow-status --a733-prereq-stack-status
scripts/kernel-workflow-status --maintainer-ready-blockers
```

## Current Safe Next Action Without Approval

If the public GitHub backup gate is not explicitly reopened, the safe next
action is only local planning, evidence indexing, validation-tool correction,
or held-question drafting. Do not quietly convert this packet into permission.
