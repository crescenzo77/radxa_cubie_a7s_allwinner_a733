# A733 H156 Claude doc intake

Captured: 2026-06-13T02:54Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Record the Claude-created or Claude-maintained documentation found on the Mac, distinguish durable canonical records from cache-only material, and preserve the handoff rules for continuing Radxa Cubie A7S / Allwinner A733 mainline kernel work in Codex Desktop.

This note is documentation only. It does not approve hardware runs, Cubie staging, kernel commits, service changes, cron changes, or patch publication.

## Canonical durable records already in homelab

- `task-packets/kernel/reviews/a733-mac-session-progress-20260613.md`
  - Claude session progress note for the v8/export alignment, Cubie2 proof, CCU criticals, and Strix preflight pass.
- `task-packets/kernel/reviews/a733-rccu-rtc-clk-hang-audit-20260612.md`
  - Claude-created CCU/PRCM root-cause audit, later updated with hardware verification.
- `task-packets/kernel/a733-h150-ccu-rfc-feedback-draft-20260613.txt`
  - Draft reply for the in-flight A733 CCU RFC. It remains a draft and must not be sent without final human review and live-thread recipient recheck.

## Claude memory records found

Location: `/Users/enzo/.claude/projects/-Users-enzo/memory/`

- `project_a733_mainline.md`
  - A733 mainline project memory: repo paths, topology, blockers, guardrails, and prior status.
- `MEMORY.md`
  - Memory index linking the A733 project, macOS case-collision warning, and no-offload rule.
- `feedback_llm_work_in_claude.md`
  - Operator rule from the Claude session: do not dispatch LLM work to local homelab model lanes or OpenRouter.
- `reference_macos_case_collisions.md`
  - Warning that `/Users/enzo/projects/linux-a733` has APFS case-insensitivity phantom changes; do not stage, stash, or "fix" them.

For this Codex Desktop continuation, apply `feedback_llm_work_in_claude.md` as: keep reasoning, review, synthesis, and drafting inside hosted Codex Desktop. Do not use local model lanes or OpenRouter for this kernel work unless the operator explicitly changes that rule.

## Claude cache-only or transcript-only material

- Claude file history contains drafts or earlier versions of:
  - the CCU/PRCM audit,
  - the A733 Mac session progress note,
  - the H150 CCU RFC feedback draft,
  - helper-script changes around offload/status/shape gates,
  - the Claude memory records above.
- The important versions appear to have durable homelab copies except for the long-form narrative summary requested in Claude.
- The long-form summary of all Radxa Cubie A7S kernel patching work appears to exist in the Claude transcript (`d578de30-7622-4c6d-b0e6-87f61173238b.jsonl`) rather than as a standalone canonical file.

## Relevance to current patchwork

Current authoritative continuation state is the homelab repo plus Strix kernel worktrees and outgoing artifacts, not the Claude cache.

Use the Claude docs as supporting provenance for:

- why `ahb-cpus` is required critical;
- why `ahb-store` and `mbus-store` are part of the storage-fabric critical set;
- why `mbus-msi-lite0` is still an evidence-preserving inclusion unless H154 proves it unnecessary;
- why Cubie1 must remain excluded from proof work;
- why local/OpenRouter model offload should not be required for this continuation;
- why Mac `linux-a733` case-collision status must not be "cleaned" mechanically.

## Current next patchwork decision

The next kernel-facing action remains approval-gated hardware proof of the H154 no-`mbus-msi-lite0` package on Cubie3, using the commands recorded in:

- `task-packets/kernel/a733-h155-h154-proof-package-readiness-20260613T0248Z.md`

Until approved, safe work is limited to documentation, review, static validation, package verification, and maintainer-facing draft preparation.

## Guardrails

- Do not use Cubie1 for proof or reproduction.
- Do not write `/boot`, reboot, power-cycle, or run UART proof sessions without explicit operator approval.
- Do not send CCU RFC feedback or publish patches without final human review.
- Do not route this kernel work through local model endpoints or OpenRouter.
- Do not stage, stash, or clean the known APFS phantom changes in `/Users/enzo/projects/linux-a733`.
