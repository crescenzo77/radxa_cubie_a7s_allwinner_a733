# A733 H256 - DTS Final Gate Refresh

Captured UTC: 2026-06-13T09:16Z

## Purpose

Refresh the non-CCU A733/Cubie A7S DTS submission track after the H200-H255
CCU/SDMMC work, so the broader mainline patch project keeps a current record of
the final DTS branch and public export state.

This packet is documentation only. It is not a GitHub push, not a `b4 send`,
not a `b4 send --reflect`, not a source change, and not a hardware, service,
cron, or model-routing action.

## Final DTS Branch

The final DTS branch still exists on the build host:

```text
branch: local-prefix/final/a733-dts-v1
head:   1d2642221795d611d607b153c119218e496856a8
base:   1626ce5bc85bd3faaa92877d1b65c924d86a9546
```

Branch status was clean.

Recent commit order:

```text
1d2642221795 arm64: dts: allwinner: add Radxa Cubie A7S
fa78896900ad arm64: dts: allwinner: add Allwinner A733 SoC
b2523cc96c17 dt-bindings: mmc: add Allwinner A733 compatible
3f6a96f1ba79 dt-bindings: arm: sunxi: add Radxa Cubie A7S
cf9cd8d39fda arm64: dts: allwinner: add A733/Cubie A7S DTS support
1626ce5bc85b MAINTAINERS: add Allwinner sun60i pattern
```

The cover commit remains the start commit for the b4 prep-managed series.

## Final Gate Refresh

Reran the no-send final gate:

```text
scripts/kernel-b4-final-gate --repo FINAL_DTS_WORKTREE
```

Observed b4 metadata:

```text
cover-subject: arm64: dts: allwinner: add A733/Cubie A7S DTS support
base-commit: 1626ce5bc85bd3faaa92877d1b65c924d86a9546
start-commit: cf9cd8d39fdab0ba4a762c7cefb1ed36027829fd
end-commit: 1d2642221795d611d607b153c119218e496856a8
revision: 1
cover-strategy: commit
needs-editing: False
needs-recipients: False
has-prerequisites: True
needs-auto-to-cc: False
needs-checking: False
needs-checking-deps: False
preflight-checks-failing: False
```

Gate result:

```text
kernel-b4-final-gate: PASS
```

## Public Export Repo Snapshot

The Mac public/export coordination repo exists at the expected project path and
is clean:

```text
branch: main
head:   db53521a63f9cc6a4fc684a927b3bac78173b859
status: ahead of public/main by 215
```

Recent top commit:

```text
db53521 patches: align A733 DTS export with in-flight RFC bindings
```

The older `a733-public-expected-head.json` file still names `b54dade62c44`.
That file is stale relative to the current clean Mac export repo head
`db53521a63f9`.

The build-host public-export working copy is not authoritative for this refresh:
it has unrelated dirty/staged local workflow files. Do not use that dirty copy
as the public DTS send source.

## Interpretation

The DTS submission track remains machine-ready for human reflect review under
the H142/H141 model:

- machine gates through `kernel-b4-final-gate` still pass;
- no real send has been run;
- no reflect send was run in this refresh;
- the public/export Mac repo has a newer clean head than the stale expected-head
  record;
- the build-host dirty public-export copy should be ignored for send authority.

This does not change H215/H219. The CCU/SDMMC follow-up remains separately
controlled by the H219 resend/alternate-action gate.
