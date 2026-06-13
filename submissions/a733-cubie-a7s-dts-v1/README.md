# A733/Cubie A7S DTS v1 Submission Evidence

This directory records the public evidence for the initial upstream Linux DTS
submission for the Radxa Cubie A7S board and Allwinner A733 SoC.

Public thread:

```text
https://patch.msgid.link/20260613-a733-dts-v1-public-ready-v1-0-7787c94681db@gmail.com
```

## Files

- `cover-letter.txt` - cover letter fetched back from the public archive.
- `series.mbx` - public mbox fetched from the public archive with `b4 am`.
- `b4-am-verify.txt` - sanitized `b4 am` verification output showing the
  public archive fetch and attestation check.
- `manifest.json` - machine-readable summary of the evidence package.
- `runtime-proof-summary.md` - public-safe summary of the private runtime proof.
- `maintainer-feedback.md` - short summary of review feedback received after
  the v1 submission.

## Status

The v1 series is submitted, archived, and fetchable. It is not final accepted
kernel work. Maintainer feedback has identified follow-up work before any v2:

- move the UART0 pin definition into the main A733 DTSI, matching the style
  used by other Allwinner SoCs
- treat the DT series as early until at least the relevant A733 clock support
  lands

No Ethernet, VPU/Cedrus, display, Wi-Fi, Bluetooth, USB-C, PCIe, or other
peripheral support is claimed by this evidence package.

The cover letter and mbox are preserved in their fetched mail form. They may
contain email-format whitespace such as signature separators.
