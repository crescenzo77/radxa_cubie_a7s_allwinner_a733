# A733 Local Prep Backup Checkpoint

Status: local-only post-backup checkpoint
Updated: 2026-06-13

This checkpoint records the current committed A733 coordination prep bundle
after the operator explicitly requested a GitHub backup. It is not a public communication,
not approval to send kernel mail, not approval to open pull requests, and not
permission to mutate hardware. This checkpoint is not permission to mutate hardware.

## Repository State

- Repository: `/Users/enzo/projects/homelab`
- Branch: `main`
- HEAD: `88a6aa62301f9fe438fc3376b3884b4e3d763dcc`
- HEAD summary: `a733: document local evidence gates`
- Relation to local `origin`: `main...origin/main [ahead 2]`
- GitHub backup remote: `github-backup`
- GitHub backup branch: `homelab-backup-main`
- GitHub backup branch HEAD: `88a6aa62301f9fe438fc3376b3884b4e3d763dcc`
- GitHub public-evidence branch: `main`
- GitHub public-evidence branch HEAD:
  `dac2a6f83894d1de6b6177da8d83461fef62d6c0`
- Backup note: pushing local `main` directly to GitHub `main` was rejected as
  non-fast-forward because GitHub `main` carries a separate public-evidence
  history. The coordination repo was therefore backed up to
  `homelab-backup-main` without overwriting GitHub `main`.

## Included Prep Bundle

- Display/media/GPU evidence boundary and queue gate.
- NPU/RISC-V MCU boundary and queue gate.
- Regulator/power-domain evidence boundary.
- DTS v2 local readiness checklist.
- DTS v2 local delta plan for the UART0 pinctrl source movement.
- DTS v2 static proof plan for build/checkpatch/get-maintainer validation.
- Audio/I2S evidence boundary and queue gate.
- PWM/backlight/fan evidence boundary and queue gate.
- Mac-mini kernel checkout quarantine refresh and clean-tree selection rule.
- Checkpoint path:
  `task-packets/kernel/a733-local-pending-prep-checkpoint.md`
- Validator coverage for the evidence sheets and queue IDs through
  A733-BATCH-016, plus DTS v2 local delta, DTS v2 static proof, kernel
  checkout quarantine, and workflow-path anchors.
- Validator coverage preserves DTS v2 local delta, kernel checkout quarantine, and workflow-path anchors.
- Validator coverage includes the kernel checkout quarantine and workflow-path anchors.
- Peripheral evidence map coverage for the new queue IDs.
- Substantive prep cycle-ledger records through A733-CYCLE-049, starting at
  A733-CYCLE-033.
- Checkpoint-only refresh cycles after A733-CYCLE-049 are recorded in the
  cycle ledger. This checkpoint does not roll its coverage forward for refresh-only cycles
  unless they add or change a substantive prep artifact.
  This prevents self-referential checkpoint churn.

## Artifact Hashes

The checkpoint file is intentionally omitted from this hash block because a
self-referential hash changes when the checkpoint is refreshed. The final
checkpoint hash for a given cycle is recorded in that cycle's ledger entry.

```text
b1cdf0ac3f4b9d3e10e5f3b0a05ee99ec7f46e6d5c314feb17a9506ce1e7f8d3  task-packets/kernel/a733-pwm-backlight-fan-evidence-sheet.md
a508336eef34680bcf9364307c552520e5ba7b62710db08b65afbafbd50182b7  task-packets/kernel/a733-current-evidence-index.md
002bb423ec7a7f225830cb58587f10b869071b5cfb0937831e9f8c75c016911d  task-packets/kernel/a733-peripheral-evidence-map.md
cab28074eebba7a7177bd101d6ea3fd69f9de1a89a7a5d59bb04835f0f4d748d  task-packets/kernel/a733-supervised-batch-queue.md
572b0d5d9a3636e54668bc5ab9eca51f2f75e5745d9fbe65d710fc2d0d51865a  tools/validate/a733_authority_check.py
65859fe637dd399b4cf74e5e486f33b041e3ad307719764f1b895ebd2b1e9225  task-packets/kernel/a733-audio-i2s-evidence-sheet.md
eb5864cd571955e2ede7e1384ce329dff10c60f411d40742c9302e91367f0d22  task-packets/kernel/a733-display-media-evidence-sheet.md
ecf593ab18ee25258aa24ded406a11fc50267284d7528e2d2fef85ad71f629ad  task-packets/kernel/a733-npu-riscv-boundary-sheet.md
7924ec5ea109c98082bf5459946b94fd0a2280bab760a2de154d044543c1f3f2  task-packets/kernel/a733-regulator-power-domain-evidence-sheet.md
8b7cc232fcadf2a20d455c5c6945c3c1f7b4eb98a1a768be78a2867d6b5a18e5  inventory/kernel-checkout-quarantine-20260606.md
793374bdab656ff0a063ae912946af2d714b28fcac50395614af6016e32d5d37  inventory/kernel-workflow-paths.json
dc46e72546571de68c078e061b96b66d6f624fa50aaa07c146603378f5785a78  task-packets/kernel/a733-dts-v2-local-delta-plan.md
7e0ee23d02885c4179b4dd7cd619ade6ac9edca54dd729f3112ad6a5777e0e32  task-packets/kernel/a733-dts-v2-local-readiness-checklist.md
97ec3c1cc67d94b753db75548fed1675fe11a425f38ea7c6e8c851844afac79d  task-packets/kernel/a733-current-evidence-index.md
adb0a3b5938b9060b03bac2c7afefff0a83c162532860591901396bb97e69be1  task-packets/kernel/a733-dts-v2-static-proof-plan.md
d97511329c0bac341c62960e00cbdaa7f16d5f6cc4ea0e499d8e4be5bea3f60e  task-packets/kernel/a733-dts-v2-local-delta-plan.md
121615391d5c52259b7dae934bc7988934aa6c6f0509060b257487401f0d03cf  task-packets/kernel/a733-current-evidence-index.md
```

## Validation At Checkpoint

- `python3 tools/validate/a733_authority_check.py`: pass
- `python3 -m py_compile tools/validate/a733_authority_check.py`: pass
- `python3 -m json.tool inventory/hardware/cubie-a7s-lab.json`: pass
- `git diff --check` over the checkpoint refresh bundle: pass

## Boundaries

- No hardware mutation was performed for this prep bundle.
- No kernel tree files were edited for this prep bundle.
- No public kernel communication was performed for this prep bundle.
- The GitHub backup push was performed only because the operator explicitly
  requested it for this turn.
- GitHub `main` was not overwritten.
- Hardware runtime work remains blocked until board roles, drilled recovery,
  and claim service permit it.
