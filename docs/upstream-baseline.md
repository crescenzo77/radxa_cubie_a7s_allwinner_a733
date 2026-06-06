# Upstream Baseline

This file is the standing policy for A733/Cubie A7S upstream candidate work.
Keep public records concise, technical, and reproducible.

## Scope

The public branch may contain:

- submission-oriented documentation
- generated patch files from clean Linux topic branches
- concise validation summaries tied to exact commits
- evidence summaries that explain hardware claims

The public branch must not contain:

- generated kernels, modules, DTBs, images, or boot payloads
- raw UART captures or uncurated build logs
- private machine topology, SSH paths, credentials, or personal automation
- raw model conversations, model-review dumps, or task packets
- diagnostic patches presented as candidate patches
- history that requires private lab context to understand

## Maintainer Rules

- Use the current Linux documentation and subsystem maintainer instructions as
  the source of truth.
- Search public mailing-list archives for overlapping work before producing a
  candidate branch. Do not send competing CCU, pinctrl, or DTS work without a
  stated relationship to existing RFCs.
- Bindings and dt-binding headers must precede DTS users.
- DTS patches must be last in a mixed series unless a maintainer gives a
  different dependency plan.
- A patch must be reviewable, bisectable, and self-contained.
- A commit message must explain why the change is correct, not how the local
  lab discovered it.
- A hardware value is acceptable only when it can be justified from public
  code, public vendor material, measured hardware evidence, or a recorded
  runtime observation.
- A733-only Ethernet sequencing belongs in Allwinner STMMAC glue code, not in
  generic STMMAC core code.
- Ethernet remains disabled until reset, clocks, wrapper programming, MDIO,
  PHY reset, PHY power, and link behavior are proven.
- Board DTS patches that enable UART, MMC, regulators, or other peripherals
  require a boot/runtime record for the exact kernel and DTB before submission.
- Multiple `DT_SCHEMA_FILES` entries must be passed to DT validation using the
  delimiter expected by the kernel tree under test; for the current base, that
  delimiter is `:`.
- `Signed-off-by:` is human-only. Do not add it until the human submitter has
  reviewed and accepted responsibility under the DCO.
- Use `Assisted-by:` when coding assistance materially contributed to final
  patch content, review, or commit wording. The documented form is
  `Assisted-by: AGENT_NAME:MODEL_VERSION [TOOLS]`.

## Current Direction

The current clean series is platform bring-up only:

- board compatible
- minimal A733 CCU support needed by the DTS
- A733 pinctrl support
- MMC compatible
- initial SoC and Cubie A7S DTS

Do not expand the public series with additional peripherals until each
peripheral has its own binding, driver dependency, validation record, and
runtime evidence.
