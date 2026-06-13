# A733-SDMMC-H223: H210 Post-Send Reproducibility Refresh

Captured: 2026-06-13T07:19:14Z

## Purpose

Refresh the reproducibility evidence for the H210/H215 patch artifacts after
H215 was sent and after the post-send delivery/indexing records H216-H222.

This packet does not send mail, change kernel source, or run hardware.

## Inputs

- Patch bundle: H210 normalized RFC/RFT candidate bundle
- Kernel source repository: H200 maintainer-polish worktree
- Apply base: `d9aa2e15caae5085b51a28529fc0c35d189df543`
- Exact H200 tested commit: `de486cb24c361a86cba26738f24332df780872b0`

## Check

On the build host, a temporary detached worktree was created from base
`d9aa2e15caae`. The four H210 source patches were applied with:

```text
git am --3way 000[1-4]-*.patch
```

The cover letter was not applied, as expected.

## Result

- `git am --3way`: PASS
- recreated apply head: `b1f28861fa29e774ffa29f8bfe75aa77de0cf584`
- temporary worktree status after apply: clean
- `git diff --check d9aa2e15caae..HEAD`: PASS
- source equivalence against H200 for
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`: PASS
- temporary worktree cleanup: PASS

Applied patches:

```text
Applying: clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
Applying: clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
Applying: clk: sunxi-ng: a733: commit the boot-programmed NSI clock state
Applying: clk: sunxi-ng: a733: keep GIC and CPU peri clocks critical
```

Patch hashes:

```text
f08381cdca45431e24af2a2e172506239a53852b3bacf037e21a0f8800c5e3be  0000-cover-letter.patch
6cc2b2a3fd5d26b8c36340b2b83369a8c3455af5898756acedc6f29c2e25f01f  0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
865ef2eaaf01b213a80158fae2a8b4338cdf89e9ae90444d37b9080c06d804c7  0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
3f28b742b4e66539d8a5f5cd055103a1cf875b89779a9eb61dd993c2bcb79f6c  0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
70b70b56f834fdc92b51f52988ac356514c21e6b840031db6ccadb7df716d33f  0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

## Interpretation

The sent H210/H215 source patch artifacts remain reproducible from the recorded
base and still recreate the exact H200 source state for the A733 CCU file.

This strengthens the H219 resend/alternate-action gate: if a resend or v2 is
ever required, the existing H210 artifacts remain a valid source-equivalent
starting point. It does not change the current wait/monitor posture.
