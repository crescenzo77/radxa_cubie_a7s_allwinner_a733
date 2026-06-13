# A733-SDMMC-H245: Common Update-Bit V2 Series Option

Captured: 2026-06-13T08:42:00Z

## Purpose

Convert the H244 "delta from H200" common update-bit option into the actual
series shape that would be needed for a maintainer-directed v2: four patches
from the original H215 base, with common update-bit handling as patch 3 instead
of the A733-specific NSI pulse.

This packet is local prep only. It is not a resend approval, not a new public
thread, not a replacement for H215, not a hardware action, and not a service,
cron, mail-routing, or model-routing change.

## Artifact

Local artifact directory:

```text
task-packets/kernel/a733-h245-common-update-bit-v2-series-option/
```

Files:

```text
0000-cover-letter.patch
0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
0003-clk-sunxi-ng-commit-update-bit-clocks-during-registr.patch
0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
checkpatch-strict.txt
series-summary.txt
```

Base:

```text
d9aa2e15caae
```

Temporary series head:

```text
fb85982739f16aed406dffec93798546bd904a9b
```

Commit order:

```text
d417b59851a9 clk: sunxi-ng: a733: keep the CPUS AHB bridge clock critical
73d8f74a606e clk: sunxi-ng: a733: keep storage and NSI fabric clocks critical
2829d0eb397c clk: sunxi-ng: commit update-bit clocks during registration
fb85982739f1 clk: sunxi-ng: a733: keep GIC and CPU peri clocks critical
```

## Difference From H244

H244 is a useful single-patch delta from exact H200. It removes the A733 NSI
probe-time pulse and adds common registration handling.

H245 is the real v2-series option from the original H215 base:

- patches 1 and 2 match the H210/H215 structure;
- patch 3 adds common update-bit handling in `ccu_common.c`;
- patch 3 does not remove an A733-specific NSI pulse, because that pulse is not
  introduced in this v2 shape;
- patch 4 keeps the H210/H215 GIC and CPU-peripheral critical-clock change.

Compared with H200's touched A733 CCU source, the expected source delta is only
that the local `SUN60I_A733_NSI_REG` define and the A733-specific NSI update-bit
write are absent; the common helper owns that behavior instead.

## Validation

Series generation and patch checks:

```text
git diff --check d9aa2e15caae..HEAD: PASS
scripts/checkpatch.pl --strict --show-types patches 1-4: PASS
git am --3way patches 1-4 from d9aa2e15caae: PASS
applied series diffcheck: PASS
```

Focused build/static checks after applying the generated patches from the
recorded base:

```text
arm64 GCC W=1 ccu_common.o: PASS
arm64 GCC W=1 ccu-sun55i-a523.o: PASS
arm64 GCC W=1 ccu-sun60i-a733.o: PASS
arm64 sparse C=1 ccu_common.o: PASS
arm64 sparse C=1 ccu-sun55i-a523.o: PASS
arm64 sparse C=1 ccu-sun60i-a733.o: PASS
sparse version: 0.6.4
diagnostic grep: no warning/error/sparse lines
```

Artifact hygiene:

```text
public_hygiene_gate.py on the H245 artifact directory: PASS
```

Temporary worktrees were removed after the checks. The exact H200 source tree
remained clean.

## Interpretation

H245 is the first locally prepared common-update-bit option that has the right
series shape for a maintainer-directed v2. It is more directly usable than H244
if reviewers ask for common handling.

It still should not replace H215 by default. H215 remains the submitted,
exact-hardware-proven narrow A733 expression. The H245 option is broader because
it commits boot-programmed state for every `CCU_FEATURE_UPDATE_BIT` clock in a
registered CCU descriptor, including non-A733 clocks.

## Next Action

Keep H215 as the current submitted posture. If maintainer feedback asks for
common update-bit handling, use H245 as the starting artifact for a real v2,
then rerun full validation including A733 hardware proof before any resend or
new submission.
