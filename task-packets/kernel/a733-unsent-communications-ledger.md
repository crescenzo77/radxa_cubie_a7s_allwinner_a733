# A733 Unsent Communications Ledger

Status: active blackout ledger
Updated: 2026-06-13

This document tracks communications that would normally be sent during
upstream Linux kernel development for Radxa Cubie A7S / Allwinner A733, but
are intentionally withheld while the project is in local-work-only mode.

Do not send any item from this ledger automatically. Each item must be
revalidated against current code, current public threads, current maintainer
feedback, and operator approval before it can leave the local workspace.

## Status Values

- `draft-needed`: the communication is known but no draft exists yet.
- `drafted-not-reviewed`: a draft exists but has not passed final review.
- `ready-held`: the draft is locally ready, but communication is paused.
- `question-held`: a bounded cycle hit maintainer-dependent uncertainty and
  converted it into a precise held question.
- `obsolete-unsent`: no longer appropriate to send.
- `sent-before-blackout`: historical public communication that was already
  sent before the current local-only gate; retain as a no-resend record.

## Ledger

| ID | Date | Type | Target | Status | Draft | Send blocker |
|---|---:|---|---|---|---|---|
| A733-COMM-001 | 2026-06-13 | review acknowledgement | Jernej's v1 DTS patch 4/4 feedback | `sent-before-blackout` | Gmail reply in lore | Historical sent item; retain only as history and do not resend |
| A733-COMM-002 | 2026-06-13 | v2 cover letter | A733/Cubie A7S DTS v2 | `draft-needed` | TBD | Do not send v2 until local DTS cleanup, clock prerequisite status, validation, and operator approval are refreshed |
| A733-COMM-003 | 2026-06-13 | changelog note | A733/Cubie A7S DTS v2 | `draft-needed` | TBD | Same blocker as A733-COMM-002 |
| A733-COMM-004 | 2026-06-13 | prerequisite status note | A733 RTC, CCU/PRCM, and pinctrl prerequisite threads | `draft-needed` | TBD | No communication while blackout is active; also requires fresh public-thread recheck |
| A733-COMM-005 | 2026-06-13 | potential Tested-by | prerequisite RTC/CCU/pinctrl series | `draft-needed` | TBD | Only valid after exact source, exact hardware, and exact proof are recorded |
| A733-COMM-006 | 2026-06-13 | potential RFC/RFT cover | SDMMC0 IDMAC root-cause or diagnostic series | `draft-needed` | TBD | Requires source-backed root cause, maintainer-shaped patch, reproducible proof, and approval |
| A733-COMM-007 | 2026-06-13 | potential RFC/RFT cover | Ethernet/GMAC support | `draft-needed` | TBD | Requires GMAC wrapper, clocks, resets, MDIO, PHY reset/power, and runtime link proof |
| A733-COMM-008 | 2026-06-13 | potential RFC/RFT cover | PCIe/NVMe support | `draft-needed` | TBD | Requires controller/PHY model, binding, link proof, NVMe proof, and validation |
| A733-COMM-009 | 2026-06-13 | potential RFC/RFT cover | USB/USB-C support | `draft-needed` | TBD | Requires controller/PHY/role-switch evidence and host/device proof |
| A733-COMM-010 | 2026-06-13 | potential RFC/RFT cover | Wi-Fi/Bluetooth enablement | `draft-needed` | TBD | Requires exact module, mainline driver/firmware path, power sequencing, and runtime proof |
| A733-COMM-011 | 2026-06-13 | potential RFC/RFT cover | display/DP/media work | `draft-needed` | TBD | Requires split subsystem patches and proof for each block |
| A733-COMM-012 | 2026-06-13 | potential RFC/RFT cover | NPU or RISC-V MCU work | `draft-needed` | TBD | Requires a credible mainline subsystem path and firmware/userspace ABI story |
| A733-COMM-013 | 2026-06-13 | review feedback reply | A733 CCU RFC patch 7 thread | `sent-before-blackout` | `task-packets/kernel/a733-h190-ccu-rfc-feedback-sent-20260613T0421Z.md` | Historical sent item; retain only as history and do not resend |
| A733-COMM-014 | 2026-06-13 | follow-up reply | A733 CCU RFC patch 7 thread | `sent-before-blackout` | `task-packets/kernel/a733-h204-h203-ccu-rfc-follow-up-sent-20260613T0620Z.md` | Historical sent item; retain only as history and do not resend |
| A733-COMM-015 | 2026-06-13 | RFC/RFT series | A733 CCU/SDMMC0 clock keepalive experiment | `sent-before-blackout` | `task-packets/kernel/a733-h215-h210-rfc-rft-series-sent-20260613T0651Z.md` | Historical sent item; retain only as history and do not resend |
| A733-COMM-016 | 2026-06-13 | b4 patch series | Radxa Cubie A7S DTS v1 | `sent-before-blackout` | `task-packets/kernel/a733-h265-dts-v1-public-sent-indexed-20260613T0950Z.md` | Historical sent item; retain only as history and do not resend |

