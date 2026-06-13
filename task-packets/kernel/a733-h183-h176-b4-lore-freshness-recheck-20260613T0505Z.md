# A733 H183 H176 b4/lore freshness recheck

Captured: 2026-06-13T05:05Z

## Purpose

Refresh the mailing-list context for the H176 A733 CCU RFC feedback
send-candidate after the H182 technical claim audit, without sending mail or
changing kernel source.

This note is documentation only. It does not approve sending mail, publishing
patches, kernel commits, hardware runs, service changes, cron changes, or
model-routing changes.

## Read-only command

On the build host, using the existing `b4` environment:

```sh
b4 mbox \
  -o <temporary-output-directory> \
  20260310-a733-clk-v1-7-36b4e9b24457@pigmoral.tech
```

Result:

- lore lookup succeeded;
- `b4 mbox` fetched the patch-7 thread;
- b4 reported 15 messages in the thread;
- no mail was sent;
- no kernel worktree was modified.

## Refreshed patch-7 metadata

Patch subject:

```text
[PATCH RFC 7/8] clk: sunxi-ng: a733: Add bus clock gates
```

Patch message-id:

```text
<20260310-a733-clk-v1-7-36b4e9b24457@pigmoral.tech>
```

Patch sender:

```text
Junhui Liu <junhui.liu@pigmoral.tech>
```

Patch 7 still has 15 `To` recipients:

- Michael Turquette <mturquette@baylibre.com>
- Stephen Boyd <sboyd@kernel.org>
- Rob Herring <robh@kernel.org>
- Krzysztof Kozlowski <krzk+dt@kernel.org>
- Conor Dooley <conor+dt@kernel.org>
- Chen-Yu Tsai <wens@kernel.org>
- Jernej Skrabec <jernej.skrabec@gmail.com>
- Samuel Holland <samuel@sholland.org>
- Philipp Zabel <p.zabel@pengutronix.de>
- Junhui Liu <junhui.liu@pigmoral.tech>
- Paul Walmsley <pjw@kernel.org>
- Palmer Dabbelt <palmer@dabbelt.com>
- Albert Ou <aou@eecs.berkeley.edu>
- Alexandre Ghiti <alex@ghiti.fr>
- Richard Cochran <richardcochran@gmail.com>

Patch 7 still has 7 `Cc` recipients:

- linux-clk@vger.kernel.org
- devicetree@vger.kernel.org
- linux-arm-kernel@lists.infradead.org
- linux-sunxi@lists.linux.dev
- linux-kernel@vger.kernel.org
- linux-riscv@lists.infradead.org
- netdev@vger.kernel.org

## Thread comparison

The refreshed mbox still contains 15 messages. The only patch-7 reply in this
thread remains:

```text
From: Andre Przywara <andre.przywara@arm.com>
Subject: Re: [PATCH RFC 7/8] clk: sunxi-ng: a733: Add bus clock gates
Date: Thu, 16 Apr 2026 00:14:46 +0200
Message-ID: <646385ea-228b-46be-a199-02134cf76ed0@arm.com>
```

A targeted check of that reply found expected hits in quoted patch context for
clock names and registers, but no direct conflict with H176's runtime-feedback
claims:

- `ahb-cpus` CPUS/R-domain access path;
- storage and NSI fabric keepalive evidence;
- NSI update-bit interpretation;
- the question of critical clocks versus explicit modelling.

## H176 status

H176 remains aligned with the refreshed patch-7 thread:

- same patch-7 subject, with a `Re:` prefix;
- same patch-7 `In-Reply-To`;
- same cover and patch-7 `References`;
- same 15 `To` recipients;
- same 7 `Cc` recipients.

H176 remains unsent and is not approved to send.

## Remaining gates

- final human review of the outgoing mail;
- explicit operator approval to send;
- decision whether to send H176 now or first run the approval-gated H154
  no-`mbus-msi-lite0` hardware proof.

## Guardrails

- Do not send H176 without explicit operator approval.
- Do not treat this recheck as approval for H154 hardware proof.
- Do not create kernel-source commits or generated patch series from this note.
