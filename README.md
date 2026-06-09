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

## Current Review Export

The current public artifact is a 3-patch maintainer-shape review export in
[patches/](patches/). It is not mailed, and it still needs regeneration from
the final clean kernel branch plus full validation before any upstream send.

The previous full validation branch remains in the Linux fork:

```text
https://github.com/crescenzo77/linux.git
candidate/a733-platform-clean-v4
```

The current review export covers:

- Radxa Cubie A7S board compatible
- initial A733 SoC DTSI
- Cubie A7S DTS with UART0 console and MMC0 storage

Ethernet is not enabled and no Ethernet support is claimed.

The CCU/PRCM and pinctrl work is treated as external prerequisite work through
explicit `Depends-on:` references. The local CCU, pinctrl, standalone MMC
binding, and MAINTAINERS scaffolding patches from the earlier 9-patch draft are
not part of the current review export.

The expected sendable direction is this narrow board-compatible plus DTS slice
stacked on the accepted or current CCU/PRCM and pinctrl prerequisite branches,
unless subsystem maintainers ask for a different plan. Runtime proof for the
exact v4 kernel and DTB has been captured in the private workflow; raw logs
remain out of public git. Before mailing, regenerate the patches from a clean
kernel branch that matches the prerequisite state and rerun all validation.
Current prerequisite API reconciliation is still open: the DTS must be checked
against the active A733 CCU clock-input binding, and the A733 MMC compatible
must either be documented in the series or already exist in the chosen base.

## Submission Discipline

This repository follows the Linux kernel submission process:

- patches must be small, reviewable, and split by subsystem
- bindings and dt-binding headers must precede DTS users
- DTS patches stay at the end of a series
- every hardware value needs evidence that can be explained without private
  lab history
- board enablement needs a boot/runtime proof for the exact kernel and DTB
- final submission shape must be checked against current CCU/PRCM and pinctrl
  prerequisite status
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
