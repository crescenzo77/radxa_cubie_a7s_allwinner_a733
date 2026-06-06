# Current Status

Last updated: 2026-06-06.

## Draft Review Export

- Linux fork: `https://github.com/crescenzo77/linux.git`
- branch: `candidate/a733-platform-clean-v3`
- base: `6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5`
- base subject: `Merge tag 'for-7.1/dm-fixes-3' of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm`
- head: `3dc9e72c5ccdb19542f8dc068bd5a388d66fdc32`
- head subject: `MAINTAINERS: add Allwinner sun60i pattern`

The base commit is reachable from the updated `torvalds/linux` `master` ref
observed locally at `8e65320d91cdc3b241d4b94855c88459b91abf66`.

This export is a public review snapshot only. It is not a sendable candidate
series while the CCU/PRCM and pinctrl overlap questions remain unresolved.

## Scope

The current public draft export prepares minimal platform support:

- Radxa Cubie A7S board compatible
- A733 CCU binding and initial driver support
- A733 pinctrl binding and driver support
- A733 MMC compatible
- initial A733 SoC DTSI
- Cubie A7S DTS with UART0 console and MMC0 storage
- explicit Allwinner `sun60i` MAINTAINERS pattern

Ethernet is intentionally out of scope. The public series must not claim
Ethernet support until reset, clocking, wrapper setup, MDIO, PHY reset, PHY
power, and link behavior are proven.

## Issue-Class Audit

The current exported series does not contain:

- automatic coding-assistance trailers
- deferred parent IRQ registration or an irq_domain bypass
- Ethernet nodes, generic DWMAC fallback enablement, or STMMAC glue changes
- VPU, Cedrus, media-driver, or VPU clock/DTS changes

Review-blocker cleanup now present in v3:

- new CCU and pinctrl binding maintainer blocks list
  `Enzo Adriano <enzo.adriano.code@gmail.com>`
- `MAINTAINERS` includes an explicit `N: sun60i` Allwinner pattern
- A733 Cortex-A55 CPU nodes use `capacity-dmips-mhz = <530>`
- A733 Cortex-A76 CPU nodes use `capacity-dmips-mhz = <1024>`
- the GICv3 redistributor region is `0x100000`, not the previous irregular
  `0xff004`

Future IRQ, Ethernet, or VPU work is blocked by the workflow rules in
`docs/mainline-cleanup-workflow.md` until it is split by subsystem, justified
in commit messages, and validated per patch.

## External Work To Coordinate

- Junhui Liu posted an RFC A733 CCU/PRCM series:
  `https://lore.kernel.org/r/20260310-a733-clk-v1-0-36b4e9b24457@pigmoral.tech`
- Andre Przywara posted an RFC A733 pinctrl series:
  `https://lore.kernel.org/r/20250821004232.8134-1-andre.przywara@arm.com`

The CCU and pinctrl portions of this series must not be sent upstream until
they are rebased on, coordinated with, or explicitly justified against that
in-flight work.

Current local review consensus:

- A733 CCU/PRCM work is on hold because it overlaps the in-flight Linux RFC and
  still depends on reviewed clock/reset evidence.
- A733 pinctrl work is on hold because it overlaps the in-flight Linux RFC and
  still needs hardware evidence for IRQ/bank behavior.
- A733 GMAC remains out of scope until clock/reset identifiers, wrapper setup,
  MDIO, PHY reset, PHY power, and link behavior are proven.

## Validation Record

Repository hygiene checks run during this cleanup:

- `git diff --check public/master..HEAD` in the clean Linux branch: pass
- public patch directory regenerated from `public/master..HEAD`
- `git am` of exported patches onto the recorded base in a temporary worktree:
  pass
- `scripts/get_maintainer.pl --no-tree --nogit --nogit-fallback`: pass
- `scripts/get_maintainer.pl --no-tree --nogit --nogit-fallback -f` for new
  clock, pinctrl, and DTS files: pass; Allwinner coverage is provided by
  existing `F:` directory patterns and the new `N: sun60i` pattern
- patch export scan for BSP-only `sun60iw2`/`sun60iw2p1` compatibles: pass,
  none present
- patch export scan for automatic coding-assistance trailers and local author
  aliases: pass, none present
- patch export scan for the previous GIC redistributor size `0xff004`: pass,
  none present
- MMC binding and DTS use the existing `allwinner,sun20i-d1-mmc` fallback:
  pass

AMD validation container proof records for exact head
`3dc9e72c5ccdb19542f8dc068bd5a388d66fdc32`:

- `git diff --check 6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5 HEAD`:
  pass,
  `a733-v3-public-git-diff-check-997b45f3f8ff`,
  SHA256 `a36c0ff798d880ac9faa25890e29a640f8af41b10eff5eeef6fb49bd8e93231b`
- per-patch `git diff --check`: pass for patches 1 through 9:
  `a733-v3-public-patch01-git-diff-check-980fd9adb30c`,
  `a733-v3-public-patch02-git-diff-check-668dda230905`,
  `a733-v3-public-patch03-git-diff-check-85bfb1fcb78d`,
  `a733-v3-public-patch04-git-diff-check-1704b3b6dc19`,
  `a733-v3-public-patch05-git-diff-check-7d5b40b1418b`,
  `a733-v3-public-patch06-git-diff-check-12e8278c7b75`,
  `a733-v3-public-patch07-git-diff-check-68d14b03dd1a`,
  `a733-v3-public-patch08-git-diff-check-a94d89ef8a01`,
  `a733-v3-public-patch09-git-diff-check-6160e3d58ca9`

