# A733 H185 decision-ready handoff

Captured: 2026-06-13T05:25Z

## Purpose

Consolidate the current decision point for the A733 CCU/NSI patchwork after
the latest H176 thread refresh and H154 proof-package refresh.

This note is documentation only. It does not approve sending mail, publishing
patches, kernel commits, hardware runs, Cubie staging, service changes, cron
changes, or model-routing changes.

## Current decision

There are two valid next paths. Both remain approval-gated.

Path A: send H176 as maintainer feedback now.

- H176 is the current send-candidate reply to the A733 CCU patch-7 thread.
- H182 found H176's technical claims supported by the current evidence.
- H183 confirmed the patch-7 thread and recipient set are still aligned.
- H176 already preserves the `mbus-msi-lite0` uncertainty as a caveat.
- This path is best when maintainer guidance is more valuable than waiting for
  one more local hardware comparison.

Path B: run the H154 proof first.

- H154 removes only `mbus-msi-lite0` from the H153 known-good critical bundle.
- H184 confirmed the H154 proof package is still present and hash-valid.
- H157 remains the approval packet and command source for exactly one bounded
  Cubie3 proof.
- This path is best when the public feedback should be as narrow as possible
  before any maintainer reply.

## Decision rule

If the operator wants maintainer guidance now, approve Path A.

If the operator wants the cleanest possible `mbus-msi-lite0` story before
public feedback, approve Path B.

If neither approval is given, continue only with local review, documentation,
static validation, or preparation of a fresh materialization worktree plan.

## Exact approvals

To approve Path A:

```text
Approve sending H176 as the A733 CCU RFC patch-7 reply.
```

To approve Path B:

```text
Approve the H157 one-shot Cubie3 H154 proof sequence.
```

## Last checks before Path A

Before any send after explicit approval:

- parse H176 as raw email;
- run public hygiene on H176;
- run focused private/local/model-routing grep on H176;
- refresh the patch-7 thread if significant time has passed;
- confirm whether the operator still wants to send before H154 proof.

## Last checks before Path B

Before any proof after explicit approval:

- recheck the H154 package manifest and file hashes;
- confirm the proof target is Cubie3;
- stop if the helper selects or implies any other board;
- run exactly one proof attempt unless the operator approves a retry;
- record pass, fail, or indeterminate result in a new task packet.

## After Path A

If H176 is sent:

- record the sent message-id and exact payload;
- update the queue with the send result;
- keep H154 available as optional follow-up proof;
- do not create sendable CCU/NSI patches until maintainer feedback or explicit
  operator approval.

## After Path B

If H154 passes:

- keep the narrowed patch-2 shape for future materialization;
- update H176 or its successor to remove the `mbus-msi-lite0` uncertainty;
- rerun technical, hygiene, and thread checks before any send.

If H154 fails or is indeterminate:

- keep H153 as the evidence-preserving default;
- keep H176's existing `mbus-msi-lite0` caveat;
- record the result and do not rerun hardware without new approval.

## Guardrails

- Do not send H176 without explicit approval.
- Do not run H154 proof without explicit approval.
- Do not use Cubie1.
- Do not touch boot defaults as part of local preparation.
- Do not create kernel-source commits or generated patch series without
  explicit approval.
- Do not use unapproved model-routing lanes for this continuation.
