# Kernel Checkout Quarantine - 2026-06-06

Scope: private workflow inventory. This file records a local checkout state
that must not be used as a maintainer-facing source branch until the dirty
changes are reviewed by a human operator.

Last refreshed: 2026-06-13 by read-only local inspection.

## Quarantined Checkout

- Path: `/Users/enzo/projects/linux-a733`
- Current branch: `candidate/a733-platform-clean-v6`
- Current HEAD: `b1f20d455a600d33999cf893fdf0df8fb2ace538`
- Current HEAD summary: `fixup! arm64: dts: allwinner: drop A733 vendor pinmux properties`
- Previous recorded branch: `candidate/a733-platform-clean-v3`
- Previous recorded HEAD: `38427a8bcfa7fab1bc27f066bdef59cd1949f3ae`
- Previous dirty diff SHA-256:
  `dafea07695d283ddd025acce7aa55788cd4e57276447dc237de20555cfac3022`

## Dirty File Scope

The remaining uncommitted files are not part of the A733/Cubie bring-up slice:

- `include/uapi/linux/netfilter/xt_CONNMARK.h`
- `include/uapi/linux/netfilter/xt_DSCP.h`
- `include/uapi/linux/netfilter/xt_MARK.h`
- `include/uapi/linux/netfilter/xt_RATEEST.h`
- `include/uapi/linux/netfilter/xt_TCPMSS.h`
- `include/uapi/linux/netfilter_ipv4/ipt_ECN.h`
- `include/uapi/linux/netfilter_ipv4/ipt_TTL.h`
- `include/uapi/linux/netfilter_ipv6/ip6t_HL.h`
- `net/netfilter/xt_DSCP.c`
- `net/netfilter/xt_HL.c`
- `net/netfilter/xt_RATEEST.c`
- `net/netfilter/xt_TCPMSS.c`
- `tools/memory-model/litmus-tests/Z6.0+pooncelock+poonceLock+pombonce.litmus`

This dirty scope is still present as of the 2026-06-13 refresh. Treat it as
known local checkout noise, not as A733 patch material. Do not stage, stash, reset, or clean
these files as part of A733 kernel work.

## Clean Sparse Checkout

- Path: `/Users/enzo/projects/linux-a733-sparse`
- Current branch: `candidate/a733-platform-clean-v4`
- Current HEAD: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- Current HEAD summary: `MAINTAINERS: add Allwinner sun60i pattern`
- Current status: clean by `git status --porcelain=v1`

## Workflow Rule

Use `/Users/enzo/projects/linux-a733-sparse` on
`candidate/a733-platform-clean-v4` as the clean A733 candidate checkout for
clean validation, review, and local documentation while the dirty file scope
above is present. Do not export, validate, or push patches from
`/Users/enzo/projects/linux-a733` while the dirty file scope above is present.

If any of these dirty changes are later needed, first move them to a separate
review branch with a non-A733 title and run the normal proof workflow for that
separate topic.

Read-only source searches may still inspect `/Users/enzo/projects/linux-a733`
when they need files absent from the sparse checkout, but any patch/export
claim must record why the quarantined tree was inspected and must not treat its
dirty status as an A733 change.
