# A733 DTS v2 Held Cover And Changelog Draft

Status: drafted-not-reviewed; local-only; no-send
Updated: 2026-06-13

This is a held local draft for A733-COMM-002 and A733-COMM-003. It is not a
sent message, not b4 metadata, not a pull request, not maintainer-approved,
not validation proof, and not permission to mutate hardware.

This draft is not a sent message.

## Send Blockers

- Communication blackout remains active.
- Operator approval is not open.
- DTS v2 local cleanup has not been applied to a kernel tree.
- Static proof is not complete.
- Runtime proof remains queued-only under A733-BATCH-002.
- Board roles, recovery drill, artifact path, UART path, rollback path, and
  claim service do not yet permit runtime proof.
- Public recipients and current thread state have not been refreshed.

## Source Inputs

- DTS v1 historical send: A733-COMM-016 / H265
- Maintainer feedback: move UART0 pins into the main A733 DTSI and do not rush
  DT while clock prerequisites are still early
- Local delta plan:
  `task-packets/kernel/a733-dts-v2-local-delta-plan.md`
- Static proof plan:
  `task-packets/kernel/a733-dts-v2-static-proof-plan.md`
- No-send preview patch:
  `task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch`

## A733-COMM-002 Draft Cover Notes

```text
Subject: [PATCH v2 0/1] arm64: dts: allwinner: Add Radxa Cubie A7S

This is a v2 of the Radxa Cubie A7S board description.

The only intended change from v1 is to move the UART0 PB9/PB10 pin group from
the board DTS into the A733 SoC DTSI, so the board DTS only references a
SoC-level pin group.

The board scope remains intentionally minimal:

- UART0 serial console
- SD-card boot through SDMMC0

Ethernet and other peripherals remain omitted until their A733-specific
wrapper, clock, reset, power, PHY, firmware, and runtime behavior are proven.

This version should be sent only after the prerequisite clock/reset/pinctrl/MMC
state, static validation, runtime proof, recipients, and operator approval are
refreshed.
```

## A733-COMM-003 Draft Changelog Notes

```text
Changes in v2:

- Move the UART0 PB9/PB10 pin group from sun60i-a733-cubie-a7s.dts into
  sun60i-a733.dtsi.
- Keep the Cubie A7S board DTS referencing the SoC-level UART0 pin group.
- Keep the board scope limited to UART0 console and SD-card boot.
- Continue to leave Ethernet and other peripherals out of scope until they are
  source-backed and runtime-proven.
```

## Revalidation Required Before Any Send

Before this draft can become ready-held or public:

```sh
python3 tools/validate/a733_authority_check.py
git apply --check task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch
git diff --check -- arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts
make O="$O" ARCH=arm64 allwinner/sun60i-a733-cubie-a7s.dtb
make O="$O" ARCH=arm64 CHECK_DTBS=y allwinner/sun60i-a733-cubie-a7s.dtb
scripts/checkpatch.pl --strict <generated patch>
scripts/get_maintainer.pl <generated patch>
b4 prep --show-info
```

If any command cannot run on the selected host, record it as blocked or rerun
on a suitable full kernel tree. Do not convert unavailable tooling into a pass.

## Current Status

- A733-COMM-002: `drafted-not-reviewed`, no-send.
- A733-COMM-003: `drafted-not-reviewed`, no-send.
- A733-BATCH-002: still queue-only.
- Public communication: closed.
- Hardware mutation: closed.
