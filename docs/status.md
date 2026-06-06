# Current Status

Last updated: 2026-06-06.

## Draft Review Export

- Linux fork: `https://github.com/crescenzo77/linux.git`
- branch: `candidate/a733-platform-clean-v4`
- base: `6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5`
- base subject: `Merge tag 'for-7.1/dm-fixes-3' of git://git.kernel.org/pub/scm/linux/kernel/git/device-mapper/linux-dm`
- head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- head subject: `MAINTAINERS: add Allwinner sun60i pattern`

The base commit is reachable from the updated `torvalds/linux` `master` ref
observed locally at `8e65320d91cdc3b241d4b94855c88459b91abf66`.

This export is a public review snapshot only. It is not a sendable candidate
series while the CCU/PRCM and pinctrl overlap questions remain unresolved.

The patch files were regenerated from the v4 candidate branch after removing a
deprecated pinctrl include, removing unused child-bus properties from the GIC
node, and tightening the RFC dependency language. Before any submission,
regenerate the series again from the final clean kernel candidate branch and
rerun validation so the source branch, patch files, and proof records describe
the same code.

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

Review-blocker cleanup now present in v4:

- new CCU and pinctrl binding maintainer blocks list
  `Enzo Adriano <enzo.adriano.code@gmail.com>`
- `MAINTAINERS` includes an explicit `N: sun60i` Allwinner pattern
- A733 Cortex-A55 CPU nodes use `capacity-dmips-mhz = <530>`
- A733 Cortex-A76 CPU nodes use `capacity-dmips-mhz = <1024>`
- the GICv3 redistributor region is `0x100000`, not the previous irregular
  `0xff004`
- the GICv3 node omits unused child-bus properties because it has no child
  nodes
- the A733 pinctrl draft does not include deprecated `linux/of_device.h`

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

The expected sendable direction is a smaller board/SoC DTS series stacked on
accepted or current CCU and pinctrl prerequisites, unless subsystem maintainers
ask for a different dependency plan.

Current local review consensus:

- A733 CCU/PRCM work is on hold because it overlaps the in-flight Linux RFC and
  still depends on reviewed clock/reset evidence.
- A733 pinctrl work is on hold because it overlaps the in-flight Linux RFC and
  still needs hardware evidence for IRQ/bank behavior.
- A733 GMAC remains out of scope until clock/reset identifiers, wrapper setup,
  MDIO, PHY reset, PHY power, and link behavior are proven.

## Validation Record

The current v4 patch files have been regenerated from
`candidate/a733-platform-clean-v4`. The v4 proof IDs below were produced by
the validation container.

Current v4 repository hygiene checks run during this cleanup:

