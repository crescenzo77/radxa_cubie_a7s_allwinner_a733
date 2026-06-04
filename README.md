# Radxa Cubie A7S / Allwinner A733 Mainline Linux Bring-up

This repository tracks upstream-facing analysis for Radxa Cubie A7S support in
mainline Linux. The target is clean kernel enablement for the Allwinner A733
SoC and the Cubie A7S board.

This branch is intentionally not a lab notebook, artifact store, or patch dump.
It contains only submission-oriented documentation and policy for work that may
eventually become Linux kernel patches.

## Current Status

No Ethernet support is claimed.

Known working areas:

- A733 boot and board identification have been exercised through local
  mainline test kernels.
- A733 pinctrl and GPIO interrupt layout have enough evidence to guide a clean
  upstream design.
- GMAC0 at `0x04500000` has been identified as a Synopsys DWMAC 5.20 instance
  behind an Allwinner GMAC210 wrapper.

Current Ethernet blocker:

- The DWMAC DMA software reset bit remains stuck during local tests.
- MDIO reads are not yet proof of real external PHY communication.
- The Allwinner GMAC210 wrapper setup must be mapped into an upstreamable glue
  driver before any Ethernet patch is proposed.
- Any upstream-facing Cubie A7S board DTS must leave Ethernet disabled until
  that reset, clock, wrapper, MDIO, and PHY behavior is proven.

See [docs/status.md](docs/status.md) for the current technical state.

## Upstream Discipline

This repository follows the Linux kernel submission process rather than a
prototype-app workflow:

- No generated kernels, DTBs, UART logs, or binary artifacts are tracked here.
- Diagnostic patches are not presented as upstream candidates.
- Kernel patches must be small, reviewable, and split by subsystem.
- A733-specific Ethernet sequencing belongs in an Allwinner STMMAC glue driver,
  not in generic STMMAC core files.
- DTS changes must follow accepted YAML bindings and accepted clock/reset
  headers; synthetic local IDs are not acceptable upstream.
- Register offsets must be named and justified, not scanned by ad hoc loops.
- Final patches must pass kernel style, DT schema, and relevant build checks.
- AI assistance, if used for a kernel contribution, must be disclosed with the
  kernel-documented `Assisted-by:` trailer.

See [docs/upstream-discipline.md](docs/upstream-discipline.md).
See [docs/public-repo-expectations.md](docs/public-repo-expectations.md) for
the public branch appearance contract.
See [docs/maintainer-acceptance-contract.md](docs/maintainer-acceptance-contract.md)
for the non-negotiable maintainer acceptance rules.
See [docs/resume-brief-20260604.md](docs/resume-brief-20260604.md) for the
current compact handoff.

## Public Branch Policy

The public `main` branch is kept as an upstream-facing project state. Local
hardware logs, experimental scripts, and generated artifacts are preserved
outside this branch.

The private lab history from before this cleanup is preserved in the local and
private `origin` branch:

```text
lab-history-20260604
```

That branch is intentionally not pushed to the public GitHub remote.

## Useful References

- Linux kernel AI assistant policy:
  <https://docs.kernel.org/process/coding-assistants.html>
- Kernel patch submission guide:
  <https://docs.kernel.org/process/submitting-patches.html>
- Kernel coding style:
  <https://docs.kernel.org/process/coding-style.html>
- Netdev maintainer handbook:
  <https://docs.kernel.org/process/maintainer-netdev.html>
