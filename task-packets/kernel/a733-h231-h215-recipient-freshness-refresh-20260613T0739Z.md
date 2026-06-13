# A733-SDMMC-H231: H215 Recipient Freshness Refresh

Captured: 2026-06-13T07:39:14Z

## Purpose

Refresh recipient evidence for the H210 patch bundle that was sent as H215, so
any future resend-gate, v2, or maintainer-response work starts from the current
kernel-native recipient set.

This packet is documentation only. It is not a resend approval, not a new mail
draft, not a source change, and not a hardware action.

## Candidate

- Bundle: H210 normalized RFC/RFT send candidate
- Sent as: H215 RFC/RFT series
- Source patches checked: `0001` through `0004`
- Exact hardware-proven source: `de486cb24c361a86cba26738f24332df780872b0`

## Method

Ran kernel-native `scripts/get_maintainer.pl` from the exact H200 source tree
against the H210 source patches:

```sh
perl scripts/get_maintainer.pl --no-rolestats --no-git-fallback \
  000[1-4]-*.patch
```

The H200 source tree status was clean before the check.

## Result

Fresh normalized unique recipient/list set:

```text
Brian Masney <bmasney@redhat.com>
Chen-Yu Tsai <wens@kernel.org>
Jernej Skrabec <jernej.skrabec@gmail.com>
Michael Turquette <mturquette@baylibre.com>
Samuel Holland <samuel@sholland.org>
Stephen Boyd <sboyd@kernel.org>
linux-arm-kernel@lists.infradead.org
linux-clk@vger.kernel.org
linux-kernel@vger.kernel.org
linux-sunxi@lists.linux.dev
```

Normalized recipient-list SHA256:

```text
c15e6c78b7a1c586864a1fe65598088a793422632ec82d5ee71b21d51194cc90
```

## Comparison to H214

The fresh `get_maintainer.pl` set matches H214. The Brian Masney correction
remains required, and no additional kernel-native recipient appeared in this
refresh.

## Decision

H214's recipient correction remains current for H215/H210. If H219's resend
gate is ever satisfied, re-run recipient discovery again immediately before
send, then use at least this set plus any required public-thread recipients.

## Next Action

Continue waiting for H215 public indexing or maintainer response. Do not send a
duplicate follow-up unless H219's resend/alternate-action gate is satisfied.
