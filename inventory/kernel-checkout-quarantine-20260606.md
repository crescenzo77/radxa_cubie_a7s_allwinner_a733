# Kernel Checkout Quarantine - 2026-06-06

Scope: private workflow inventory. This file records a local checkout state
that must not be used as a maintainer-facing source branch until the dirty
changes are reviewed by a human operator.

## Quarantined Checkout

- Path: `/Users/enzo/projects/linux-a733`
- Branch: `candidate/a733-platform-clean-v3`
- HEAD: `38427a8bcfa7fab1bc27f066bdef59cd1949f3ae`
- Dirty diff SHA-256: `dafea07695d283ddd025acce7aa55788cd4e57276447dc237de20555cfac3022`

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

## Workflow Rule

Use `/Users/enzo/projects/linux-a733-sparse` on
`candidate/a733-platform-clean-v4` as the clean A733 candidate checkout for
validation, review, and public documentation. Do not export, validate, or push
patches from `/Users/enzo/projects/linux-a733` while the dirty file scope above
is present.

If any of these dirty changes are later needed, first move them to a separate
review branch with a non-A733 title and run the normal proof workflow for that
separate topic.
