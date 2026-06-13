# A733 H155 H154 proof package readiness

Captured: 2026-06-13T02:48Z

Model/tooling constraint: continued work used Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Prepare the H154 no-`mbus-msi-lite0` comparison candidate as a bootable proof package without staging it to any Cubie and without running hardware.

## Artifact

- Host: `strix`
- Worktree: `/srv/projects/kernel-work/runtime/a733-ccu-nsi-no-mbus-msi-lite0-draft`
- Branch: `codex/a733-ccu-nsi-no-mbus-msi-lite0-draft`
- Base head: `d9aa2e15caae5085b51a28529fc0c35d189df543`
- Artifact directory: `/srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-d9aa2e15caae-20260613T024821Z`
- Latest symlink: `/srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-latest`

Files:

- `Image`
- `sun60i-a733-cubie-a7s.dtb`
- `config`
- `build.log`
- `source.diff`
- `source-status.txt`
- `manifest.txt`
- `manifest.txt.sha256`

## Validation

On `strix`:

```sh
out="$(readlink -f /srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-latest)"
cd "$out"
sha256sum -c manifest.txt.sha256
sha256sum -c <(tail -6 manifest.txt | sed "s#  $out/#  #")
```

Results:

- `manifest.txt`: OK
- `Image`: OK
- `sun60i-a733-cubie-a7s.dtb`: OK
- `config`: OK
- `build.log`: OK
- `source.diff`: OK
- `source-status.txt`: OK

## Package hashes

```text
f9946e3d014abf12010c812d337880cce7aa1b531b0933e55be0a862d8df2815  Image
6edbb3790de674f7011c8accd0e02d94ea5bcafa11dc127238c8a54da71c622a  sun60i-a733-cubie-a7s.dtb
dda33f2fac329a3e79d633fe200497a5d4c599a2338de3caa10ef8cd3e634202  config
387c2dabf3b2f305eb31d2060d1364038a45dac15f930469cf250ae791f91501  build.log
d67d22dcdd5fe34e11e8428b5019775d2a8765d0f6de1df3cea33cf1838d5389  source.diff
2144198375e073f1c4cc656351c0b3d7fffa0477ff14b03917f8cf854c7c733a  source-status.txt
```

## Approval-gated proof commands

These commands are not approved by this note. They are recorded so the next run can execute a single controlled proof if the operator approves hardware work.

Stage the exact artifacts to Cubie3's `/boot/cthu` path:

```sh
out="$(readlink -f /srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-latest)"
target="codex@192.168.50.95"
scp "$out/Image" "$out/sun60i-a733-cubie-a7s.dtb" "$out/config" "$out/manifest.txt" "$target:/tmp/"
ssh -o BatchMode=yes "$target" '
  sudo install -m 0644 /tmp/Image /boot/cthu/Image
  sudo install -m 0644 /tmp/sun60i-a733-cubie-a7s.dtb /boot/cthu/a733.dtb
  sudo install -m 0644 /tmp/config /boot/cthu/config
  sudo install -m 0644 /tmp/manifest.txt /boot/cthu/manifest.txt
  sync
  sha256sum /boot/cthu/Image /boot/cthu/a733.dtb /boot/cthu/config /boot/cthu/manifest.txt
'
```

Run the direct U-Boot RAM boot/capture on Strix:

```sh
cd /srv/projects/homelab
CUBIE_BOOT_CAPTURE_SECONDS=180 \
  scripts/cubie-direct-uboot-load-session a733-h154-no-mbus-msi-lite0
```

Expected pass markers:

- `Linux version` for the H154 Image
- `sunxi-mmc 4020000.mmc: initialized`
- `mmc0: new high speed SDXC card`
- `mmcblk0`
- `mmcblk0: p1 p2 p3`
- `EXT4-fs (mmcblk0p3): mounted filesystem ... ro without journal`
- `Run /bin/sh as init process`

Expected fail/regression markers:

- `Waiting for root device` without later `mmcblk0`
- `Bad Linux ARM64 Image magic`
- failed `ext4load`
- failed `fdt addr`

## Guardrails

- Do not run the approval-gated commands without explicit operator approval.
- Do not use Cubie1 for this proof.
- Do not commit kernel source from this package until the hardware result is known.
- After any proof run, pull the UART log metadata back into the homelab repo and update `a733-hypothesis-queue.json`.
