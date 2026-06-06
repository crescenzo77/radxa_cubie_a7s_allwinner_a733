# Current Status

Last updated: 2026-06-06.

## Candidate Series

- Linux fork: `https://github.com/crescenzo77/linux.git`
- branch: `candidate/a733-platform-clean`
- base: `6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5`
- base subject: `Merge tag 'for-7.1/dm-fixes-3' of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm`
- head: `c73b7fa0359f63923ff53d8d301312a55a6b244c`
- head subject: `arm64: dts: allwinner: add Radxa Cubie A7S`

The base commit is reachable from the updated `torvalds/linux` `master` ref
observed locally at `8e65320d91cdc3b241d4b94855c88459b91abf66`.

## Scope

The current public series prepares minimal platform support:

- Radxa Cubie A7S board compatible
- A733 CCU binding and initial driver support
- A733 pinctrl binding and driver support
- A733 MMC compatible
- initial A733 SoC DTSI
- Cubie A7S DTS with UART0 console and MMC0 storage

Ethernet is intentionally out of scope. The public series must not claim
Ethernet support until reset, clocking, wrapper setup, MDIO, PHY reset, PHY
power, and link behavior are proven.

## Validation Record

Repository hygiene checks run during this cleanup:

- `git diff --check public/master..HEAD` in the clean Linux branch: pass
- public patch directory regenerated from `public/master..HEAD`
- `git am` of exported patches onto the recorded base in a temporary worktree:
  pass
- `scripts/get_maintainer.pl --no-tree --nogit --nogit-fallback`: pass
- AMD validation container, per-schema `dt_binding_check`: pass for
  `arm/sunxi.yaml`, `clock/allwinner,sun60i-a733-ccu.yaml`,
  `pinctrl/allwinner,sun60i-a733-pinctrl.yaml`, and
  `mmc/allwinner,sun4i-a10-mmc.yaml`
- AMD validation container, out-of-tree `arm64 defconfig` plus
  `allwinner/sun60i-a733-cubie-a7s.dtb`: pass
- AMD validation container, manual `dt-validate` of the generated Cubie A7S
  DTB against the generated processed schema: pass
- AMD validation container, `W=1` object build for
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.o` and
  `drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o`: pass

Validation issue found:

- kernel `make dtbs_check` wrapper failed in the current validation image with
  a `dt-validate` argument-parsing error
- manual `dt-validate` of the same generated DTB passed
- repair the validation image or wrapper before treating `make dtbs_check`
  itself as proven

Current checkpatch result:

- `scripts/checkpatch.pl --strict --no-tree patches/*.patch`: fail
- reason: all patches intentionally lack human `Signed-off-by:` trailers
- additional warning: checkpatch asks whether new files need MAINTAINERS
  updates; current `get_maintainer.pl` output finds existing subsystem
  coverage

Validation still required before any upstream submission:

- human DCO sign-off, followed by a clean `scripts/checkpatch.pl --strict`
- `make dt_binding_check` for touched schemas
- `make ARCH=arm64 dtbs_check` for the A733/Cubie DTS files
- relevant object builds with `W=1`
- hardware boot/runtime record for any behavior claimed in the cover letter
