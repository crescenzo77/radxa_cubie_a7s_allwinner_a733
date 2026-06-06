# Current Status

Last updated: 2026-06-06.

## Candidate Series

- Linux fork: `https://github.com/crescenzo77/linux.git`
- branch: `candidate/a733-platform-clean-v2`
- base: `6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5`
- base subject: `Merge tag 'for-7.1/dm-fixes-3' of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm`
- head: `11db6033ce0040edd70cac3def158e1befc6ecb6`
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

## External Work To Coordinate

- Junhui Liu posted an RFC A733 CCU/PRCM series:
  `https://lore.kernel.org/r/20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech`
- Andre Przywara posted an RFC A733 pinctrl series:
  `https://lore.kernel.org/r/20250821004232.8134-1-andre.przywara@arm.com`

The CCU and pinctrl portions of this series must not be sent upstream until
they are rebased on, coordinated with, or explicitly justified against that
in-flight work.

## Validation Record

Repository hygiene checks run during this cleanup:

- `git diff --check public/master..HEAD` in the clean Linux branch: pass
- public patch directory regenerated from `public/master..HEAD`
- `git am` of exported patches onto the recorded base in a temporary worktree:
  pass
- `scripts/get_maintainer.pl --no-tree --nogit --nogit-fallback`: pass
- `scripts/get_maintainer.pl --no-tree --nogit --nogit-fallback -f` for new
  clock, pinctrl, and DTS files: pass; Allwinner coverage is provided by
  existing `F:` directory patterns even though `N:` patterns do not yet name
  `sun60i`
- AMD validation container, per-schema `dt_binding_check`: pass for
  `arm/sunxi.yaml`, `clock/allwinner,sun60i-a733-ccu.yaml`,
  `pinctrl/allwinner,sun60i-a733-pinctrl.yaml`, and
  `mmc/allwinner,sun4i-a10-mmc.yaml`
- AMD validation container, `make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-`
  `CHECK_DTBS=y` with colon-separated `DT_SCHEMA_FILES` for the Cubie A7S DTB:
  pass
- AMD validation container, `W=1` object build for
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.o` and
  `drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o`: pass
- patch export scan for BSP-only `sun60iw2`/`sun60iw2p1` compatibles: pass,
  none present
- MMC binding and DTS use the existing `allwinner,sun20i-d1-mmc` fallback:
  pass

Validation issue fixed:

- the earlier `dtbs_check` wrapper failure was caused by space-separated
  `DT_SCHEMA_FILES`
- this tree's kernel makefile expects multiple `DT_SCHEMA_FILES` values to be
  colon-separated

Current checkpatch result:

- `scripts/checkpatch.pl --strict --no-tree patches/000[1-8]-*.patch`:
  `0 errors, 6 warnings, 0 checks`
- remaining warnings are MAINTAINERS new-file questions; current
  `get_maintainer.pl` output finds existing subsystem coverage

Validation still required before any upstream submission:

- hardware boot/runtime record for the exact kernel and DTB
- decision on whether MAINTAINERS should gain an explicit `sun60i` pattern or
  file entries despite existing directory coverage
- coordination/rebase decision for the in-flight CCU and pinctrl RFCs
- final non-draft cover letter
