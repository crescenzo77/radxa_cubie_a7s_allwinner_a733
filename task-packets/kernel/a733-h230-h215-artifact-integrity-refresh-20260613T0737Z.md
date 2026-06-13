# A733-SDMMC-H230: H215 Artifact Integrity Refresh

Captured: 2026-06-13T07:37:08Z

## Purpose

Refresh integrity evidence for the exact H210 patch bundle that was sent as
H215, so future maintainer-response, resend-gate, or v2 work can rely on stable
artifact identity.

This packet is documentation only. It is not a resend approval, not a new mail
draft, not a source change, and not a hardware action.

## Bundle Identity

- Bundle: H210 normalized RFC/RFT send candidate
- Sent as: H215 RFC/RFT series
- Base: `d9aa2e15caae`
- Exact hardware-proven source: `de486cb24c361a86cba26738f24332df780872b0`
- Reply target: `<20260310-a733-clk-v1-7-36b4e9b24457@pigmoral.tech>`

## Recomputed SHA256

```text
f08381cdca45431e24af2a2e172506239a53852b3bacf037e21a0f8800c5e3be  0000-cover-letter.patch
6cc2b2a3fd5d26b8c36340b2b83369a8c3455af5898756acedc6f29c2e25f01f  0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
865ef2eaaf01b213a80158fae2a8b4338cdf89e9ae90444d37b9080c06d804c7  0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
3f28b742b4e66539d8a5f5cd055103a1cf875b89779a9eb61dd993c2bcb79f6c  0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
70b70b56f834fdc92b51f52988ac356514c21e6b840031db6ccadb7df716d33f  0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

These hashes match the H210 recorded hashes.

## Gate Refresh

- Public hygiene gate on H210 bundle: PASS
- Trailer gate on H210 patches 1-4: PASS

## Apply and Source-Equivalence Refresh

On the build host, a temporary detached worktree was created from the H215 base
`d9aa2e15caae`, then H210 patches 1-4 were applied with `git am --3way`.

Result:

- Apply result: PASS
- Recreated applied head: `3b73eb78e3f8773bd0a4cec2d74bcfc46701a091`
- `git diff --check d9aa2e15caae..HEAD`: PASS
- Source equivalence against exact H200 for
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`: PASS
- Temporary worktree status after check: clean

Applied commits:

```text
05759f2b422c clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
80acdd5131e1 clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
aba6f62eaf25 clk: sunxi-ng: a733: commit the boot-programmed NSI clock state
3b73eb78e3f8 clk: sunxi-ng: a733: keep GIC and CPU peri clocks critical
```

## Interpretation

The current H210 artifact bundle on disk still matches its recorded hashes,
passes public/trailer gates, applies from the recorded base, and recreates the
same touched-driver source as the exact H200 hardware-proven commit.

This complements H223 reproducibility and provides a fresh artifact-integrity
checkpoint after H225-H229.

## Next Action

Continue to wait for H215 public indexing or maintainer response. Do not send a
duplicate follow-up unless H219's resend/alternate-action gate is satisfied.
