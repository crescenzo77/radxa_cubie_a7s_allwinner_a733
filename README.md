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

## Current Upstream Submission

The initial 4-patch A733/Cubie A7S DTS series has been submitted upstream as
v1 and is visible on the public kernel archives:

```text
https://patch.msgid.link/20260613-a733-dts-v1-public-ready-v1-0-7787c94681db@gmail.com
```

The public v1 covers:

- Radxa Cubie A7S board compatible
- A733 MMC compatible binding coverage
- initial A733 SoC DTSI with CPUs, timer, GICv3, RTC oscillator provider,
  CCU/R-CCU, pinctrl, UART0, and SDMMC0
- Cubie A7S DTS with UART0 console and SD card boot storage

The [patches/](patches/) directory remains a public review snapshot. The
authoritative submitted series is the b4/lore thread above. Public evidence
for the submitted v1 is recorded in
[submissions/a733-cubie-a7s-dts-v1/](submissions/a733-cubie-a7s-dts-v1/).

The previous full validation branch remains in the Linux fork:

```text
https://github.com/crescenzo77/linux.git
candidate/a733-platform-clean-v4
```

Ethernet is not enabled and no Ethernet support is claimed.

The RTC, CCU/PRCM, and pinctrl work is treated as external prerequisite work
through explicit `Depends-on:` references. The local CCU and pinctrl driver
patches from the earlier 9-patch draft are not part of the current review
export. The focused MMC binding patch is now included because the DTS uses
`allwinner,sun60i-a733-mmc`.

The submitted v1 was prepared with `b4`, reflected to the sender before the
public send, checked for public hygiene, sent through the kernel.org b4 relay,
and fetched back from lore. Runtime proof for the exact v4 kernel and DTB has
been captured privately; raw logs remain out of public git.

Maintainer feedback received after v1 says the UART0 pin definition should move
into the main A733 DTSI and that DT submission is early until at least the
relevant A733 clock support lands. That feedback makes v1 a useful public
checkpoint, not an acceptance-ready final form.

## Submission Discipline

This repository follows the Linux kernel submission process:

- patches must be small, reviewable, and split by subsystem
- bindings and dt-binding headers must precede DTS users
- DTS patches stay at the end of a series
- every hardware value needs evidence that can be explained without private
  lab history
- board enablement needs a boot/runtime proof for the exact kernel and DTB
- final submission shape must be checked against current RTC, CCU/PRCM, and
  pinctrl prerequisite status
- generated artifacts and local debug output stay out of git
- failed experiments are not presented as candidate patches
- `Signed-off-by:` is added only by the human submitter after final review
- all trailers are final human review items; tooling must not invent or add
  nonstandard trailers automatically

See [docs/upstream-baseline.md](docs/upstream-baseline.md),
[docs/mainline-cleanup-workflow.md](docs/mainline-cleanup-workflow.md), and
[docs/status.md](docs/status.md).

## Primary Kernel References

- Linux patch submission guide:
  <https://docs.kernel.org/process/submitting-patches.html>
- Devicetree binding submission rules:
  <https://docs.kernel.org/devicetree/bindings/submitting-patches.html>
- Devicetree schema guide:
  <https://docs.kernel.org/devicetree/bindings/writing-schema.html>
- SoC maintainer handbook:
  <https://docs.kernel.org/process/maintainer-soc.html>
