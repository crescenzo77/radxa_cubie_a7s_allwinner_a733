# A733 H032 Send Approval Decision Packet

Status: requires user decision; nothing sent
Created: 2026-06-10T20:28:00Z

## Current Decision

The A733 SDMMC0 descriptor-fetch question is ready, public-clean, and dry-run
validated. It should not be sent until the user chooses:

1. Approval: send now, hold, or use a non-email route.
2. Public From identity.
3. Send host or route.

## Recommended Choice

Recommended route: send the H030 public-clean draft to Linux MMC plus sunxi
maintainers/lists from the Mac using this candidate public From identity if
the user approves it:

```text
Enzo Adriano <enzo.adriano.code@gmail.com>
```

This identity appears in the existing public patch exports as `From:` and
`Signed-off-by:`. A Mac `git send-email --dry-run` with this identity passed.

Draft:

```text
/Users/enzo/projects/homelab/task-packets/kernel/a733-h030-public-email-draft-20260610T2021Z.txt
```

Draft SHA256:

```text
3d3aeca3ee6292c08699e817822c9d9c042190656118739ca88cdef6b1f0636a
```

## Known Preflight

- Mac: `git send-email` available.
- Mac dry-run: passed.
- Mac default From: `enzo <enzo@enzos-Mac-mini.local>`.
- Strix: `git-send-email` missing.
- Strix global `user.email`: `enzo@homelab.local`.

Do not send as `enzo@enzos-Mac-mini.local` or `enzo@homelab.local` unless the
user explicitly approves one of those addresses for public lists.

## Exact Mac Command After Approval

Use this only after explicit user approval:

```sh
git send-email \
  --confirm=always \
  --from='Enzo Adriano <enzo.adriano.code@gmail.com>' \
  /Users/enzo/projects/homelab/task-packets/kernel/a733-h030-public-email-draft-20260610T2021Z.txt
```

## Exact Hold Decision

If the user chooses not to email yet, record:

```text
H032 decision: hold external send.
Reason:
Next route:
Review date:
```

## Exact Alternate Routes

- Radxa issue/discussion: paste the H030 public-clean draft, minus mailing-list
  headers, and record the URL.
- Manual mail client: paste the H030 draft body, set the To/Cc exactly as in
  the draft, and record the sent timestamp plus Message-ID if available.
- Strix: install/configure `git-send-email` first, then re-run dry-run with the
  approved From identity.

## Required Result Artifact After Decision

Create an H032 result JSON recording:

- decision: sent, held, alternate_route, or blocked
- approved_from
- route
- timestamp
- message hash
- Message-ID or URL if sent
- responses, initially empty
- next queued item

If sent and a response identifies a concrete register, reset/clock ordering,
firmware handoff, master ID, binding, or erratum, queue H033 as one narrow
runtime proof. Otherwise keep local behavior patching paused.
