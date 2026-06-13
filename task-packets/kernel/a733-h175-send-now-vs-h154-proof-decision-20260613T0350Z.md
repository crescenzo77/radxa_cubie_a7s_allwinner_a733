# A733 H175 H176 send timing decision packet

Captured: 2026-06-13T03:50Z

## Purpose

Separate the remaining human decision about the H176 maintainer-feedback send
candidate:

- send the CCU RFC feedback now, before H154 hardware proof; or
- wait until the optional H154 no-`mbus-msi-lite0` proof resolves the narrower
  patch-2 question.

This note is documentation only. It does not approve sending mail, publishing
patches, kernel commits, hardware runs, service changes, cron changes, or
model-routing changes.

## Current state

H176 is the current send-candidate payload:

- `task-packets/kernel/a733-h176-ccu-rfc-feedback-send-candidate-20260613T0355Z.txt`

H176 differs from H173 only by removing the bracketed internal draft warning
from the email body. H173 remains useful as the reviewed draft with explicit
do-not-send text; H176 is the file to use if sending is explicitly approved.

H176 is mechanically ready as a draft reply:

- raw email headers parse;
- public hygiene passes;
- focused private/local/model-routing grep is clean;
- b4/lore recipient and thread recheck passed;
- H174 found the technical body consistent with H151, H158, H170, H171, and
  H172.

H154 is ready only as an optional hardware-proof candidate:

- the boot package exists and hash validation passed in H155/H159;
- H157 contains exact approval-gated commands and pass/fail criteria;
- no board staging or H154 hardware proof has run.

## Option A: send H176 before H154 proof

Use when the priority is maintainer feedback while the A733 CCU RFC is still
fresh and before local work drifts further.

Benefits:

- Maintainers see the verified `ahb-cpus`, storage-fabric, and NSI evidence
  sooner.
- H176 already phrases `mbus-msi-lite0` carefully as part of the verified
  bundle, not as independently proven required.
- The message asks for modelling guidance instead of presenting a final patch
  series.
- H154 can still run later; any narrower result can be sent as a follow-up.

Costs:

- The message cannot say whether `mbus-msi-lite0` is unnecessary.
- If H154 later passes, a follow-up may be needed to narrow the storage-fabric
  claim.

Recommended if:

- the goal is to unblock maintainer discussion quickly;
- the operator does not want to run hardware now;
- the operator is comfortable with the explicit caveat already in H176.

## Option B: run H154 proof before sending

Use when the priority is making the public feedback as narrow as possible.

Benefits:

- If H154 passes, the feedback can say `mbus-msi-lite0` was not required by the
  no-`mbus-msi-lite0` A/B result.
- If H154 fails, the current H176 caveat remains correct and stronger.
- The local patch-2 direction becomes cleaner before any public exchange.

Costs:

- Requires explicit hardware approval.
- Touches Cubie3 staging and proof flow.
- Adds delay and live-board risk.
- If the result is indeterminate, the send decision returns to the same H176
  caveat state.

Recommended if:

- the operator wants the cleanest possible patch-2 story before public feedback;
- Cubie3 is available and a bounded proof run is acceptable;
- the operator explicitly approves the H157 sequence.

## Recommendation

Default recommendation: send H176 before H154 proof only if the operator wants
maintainer guidance now.

Reason:

- H176 is already honest about the `mbus-msi-lite0` uncertainty.
- It is a feedback/guidance reply, not a final patch submission.
- Waiting for H154 improves precision, but does not block the core maintainer
  questions about `ahb-cpus`, NSI update-bit handling, and fabric modelling.

If the operator prefers minimum public churn, run H154 first using H157. If the
operator prefers speed and maintainer guidance, request explicit send approval
for H176.

## Exact approvals still needed

To send H176:

- "Approve sending H176 as the A733 CCU RFC patch-7 reply."

To run H154 proof first:

- "Approve the H157 one-shot Cubie3 H154 proof sequence."

Without one of those explicit approvals, continue only with local review,
documentation, or static validation.

## Guardrails

- Do not send H176 without explicit operator approval.
- Do not run H154 proof without explicit operator approval.
- Do not use Cubie1.
- Do not create kernel-source commits or generated patch series without
  explicit operator approval.