The per-patch diff hygiene proofs do not replace full per-patch build and DT
validation for bisectability.
- per-patch `make O=/workspace/.proof-build/... ARCH=arm64 defconfig`: pass
  for patches 1 through 9:
  `a733-v3-public-patch01-defconfig-arm64-build-536dcbfa0035`,
  `a733-v3-public-patch02-defconfig-arm64-build-d734ec4f9857`,
  `a733-v3-public-patch03-defconfig-arm64-build-965929279a91`,
  `a733-v3-public-patch04-defconfig-arm64-build-bc71fabb400a`,
  `a733-v3-public-patch05-defconfig-arm64-build-54fb98c6ec5d`,
  `a733-v3-public-patch06-defconfig-arm64-build-f74528d95f38`,
  `a733-v3-public-patch07-defconfig-arm64-build-1ea5d66aa955`,
  `a733-v3-public-patch08-defconfig-arm64-build-b69edd5bd066`,
  `a733-v3-public-patch09-defconfig-arm64-build-f9eda2075f2a`

The per-patch `defconfig` proofs confirm Kconfig/default-config generation,
not full object builds or DT validation at each patch.
- per-patch targeted CCU object builds: pass for patches 3 through 9:
  `a733-v3-public-patch03-ccu-object-object-build-c2af45731dff`,
  `a733-v3-public-patch04-ccu-object-object-build-0642ef45be3a`,
  `a733-v3-public-patch05-ccu-object-object-build-2f305292ee65`,
  `a733-v3-public-patch06-ccu-object-object-build-3cd4b2f9d2ca`,
  `a733-v3-public-patch07-ccu-object-object-build-3c8a697980e0`,
  `a733-v3-public-patch08-ccu-object-object-build-9b7f8af5de46`,
  `a733-v3-public-patch09-ccu-object-object-build-5de0c6dc7af0`
- per-patch targeted pinctrl object builds: pass for patches 5 through 9:
  `a733-v3-public-patch05-pinctrl-object-object-build-47692854398c`,
  `a733-v3-public-patch06-pinctrl-object-object-build-036bd9409a09`,
  `a733-v3-public-patch07-pinctrl-object-object-build-d4c7b9123d50`,
  `a733-v3-public-patch08-pinctrl-object-object-build-e59cc88f4c3c`,
  `a733-v3-public-patch09-pinctrl-object-object-build-4f0865931157`

The targeted object proofs compile the introduced driver objects where they
exist. They do not replace per-patch DT binding or DTB validation.
- per-patch DT binding checks: pass for binding patches 1, 2, 4, and 6:
  `a733-v3-public-patch01-dt-binding-dt-binding-check-80cf1c07960b`,
  `a733-v3-public-patch02-dt-binding-dt-binding-check-73a6ccb3ca4c`,
  `a733-v3-public-patch04-dt-binding-dt-binding-check-70cdf0b0512c`,
  `a733-v3-public-patch06-dt-binding-dt-binding-check-c3d3c6d9ba12`
- environment version report: pass,
  `a733-v3-version-report-bf0065764dd3`,
  SHA256 `c7045daf779e498eed5d523fc4cc03174c376598dc968a843ce0f0bdc73736ca`
- `make O=/workspace/build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-`
  `defconfig`: pass,
  `a733-v3-arm64-build-aa708f565ae7`,
  SHA256 `6622155b35c4b8e8ffbab1226f4f0b3bdfb66ea4e2ebb85f3afc14042df022c5`
- AMD validation container, touched-schema `dt_binding_check`: pass for
  `arm/sunxi.yaml`, `clock/allwinner,sun60i-a733-ccu.yaml`,
  `pinctrl/allwinner,sun60i-a733-pinctrl.yaml`, and
  `mmc/allwinner,sun4i-a10-mmc.yaml`,
  `a733-v3-dt-binding-check-67d53cb809e7`,
  SHA256 `38d1e5fa8c514fed7d385e665d372c4c091e8e19d96373a8af0d30ebaafef1a3`
- AMD validation container, `make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-`
  `CHECK_DTBS=y` with colon-separated `DT_SCHEMA_FILES` for the Cubie A7S DTB:
  pass,
  `a733-v3-dtbs-check-20b66a78fc8c`,
  SHA256 `2da6684e69ab605051de65521b40c2b50c919a981724eb0d0d405f34c01374f4`
- AMD validation container, `W=1` object build for
  `drivers/clk/sunxi-ng/ccu-sun60i-a733.o` and
  `drivers/pinctrl/sunxi/pinctrl-sun60i-a733.o`: pass,
  `a733-v3-object-build-d819e4c35268`,
  SHA256 `45fe83a79676d352f74d783471cb85f4f705c18a8a34b37c2f66c8531e9468f2`

Validation issue fixed:

- the earlier `dtbs_check` wrapper failure was caused by space-separated
  `DT_SCHEMA_FILES`
- this tree's kernel makefile expects multiple `DT_SCHEMA_FILES` values to be
  colon-separated

Current checkpatch result:

- `scripts/checkpatch.pl --strict --no-tree patches/000[1-9]-*.patch`:
  `0 errors, 6 warnings, 0 checks`
- remaining warnings are the unconditional MAINTAINERS new-file questions
  emitted for new files in patches 2, 3, 4, 5, 7, and 8; patch 9 adds the
  explicit `N: sun60i` MAINTAINERS coverage

Validation still required before any upstream submission:

- hardware boot/runtime record for the exact kernel and DTB
- full per-patch bisectability record for the exported series, beyond the
  current per-patch diff hygiene, `defconfig`, targeted object, and binding
  proofs
- coordination/rebase decision for the in-flight CCU and pinctrl RFCs
- final human decision on coding-assistance disclosure/trailer policy
- final non-draft cover letter
