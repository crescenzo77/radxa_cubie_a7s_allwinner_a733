# A733 H200: H199 Maintainer-Polish Readiness

Date: 2026-06-13T06:04:00Z

## Summary

H200 is the maintainer-polished version of the H199 clean CCU/NSI series. It is
source-equivalent to H199 for `drivers/clk/sunxi-ng/ccu-sun60i-a733.c`, but the
commit messages were cleaned so generated patches carry only standard
`Signed-off-by` trailers. At the time this note was created, H199 remained the
exact hardware-proven hash and H200 was the cleaner review/send candidate if the
project decided to post patch text. H201 later proved H200 directly on Cubie3.

## Candidate

Worktree:

```text
/srv/projects/kernel-work/final/a733-ccu-nsi-v4-h199-maintainer-polish
```

Branch:

```text
codex/a733-ccu-nsi-v4-h199-maintainer-polish
```

Head:

```text
de486cb24c361a86cba26738f24332df780872b0
```

Base:

```text
d9aa2e15caae arm64: dts: allwinner: add Radxa Cubie A7S
```

## Patch series

Mac copy:

```text
/Users/enzo/projects/homelab/task-packets/kernel/a733-h200-h199-maintainer-polish-series/
```

Strix copy:

```text
/srv/projects/kernel-work/outgoing/a733-h200-h199-maintainer-polish-de486cb24c36-20260613T060250Z
```

Patches:

```text
0001-clk-sunxi-ng-a733-keep-the-CPUS-AHB-bridge-clock-cri.patch
0002-clk-sunxi-ng-a733-keep-storage-and-NSI-fabric-clocks.patch
0003-clk-sunxi-ng-a733-commit-the-boot-programmed-NSI-clo.patch
0004-clk-sunxi-ng-a733-keep-GIC-and-CPU-peri-clocks-criti.patch
```

## Validation

- H200 final `drivers/clk/sunxi-ng/ccu-sun60i-a733.c` is source-equivalent to
  H199 for that file.
- H200 worktree status was clean during export.
- `git diff --check d9aa2e15caae..HEAD`: pass.
- `scripts/checkpatch.pl --strict` per generated patch: pass, 0 errors and 0
  warnings for all four patches.
- `tools/validate/trailer_gate.py` on the four Mac patch files: pass.
- `tools/validate/public_hygiene_gate.py --json` on a temp directory containing
  only the four patch files: pass, 4 files scanned, 0 matches.

The full artifact directory is not public-sendable as-is because metadata files
inside it intentionally include local paths and branch names. That does not
apply to the four patch files after copying them into a patches-only staging
directory.

## Relationship to H199

H199:

```text
c5b942c818a3c5027c7e2577404041569efb9e98
```

was the hardware-proven hash at the time this note was created. Its direct Cubie3 boot proof reached SDMMC0
enumeration, read-only root mount, and `/bin/sh`, then Cubie3 was restored to
vendor kernel `5.15.147-21-a733`.

H200:

```text
de486cb24c361a86cba26738f24332df780872b0
```

was later booted as an exact commit hash in H201. The H201 direct Cubie3 proof
reached SDMMC0 enumeration, read-only root mount, and `/bin/sh`, then Cubie3 was
restored to vendor kernel `5.15.147-21-a733`.

## Upstream context

The A733 CCU/PRCM support is still represented publicly by Junhui Liu's RFC
series:

```text
https://patchew.org/linux/20260310-a733-clk-v1-0-36b4e9b24457%40pigmoral.tech/
```

H200 modifies gates added by RFC patch 7:

```text
https://patchew.org/linux/20260310-a733-clk-v1-0-36b4e9b24457%40pigmoral.tech/20260310-a733-clk-v1-7-36b4e9b24457%40pigmoral.tech/
```

Because the underlying CCU driver is still part of an in-flight external RFC,
H200 should not be sent as an ordinary standalone upstream series without an
explicit decision. The safer external action is to reply on the existing CCU RFC
thread with the H199/H200 result, offer the polished local patch stack, and ask
maintainers whether they prefer critical-clock annotations, a deeper fabric
model, or a different split.

## Next decision

Safe now:

- Keep H199 as the evidence-bearing hardware proof.
- Use H200 as the clean exact-hash hardware-proven patch-text reference for
  review discussion.
- Refresh lore/b4 indexing for the already-sent H190 feedback and watch for
  maintainer response.

Needs approval:

- Send H200 patch text publicly.
- Send another follow-up on the CCU RFC thread.
