# A733 H161 CCU RFC thread recheck

Captured: 2026-06-13T03:04Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Recheck the public A733 CCU/PRCM RFC thread metadata before any maintainer-facing reply draft is considered sendable.

This note is documentation only. It does not approve sending mail, publishing patches, kernel commits, hardware runs, service changes, or model-routing changes.

## Tooling

- `b4` is not installed or not available in the current Mac terminal environment.
- `lore.kernel.org` raw/search endpoints returned `403 Forbidden` from this environment.
- `patchew.org` public series page and mbox endpoint were reachable with `curl`.

## Public thread checked

- Series page: `https://patchew.org/linux/20260310-a733-clk-v1-0-36b4e9b24457%40pigmoral.tech/`
- Series title: `[PATCH RFC 0/8] clk: sunxi-ng: Add support for Allwinner A733 CCU and PRCM`
- Author: `Junhui Liu <junhui.liu@pigmoral.tech>`
- Posted: 2026-03-10
- Cover message-id: `<20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech>`
- Series mbox endpoint: `https://patchew.org/linux/20260310-a733-clk-v1-0-36b4e9b24457%40pigmoral.tech/mbox`

## Relevant patches

The live mbox includes patches 1/8 through 8/8. The local evidence touches patch 7 most directly:

- Patch 5/8: `[PATCH RFC 5/8] clk: sunxi-ng: a733: Add bus clocks support`
  - Message-id: `<20260310-a733-clk-v1-5-36b4e9b24457@pigmoral.tech>`
  - Hits in mbox scan: `nsi_clk`, `0x580`
- Patch 6/8: `[PATCH RFC 6/8] clk: sunxi-ng: a733: Add mod clocks support`
  - Message-id: `<20260310-a733-clk-v1-6-36b4e9b24457@pigmoral.tech>`
  - Hits in mbox scan: `nsi_clk`
- Patch 7/8: `[PATCH RFC 7/8] clk: sunxi-ng: a733: Add bus clock gates`
  - Message-id: `<20260310-a733-clk-v1-7-36b4e9b24457@pigmoral.tech>`
  - Hits in mbox scan: `nsi_clk`, `bus_nsi`, `ahb_cpus`, `ahb_store`, `mbus_store`, `mbus_msi_lite0`, `0x580`, `0x5c0`, `0x5e0`

Recommendation: aim the maintainer feedback at patch 7/8 rather than only the cover letter, because patch 7 carries the clock definitions that need critical flags and NSI update-bit discussion. The body can still mention the broader series.

## Archived recipients from patch 7/8

From:

- `Junhui Liu <junhui.liu@pigmoral.tech>`

To:

- `Michael Turquette <mturquette@baylibre.com>`
- `Stephen Boyd <sboyd@kernel.org>`
- `Rob Herring <robh@kernel.org>`
- `Krzysztof Kozlowski <krzk+dt@kernel.org>`
- `Conor Dooley <conor+dt@kernel.org>`
- `Chen-Yu Tsai <wens@kernel.org>`
- `Jernej Skrabec <jernej.skrabec@gmail.com>`
- `Samuel Holland <samuel@sholland.org>`
- `Philipp Zabel <p.zabel@pengutronix.de>`
- `Junhui Liu <junhui.liu@pigmoral.tech>`
- `Paul Walmsley <pjw@kernel.org>`
- `Palmer Dabbelt <palmer@dabbelt.com>`
- `Albert Ou <aou@eecs.berkeley.edu>`
- `Alexandre Ghiti <alex@ghiti.fr>`
- `Richard Cochran <richardcochran@gmail.com>`

Cc:

- `linux-clk@vger.kernel.org`
- `devicetree@vger.kernel.org`
- `linux-arm-kernel@lists.infradead.org`
- `linux-sunxi@lists.linux.dev`
- `linux-kernel@vger.kernel.org`
- `linux-riscv@lists.infradead.org`
- `netdev@vger.kernel.org`

## Draft impact

H160 has correct technical content but should not be sent as-is because:

- it says the reply target is the cover letter;
- its recipient list is narrower than the archived patch 7 recipients;
- live recipient recheck was not yet recorded when it was written.

Prepare a v3 draft targeting patch 7/8 with the archived recipient set before any human send review.

## Guardrails

- Do not send mail from this note.
- Do not rely on H160 as send-ready.
- If `b4` becomes available later, re-run a final b4/lore recipient check before any actual send.
