# Kernel Pipeline Layout

Status: base layout initialized; cortex sidecar online
Operator surface: Codex Desktop only

## Hosts

- `192.168.50.252`: build/proof host and fast RTX 3090 model lane
- `192.168.50.11`: Strix review model lane and Cubie UART host
- `192.168.50.225`: lightweight services/gateway and kernel-cortex storage host
- `192.168.50.248`: Framework laptop, physical client only

## Remote Paths

On `192.168.50.252`:

```text
/srv/projects/kernel-work/mirrors
/srv/projects/kernel-work/scratch
/srv/projects/kernel-work/proof-logs
/srv/projects/kernel-work/outgoing
/srv/projects/kernel-work/task-packets
/srv/projects/kernel-work/cache
/srv/projects/kernel-proof
/srv/projects/kernel-work/scratch/strix-mainline-linux
/srv/projects/kernel-cortex
```

On `192.168.50.11`:

```text
/srv/projects/cubie-hardware-lab/uart-logs
/srv/projects/cubie-hardware-lab/power-events
/srv/projects/cubie-hardware-lab/inventory
/srv/projects/cubie-hardware-lab/boot-artifacts
/srv/projects/cubie-hardware-lab/notes
/srv/projects/cubie-uart/logs
```

On `192.168.50.225`:

```text
/srv/projects/kernel-services/gateway
/srv/projects/kernel-services/proof-index
/srv/projects/kernel-services/status
/srv/projects/kernel-services/cortex
```

## Host Tool Roles

`192.168.50.252` is the validation and fast-model host. Codex Desktop uses SSH
to run:

- Docker Engine for the `local/kernel-build-validate:20260606` proof container
- `kernel-proof-runner` inside that container
- `git diff --check`
- `scripts/checkpatch.pl --strict`
- `make ARCH=arm64 dt_binding_check`
- targeted `CHECK_DTBS=y` Cubie A7S DTB builds
- the RTX 3090 llama.cpp Vulkan endpoint at `127.0.0.1:8001`
- the RX 7900 XT ROCm embedding endpoint for kernel-cortex batches at
  `192.168.50.252:8091`

`192.168.50.11` is the review and hardware-observation host. Codex Desktop uses
SSH to run:

- the Strix llama.cpp Vulkan endpoint at `127.0.0.1:8082`
- maintainer-risk review handoffs through the OpenAI-compatible local API
- UART inventory and capture helpers for Cubie boards
- local artifact/evidence searches against existing Cubie kernel work

The Mac runs Codex Desktop and scripts only. It does not run Docker Desktop,
validation containers, or sustained model workloads.

`192.168.50.225` is the kernel-cortex container and storage host. It owns
Qdrant, ingestion queues, source-text staging, and vector storage. It calls the
AMD embedding endpoint for batch work and keeps Qdrant on ThinkCentre loopback
unless a human explicitly approves broader exposure.

## Commands

```sh
scripts/kernel-layout init
scripts/kernel-layout status
scripts/kernel-layout scan
scripts/kernel-machine-readiness
scripts/kernel-sync-strix-to-amd status
scripts/kernel-sync-strix-to-amd dry-run
scripts/kernel-sync-strix-to-amd sync
scripts/kernel-maintainer-review payload --task-id TASK-ID --proof-id PROOF-ID
scripts/kernel-maintainer-review review --task-id TASK-ID --proof-id PROOF-ID
scripts/kernel-cortex status
scripts/kernel-cortex deploy-plan
scripts/kernel-token-offload status
scripts/kernel-research-query "A733 upstream overlap"
scripts/kernel-log-triage --proof-json tools/proof-logs/PROOF-ID.json
scripts/kernel-diff-brief --repo /path/to/kernel/tree
scripts/kernel-review-matrix --file task-packets/kernel/reviews/PAYLOAD.md
scripts/kernel-idle-review-sweep --limit 1 --run --allow-unavailable
scripts/kernel-idle-review-sweep --loop --max-runs 3 --run --allow-unavailable
scripts/kernel-idle-ledger status
```

## Kernel Knowledge Cortex

The companion evidence-retrieval workflow is documented in
`runbooks/kernel-knowledge-cortex.md`.

The local hardware token-offload workflow is documented in
`runbooks/kernel-token-offload.md`.

The host install and readiness checklist is documented in
`runbooks/kernel-machine-install-checklist.md`.

Initial cortex proof is recorded in
`task-packets/kernel/research/cortex-bringup-proof-20260606.md`.

Default split:

- ThinkCentre `192.168.50.225`: Qdrant, ingestion worker, vector storage
- AMD `192.168.50.252`: RX 7900 XT ROCm embedding worker
- Mac mini: Codex Desktop dispatcher only

The AMD-to-Mac direct link exists at `192.168.200.1` to `192.168.200.2`, but
the default cortex path does not depend on it because ThinkCentre is the
container host.

## Synced Kernel Scratch

The current Strix kernel tree has been copied to AMD for validation:

- Source: `192.168.50.11:/srv/projects/cubie-a7s-armbian/sources/mainline-linux`
- Destination:
  `192.168.50.252:/srv/projects/kernel-work/scratch/strix-mainline-linux`
- Base commit: `8fde5d1d47f6`
- Copy size after build-artifact excludes: about `4.6G`

The sync is additive by default. It does not pass `--delete` unless
`KERNEL_SYNC_DELETE=1` is set explicitly.

The rsync exclusions are root-anchored for root-level build products such as
`/vmlinux` and `/System.map`, so source files named `vmlinux.*` are not
accidentally skipped.

After status commands, a dry-run may still show `.git/index` as a repeat
transfer. Treat that as Git cache volatility, not a source-content mismatch.

## Current Kernel State

The original Cubie A7S DTB build failed because `sun60i-a733.dtsi` referenced
`CLK_BUS_GMAC0` and `RST_BUS_GMAC0`, but the A733 dt-bindings headers did not
define those identifiers.

Current evidence:

- `synced-strix-mainline-dt-binding-check-73bf3de72d64`: A733 CCU binding
  schema `PASS`
- `synced-strix-mainline-dtbs-check-b6e4c7ddfccf`: Cubie A7S DTB build `FAIL`
- `a733-mmc-compatible-binding-dt-binding-check-562c5187dab1`: MMC binding
  schema `PASS`
- `a733-defer-unproven-gmac-cubie-a7s-dtbs-check-94d5f0714c56`: Cubie A7S DTB
  build `PASS` after deferring GMAC
- `a733-defer-unproven-gmac-checkpatch-current-diff-strict-d61c953b97c1`:
  strict checkpatch `FAIL`, with `0 errors, 7 warnings, 1 checks`
- Task packet:
  `task-packets/kernel/a733-gmac-clock-reset-bindings.json`
- Task packet:
  `task-packets/kernel/a733-mmc-compatible-binding.json`
- Strix review:
  `task-packets/kernel/reviews/a733-gmac-clock-reset-bindings-9b373d6a0c4b4ba6.strix-review.txt`

Do not invent GMAC clock or reset numbers. Either find evidence for the A733
GMAC clock/reset map, or remove/defer unproven Ethernet from the first
validation slice.

## Rule

Do not use hostnames in control paths. Use the IP addresses above.
