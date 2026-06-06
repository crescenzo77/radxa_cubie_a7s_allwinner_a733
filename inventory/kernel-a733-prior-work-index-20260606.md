# A733 Prior Work Index

Date: 2026-06-06

Scope: private lab index of older A733/Cubie A7S notes found on Strix,
ThinkCentre, and the local Mac workspace. This is not a public submission
artifact and must not be copied wholesale into the public kernel-facing repo.

## Sources Reviewed

- Strix `192.168.50.11`: `/srv/projects/cubie-a7s-local-agent`
- ThinkCentre `192.168.50.225`: `/srv/projects/kernel-services/cortex/ingest`
- Local Mac workspace: `/Users/enzo/projects` and the archived local stack
  note in `/Users/enzo/Downloads/local-ai-mainline-coding-stack-20260605.md`

## High-Value Strix Records

- `VERIFIED_BASELINE.md`: vendor RadxaOS baseline boots through
  BOOT0 -> BL31 -> U-Boot 2018.07 -> extlinux -> Linux -> Debian login.
  Vendor console is `ttyAS0`; the current Strix UART path is confirmed for
  Cubie3 at 115200 8N1.
- `MAINLINE_RFC_V7_BOOT_STAGING_20260530.md`: older first-boot work proved
  the useful mainline milestone through a non-default extlinux label. It also
  records that root writes required interactive sudo and that root SSH was
  denied, matching the current root-install gate.
- `VENDOR_UBOOT_DTB_HANDOFF_ANALYSIS_20260531.md`: clean mainline DTB handoff
  under vendor U-Boot was sensitive to the vendor DTB mutation path. The
  successful test used a temporary non-persistent `drm_debug=1` bootloader
  workaround and reached a mainline `ttyS0` serial REPL.
- `A733_UNCERTAINTY_REGISTER_20260530.md`: records first-slice evidence for
  UART0, PB9/PB10 console pins, `snps,dw-apb-uart`, SDMMC0, CCU/APB-UART
  modeling, and the decision to keep GMAC out of the first upstream slice.
- `BASELINE_PACKAGE_METADATA_FINDINGS.md`: vendor package provenance points
  to Radxa A733 Bullseye packages for `linux-image-5.15.147-21-a733`,
  `u-boot-aw2501`, firmware, and AIC8800 Wi-Fi firmware. Treat as reference
  evidence only.
- `ORANGE_PI_6_6_A733_INSPECTION_20260529.md`: Orange Pi's public
  `orange-pi-6.6-sun60iw2` branch provides reference addresses, clock/reset
  IDs, and pinmux clues, but A733 support is BSP-shaped and not a clean
  implementation base.

## High-Value ThinkCentre Records

- `a733-overlap-scan-20260606.md`: local 7900XT research found overlapping
  Linux A733 CCU/PRCM and pinctrl RFCs and recommends holding independent
  local CCU/pinctrl submissions.
- `a733-inflight-ccu-pinctrl-state-20260606.md`: public-inbox cache search
  found no newer A733-specific Linux CCU or pinctrl v2 after the known RFCs
  through 2026-06-06.
- `a733-rfc-recheck-20260606.md`: confirms the workflow direction remains
  evidence collection, runtime proof, and coordination state rather than new
  CCU/pinctrl patch generation.
- `cubie-hardware-readiness-20260606.md`: older packet listed Cubie2 stale at
  `192.168.50.85`, Cubie3 at `192.168.50.95`, Strix UART host
  `192.168.50.11`, and disabled power automation until switch mapping is
  confirmed.

## Workflow Impact Already Applied

- Current Cubie3 staging now includes `drm_debug=1` in the temporary
  non-default test label bootargs.
- Current Cubie3 staged installer was regenerated after fixing the generated
  sudo verifier to use `cd "$1"` rather than a wrongly expanded local value.
- `scripts/cubie-boot-staging-status` now reports `extlinux_extra_args` so the
  temporary boot command line is visible in proof/status output.
- Root install remains gated on an interactive sudo password for
  `radxa@192.168.50.95`.

## Guardrails

- Do not add vendor-only aliases, path names, compatible strings, or U-Boot
  workaround details to upstream DTS patches unless there is a Linux-facing
  reason maintainers can review.
- Keep `drm_debug=1` as a temporary boot-test constraint for vendor U-Boot,
  not as a kernel patch claim.
- Keep raw UART captures, local model reviews, private topology, and scratch
  task packets out of the public repository.
- Before final DTS submission, re-check the current CCU/PRCM and pinctrl
  prerequisite status and regenerate a DTS-only branch on top of accepted or
  current prerequisite work.
