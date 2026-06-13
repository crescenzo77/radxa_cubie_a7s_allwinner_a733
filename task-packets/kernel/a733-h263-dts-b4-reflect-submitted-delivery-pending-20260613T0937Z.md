# A733 H263 DTS b4 reflect submitted, delivery pending

Captured: 2026-06-13T09:37Z

## Purpose

Record the first real b4 web-endpoint reflect attempt for the public-ready
A733/Cubie A7S DTS series.

This packet records a reflect-only action. It does not record or authorize a
public list send.

## Inputs

- Canonical homelab coordination repo
- Runtime kernel worktree for the final DTS branch
- Branch: `a733-dts-v1-public-ready`
- Head: `0356b43f505bbb3ec6a7679a49748750b37fe099`
- b4 binary from the kernel-work virtual environment
- Prior gate packet:
  `task-packets/kernel/a733-h262-dts-public-ready-branch-send-preview-pass-20260613T0931Z.md`

## Pre-reflect readiness

Before reflect, the runtime host still reported:

- DTS branch: `a733-dts-v1-public-ready`
- DTS head: `0356b43f505bbb3ec6a7679a49748750b37fe099`
- DTS worktree status: clean
- `scripts/kernel-b4-final-gate --repo <final-dts-worktree>`: PASS

## b4 endpoint authentication

Initial reflect reached the web endpoint but failed with:

- `No matching key, please complete web auth first.`

The endpoint auth request was then initiated for:

- Endpoint: `https://lkml.kernel.org/_b4_submit`
- Identity: `enzo.adriano.code@gmail.com`
- Selector: `a733-cubie-a7s`
- Public key:
  `ed25519:5S3Wmdqa4XfCdeZF/HfeYqnQF8GN9JGt3SE1cxqSX8E=`

The challenge email was received from `B4 Relay <devnull@kernel.org>` and the
challenge was verified successfully on the runtime host. b4 reported:

- `Challenge successfully verified for enzo.adriano.code@gmail.com`
- `You may now use this endpoint for submitting patches.`

## Reflect result

Command:

```sh
printf "\n" | b4 send --reflect
```

b4 rendered 5 messages:

- `[PATCH 0/4] arm64: dts: allwinner: add A733/Cubie A7S DTS support`
- `[PATCH 1/4] dt-bindings: arm: sunxi: add Radxa Cubie A7S`
- `[PATCH 2/4] dt-bindings: mmc: add Allwinner A733 compatible`
- `[PATCH 3/4] arm64: dts: allwinner: add Allwinner A733 SoC`
- `[PATCH 4/4] arm64: dts: allwinner: add Radxa Cubie A7S`

b4 showed the normal public To/Cc headers, but explicitly stated reflect mode
would deliver only to:

- `enzo.adriano.code@gmail.com`

and that addresses in To/Cc would not receive the series.

Final b4 result:

- `Reflected 5 messages`

## Delivery check

Immediately after the successful reflect, Gmail searches for the reflected
cover and patch subjects did not yet find the reflected messages. The only
matching recent kernel relay message visible at that time was the web endpoint
verification email.

Treat reflect submission as successful, but mailbox delivery/review as still
pending until the reflected patch copies are visible and reviewed.

## Current status

- Public list send: not run.
- Reflect submission: submitted successfully through the b4 web endpoint.
- Reflect mailbox delivery: pending verification.
- Gate 08: not fully closed until the reflected messages are received and
  reviewed.
