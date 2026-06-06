# Radxa Cubie A7S / Allwinner A733 Mainline Linux Bring-up

This repository is the public preparation record for upstream Linux work on
the Radxa Cubie A7S board and the Allwinner A733 SoC.

It is intentionally narrow. The public branch should help kernel maintainers
answer three questions:

- what patch series is being prepared
- what base and validation were used
- what is, and is not, being claimed

Local lab automation, raw model output, generated kernels, DTBs, UART captures,
and private machine details do not belong on this branch.

## Current Series

The current candidate work is the 9-patch platform bring-up series exported in
[patches/](patches/).

The current authoritative development branch is in the Linux fork:

```text
https://github.com/crescenzo77/linux.git
candidate/a733-platform-clean-v3
```

The exported series currently covers:

- Radxa Cubie A7S board compatible
- initial Allwinner A733 CCU binding and driver
- A733 pinctrl binding and driver
- A733 MMC compatible
- initial A733 SoC DTSI
- Cubie A7S DTS with UART0 console and MMC0 storage
- explicit Allwinner `sun60i` MAINTAINERS pattern

Ethernet is not enabled and no Ethernet support is claimed.

The series is not ready to send upstream until the open items in
[docs/status.md](docs/status.md) are resolved.

## Submission Discipline

This repository follows the Linux kernel submission process:

- patches must be small, reviewable, and split by subsystem
- bindings and dt-binding headers must precede DTS users
- DTS patches stay at the end of a series
- every hardware value needs evidence that can be explained without private
  lab history
- generated artifacts and local debug output stay out of git
- failed experiments are not presented as candidate patches
- `Signed-off-by:` is added only by the human submitter after final review
- coding-assistance disclosure and trailer decisions are final human review
  items; tooling must not add those trailers automatically

See [docs/upstream-baseline.md](docs/upstream-baseline.md),
[docs/mainline-cleanup-workflow.md](docs/mainline-cleanup-workflow.md), and
[docs/status.md](docs/status.md).

## Primary Kernel References

- Linux patch submission guide:
  <https://docs.kernel.org/process/submitting-patches.html>
- Linux coding assistant policy:
  <https://docs.kernel.org/process/coding-assistants.html>
- Devicetree binding submission rules:
  <https://docs.kernel.org/devicetree/bindings/submitting-patches.html>
- Devicetree schema guide:
  <https://docs.kernel.org/devicetree/bindings/writing-schema.html>
- SoC maintainer handbook:
  <https://docs.kernel.org/process/maintainer-soc.html>
