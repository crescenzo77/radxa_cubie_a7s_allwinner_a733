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
  records that root writes required interactive sudo and that direct root SSH
  was denied. That matches the current gate shape: user-space staging works,
  while the final `/boot` install still requires the Cubie sudo password.
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
- Current A733 SDMMC runtime triage is tracked in
  `task-packets/kernel/a733-hypothesis-queue.json`. As of H022, rootfs,
  protocol flow, descriptor geometry, visible GCTRL/DMAC bits, IOMMU, 64-bit
  DMA-mask intent, data-buffer placement, descriptor allocation class,
  SDMMC0 fabric-clock consumers, the safe MSI-lite/IOMMU fabric subset, and a
  new SDMMC-local vendor wrapper-write search are not the standalone fix. H022
  found the next source-backed path below SDMMC: vendor NSI controller/PMU
  init is active during known-good SD reads. The next work order is H023:
  test minimum lab-only NSI clock/reset init while keeping all GMAC, display,
  VPU, GPU, CE, DMA, USB, PCIe, and unrelated fabric bits out of scope.
- 2026-06-10 H023/H024 update: H023 and H024 reached `mmcblk0`, applied the
  H021 MSI/IOMMU subset, and dumped CCU NSI plus NSI ports 1/11/12/14/15.
  Removing CPU0/CPU1 NSI reads did not move the stop; UART still went silent
  after the port 15 pre-dump and before any NSI-minimum write result or
  descriptor evidence. The next work order is H025: remove IAG reads from the
  behavior proof and split/breadcrumb the CCU 0x580 and 0x584 writes.
- 2026-06-10 H025 update: H025 removed IAG reads from the behavior path and
  proved the CCU NSI minimum writes land (`0x580: 0x43000005 -> 0xc3000005`,
  `0x584: 0x00010000 -> 0x00010001`). The forced CMD18 still stalls with the
  descriptor unchanged, `OWN` set, `CHDA=DLBA`, `CBDA=0`, and `IDST=0x4000`.
  The next work order is a no-build H026 source/log/sysfs audit for
  lower-level descriptor-fetch reachability state before any new behavior
  patch.

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

## 2026-06-10 H026 Addendum

- H026 stayed no-build. It decoded the H025 stall as IDMAC `DESC_READ`, found
  vendor NSI sysfs exposes `DRIVER=NSI_PMU` but no `sdmmc`/`smhc`/storage
  `nsi_master`, and found no local source-backed firewall/security/interconnect
  write to test. The next work order is H027: a narrow vendor-style normal
  IDMAC DMA mask/address translation diagnostic, preserving H025 breadcrumbs
  and avoiding DTS or fabric expansion.

## 2026-06-10 H027 Addendum

- H027 booted Strix kernel
  `9c631195b663 mmc: test A733 vendor normal IDMAC address path`.
  It matched the vendor normal-IDMAC evidence by setting a 64-bit
  DMA/coherent mask, using coherent descriptor allocation, keeping descriptor
  size bits `12`, and using shifted `DLBA=0x3f840000`. The forced CMD18 still
  stalled in `DESC_READ`: descriptor checksum unchanged, `OWN` set,
  `CHDA=DLBA`, `CBDA=0`, `IDST=0x4000`, `CBCR=0x400`, and `BBCR=0`.
- H027 closes vendor normal-IDMAC DMA mask/address translation as a standalone
  fix. The next work order is H028: firmware handoff and storage-master
  permission inventory across boot0/BL31/ATF/SCP/vendor U-Boot, security or
  firewall setup, and NSI/MBUS permission tables before any new behavior patch.

## 2026-06-10 H028 Addendum

- H028 stayed no-build and produced
  `task-packets/kernel/a733-h028-firmware-handoff-inventory-20260610T2014Z.json`.
- It found no local source-backed boot0, BL31/ATF, SCP/ARISC, vendor U-Boot,
  security/firewall, IOMMU, NSI/MBUS, or SDMMC/SMHC storage-master permission
  delta suitable for another behavior patch. Boot logs show firmware handoff
  and `secure enable bit: 0`, but no named storage permission setup. Vendor DT
  and source still describe the already-tested SDMMC0 v5p3x clock/descriptor
  shape, with no SDMMC IOMMU/interconnect/firewall/NSI-master binding.
- The next work order is H029: prepare a maintainer/vendor descriptor-fetch
  question packet using H009-H028 evidence. Do not build another descriptor,
  DMA-mask, clock, or fabric patch unless that packet or new source evidence
  identifies a single concrete delta.

## 2026-06-10 H029 Addendum

- H029 produced
  `task-packets/kernel/a733-h029-maintainer-vendor-question-packet-20260610T2018Z.md`.
- The draft is a coordination artifact, not a patch. It captures the exact
  SDMMC0 IDMAC `DESC_READ` stall signature, the working PIO/rootfs proof, the
  H009-H028 ruled-out list, the A733 CCU/pinctrl RFC dependency posture, and
  direct questions about SDMMC0 descriptor-fetch preconditions.
- The next work order is H030: route the question packet and log responses.
  Keep local behavior patching paused until an answer or new source reference
  identifies one concrete runtime proof.

## 2026-06-10 H030 Addendum

- H030 produced
  `task-packets/kernel/a733-h030-public-email-draft-20260610T2021Z.txt` and
  `task-packets/kernel/a733-h030-routing-tracker-20260610T2021Z.json`.
- Recommended first route: Linux MMC plus sunxi maintainers/lists. DT
  maintainers are not on the first route because this is a runtime IDMAC
  question, not a binding submission.
- Nothing was sent. The next work order is H031: get explicit approval and
  working mail transport, then send the public-clean draft or record the chosen
  route/blocker.

## 2026-06-10 H031 Addendum

- H031 produced
  `task-packets/kernel/a733-h031-send-preflight-result-20260610T2025Z.json`.
- Mac `git send-email --dry-run` passed and parsed the public-clean draft, but
  the default From identity was `enzo <enzo@enzos-Mac-mini.local>`. Strix does
  not have `git-send-email` installed.
- Nothing was sent. The next work order is H032: user approval plus public From
  identity and send host/route selection.

## 2026-06-10 H032 Addendum

- H032 prepared
  `task-packets/kernel/a733-h032-approval-send-decision-20260610T2028Z.md`.
- The packet contains exact send, hold, alternate-route, and result-recording
  templates. H032 remains open until the user chooses send/hold/alternate
  route and a public From identity.
