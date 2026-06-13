# A733 H190 CCU RFC feedback sent

Captured: 2026-06-13T04:21Z

## Purpose

Record that the H189 maintainer-feedback reply was sent after the H154
no-`mbus-msi-lite0` hardware comparison failed.

This note is documentation only. It does not publish the local H153 CCU/NSI
patches, change any kernel worktree, approve any new hardware proof, or change
Hermes/model routing.

## Source sent

- `/Users/enzo/projects/homelab/task-packets/kernel/a733-h189-ccu-rfc-feedback-send-candidate-after-h154-20260613T0630Z.txt`

## Pre-send checks

- `git send-email --dry-run` parsed the raw message successfully.
- The reply targeted:
  - Subject: `Re: [PATCH RFC 7/8] clk: sunxi-ng: a733: Add bus clock gates`
  - In-Reply-To: `<20260310-a733-clk-v1-7-36b4e9b24457@pigmoral.tech>`
  - 15 `To` recipients
  - 7 `Cc` list recipients
- The explicit sender was:
  - `Enzo Adriano <enzo.adriano.code@gmail.com>`
- Transport selected by `git send-email`:
  - `/usr/sbin/sendmail`

## Send result

Command:

```sh
git send-email \
  --from="Enzo Adriano <enzo.adriano.code@gmail.com>" \
  --confirm=never \
  /Users/enzo/projects/homelab/task-packets/kernel/a733-h189-ccu-rfc-feedback-send-candidate-after-h154-20260613T0630Z.txt
```

Result:

- `Result: OK`
- Message-ID: `<20260613042105.18962-1-enzo.adriano.code@gmail.com>`

## Follow-up state

H190 closes the local maintainer-feedback send gate for the H153/H154 CCU/NSI
investigation. The next kernel-facing action is to materialize the H153 default
source shape into real commits in a fresh clean Strix worktree, then run the
normal patch validation flow before considering any patch publication.

H154 remains rejected for source materialization because its Cubie3 proof failed
before SDMMC0 initialization.

## Guardrails

- Continue using hosted Codex Desktop for reasoning, review, synthesis, and
  drafting.
- Do not route this kernel work through local model endpoints or OpenRouter.
- Do not use Cubie1 for proof or reproduction.
- Do not send the raw H153 split diffs as mail-ready patches.