When CLASSIFY-GATE diverts work here, the entry should be written as a
question, not as a half-built patch plan. Include the smallest answerable
question and the evidence that would let a maintainer answer in one reply.

## Historical Sent Items

### A733-COMM-001

Type: review acknowledgement.

Public message:

```text
<CAHWUu5HKy6g5aFbrriBz1cC7dQkss7x5pTBQ1qXe2NA=H2aejw@mail.gmail.com>
```

Summary:

- acknowledged Jernej's request to move UART0 pin definition into the main
  A733 DTSI
- acknowledged that DT is early until clock prerequisites are in a better
  state
- promised not to rush v2

This item was sent before the current no-communication ledger was established.
It must not be resent.

### A733-COMM-013

Type: review feedback reply.

Public message:

```text
<20260613042105.18962-1-enzo.adriano.code@gmail.com>
```

Source record:

```text
task-packets/kernel/a733-h190-ccu-rfc-feedback-sent-20260613T0421Z.md
```

Summary:

- sent H189 maintainer-feedback reply on the A733 CCU RFC patch 7 thread
- local `git send-email` result was recorded as `Result: OK`
- H154 `no-mbus-msi-lite0` source shape remained rejected after Cubie3 proof
  failed before SDMMC0 initialization

This item was sent before the current local-only cycle. It must not be resent.

### A733-COMM-014

Type: follow-up reply.

Public message:

```text
<20260613062037.84593-1-enzo.adriano.code@gmail.com>
```

Source record:

```text
task-packets/kernel/a733-h204-h203-ccu-rfc-follow-up-sent-20260613T0620Z.md
```

Summary:

- sent H203 follow-up on the existing A733 CCU RFC patch 7 thread
- local `git send-email` result was recorded as `Result: OK`
- follow-up referenced H200/H201 proof chain and recommended waiting for
  indexing or maintainer response before more mail

This item was sent before the current local-only cycle. It must not be resent.

### A733-COMM-015

Type: RFC/RFT series.

Public messages:

```text
<20260613065059.12041-1-enzo.adriano.code@gmail.com>
<20260613065059.12041-2-enzo.adriano.code@gmail.com>
<20260613065059.12041-3-enzo.adriano.code@gmail.com>
<20260613065059.12041-4-enzo.adriano.code@gmail.com>
<20260613065059.12041-5-enzo.adriano.code@gmail.com>
```

Source record:

```text
task-packets/kernel/a733-h215-h210-rfc-rft-series-sent-20260613T0651Z.md
```

Summary:

- sent H210 as a five-message RFC/RFT series on the existing A733 CCU RFC
  patch 7 thread
- local `git send-email` returned five `Result: OK` messages
- later local records noted that public indexing remained unconfirmed in
  checked views

This item was sent before the current local-only cycle. It must not be resent.

### A733-COMM-016

Type: b4 patch series.

Public message:

```text
<20260613-a733-dts-v1-public-ready-v1-0-7787c94681db@gmail.com>
```

Public archive:

```text
https://patch.msgid.link/20260613-a733-dts-v1-public-ready-v1-0-7787c94681db@gmail.com
```

Source record:

```text
task-packets/kernel/a733-h265-dts-v1-public-sent-indexed-20260613T0950Z.md
```

Summary:

- sent Radxa Cubie A7S DTS v1 through `b4 send`
- local record says `b4` sent five messages and tagged
  `sent/20260613-a733-dts-v1-public-ready-8cbb37133b64-v1`
- lore visibility by cover Message-ID was recorded as present

This item was sent and indexed before the current local-only cycle. It must
not be resent.

## Draft Template

Use this shape for new held communications:

```text
### A733-COMM-NNN

Date:
Type:
Target thread/subsystem:
Intended recipients:
Trigger:
Precise question:
Evidence for one-reply answer:
Draft path:
Status:
Send blocker:
Reopen condition:
Summary:

Draft:
```

Do not add `Signed-off-by`, `Tested-by`, `Reviewed-by`, `Acked-by`, or similar
trailers unless they are valid for the exact communication and explicitly
authorized.
