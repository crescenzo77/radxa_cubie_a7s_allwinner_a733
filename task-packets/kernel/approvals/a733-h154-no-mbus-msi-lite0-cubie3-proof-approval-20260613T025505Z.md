# A733 H154 no-mbus-msi-lite0 Cubie3 proof approval packet

Generated: 2026-06-13T02:55:05Z
Status: `needs-approval`

Model/tooling constraint: prepared in Codex Desktop / hosted ChatGPT only. No local model and no OpenRouter model was used.

## Purpose

Request approval for one controlled Cubie3 proof run of the H154 comparison candidate that removes only `mbus-msi-lite0` from the H153 evidence-preserving storage-fabric critical set.

This proof answers one narrow question:

- Can A733 still enumerate SDMMC0, discover `mmcblk0` partitions, mount root read-only, and run `/bin/sh` when `mbus-msi-lite0` is not marked critical, while `ahb-cpus`, `ahb-store`, `mbus-store`, `nsi`, and `bus-nsi` remain handled?

It does not approve patch publication, CCU RFC mail, Cubie1 use, repeated retry loops, kernel-source commits, service changes, cron changes, or model-routing changes.

## Board

- Board: `cubie3`
- Board IP: `192.168.50.95`
- UART/power host: `strix`
- UART helper: `/srv/projects/homelab/scripts/cubie-direct-uboot-load-session`
- Expected UART target: Cubie3 mapping already recorded in homelab inventory.
- Excluded board: `cubie1` must not be used for this proof.

## Artifact

- Host: `strix`
- Worktree: `/srv/projects/kernel-work/runtime/a733-ccu-nsi-no-mbus-msi-lite0-draft`
- Branch: `codex/a733-ccu-nsi-no-mbus-msi-lite0-draft`
- Base head: `d9aa2e15caae5085b51a28529fc0c35d189df543`
- Artifact directory: `/srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-d9aa2e15caae-20260613T024821Z`
- Latest symlink: `/srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-latest`
- Readiness note: `task-packets/kernel/a733-h155-h154-proof-package-readiness-20260613T0248Z.md`

Required package validation from H155:

- `manifest.txt`: OK
- `Image`: OK
- `sun60i-a733-cubie-a7s.dtb`: OK
- `config`: OK
- `build.log`: OK
- `source.diff`: OK
- `source-status.txt`: OK

## Approval Requested

Approve these steps as one bounded proof sequence:

1. Re-verify the H154 outgoing package manifest on Strix.
2. Stage the exact H154 `Image`, DTB, config, and manifest to Cubie3's existing `/boot/cthu` path.
3. Run one direct U-Boot RAM boot/capture session for `a733-h154-no-mbus-msi-lite0`.
4. Pull the UART log path/metadata into a follow-up homelab task packet and update the hypothesis queue.

## Exact Commands After Approval

Run on `strix`:

```sh
out="$(readlink -f /srv/projects/kernel-work/outgoing/a733-h154-no-mbus-msi-lite0-latest)"
cd "$out"
sha256sum -c manifest.txt.sha256
sha256sum -c <(tail -6 manifest.txt | sed "s#  $out/#  #")
```

Stage the exact artifacts to Cubie3:

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

Run the proof capture:

```sh
cd /srv/projects/homelab
CUBIE_BOOT_CAPTURE_SECONDS=180 \
  scripts/cubie-direct-uboot-load-session a733-h154-no-mbus-msi-lite0
```

## Pass Criteria

The proof can support removing `mbus-msi-lite0` from the upstream-shape series only if the UART log shows all of:

- H154 kernel starts from the staged Image.
- `sunxi-mmc 4020000.mmc: initialized`
- `mmc0: new high speed SDXC card`
- `mmcblk0`
- `mmcblk0: p1 p2 p3`
- root filesystem mounts read-only from `mmcblk0p3`
- `Run /bin/sh as init process`

If SDMMC0 initializes but the log stops at `Waiting for root device` without later `mmcblk0`, H154 failed the comparison and H153 remains the evidence-preserving default.

## Stop Conditions

- Stop after one proof attempt unless the operator explicitly approves a retry.
- Stop immediately if the artifact hashes do not match H155.
- Stop immediately if Cubie3 is not reachable for staging.
- Stop immediately if the helper selects or implies any board other than Cubie3.
- Do not use Cubie1.
- Do not alter boot defaults beyond staging the existing `/boot/cthu` payload files.
- Do not commit kernel source from the H154 worktree based on static validation alone.
- Do not send mail or publish patches based on this approval packet.

## Follow-up Required After Any Approved Run

- Capture the UART log path and result in a new task packet.
- Update `task-packets/kernel/a733-hypothesis-queue.json`.
- State whether H154 passed, failed, or produced an indeterminate result.
- If H154 passes, prepare a source review of the narrowed series before any kernel commit.
- If H154 fails, keep H153 as the default upstream-shape candidate and document `mbus-msi-lite0` as retained by evidence-preserving policy.
