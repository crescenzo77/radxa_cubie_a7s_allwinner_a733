# A733 DTS v2 Local Delta Plan

Status: local-only patch-prep plan
Updated: 2026-06-13

This plan records the minimal Radxa Cubie A7S DTS v2 source delta that can be
prepared locally after the v1 maintainer feedback. It is not a patch, not a
cover letter, not send approval, not runtime proof, and not permission to
mutate hardware.

## Authority

- Workflow: `runbooks/kernel-a733-mainline-enablement-workflow.md`
- Readiness checklist:
  `task-packets/kernel/a733-dts-v2-local-readiness-checklist.md`
- Communication holds: A733-COMM-002 and A733-COMM-003
- Runtime proof queue: A733-BATCH-002
- Clean Mac-mini source tree:
  `/Users/enzo/projects/linux-a733-sparse`
- Clean source branch: `candidate/a733-platform-clean-v4`
- Clean source head: `abc8d07b0a63255e11ee8dd864dcdaa83cf8d38e`

## Current Read-Only Source Finding

Clean sparse source inspection shows:

- `sun60i-a733-cubie-a7s.dts` defines `uart0_pb9_pb10_pins` under `&pio`.
- `sun60i-a733-cubie-a7s.dts` enables `&uart0` and references
  `pinctrl-0 = <&uart0_pb9_pb10_pins>;`.
- `sun60i-a733.dtsi` already contains the SoC `pio` node and a precedent
  SoC-level `mmc0_pins` group.
- `sun60i-a733.dtsi` does not yet contain the UART0 PB9/PB10 pin group.

The quarantined full checkout shows the same pattern by read-only inspection,
but must not be used for patch export while its non-A733 dirty-file quarantine
remains active.

## Minimal Intended Delta

Local preview patch:

```text
task-packets/kernel/a733-dts-v2-uart-pinctrl-local-preview.patch
```

This preview passed `git apply --check` against
`/Users/enzo/projects/linux-a733-sparse` on `candidate/a733-platform-clean-v4`.
It is still a local-only no-send artifact and does not replace the static proof
plan.

Move only the pin group definition:

```dts
uart0_pb9_pb10_pins: uart0-pb9-pb10-pins {
	pins = "PB9", "PB10";
	allwinner,pinmux = <2>;
	function = "uart0";
};
```

from:

```text
arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts
```

to:

```text
arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi
```

Place it inside the existing `pio: pinctrl@2000000` node near the other SoC
pin group definitions, next to `mmc0_pins`, following local ordering and
indentation.

Keep the board DTS `&uart0` node referencing the same label:

```dts
&uart0 {
	pinctrl-names = "default";
	pinctrl-0 = <&uart0_pb9_pb10_pins>;
	status = "okay";
};
```

## Must Not Change In This Delta

- Do not add Ethernet, eMMC, PCIe, USB, USB-C, Wi-Fi, Bluetooth, display,
  media, NPU, RISC-V MCU, thermal, cpufreq, fan, PWM, audio, or regulator
  expansion.
- Do not change `compatible`, `model`, aliases, `stdout-path`, SD-card
  `mmc0` boot scope, `no-mmc`, or `no-sdio`.
- Do not add new binding compatibles or private prerequisite scaffolding.
- Do not remove `allwinner,pinmux` as part of this DTS v2 delta unless the
  selected prerequisite branch has already made that cleanup consistently and
  the proof plan records it as a separate source-equivalent rebase fact.
- Do not claim runtime proof from this source movement.

## Static Proof Needed After A Future Kernel Edit

Before running validation, read
`task-packets/kernel/a733-dts-v2-static-proof-plan.md`. It records the current
Mac-mini tool and checkout limits: the clean sparse tree lacks the full build
and script surface, the full tree remains quarantined for patch export, and
this host currently lacks `aarch64-linux-gnu-gcc` on PATH.

Run from the selected clean kernel tree or a temporary local worktree:

```sh
git diff --check -- arch/arm64/boot/dts/allwinner/sun60i-a733.dtsi arch/arm64/boot/dts/allwinner/sun60i-a733-cubie-a7s.dts
make ARCH=arm64 allwinner/sun60i-a733-cubie-a7s.dtb
make ARCH=arm64 CHECK_DTBS=y allwinner/sun60i-a733-cubie-a7s.dtb
scripts/checkpatch.pl --strict <generated patch>
scripts/get_maintainer.pl <generated patch>
```

If any command is unavailable on the current host, record the exact reason and
the host/tree where it must be rerun. Do not convert an unavailable command
into a pass.

## Runtime Proof Gate

Runtime proof remains queued-only under A733-BATCH-002 until board roles,
recovery drill, artifact path, UART path, rollback path, and claim-service
state positively permit it. This local delta plan does not authorize booting,
installing, power-cycling, UART capture, SSH probing, or board mutation.

## Communication Gate

A future v2 cover letter and changelog remain held under A733-COMM-002 and
A733-COMM-003. Do not send, resend, post, push, or refresh public recipient
state from this plan.

## Stop Conditions

- The clean source tree no longer matches the finding above.
- Moving the pin group requires unrelated DTS changes.
- A validation command fails in a way that changes the patch content.
- The next action depends on maintainer preference rather than a concrete
  local correction.
- Any step would require hardware mutation, public communication, or public
  push while local-only mode remains active.
