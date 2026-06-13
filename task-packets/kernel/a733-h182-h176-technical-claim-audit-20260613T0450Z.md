# A733 H182 H176 technical claim audit

Captured: 2026-06-13T04:50Z

## Purpose

Audit the public technical claims in H176 against the current evidence packets
before any maintainer reply is sent.

This note is documentation only. It does not approve sending mail, publishing
patches, kernel commits, hardware runs, service changes, cron changes, or
model-routing changes.

## Source audited

- `task-packets/kernel/a733-h176-ccu-rfc-feedback-send-candidate-20260613T0355Z.txt`

## Evidence reviewed

- `task-packets/kernel/a733-h151-nsi-root-cause-verification-20260613T0226Z.md`
- `task-packets/kernel/a733-h158-h153-h154-source-review-20260613T0257Z.md`
- `task-packets/kernel/a733-h169-split-patch-readiness-review-20260613T0324Z.md`
- `task-packets/kernel/a733-h170-ccu-nsi-commit-message-draft-20260613T0329Z.md`
- `task-packets/kernel/a733-h171-nsi-update-bit-design-review-20260613T0335Z.md`
- `task-packets/kernel/a733-h177-h176-send-candidate-review-20260613T0357Z.md`
- `task-packets/kernel/a733-h180-h176-b4-lore-refresh-20260613T0425Z.md`

## Claim audit

H176 says `ahb-cpus` must stay enabled because later R-CCU and RTC register
accesses can stall after `clk_disable_unused()`.

Result: supported. The earlier CCU/PRCM audit and later drafting records
document the verified hardware behavior, the `0x5c0 BIT(28)` gate, and the
reason this is a bridge/register-reachability issue rather than a DTS
workaround.

H176 says storage and NSI fabric clocks need special handling for SDMMC0
normal IDMA to reach memory.

Result: supported. H151 records the sequence from storage-fabric criticals
alone, to NSI update pulse alone, to NSI update pulse plus critical `nsi` and
`bus-nsi`. Only the final shape reached `mmcblk0`, partitions, read-only root,
and `/bin/sh`.

H176 says the NSI clock uses `CCU_FEATURE_UPDATE_BIT` and that committing the
boot-programmed NSI mux/divider state during probe was required in the tested
boot path, together with keeping NSI fabric clocks enabled.

Result: supported with the wording already used in H176. H151 maps H149's
`0x02002580 bit 27` to the A733 NSI clock register at offset `0x580` and the
self-clearing update bit. H171 confirms the helper behavior and registration
gap. H176 correctly avoids claiming the pulse alone fixes SDMMC0.

H176 says the diagnostic shape that reached root kept `ahb-store`,
`mbus-store`, `mbus-msi-lite0`, `nsi`, and `bus-nsi` critical.

Result: supported. H151 and H158 preserve this as the known-good diagnostic
bundle. H176 also correctly states that `mbus-msi-lite0` was not independently
isolated.

H176 says a no-`mbus-msi-lite0` build exists and is statically validated but
has not been hardware-proven.

Result: supported. H158 records the exact source delta and decision rule.
H159 records static validation. The hardware proof remains approval-gated and
unrun.

H176 says `0x02002580 bit 27` maps to the A733 NSI register at `0x580` and the
self-clearing update bit.

Result: supported. H151 records the mapping and the expected unchanged
readback. H171 records the relevant `CCU_FEATURE_UPDATE_BIT` and
`CCU_SUNXI_UPDATE_BIT` definitions.

H176 says helper paths can pulse the update bit, while the MP rate path itself
does not appear to OR in the update bit, and no normal early consumer path was
observed to commit NSI before SDMMC0 IDMA needed it.

Result: supported. H171 documents gate, mux, div, MP parent, MP rate, and
registration behavior. The statement is appropriately scoped to the tested
path and does not overgeneralize to every clock operation.

H176 says it is asking for maintainer guidance rather than sending patches.

Result: supported and appropriate. H169 records that the current H153/H154
source deltas are validated raw diffs, not mail-ready patches. H180 records
that H176 is aligned with the patch-7 thread and recipient set, but not sent.

## Conclusion

No H176 technical text change is required by this audit.

The message is still not approved to send. Remaining gates are explicit
operator approval, final human review of the outgoing mail, and the send-timing
choice recorded in H175: send H176 with the current `mbus-msi-lite0` caveat, or
run the approval-gated H154 no-`mbus-msi-lite0` proof first.

## Guardrails

- Do not send H176 without explicit operator approval.
- Do not treat this audit as approval for H154 hardware proof.
- Do not create kernel-source commits or generated patch series from this note.
- Keep H153 as the default source shape unless H154 hardware proof passes.
