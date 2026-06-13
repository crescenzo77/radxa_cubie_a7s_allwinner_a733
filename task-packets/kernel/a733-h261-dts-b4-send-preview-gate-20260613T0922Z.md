# A733 H261 - DTS b4 Send-Preview Gate

Captured UTC: 2026-06-13T09:22Z

## Purpose

Tighten the no-send final b4 gate for the A733/Cubie A7S DTS series so it
checks whether b4 can render outbound messages into a local dry-run directory.

This packet is documentation only. It is not a `b4 send`, not a `b4 send
--reflect`, not a public push, not a source change, and not a hardware, service,
cron, or model-routing action.

## Gate Change

Updated:

```text
scripts/kernel-b4-final-gate
```

The gate already checked:

- branch is not detached;
- `b4 prep --show-info` is readable;
- `b4 prep --check-deps` runs;
- `b4 prep --check` runs;
- b4 metadata does not show unresolved editing, recipient, dependency, checking,
  or preflight blockers.

H261 adds one more no-send check:

```text
b4 send -o <temporary-send-preview-directory>
```

The `-o` mode writes raw messages to a local directory and forces dry-run
behavior. It does not send mail.

## Result On Final DTS Branch

Final DTS branch:

```text
branch: local-prefix/final/a733-dts-v1
head:   1d2642221795d611d607b153c119218e496856a8
```

The older metadata checks still pass:

```text
needs-editing: False
needs-recipients: False
has-prerequisites: True
needs-auto-to-cc: False
needs-checking: False
needs-checking-deps: False
preflight-checks-failing: False
```

The new send-preview step fails before producing messages:

```text
E: patatt.signingkey is not set
E: Perhaps you need to run genkey first?
CRITICAL: Error signing: no key configured
Run "patatt genkey" or configure "user.signingKey" to use PGP
FAIL: b4 send dry-run render failed
```

## No-Sign Probe

A separate dry-run probe with `--no-sign` was also attempted only to inspect
whether unsigned messages could be rendered. b4 refused because the configured
path uses the web endpoint and signing was disabled:

```text
CRITICAL: Web endpoint will be used for sending, but signing is turned off
Please re-enable signing or use SMTP
```

No raw messages were generated and no mail was sent.

## Interpretation

The DTS series is no longer machine-ready for reflect review under the stricter
gate. The current blocker is missing patch attestation/signing configuration,
not b4 metadata, source shape, or recipient metadata.

The final-send checklist gate 07 is reopened by this stricter check. Gate 08
reflect review remains open.

## Next Safe Options

- Configure a valid patatt signing key or PGP signing key for this send path,
  then rerun `scripts/kernel-b4-final-gate`.
- Configure and verify an SMTP send path if intentionally avoiding the web
  endpoint.
- Do not run `b4 send --reflect` or a real `b4 send` until the stricter final
  gate passes.