- source branch `candidate/a733-platform-clean-v4` pushed to
  `https://github.com/crescenzo77/linux.git` at
  `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- `git diff --check 6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5..HEAD` in
  the sparse v4 Linux branch: pass
- public patch directory regenerated from the v4 branch with
  `git format-patch --base`
- `git apply --numstat patches/000[1-9]-*.patch`: pass, all exported patch
  files parse as patches
- patch export scan for automatic coding-assistance trailers and local author
  aliases: pass, none present
- patch export scan for `linux/of_device.h`, the previous GIC redistributor
  size, and third-party binding maintainer blocks in A733 files: pass, none
  present
- MMC binding and DTS use the existing `allwinner,sun20i-d1-mmc` fallback:
  pass
- exported v4 patches applied cleanly with `git am --3way` onto the recorded
  base in a temporary validation worktree; the resulting tree matched v4 head
  `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`
- `scripts/get_maintainer.pl --no-tree --nogit --nogit-fallback` over the
  exported v4 patches: pass, produced 21 maintainer/list entries including
  the Devicetree, Allwinner, clock, MMC, pinctrl, and reset recipients

Validation container proof records for v4 exact head
`abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`:

- environment version report: pass,
  `a733-v4-public-version-report-83eafc55329b`,
  SHA256 `fd3864ed1220cf094066c41deaa5ae7feb249c37fae460c72812ece8c065681a`
- `git diff --check 6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5 HEAD`:
  pass,
  `a733-v4-public-git-diff-check-48177e45d386`,
  SHA256 `9f91001a63989800a3b5ae57d143393e44d1415406f8384cf18647e44494c6ea`
- `scripts/checkpatch.pl --strict --no-tree` over exported v4 patches:
  fail, `0 errors` and MAINTAINERS new-file warnings only,
  `a733-v4-public-checkpatch-strict-369568551e94`,
  SHA256 `52818bb78265913cbbafe554fb5dab783e1b0bd9b2919b9c2f6c1ec0636eb53f`
- touched-schema `dt_binding_check`: pass for `arm/sunxi.yaml`,
  `clock/allwinner,sun60i-a733-ccu.yaml`,
  `pinctrl/allwinner,sun60i-a733-pinctrl.yaml`, and
  `mmc/allwinner,sun4i-a10-mmc.yaml`,
  `a733-v4-public-dt-binding-check-04bd27078f58`,
  SHA256 `dfd68a98032110c2c1bdf608bb6859ca70003db49b0a3964fc91db5a3ed86804`
- Cubie A7S DTB schema check: pass,
  `a733-v4-public-cubie-a7s-dtbs-check-3bebeb5a5294`,
  SHA256 `d8d753535a31c30888f8e0a051f051d92e9f1eecd0b1fa8a8d84e555bbab4bb7`
- `W=1` object build for `ccu-sun60i-a733.o` and
  `pinctrl-sun60i-a733.o`: pass,
  `a733-v4-public-object-build-0777f6143da5`,
  SHA256 `cf20fb28f752c831cca03dcf0b2f1f69fc29822e406abdadf5856286fd631e95`
- per-patch `git diff --check`: pass for patches 1 through 9:
  `a733-v4-public-patch01-git-diff-check-e8b1f2d50862`,
  `a733-v4-public-patch02-git-diff-check-526c99256dbb`,
  `a733-v4-public-patch03-git-diff-check-b56a032d84ba`,
  `a733-v4-public-patch04-git-diff-check-e1c456dd23f8`,
  `a733-v4-public-patch05-git-diff-check-8b8edfce2761`,
  `a733-v4-public-patch06-git-diff-check-2a901e46233c`,
  `a733-v4-public-patch07-git-diff-check-bb451ee4cc7b`,
  `a733-v4-public-patch08-git-diff-check-b68e0e137690`,
  `a733-v4-public-patch09-git-diff-check-4787401b6ca3`
- per-patch `make O=/workspace/.proof-build/... ARCH=arm64 defconfig`:
  pass for patches 1 through 9:
  `a733-v4-public-patch01-arm64-build-32e9ed47522c`,
  `a733-v4-public-patch02-arm64-build-4fefd6c7aa59`,
  `a733-v4-public-patch03-arm64-build-529f250399e1`,
  `a733-v4-public-patch04-arm64-build-ffa063e1f7cf`,
  `a733-v4-public-patch05-arm64-build-8a04b5990b78`,
  `a733-v4-public-patch06-arm64-build-d04fa9d7ee31`,
  `a733-v4-public-patch07-arm64-build-61de7246f283`,
  `a733-v4-public-patch08-arm64-build-e8b98f369855`,
  `a733-v4-public-patch09-arm64-build-7bfebb5fb756`
- per-patch targeted CCU object builds: pass for patches 3 through 9:
  `a733-v4-public-patch03-ccu-object-build-74301c4975ca`,
  `a733-v4-public-patch04-ccu-object-build-270f9995187a`,
  `a733-v4-public-patch05-ccu-object-build-95ac8b64af8f`,
  `a733-v4-public-patch06-ccu-object-build-def494604ea5`,
  `a733-v4-public-patch07-ccu-object-build-4932475da954`,
  `a733-v4-public-patch08-ccu-object-build-fce01fc567ce`,
  `a733-v4-public-patch09-ccu-object-build-7002ddde2ff5`
- per-patch targeted pinctrl object builds: pass for patches 5 through 9:
  `a733-v4-public-patch05-pinctrl-object-build-16c82eaf4392`,
  `a733-v4-public-patch06-pinctrl-object-build-19855c97794a`,
  `a733-v4-public-patch07-pinctrl-object-build-68d73d1161c2`,
  `a733-v4-public-patch08-pinctrl-object-build-a20c85a8655c`,
  `a733-v4-public-patch09-pinctrl-object-build-9cf0f191d304`
- per-patch DT binding checks: pass for binding patches 1, 2, 4, and 6:
  `a733-v4-public-patch01-dt-binding-dt-binding-check-9f091f3fa4b9`,
  `a733-v4-public-patch02-dt-binding-dt-binding-check-3e0125bfc967`,
  `a733-v4-public-patch04-dt-binding-dt-binding-check-3cd807c8b310`,
  `a733-v4-public-patch06-dt-binding-dt-binding-check-02fab038785c`
- per-patch Cubie A7S DTB checks: pass for patches 8 and 9:
  `a733-v4-public-patch08-cubie-dtbs-cubie-a7s-dtbs-check-38869c67f5f0`,
  `a733-v4-public-patch09-cubie-dtbs-cubie-a7s-dtbs-check-360c43564c2a`

Still required for v4:

- hardware boot/runtime evidence for the exact kernel and DTB

Historical validation container proof records for v3 exact head
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
- per-patch Cubie A7S DTB checks: pass for patches 8 and 9, where the board
  DTB exists:
  `a733-v3-public-patch08-cubie-dtbs-dtbs-check-de84f6d49370`,
  `a733-v3-public-patch09-cubie-dtbs-dtbs-check-41e21eb001ae`
- environment version report: pass,
  `a733-v3-version-report-bf0065764dd3`,
  SHA256 `c7045daf779e498eed5d523fc4cc03174c376598dc968a843ce0f0bdc73736ca`
- `make O=/workspace/build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-`
  `defconfig`: pass,
  `a733-v3-arm64-build-aa708f565ae7`,
  SHA256 `6622155b35c4b8e8ffbab1226f4f0b3bdfb66ea4e2ebb85f3afc14042df022c5`
- validation container, touched-schema `dt_binding_check`: pass for
  `arm/sunxi.yaml`, `clock/allwinner,sun60i-a733-ccu.yaml`,
  `pinctrl/allwinner,sun60i-a733-pinctrl.yaml`, and
  `mmc/allwinner,sun4i-a10-mmc.yaml`,
  `a733-v3-dt-binding-check-67d53cb809e7`,
  SHA256 `38d1e5fa8c514fed7d385e665d372c4c091e8e19d96373a8af0d30ebaafef1a3`
- validation container, `make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-`
  `CHECK_DTBS=y` with colon-separated `DT_SCHEMA_FILES` for the Cubie A7S DTB:
  pass,
  `a733-v3-dtbs-check-20b66a78fc8c`,
  SHA256 `2da6684e69ab605051de65521b40c2b50c919a981724eb0d0d405f34c01374f4`
- validation container, `W=1` object build for
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

- run from the Linux tree root:
  `scripts/checkpatch.pl --strict --no-tree /path/to/export/patches/000[1-9]-*.patch`:
  `0 errors, 6 warnings, 0 checks`
- remaining warnings are the unconditional MAINTAINERS new-file questions
  emitted for new files in patches 2, 3, 4, 5, 7, and 8; patch 9 adds the
  explicit `N: sun60i` MAINTAINERS coverage

Validation still required before any upstream submission:

- hardware boot/runtime record for the exact kernel and DTB
- full per-patch bisectability record for the exported series, beyond the
  current per-patch diff hygiene, `defconfig`, targeted object, and binding
  proofs, plus Cubie DTB checks for patches where the board DTB exists
- coordination/rebase decision for the in-flight CCU and pinctrl RFCs
- final human decision on coding-assistance disclosure/trailer policy
- final non-draft cover letter
