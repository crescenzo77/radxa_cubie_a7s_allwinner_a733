# A733 H265 DTS v1 public sent and indexed

Captured: 2026-06-13T09:50Z

## Purpose

Record the public b4 send of the A733/Cubie A7S DTS v1 series and the first
archive/mailbox visibility checks.

## Preconditions

- H262 stricter final b4 send-preview gate: PASS
- H263 reflect submission: PASS
- H264 reflected mailbox review: PASS
- Last-moment final gate on the public-ready DTS branch: PASS

## Public send result

`b4 send` was run without reflect mode after the final gate passed.

b4 reported:

- converted the branch to 5 messages
- ready to send to actual recipients through the web endpoint
- `Sent 5 messages`
- tagged `sent/20260613-a733-dts-v1-public-ready-8cbb37133b64-v1`
- recorded the v1 series message-id in cover-letter tracking
- created a new v2 prep revision

Public v1 cover Message-ID:

- `<20260613-a733-dts-v1-public-ready-v1-0-7787c94681db@gmail.com>`

Public archive link:

- `https://patch.msgid.link/20260613-a733-dts-v1-public-ready-v1-0-7787c94681db@gmail.com`

## Sent tag and post-send state

Sent tag:

- `sent/20260613-a733-dts-v1-public-ready-8cbb37133b64-v1`
- tag object: `8af32e58b12801adaed298b9b16a134d1b814c0b`
- tag commit: `5f84f0959a6446ad5c07e79e0ee8abb333ea7612`

After sending, b4 rerolled the prep branch to revision 2:

- branch: `a733-dts-v1-public-ready`
- post-send head: `a2186558675d1a38f3c8cfe3a9356638b2262d11`
- revision: 2
- expected open state: needs editing/preflight before any future v2 send

This v2 state is bookkeeping only. Do not send v2 unless maintainer feedback or
a concrete correction requires it.

## Archive and mailbox check

`b4 am` against the public cover Message-ID fetched the lore thread and found
5 messages.

Initial attestation note from local `b4 am`:

- DKIM/kernel.org: signed
- local ed25519 key lookup: no public key found for the sender identity

This is recorded as a verification-distribution note, not as a send failure.

Gmail also received the public cover copy. Gmail labeled it as spam, similar to
the reflect copies.

## Current status

- DTS v1 public send: complete
- Lore visibility by cover Message-ID: present
- Public cover copy in mailbox: present
- v2 prep branch: created by b4, not ready and not intended for send yet
- Next action: monitor maintainer/list response and dependency state

