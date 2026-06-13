# A733 Claim Service Activation Checklist

Status: local-only checklist; no-run; no-service-change
Updated: 2026-06-13

This packet records what must be true before the A733 workflow may treat the
ThinkCentre claim service as active. It is not an implementation, not approval
to start services, not approval to change Hermes, and not permission to mutate
kernel trees or hardware.

Boundary summary: this is not approval to start services, not permission to
mutate kernel trees or hardware, and not a replacement for the ThinkCentre
Fault Ledger/FastMCP activation drill. Claim-service activation alone never
enables board or storage risk.

Machine-check boundary: not permission to mutate kernel trees or hardware.
Machine-check boundary: claim-service activation alone never enables board or
storage risk.

## Why This Exists

Current authority files mark the claim service as `planned-not-active`. That
blocks:

- Strix or ThinkCentre kernel-tree/proof-tree claims for DTS v2 static proof
- destructive burn-board autonomy
- cross-runtime concurrency
- stale burn-claim recovery enforcement
- server-side `AGENT_ID -> AGENT_TIER` enforcement

The workflow can still perform single-writer-safe Green documentation and
read-only analysis without the service. It must not pretend contended resources
are claimed until activation is drilled and logged.

## Source Authorities

- `runbooks/kernel-a733-mainline-enablement-workflow.md`
- `runbooks/kernel-workflow-controls.md`
- `runbooks/hermes-kernel-work-prompt.md`
- `inventory/hardware/cubie-a7s-lab.json`
- `task-packets/kernel/a733-supervised-batch-queue.md`
- `task-packets/kernel/a733-dts-v2-static-proof-isolated-copy-packet.md`

## Activation Preconditions

Before inventory may change claim-service status from `planned-not-active` to
active, a future approved cycle must prove all of these:

1. The service endpoint is identified: SSH-exec command or FastMCP tool name,
   host, working directory, and exact command syntax.
2. SQLite-WAL storage is local to ThinkCentre and has a backup/inspect path.
3. `AGENT_ID -> AGENT_TIER` is enforced by the service, not by prompts.
4. The service supports atomic claim, release, heartbeat, and list operations.
5. Claims include work item ID, cycle ID, resource IDs, server-stamped tier,
   timestamp, heartbeat timestamp, promotion state when applicable, and owner.
6. Resource IDs cover at least: work item, board lane, UART by-path, power
   handle, kernel tree path, staged artifact path, and proof output path.
7. Non-stale claim denial is proven with two attempted owners on the same
   resource.
8. Stale software/proving/reference takeover is logged before takeover.
9. Stale burn-board claim handling marks the board `UNKNOWN` and queues
   recovery-to-pristine before future proof trusts that board.
10. Release failure causes stop-and-log behavior.
11. A read-only list/status command lets agents verify active claims before
    selection.
12. No Hermes cron, model routing, Telegram route, or kernel service behavior is
    changed as part of activation unless separately approved and logged.

## Minimal Drill

A future activation drill should use dummy resources first, not live boards:

```text
work item: A733-CLAIM-DRILL-001
resources:
  - work:A733-CLAIM-DRILL-001
  - kernel-tree:/tmp/a733-claim-drill-tree
  - artifact:/tmp/a733-claim-drill-artifact
```

Required proof:

- claim succeeds for owner A
- concurrent claim for owner B is denied while owner A is non-stale
- heartbeat extends owner A claim
- release removes owner A claim
- stale takeover behavior is demonstrated on dummy non-burn resource
- list/status output shows correct claim state at each step
- logs include server-stamped tier, not a self-declared model tier

Do not run a burn-board stale-claim drill until board roles, recovery rung,
recovery drill, and pristine restore path are already recorded.

## DTS v2 Static Proof Unblock

The DTS v2 isolated-copy static proof may use the claim service only after the
dummy drill passes and the future proof cycle can claim:

- work item ID for that proof cycle
- Strix source kernel tree path
- isolated proof tree path
- build output path
- log/artifact output path

The proof cycle must still obey the isolated-copy packet, preserve untracked
A733 prerequisite files, and stop before patch/build if prerequisite hashes
differ.

## Hardware Runtime Unblock

Hardware runtime remains blocked even after claim-service activation until the
inventory also records:

- exactly one `burn`, `proving`, and `reference` role
- UART by-path mapping for each used board
- boot media for each used board
- recovery rung and drill evidence for the selected experiment class
- pristine image or known-good baseline
- power-control or recovery path needed for the experiment

Claim service activation alone never enables bootloader, SPI, eMMC-boot,
firmware, fuse, rootfs-corrupting, or destructive storage work.

## Inventory Update Gate

Only after the activation drill is logged should a future cycle update:

```text
inventory/hardware/cubie-a7s-lab.json
```

Expected fields to change then:

- `agent_coordination.claim_service.status`
- endpoint/interface details, if observed
- activation timestamp or proof packet path
- cross-runtime concurrency, only if separately verified

Until then, the correct status remains `planned-not-active`.

## Stop Conditions

Stop and log instead of activating if:

- the endpoint is ambiguous
- the service cannot server-stamp tier
- atomic denial cannot be proven
- heartbeat or release behavior is missing
- list/status cannot be inspected by agents
- stale handling is unimplemented or unclear
- activation would require changing Hermes, cron, services, model routing, or
  Telegram behavior without a separate approved contract
- activation would require touching a board, UART, power path, or kernel tree
  before dummy-resource proof passes
