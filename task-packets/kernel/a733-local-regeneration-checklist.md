# A733 Local Regeneration Checklist

Status: local-only checklist
Updated: 2026-06-13

This checklist is for future local regeneration, validation, or response-prep
work around the A733 CCU/SDMMC0 line. It is not a send approval, not a public
archive refresh, not a maintainer-response draft, not a hardware test plan,
and not new proof.

Use it only after reading the five authority files and the current evidence
index:

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-cycle-ledger.md`
- `task-packets/kernel/a733-unsent-communications-ledger.md`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-current-evidence-index.md`

## Hard Boundaries

- Stay local-only.
- Do not send or resend H215, H253, H265, or any derivative.
- Do not run `b4 send`, real `git send-email`, Gmail replies, list replies,
  GitHub comments, pull requests, issue comments, public pushes, or paid
  third-party calls.
- Do not refresh public archives or recipients during an autonomous local
  cycle unless the workflow explicitly reopens that gate.
- Do not boot, reboot, install, power-cycle, SSH probe, UART capture, or mutate
  a Cubie board from this checklist.
- Do not claim fresh hardware proof from this checklist.

## Current Anchors

| Line | Anchor | Evidence | Posture |
|---|---|---|---|
| Narrow H200/H215 source | `de486cb24c361a86cba26738f24332df780872b0` | H201 exact hardware proof | Historical sent-before-blackout via H215; no resend |
| H200 patch text | `task-packets/kernel/a733-h200-h199-maintainer-polish-series/` | H200 readiness, H201 proof | Local reference only |
| Common update-bit fallback | `e694ae3fa8477846a5a6eaf31fed4813ff991d5b` | H247 hardware proof, H253 bundle gates | No-send fallback only |
| Event routing | H260 | Current maintainer-response playbook | Planning input only |

## Select The Correct Path

### Path A: Narrow H200/H215 Local Recheck

Use this when the future task is to confirm the existing narrow
hardware-proven source line still regenerates cleanly.

Required local checks:

1. Confirm the exact base is still recorded as `d9aa2e15caae`.
2. Confirm the H200 source anchor remains
   `de486cb24c361a86cba26738f24332df780872b0`.
3. Confirm local source status is clean before any regeneration.
4. Regenerate patch text only into a new local task-packet directory.
5. Run `git diff --check` against the recorded base.
6. Run strict `scripts/checkpatch.pl` on generated patch files.
7. Run `tools/validate/trailer_gate.py` on generated patch files.
8. Run `tools/validate/public_hygiene_gate.py` only on public-facing patch
   files or a scrubbed staging directory.
9. If comparing regenerated commits, compare source content, not commit hashes,
   because fresh committer metadata changes commit IDs.
10. Record the commands, source equivalence target, hashes, and dirty-tree
    state in a new task packet.

Stop if:

- the source anchor differs from H200
- generated patches include unapproved trailers
- public-hygiene checks hit local paths, private hosts, AI metadata, or lab
  details
- any step would require public archive state or maintainer judgment

### Path B: Common H253 Fallback Local Recheck

Use this only when local prep is needed for the maintainer-directed common
`CCU_FEATURE_UPDATE_BIT` fallback shape.

Required local checks:

1. Confirm H253 remains a no-send fallback, not a replacement for H215.
2. Confirm the fallback source anchor remains
   `e694ae3fa8477846a5a6eaf31fed4813ff991d5b`.
3. Confirm the recorded base is still `d9aa2e15caae`.
4. Apply the H253 bundle from the recorded base in a temporary local worktree.
5. Run `git diff --check` after apply.
6. Confirm source equivalence against the H253 source anchor for touched files.
7. Run strict `scripts/checkpatch.pl` on patches 1-4.
8. Run `tools/validate/trailer_gate.py` on patches 1-4.
9. Run `tools/validate/public_hygiene_gate.py` on the no-send bundle staging
   directory or public-facing subset.
10. Record hashes for regenerated patch files, validation logs, and
    source-equivalence output.

Stop if:

- the fallback source no longer reconstructs from the recorded base
- source equivalence fails
- H250/H251 caveats are lost or overclaimed
- the task starts to imply public action without a reopened communication gate

## Evidence Boundaries

Allowed to cite as existing proof:

- H201 proves exact H200 boot to SDMMC0/card/rootfs/`/bin/sh` boundary on
  Cubie3, followed by restore to vendor kernel.
- H247 proves exact H253/H245 common-helper fallback to the same boundary,
  followed by restore to vendor kernel.
- H253 records a no-send fallback bundle with apply, diff-check,
  source-equivalence, public hygiene, and strict checkpatch gates.

Not allowed to claim from these records:

- Ethernet, PCIe, USB, Wi-Fi, Bluetooth, display, media, NPU, RISC-V, eMMC,
  thermal, cpufreq, fan, or other peripheral enablement
- general A733 CCU correctness beyond the tested boot-critical path
- public archive visibility beyond what the historical task packets recorded
- maintainer approval or preference
- current board safety for new autonomous hardware work

## Output Packet Template

Use a new `task-packets/kernel/a733-hNNN-...md` packet for any regeneration
work:

```text
# A733 HNNN: <short title>

Timestamp UTC:
Purpose:
Authority files read:
Selected path: H200 narrow / H253 fallback / other local-only
Base:
Anchor head:
Temporary worktree:
Generated artifacts:
Validation commands:
Validation results:
Source-equivalence target:
Artifact hashes:
Dirty-tree state:
Communication posture:
Hardware posture:
Stop conditions hit:
Next safe local action:
```

The communication posture must say one of:

- `historical sent-before-blackout; no resend`
- `no-send fallback only`
- `held question in communications ledger`

## Final Local Gate

Before recording a regenerated artifact as usable local prep, run:

```sh
python3 tools/validate/a733_authority_check.py
git diff --check -- <changed coordination files>
```

Then update `task-packets/kernel/a733-cycle-ledger.md` with the exact scope,
commands, hashes, proof result, dirty-tree state, and next pointer.
