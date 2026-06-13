# A733 H168 H167 send-readiness refresh

Captured: 2026-06-13T03:19Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Refresh the maintainer-facing A733 CCU RFC feedback draft after finding that H166 was readable as a draft note but not parseable as a raw email because its warning banner preceded the mail headers.

This note is documentation only. It does not approve sending mail, publishing patches, kernel commits, hardware runs, service changes, cron changes, or model-routing changes.

## Result

New current draft:

- `task-packets/kernel/a733-h167-ccu-rfc-feedback-draft-v6-20260613T0318Z.txt`

H167 supersedes H166 for packaging only:

- H167 starts with `Subject`, `In-Reply-To`, `References`, `To`, and `Cc` at byte one.
- The "do not send" warning was moved into a bracketed body note.
- The technical content remains the H166 v5 wording: patch 7/8 target, MP update-bit nuance preserved, and `mbus-msi-lite0` still described only as part of the verified bundle rather than independently proven required.

## Checks run

- `python3 -m json.tool task-packets/kernel/a733-hypothesis-queue.json`
  - pass before the queue update in this turn.
- Raw email parser check on H167:
  - `Subject`: present
  - `In-Reply-To`: present
  - `References`: present
  - `To`: present
  - `Cc`: present
- `scripts/kernel-public-hygiene-gate` on an isolated directory containing H167:
  - status: PASS
  - files scanned: 1
  - matches: 0
- Focused grep on H167 for private/local/model-routing terms:
  - no matches.
- Fresh Patchew mbox fetch:
  - URL: `https://patchew.org/linux/20260310-a733-clk-v1-0-36b4e9b24457%40pigmoral.tech/mbox`
  - mbox was reachable.
  - mbox still contains `<20260310-a733-clk-v1-7-36b4e9b24457@pigmoral.tech>`.
  - mbox still contains `[PATCH RFC 7/8] clk: sunxi-ng: a733: Add bus clock gates`.
  - mbox still contains the expected source terms: `SUNXI_CCU_MP_DATA_WITH_MUX_GATE_FEAT`, `ahb_cpus_clk`, and `mbus_msi_lite0_clk`.
- `b4` remains unavailable on the Mac.

## Remaining gates

- Human technical review of H167.
- Final recipient/thread check with `b4` or lore from an environment where that is available.
- Explicit operator approval before sending any mail.
- Decide whether to send the maintainer feedback before or after the optional H154 no-`mbus-msi-lite0` hardware proof.

## Guardrails

- Do not send H167 without explicit approval.
- Do not treat H167 as approval for the H154 hardware proof.
- Do not use local LLM lanes or OpenRouter for review, synthesis, or drafting.
