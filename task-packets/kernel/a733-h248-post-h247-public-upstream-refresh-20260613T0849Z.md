# A733-SDMMC-H248: Post-H247 Public and Upstream Refresh

Captured: 2026-06-13T08:49Z

## Purpose

Refresh the public/archive and upstream-prerequisite state after the H247
hardware proof of the H245 common update-bit v2 option.

This packet is documentation only. It is not a resend approval, not a new
public thread, and not a service, cron, mail-routing, hardware, or model-routing
change.

## Upstream Refs Checked

```text
mainline master:   062871f1371b2e02a272ff5279c6479aff0a37ef
clk-next:          5f7092aabf492fbc95a4cba1cc6c0d64c62a9abb
sunxi for-next:    4a481339d33a7a7f401ad59fc04481f946d8965a
SoC for-next:      f9c349592b74e96cecadd7d427f0b3dd6320d489
```

These match the prior checked refs from H241.

Raw file checks still returned 404 for checked A733 prereq files in the
selected upstream refs:

```text
drivers/clk/sunxi-ng/ccu-sun60i-a733.c
drivers/pinctrl/sunxi/pinctrl-sun60i-a733.c
```

No checked upstream baseline currently supersedes H215 or forces a rebase.

## Public Archive Checks

Exact H215 Message-ID and subject-marker searches against the direct public
inbox web endpoint returned HTTP 403 from this environment. Treat that as a
blocked lookup, not absence evidence.

The public patch-tracker page and mbox for the original A733 CCU thread were
reachable:

```text
thread page: HTTP 200, H215 markers: 0
thread mbox: HTTP 200, H215 markers: 0
```

Checked H215 marker set:

```text
20260613065059
RFC/RFT
de486cb24c36
Cubie A7S SDMMC0 path live
```

## Interpretation

H247 changes the technical fallback posture but not the public send posture.
The H245 common update-bit v2 option is now hardware-proven, but H215 remains
the submitted narrow A733 series. The H219 resend gate still controls:

- no duplicate resend from patch-tracker/search absence alone;
- direct inbox HTTP 403 is not proof of absence;
- resend or a new public action still requires sender-mailbox evidence,
  confirmed delivery failure, maintainer request, or another H219-approved
  trigger plus refreshed gates.

## Current Best Posture

Keep H215 as the public/submitted position.

Keep H245/H247 ready as the maintainer-directed v2 fallback if reviewers ask
for common `CCU_FEATURE_UPDATE_BIT` handling.

Safe next work:

- prepare a no-send v2 fallback cover/series note that cites H247 proof;
- continue bounded public/archive refreshes;
- refresh recipient/source gates only when a resend or maintainer-requested v2
  becomes plausible.
