# A733 H260 - Current Maintainer Response Playbook

Captured UTC: 2026-06-13T09:20Z

## Purpose

Create a current, single-entry playbook for what to do next if maintainer,
public-archive, delivery, or publication events occur after H215-H259.

This packet is documentation only. It is not a resend approval, not a new public
thread, not a `b4 send`, not a `b4 send --reflect`, not a public push, not a
source change, and not a hardware, service, cron, or model-routing action.

## Current State

### CCU / SDMMC0 Thread

- H215 is the submitted narrow RFC/RFT series on the existing A733 CCU thread.
- H215 local send reported five `Result: OK` messages.
- H254 still found no H215 markers in reachable Patchew or bounded public-inbox
  Git views.
- Direct public-inbox web probes remain HTTP 403 from this environment and are
  inconclusive.
- H219 still controls: do not resend H215 or open an alternate public thread
  without sender-mailbox evidence, confirmed delivery failure, maintainer
  request, or another H219-approved trigger plus refreshed gates.

### Narrow Hardware-Proven Source

- Base: `d9aa2e15caae`
- H200/H215 narrow source anchor:
  `de486cb24c361a86cba26738f24332df780872b0`
- H201 hardware proof reached unused-clock cleanup, unused power-domain cleanup,
  SDMMC0 initialization, card and partition enumeration, read-only root mount,
  and `/bin/sh`.
- H255 reconfirmed the H200/H215 source anchor is clean and diff-checks against
  the recorded base.

### Common Update-Bit Fallback

- H253 is the current no-send fallback bundle if maintainers ask for common
  `CCU_FEATURE_UPDATE_BIT` handling.
- H253 source anchor:
  `e694ae3fa8477846a5a6eaf31fed4813ff991d5b`
- H247 hardware-proved that common-helper fallback through the same Cubie A7S
  success boundary.
- H255 reconfirmed the H253 patch bundle applies from the recorded base and
  reconstructs the fallback source for the touched CCU files.

### DTS / Public Export Track

- H256 reconfirmed the final DTS branch still passes the no-send final b4 gate.
- H257 updated the public/export expected-head record to the clean Mac export
  head `db53521a63f9cc6a4fc684a927b3bac78173b859`.
- H258 proved a public push dry-run had fast-forward shape.
- H259 attempted the public push, but the public remote rejected it because the
  credential lacked workflow scope for a workflow file update. Remote state was
  verified unchanged.

## Event-Driven Actions

### If A Maintainer Replies To H215

1. Identify whether the reply is asking about proof, minimality, update-bit
   placement, recipient/threading, or a respin.
2. Use H218 for public-safe response phrasing.
3. Use H224 for the technical per-patch delta map.
4. Use H211 if a public-safe boot excerpt is requested.
5. Re-run public hygiene on any outgoing excerpt or drafted reply.
6. Do not broaden into board-DTS, Ethernet, VPU, display, USB-C, PCIe, wireless,
   camera, eMMC, or unrelated peripheral claims.

### If Maintainers Ask For Common Update-Bit Handling

1. Start from the H253 bundle and H255 source-anchor check.
2. Recheck upstream refs and public archive state before use.
3. Re-run recipient discovery, public hygiene, trailer hygiene, apply check,
   source equivalence, `git diff --check`, and focused build/static gates.
4. Preserve the H250/H251 caveat: the common helper is a registration-time
   firmware-to-Linux handoff for update-bit clocks, not a complete audit of
   every later rate-change path.
5. Treat the common-helper shape as maintainer-directed fallback material, not
   as an automatic replacement for H215.

### If Sender-Mailbox Evidence Shows H215 Failed

1. Confirm the failure applies to all relevant H215 messages, not only a local
   archive lookup.
2. Refresh public archive state.
3. Refresh recipients with the kernel-native maintainer script.
4. Re-run the H210/H215 send gates: public hygiene, trailer hygiene, strict
   checkpatch, apply from base, source equivalence to H200, and diff check.
5. Only then prepare a resend or alternate-thread action under H219.

### If H215 Appears Publicly

1. Record the archive URLs and message IDs.
2. Do not resend.
3. Continue waiting for maintainer review.
4. If a public reply appears, follow the maintainer-reply path above.

### If Public Export Backup Is Needed

1. Recheck the clean Mac public/export repo head and `public/main`.
2. If the credential has workflow scope, retry the fast-forward push and verify
   the remote head afterward.
3. If workflow scope is still unavailable, do not keep retrying the same push.
   Either obtain a credential with workflow scope or explicitly choose a
   no-workflow publication strategy.
4. Do not use the dirty build-host public-export working copy as send authority.

### If DTS Reflect Review Is Requested

1. Re-run the no-send final b4 gate on the final DTS branch.
2. Run only `b4 send --reflect` first.
3. Review the reflected copy for subject, dependencies, recipients, patch order,
   and absence of local CCU/pinctrl scaffolding or vendor U-Boot DTS workarounds.
4. Do not run a real send until the reflected copy is acceptable.

## Current Best Next Actions

- For CCU/SDMMC0: wait for maintainer/public-mail evidence, or respond using
  H218/H224/H253 only when an event requires it.
- For DTS/export: resolve the workflow-scope publication blocker or run a
  deliberate reflect-review path.
- For hardware: do not run another Cubie proof unless a new maintainer question
  requires fresh evidence.
