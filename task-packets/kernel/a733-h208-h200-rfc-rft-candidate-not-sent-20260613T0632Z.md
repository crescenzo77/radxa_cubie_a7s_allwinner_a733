# A733-SDMMC-H208: H200 RFC/RFT Candidate, Not Sent

Captured: 2026-06-13T06:32:38Z

## Purpose

Prepare a public-clean RFC/RFT candidate bundle for the H200 CCU/NSI stack
without sending it.

This is a readiness artifact only. Do not send it while H204 remains
unconfirmed in checked public views unless a maintainer asks for the patch text
or the operator explicitly asks for a new send.

## Candidate Bundle

- Mac path: `/Users/enzo/projects/homelab/task-packets/kernel/a733-h208-h200-rfc-rft-candidate-not-sent/`
- Strix path: `/srv/projects/homelab/task-packets/kernel/a733-h208-h200-rfc-rft-candidate-not-sent/`

Files:

```text
0000-cover-letter.patch
0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

## Source Identity

- Base: `d9aa2e15caae`
- H200 exact tested head: `de486cb24c361a86cba26738f24332df780872b0`
- Recreated H208 apply-check head on Strix: `d4ebdcb019fcc717f994b2cc868dbb7a66feaccc`
- Touched source: `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`

The recreated head differs from H200 because `git am` creates fresh commits
with fresh committer metadata. The source diff against H200 for the touched CCU
file was clean.

## SHA256

```text
3f81ef7fe03dcb53206cfc98fd549291e22072211cc60872ef736f88523850c9  0000-cover-letter.patch
241d4d8c6b1c89d7804bc1e1a1265cfaeffe49b75e0af70e3da0b83358025ee9  0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
b24712a5cd5069954d3accbf83153c49f0c9497508df39945752bc39eea36e6c  0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
b016e28834173cafcfe3231d7666a87a1eeda64cce1cb260dcbe1290ea4c7b9c  0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
a3fcbc564316c68d410af52b41db369acd7c2b55bdc68d522e9fcc3f5376a07b  0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

## Validation

- `python3 tools/validate/public_hygiene_gate.py --json task-packets/kernel/a733-h208-h200-rfc-rft-candidate-not-sent`: PASS
- `python3 tools/validate/trailer_gate.py --json task-packets/kernel/a733-h208-h200-rfc-rft-candidate-not-sent/000[1-4]-*.patch`: PASS
- Strix `git am --3way` apply-check from `d9aa2e15caae`: PASS
- Strix `git diff --check d9aa2e15caae..HEAD`: PASS
- Strix source diff against H200 for `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`: clean

## Current Public State

The latest checked state before creating this candidate remained:

- H204 local send result: OK, Message-ID `<20260613062037.84593-1-enzo.adriano.code@gmail.com>`
- Patchew checked views: H204/H200 text not visible yet
- lore from this environment: anti-bot HTML, visibility unconfirmed

## Next Action

Do not send the H208 candidate now. Keep it ready for either:

- a maintainer request for exact patch text;
- a later reviewed RFC/RFT send after H204 is confirmed indexed or stale enough
  to justify a follow-up; or
- folding into a next A733 CCU revision if maintainers prefer that route.
