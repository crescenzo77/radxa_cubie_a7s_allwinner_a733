# A733-SDMMC-H233: H215 Response Matrix mbus Refresh

Captured: 2026-06-13T07:43:13Z

## Purpose

Refresh the H215 maintainer-response matrix so the `mbus-msi-lite0` answer
matches the completed H154/H188 no-`mbus-msi-lite0` hardware comparison.

This packet is documentation only. It is not a resend approval, not a new mail
draft, not a source change, and not a hardware action.

## Inputs

- H188: no-`mbus-msi-lite0` comparison failed on Cubie A7S immediately after
  the unused-clock walk and did not reach SDMMC0 initialization.
- H210/H215 patch 2: already states that the narrower comparison without
  `mbus-msi-lite0` did not reach SDMMC0 initialization.
- H218: maintainer-response matrix still had softer earlier wording that said
  the narrower variant was investigated separately, without explicitly
  carrying the H188 failure result into the safe-answer text.

## Change Made

Updated H218 to:

- reference H226 as the latest public-visibility refresh instead of H217;
- add H188 as an evidence anchor;
- answer `mbus-msi-lite0` questions with the H188 result: removing the gate
  from the tested bundle regressed the Cubie A7S proof run before SDMMC0
  initialization;
- keep the important limitation that `mbus-msi-lite0` is not proven minimal
  across all possible fabric models;
- change the narrowing order so `mbus-msi-lite0` is not dropped by default.

## Decision

No narrower v2 option should be prepared from H154. H154 is a failed comparison,
not a replacement for H200/H215.

The current maintainer-ready position is:

- keep the full H200/H215 storage/NSI fabric bundle;
- if maintainers ask about `mbus-msi-lite0`, cite the failed no-`mbus-msi-lite0`
  comparison;
- only drop it if maintainers request that shape despite the regression
  evidence, or if a new fabric model/fresh proof replaces H188.

## Validation Need

Run the public hygiene gate on updated H218 and this H233 packet before relying
on them for public response prep.
