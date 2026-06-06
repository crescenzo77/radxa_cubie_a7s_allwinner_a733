# Agent Status

## Current status

The active slice is `Implement local token-offload workflow`.

## Current task

Deploy local token-offload tooling so Codex Desktop can dispatch bulk reading,
research, diff triage, log compression, and secondary/tertiary review to the
RTX 3090, RX 7900 XT, Strix, and ThinkCentre.

## What changed

- Added `scripts/model-dispatch-route-audit` and
  `tools/offload/model_dispatch_route_audit.py`; generated
  `inventory/model-dispatch-route-audit-2026-06-06.md`. The audit probes from
  ThinkCentre's viewpoint and currently reports `needs-reconciliation` because
  the direct kernel model lanes are not reachable from ThinkCentre as ordinary
  LAN URLs.
- Added `inventory/model-dispatch-repair-brief-2026-06-06.md` for the current
  ThinkCentre `model-dispatch` failure mode: `/srv/model-dispatch` is absent,
  PID 1812 is running from a deleted cwd, `/v1/models` responds, and chat
  completions drop the connection. The brief keeps repair operator-gated and
  notes that the Strix source config must be reconciled with current kernel
  offload endpoints before any live deploy.
- Hardened `scripts/routing-health` so ThinkCentre `model-dispatch` `/models`,
  `/chat/completions`, and deleted-live-path checks are visible as
  compatibility warnings without failing the direct kernel offload lanes.
- Current ThinkCentre `model-dispatch` process is stale: it advertises models
  but drops chat requests, and PID 1812 is running from deleted
  `/srv/model-dispatch`. Repair requires a separate operator-approved deploy or
  service restart because it is shared infrastructure.
- Added `runbooks/kernel-knowledge-cortex.md`.
- Added ThinkCentre Qdrant compose and environment templates under
  `services/kernel-cortex/thinkcentre/`.
- Added AMD RX 7900 XT ROCm embedding endpoint templates under
  `services/kernel-cortex/amd/`.
- Added `tools/cortex/kernel_cortex.py`, a minimal Qdrant plus
  OpenAI-compatible embeddings helper for curated text ingestion/search.
- Added `scripts/kernel-cortex` for status, directory layout, file install, and
  human-gated deployment plan commands.
- Updated `HOMELAB_LAYOUT.md`, `PLAN_INDEX.md`, `runbooks/kernel-layout.md`,
  `scripts/kernel-layout`, `DECISIONS.md`, and `CURRENT_SLICE.md`.
- Created remote cortex directories on `192.168.50.225` and `192.168.50.252`.
- Copied the cortex templates/helper code to those remote directories without
  starting services.
- Started a bounded 7900XT research endpoint on `192.168.50.252`:
  `qwen36-27b-7900xt-research` at `http://127.0.0.1:8092/v1`.
- Cloned the public `linux-sunxi` public-inbox git archive to
  `/tmp/lore-linux-sunxi-0.git` for this research run.
- Generated the first research packet:
  `task-packets/kernel/research/a733-overlap-scan-20260606.md`.
- Started Qdrant on ThinkCentre `192.168.50.225` as
  `kernel-cortex-qdrant-1`, loopback-bound on `127.0.0.1:6333-6334`.
- Started the AMD ROCm embedding service on `192.168.50.252` as
  `kernel-cortex-embedding`, exposing
  `http://192.168.50.252:8091/v1`.
- Corrected the vLLM embedding launch command for vLLM `0.22.1` by using the
  model as the positional argument with `--runner pooling --convert embed`.
- Calibrated ingest chunk defaults for `BAAI/bge-large-en-v1.5`'s 512-token
  input limit: `CORTEX_MAX_CHARS=700`, `CORTEX_OVERLAP=70`,
  `CORTEX_BATCH_SIZE=16`.
- Indexed the first A733 research packet into Qdrant collection
  `kernel_evidence`.
- Added bringup proof:
  `task-packets/kernel/research/cortex-bringup-proof-20260606.md`.
- Generated and indexed the follow-up A733 in-flight state packet:
  `task-packets/kernel/research/a733-inflight-ccu-pinctrl-state-20260606.md`.
- Used the 7900XT research model to summarize maintainer impact from the
  CCU/PRCM and pinctrl evidence.
- Added `tools/offload/kernel_token_offload.py`.
- Added wrappers:
  `scripts/kernel-token-offload`, `scripts/kernel-research-query`,
  `scripts/kernel-log-triage`, `scripts/kernel-diff-brief`,
  `scripts/kernel-review-local`, `scripts/kernel-review-matrix`, and
  `scripts/kernel-idle-review-sweep`.
- Added `runbooks/kernel-token-offload.md`.
- Updated task packets with a `token_offload_gate` covering large logs, large
  diffs, mailing-list/datasheet research, and matrix review.
- Verified all live lanes:
  AMD RTX 3090 at `192.168.50.252:127.0.0.1:8001`,
  AMD RX 7900 XT research at `192.168.50.252:127.0.0.1:8092`,
  Strix at `192.168.50.11:127.0.0.1:8082`, and ThinkCentre Qdrant at
  `192.168.50.225:127.0.0.1:6333`.
- Ran smoke cards for 3090 diff brief, 7900XT research query, 3090 log triage,
  three-lane review matrix, and one real idle review sweep.
- Added a persistent idle-review ledger at
  `task-packets/kernel/context-cards/idle-review-ledger.json`.
- Added `--next`, `--loop`, and `--max-runs` controls to
  `scripts/kernel-idle-review-sweep`.
- Ran the bounded idle sweep until the current review/research queue was empty.
- Added `scripts/kernel-idle-ledger` and `idle-ledger` commands for ledger
  status, backfill, and consumed-by-Codex markers.
- Backfilled the idle-review ledger from existing review-matrix cards so older
  reviews are recorded in the same long-term measurement ledger.
- Consumed all 9 reviewed local context cards through the ledger and recorded
  concise Codex consumption notes.
- Reviewed additional Mac-local, ThinkCentre, and Strix documentation for past
  Cubie A7S patch work. The important recovered guardrails are now summarized
  in `runbooks/cubie-a7s-hardware-lab.md`.
- Recorded `192.168.50.65` as excluded from all kernel-work probing, staging,
  boot, and proof flows because it is reserved for Wyze camera object
  detection.
- Recorded the current A733 guardrail: independent CCU/PRCM, pinctrl, and GMAC
  submission work is on hold until RFC overlap, clock/reset, pinctrl hardware,
  and validation evidence blockers are resolved.
- Updated the public kernel-development repo
  `crescenzo77/radxa_cubie_a7s_allwinner_a733` so the exported A733 series is
  described as a draft review snapshot, not a sendable candidate.
- Pushed public repo commit
  `513ca43f92d886cfc902ba63b2e25cd12fc4e24c`.
- Created a standalone AMD validation clone for public Linux branch
  `candidate/a733-platform-clean-v3` at
  `/srv/projects/kernel-work/validation/a733-v3-public-clone`.
- Recorded AMD validation proof
  `a733-v3-public-git-diff-check-997b45f3f8ff` for
  `git diff --check 6f3ed7fec72fc8979b2a8c7219c0a9fcfc8d07b5 HEAD`.
- Updated and pushed public repo commit
  `fd2504dbe9e7aad5f791f1e287170fe727b86395`.
- Ran and pulled 9 per-patch AMD validation-container `git diff --check`
  proofs for public v3; all passed.
- Updated and pushed public repo commit
  `032b523ff2c7761e63fb7a1fefef5ca71bdacc0d`.
- Ran and pulled 9 per-patch AMD validation-container `defconfig` proofs for
  public v3; all passed after moving build output out of noexec `/tmp`.
- Updated and pushed public repo commit
  `b896a2b3a7c9b315dc6caf62cc2eb738839f91f3`.
- Ran and pulled targeted per-patch AMD validation-container object-build
  proofs for public v3: CCU object on patches 3 through 9 and pinctrl object
  on patches 5 through 9; all passed.
- Updated and pushed public repo commit
  `c030ab8a0c79d286530e676d2a2f826090511582`.
- Ran and pulled per-patch AMD validation-container DT binding proofs for
  binding patches 1, 2, 4, and 6; all passed.
- Updated and pushed public repo commit
  `7cbef630922cddec153d79e282895541e7a9ca36`.
- Ran and pulled per-patch AMD validation-container Cubie A7S DTB proofs for
  patches 8 and 9, where the board DTB exists; both passed.
- Updated and pushed public repo commit
  `43c02e5c291bb27fe33ec7cd1014965d24aa5b79`.
- Ignored local public-repo `boot-artifacts/` so generated boot files stay out
  of the public-facing kernel record.
- Updated and pushed public repo commit
  `1841d0fa02eb690e5c8c4cf043fe71c8b30f77b4`.
- Ran a three-lane local public-repo audit card:
  `task-packets/kernel/context-cards/review-matrix-public-repo-audit-1841d0f-831626b6a619.md`.
- Verified the audit's checkpatch concern and found the earlier failure was an
  invocation issue, not a patch-content issue.
- Updated the public workflow/status docs to require running `checkpatch` from
  the Linux tree root against exported patch inputs.
- Updated and pushed public repo commit
  `d1a83dbd255fdabbc0f806ab2ac739545f09ba34`.
- Pushed the same public repo `main` to the ThinkCentre mirror using
  `192.168.50.225`.
- Rechecked public A733 RFC overlap state and recorded
  `task-packets/kernel/research/a733-rfc-recheck-20260606.md`.
- Indexed the A733 RFC recheck into ThinkCentre Qdrant; 2 chunks added.
- Generated local research proof card
  `task-packets/kernel/context-cards/research-query-a733-rfc-recheck-index-proof-46f6d2c435ea.md`.
- Ran idle review for the new A733 RFC recheck and consumed the resulting
  three-lane review card.
- Checked Cubie hardware lab state: Strix sees `/dev/ttyUSB0` and
  `/dev/ttyUSB1`; both 10-second passive UART captures produced 0 bytes.
- Confirmed current ping state: `cubie3` at `192.168.50.95` replied;
  `cubie2` at `192.168.50.85` did not.
- Checked Cubie SSH reachability: `cubie3` answers SSH but rejects current
  key/user attempts; `cubie2` times out on port 22.
- Recorded Strix UART identity details: both CP2102 adapters report serial
  `0001`, so `/dev/serial/by-path/` names are safer than `/dev/serial/by-id/`.
- Updated `scripts/cubie-uart` to list and accept `/dev/serial/by-path/*`
  capture targets.
- Verified by-path UART captures for both adapters; each resolved to the
  expected `/dev/ttyUSB*` device and captured 0 bytes during a 5-second passive
  window.
- Added `scripts/cubie-boot-capture-window` to open simultaneous passive
  capture windows on both Strix UART adapters without touching power control.
- Smoke-tested the boot capture window for 1 second; both captures completed
  and produced empty logs as expected.
- Ran a three-lane local review of `scripts/cubie-boot-capture-window`.
- Hardened the helper with signal cleanup, executable-helper checks, a
  `CUBIE_CAPTURE_MAX_SECONDS` guard, and first-failure exit-code preservation.
- Verified the hardened helper with `bash -n`, a max-duration refusal check,
  and another 1-second passive smoke capture.
- Added `tools/hardware/cubie_uart_report.py` and `scripts/cubie-uart-report`
  to summarize pulled UART logs, count non-empty captures, check log SHA256s,
  and flag boot/error markers.
- Integrated `scripts/cubie-uart-report` into
  `scripts/cubie-boot-capture-window` after log pull.
- Verified the reporter with `py_compile`, shell syntax checks, standalone
  report output, and an integrated 1-second capture-window smoke run.
- Ran a three-lane local review of the reporter, fixed SHA mismatch accounting
  for missing remote hashes, and consumed the review in the idle ledger.
- Ran idle review on the generated UART report, then checked Strix serial host
  state: `cp210x` is attached for both adapters and both report 115200 baud.
- Added `tools/hardware/cubie_network_status.py` and
  `scripts/cubie-network-status` for bounded Cubie ping and SSH-port checks.
- Verified current network state through the helper: `cubie2`
  `192.168.50.85` has no ping reply and port 22 times out; `cubie3`
  `192.168.50.95` replies to ping and has port 22 open.
- Ran a three-lane local review of the network helper, then changed it to load
  board IPs from `inventory/hardware/cubie-a7s-lab.json` and round ping waits
  upward.
- Passively sampled local ARP data and short mDNS browse windows for common
  switch service names. No confirmed Cubie power-switch IP/API/mapping was
  identified, so power automation remains disabled.
- Added `task-packets/kernel/reviews/cubie-hardware-readiness-20260606.md`
  as a compact Cubie hardware readiness packet.
- Ran a three-lane local review of that readiness packet; all lanes converged
  on the same safe next runtime-evidence step: run the boot-capture window and
  have the human operator manually reset or power one board.
- Indexed the readiness packet into ThinkCentre Qdrant and verified retrieval
  with the 7900XT research lane.
- Added `tools/hardware/cubie_runtime_evidence.py` and
  `scripts/cubie-runtime-evidence` to build a reviewable runtime evidence
  packet from inventory, bounded network status, and pulled UART logs.
- Verified the runtime evidence builder with imports, `py_compile`, packet
  generation, and diff hygiene. The generated packet correctly marks the
  current state as `runtime-evidence-missing`.
- Ran and consumed local reviews for the builder and generated runtime evidence
  packets. All lanes agree no runtime boot proof can be claimed until a human
  manual board reset/power event occurs during active UART capture.
- Added `tools/hardware/cubie_event_log.py` and `scripts/cubie-event-log` so
  human manual board actions can be recorded as JSONL events under the ignored
  `tools/hardware-logs/` directory.
- Integrated recent manual events into `scripts/cubie-runtime-evidence`.
- Ran a three-lane local review of the event logger, then hardened it with
  path containment under `tools/hardware-logs/` and append locking.
- Verified the event logger with `py_compile`, shell syntax checks, allowed
  and refused log-path smoke tests, runtime evidence integration, and idle
  review of the generated event-aware evidence packet.
- Hardened `scripts/cubie-boot-capture-window` so post-capture helper failures
  (`pull-logs`, UART report, runtime evidence generation) warn without masking
  the actual UART capture exit status.
- Changed the interrupted-capture path to ignore repeat signals during cleanup,
  kill/wait for child captures, record `capture-end`, and exit 130.
- Verified the hardened capture window with `bash -n`, `git diff --check`, and
  two 1-second passive Strix UART smoke windows. Both UARTs still captured
  cleanly but produced 0-byte logs.
- Ran local three-lane reviews on the hardened capture wrapper and on the new
  runtime-evidence packets using the RTX 3090, RX 7900 XT, and Strix lanes.
- Consumed all current idle-review artifacts in the ledger. Current ledger:
  26 reviewed, 26 consumed, 0 pending idle candidates.
- The next runtime-evidence step is unchanged: run
  `scripts/cubie-boot-capture-window 120 cubie-manual-boot`, then manually
  reset or power exactly one Cubie during that window. Do not automate power.
- Added `scripts/cubie-manual-boot-session`, a safer one-command wrapper for
  the same human-gated step. It runs a bounded pre-capture network check,
  opens the passive UART capture window, runs a bounded post-capture network
  check, prints recent manual events, and writes final runtime evidence.
- Smoke-tested `scripts/cubie-manual-boot-session 1 smoke-manual-session`.
  It completed without power action, produced two more empty UART captures,
  and generated event-aware runtime evidence packets.
- Ran and consumed local three-lane reviews for the new session wrapper and
  generated runtime evidence packets. Current ledger: 29 reviewed, 29
  consumed, 0 pending idle candidates.
- Added `tools/hardware/cubie_uart_map_candidates.py` and
  `scripts/cubie-uart-map-candidates` to correlate capture labels, manual
  event-log notes, UART metadata, and non-empty boot logs into read-only
  board-to-UART mapping candidates.
- Integrated mapping-candidate output into `scripts/cubie-manual-boot-session`
  and changed the printed manual action command to include `label=...` so the
  future human action can be correlated with the capture.
- Verified the mapping analyzer against current empty logs
  (`candidate_count=0`, `non_empty=0`) and a synthetic U-Boot fixture
  (`candidate_count=1`, `strength=strong-candidate`).
- Smoke-tested the integrated mapping session with
  `scripts/cubie-manual-boot-session 1 smoke-map-session`. It completed with
  no power action, generated two more empty UART captures, and printed no
  mapping candidates.
- Ran and consumed local three-lane reviews for the mapping analyzer, updated
  manual session wrapper, and generated runtime evidence packets. Current
  ledger: 32 reviewed, 32 consumed, 0 pending idle candidates.
- Integrated the read-only UART mapping candidate summary into
  `scripts/cubie-runtime-evidence` packets so future boot proof carries the
  candidate board/UART mapping in the same artifact.
- Updated the runtime evidence next-action text to use
  `scripts/cubie-manual-boot-session 120 cubie-manual-boot`.
- Verified runtime evidence with current empty logs
  (`mapping candidates: 0`) and a synthetic U-Boot fixture
  (`mapping candidates: 1`, `strong-candidate`).
- Ran and consumed local reviews for the updated runtime evidence builder and
  generated packet. Current ledger: 33 reviewed, 33 consumed, 0 pending idle
  candidates.
- Added `tools/hardware/cubie_runtime_gate.py` and
  `scripts/cubie-runtime-gate` to deterministically classify whether Cubie
  runtime evidence is ready, blocked on manual capture, unmapped, or invalid.
- Integrated `scripts/cubie-runtime-gate` into
  `scripts/cubie-manual-boot-session` so each future manual boot session ends
  with a machine-readable state classification.
- Verified current gate state as `manual-capture-required`
  (`non_empty=0`, `candidates=0`), verified `--strict` exits non-zero before
  proof is ready, verified malformed inventory reports `inventory-invalid`,
  and verified a synthetic U-Boot fixture reports `runtime-ready`.
- Ran and consumed local reviews for the runtime gate and generated evidence
  packets. Current ledger: 36 reviewed, 36 consumed, 0 pending idle candidates.
- Added `tools/hardware/cubie_uart_inventory_proposal.py` and
  `scripts/cubie-uart-inventory-proposal`, a read-only proposal generator for
  future strong board-to-UART candidates.
- Integrated the inventory proposal report into
  `scripts/cubie-manual-boot-session`. It reports `no-proposal` for current
  empty logs and never edits inventory.
- Verified a synthetic U-Boot fixture produces `proposal-ready` for `cubie3`
  with `apply_automatically=false`.
- Ran and consumed local reviews for the inventory proposal tool and generated
  evidence packets. Current ledger: 39 reviewed, 39 consumed, 0 pending idle
  candidates.
- Added an in-memory unified diff preview to
  `scripts/cubie-uart-inventory-proposal` so future strong UART mappings show
  the exact inventory change for human review without editing any files.
- Verified current real state remains `no-proposal` with an empty diff, while a
  synthetic U-Boot fixture produces a diff setting `device`, `host`,
  `resolved_device`, and `mapping_status` for `cubie3`.

## What did not change

- No files were deleted.
- No Mac mini containers were started.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No systemd state was changed.
- No routing, provider, or model-dispatch state was changed.
- No public kernel code, patch-series content, validation proof content, or
  submission metadata were changed after the proof-recording commits; only a
  local-artifact ignore rule was added.
- No public repo changes were made based on the latest maintainer-style
  assessment; that assessment was treated as advisory only.

## Files changed

- `HOMELAB_LAYOUT.md`
- `PLAN_INDEX.md`
- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`
- `runbooks/kernel-layout.md`
- `runbooks/kernel-knowledge-cortex.md`
- `scripts/kernel-layout`
- `scripts/kernel-cortex`
- `services/kernel-cortex/`
- `tools/cortex/kernel_cortex.py`
- `task-packets/kernel/research/a733-overlap-scan-20260606.md`
- `task-packets/kernel/research/cortex-bringup-proof-20260606.md`
- `task-packets/kernel/research/a733-inflight-ccu-pinctrl-state-20260606.md`
- `task-packets/kernel/context-cards/`
- `runbooks/kernel-token-offload.md`
- `tools/offload/kernel_token_offload.py`
- `scripts/kernel-token-offload`
- `scripts/kernel-research-query`
- `scripts/kernel-log-triage`
- `scripts/kernel-diff-brief`
- `scripts/kernel-review-local`
- `scripts/kernel-review-matrix`
- `scripts/kernel-idle-review-sweep`

## Checks run

- `git diff --check`
- `python3 -m py_compile tools/cortex/kernel_cortex.py`
- `bash -n scripts/kernel-cortex`
- `bash -n scripts/kernel-layout`
- `bash -n services/kernel-cortex/amd/run-vllm-embedding-rocm.sh`
- `docker compose -f services/kernel-cortex/thinkcentre/compose.yaml config`
- `docker compose -f services/kernel-cortex/thinkcentre/compose.yaml --profile manual config`
- `scripts/kernel-cortex status`
- `scripts/kernel-cortex deploy-plan`
- `curl http://127.0.0.1:8092/v1/models` on AMD over SSH
- 7900XT research model call against the A733 overlap evidence packet
- `pgrep -af 'llama-server.*8092|qwen36-27b-7900xt-research'` on AMD
- `curl http://127.0.0.1:6333/healthz` on ThinkCentre
- `curl http://192.168.50.252:8091/v1/models` on AMD
- embedding probe from ThinkCentre to AMD
- ThinkCentre default ingest worker against staged A733 packet
- semantic Qdrant search for A733 in-flight RFC conflicts
- 7900XT research synthesis for A733 CCU/pinctrl maintainer impact
- default ingest after adding the A733 in-flight state packet
- `python3 -m py_compile tools/offload/kernel_token_offload.py`
- `bash -n` for all token-offload wrappers
- `scripts/kernel-token-offload status`
- `scripts/kernel-diff-brief --repo /tmp/kernel-offload-smoke --target amd-fast`
- `scripts/kernel-research-query ... --target amd-research`
- `scripts/kernel-log-triage ... --target amd-fast`
- `scripts/kernel-review-matrix --repo /tmp/kernel-offload-smoke`
- `scripts/kernel-idle-review-sweep --limit 1 --run --allow-unavailable`
- `scripts/kernel-idle-review-sweep --next`
- `scripts/kernel-idle-review-sweep --loop --max-runs 3 --run --allow-unavailable`
- `scripts/kernel-idle-ledger status`
- `scripts/kernel-idle-ledger backfill`
- `scripts/kernel-idle-ledger mark-consumed ...`
- public repo `git diff --check HEAD~1..HEAD`
- public repo scan for coding-assistance/private-lab markers
- public repo `git ls-remote public refs/heads/main`
- AMD validation host fetch of `candidate/a733-platform-clean-v3`
- AMD validation standalone clone creation
- failed proof-log attempt using a Git worktree mount:
  `a733-v3-public-git-diff-check-d42963c6a859`
- failed proof-log attempt using an unhydrated partial clone:
  `a733-v3-public-git-diff-check-1f7f8337e3ca`
- host-side hydration/diff check in the standalone clone
- passing offline container proof:
  `a733-v3-public-git-diff-check-997b45f3f8ff`
- passing per-patch container proofs:
  `a733-v3-public-patch01-git-diff-check-980fd9adb30c` through
  `a733-v3-public-patch09-git-diff-check-6160e3d58ca9`
- failed first per-patch `defconfig` attempt:
  `a733-v3-public-patch01-defconfig-arm64-build-f6ad5e135f96`; cause was
  build output under noexec `/tmp`, not a patch failure
- passing per-patch `defconfig` proofs:
  `a733-v3-public-patch01-defconfig-arm64-build-536dcbfa0035` through
  `a733-v3-public-patch09-defconfig-arm64-build-f9eda2075f2a`
- passing targeted CCU object proofs:
  `a733-v3-public-patch03-ccu-object-object-build-c2af45731dff` through
  `a733-v3-public-patch09-ccu-object-object-build-5de0c6dc7af0`
- passing targeted pinctrl object proofs:
  `a733-v3-public-patch05-pinctrl-object-object-build-47692854398c` through
  `a733-v3-public-patch09-pinctrl-object-object-build-4f0865931157`
- passing per-patch DT binding proofs:
  `a733-v3-public-patch01-dt-binding-dt-binding-check-80cf1c07960b`,
  `a733-v3-public-patch02-dt-binding-dt-binding-check-73a6ccb3ca4c`,
  `a733-v3-public-patch04-dt-binding-dt-binding-check-70cdf0b0512c`, and
  `a733-v3-public-patch06-dt-binding-dt-binding-check-c3d3c6d9ba12`
- failed first patch 8 DTB proof:
  `a733-v3-public-patch08-cubie-dtbs-dtbs-check-114058187c2a`; cause was a
  missing `.config`, fixed by including `defconfig` in the proof command
- passing per-patch Cubie A7S DTB proofs:
  `a733-v3-public-patch08-cubie-dtbs-dtbs-check-de84f6d49370` and
  `a733-v3-public-patch09-cubie-dtbs-dtbs-check-41e21eb001ae`
- `kernel_cortex.py upsert-file ingest/a733-rfc-recheck-20260606.md`:
  indexed 2 chunks
- `scripts/kernel-research-query "A733 RFC recheck CCU pinctrl hold 2026-06-06"`
- `scripts/kernel-idle-review-sweep --next --run --allow-unavailable`
- `scripts/kernel-idle-ledger mark-consumed ...`
- `scripts/cubie-uart list`
- `scripts/cubie-uart capture /dev/ttyUSB0 passive-probe-ttyUSB0 10`
- `scripts/cubie-uart capture /dev/ttyUSB1 passive-probe-ttyUSB1 10`
- `scripts/cubie-uart pull-logs`
- read-only SSH probes to `192.168.50.85` and `192.168.50.95`
- `python3 -m json.tool inventory/hardware/cubie-a7s-lab.json`
- Qdrant collection and point-count checks
- `git status --short`

## Results of checks

- Python and shell syntax checks passed.
- ThinkCentre Qdrant compose and manual ingestion profile both render through
  Docker Compose.
- Qdrant health passed on ThinkCentre.
- AMD embedding service advertises `BAAI/bge-large-en-v1.5`.
- Embedding probe returned a 1024-dimensional vector.
- Default ingest indexed 7 chunks into `kernel_evidence`.
- Qdrant reports `count=13` after indexing the current research packets.
- Semantic search returned the expected A733 CCU/PRCM and pinctrl conflict
  chunks.
- The updated A733 in-flight state search returned the workflow action chunk as
  the top result: do not submit local A733 CCU/pinctrl patches as standalone
  Linux kernel work right now.
- Token-offload status found all live local lanes available.
- 3090 diff brief generated
  `task-packets/kernel/context-cards/diff-brief-offload-smoke-diff-3090-58c2de9e2cd6.md`.
- 7900XT research query generated
  `task-packets/kernel/context-cards/research-query-offload-smoke-research-7900xt-2698406719ba.md`.
- 3090 log triage generated
  `task-packets/kernel/context-cards/log-triage-offload-smoke-log-3090-c511e772485b.md`.
- Three-lane matrix smoke generated
  `task-packets/kernel/context-cards/review-matrix-offload-smoke-review-matrix-668731d6b93a.md`.
- Idle sweep generated a real three-lane review card for
  `a733-defer-unproven-gmac-962ab817120d7d9b.md`; each lane consumed about
  5.3k local model tokens and no lane failed.
- The idle-review ledger now tracks 9 reviewed artifacts and 0 failed
  artifacts.
- Existing review-matrix cards are fully represented in the ledger:
  `backfillable_missing_or_stale=0`.
- All 9 file-based reviewed cards are now marked consumed by Codex.
- GitHub public repo `main` now points at
  `d1a83dbd255fdabbc0f806ab2ac739545f09ba34`.
- The new public proof record is a container-backed `PASS` for full-series
  `git diff --check` against the recorded base.
- Per-patch diff hygiene is now recorded publicly, but full per-patch build/DT
  validation remains open for real bisectability.
- Per-patch `defconfig` is now recorded publicly. It proves Kconfig/default
  config generation, not object builds or DT validation at each patch.
- Targeted per-patch object builds are now recorded publicly for the introduced
  CCU and pinctrl driver objects. Per-patch DT binding/DTB validation remains
  open.
- Per-patch DT binding checks are now recorded publicly for binding patches.
  Per-patch Cubie A7S DTB validation is now recorded publicly where the board
  DTB exists. Hardware boot/runtime evidence remains open.
- Cortex search now returns the fresh A733 RFC recheck packet; workflow remains
  on hold for independent CCU/PRCM and pinctrl submission work.
- Idle-review ledger now tracks 11 reviewed file artifacts, all consumed, with
  no pending candidates.
- Strix UART devices are present and readable, but board-to-UART mapping is
  still unconfirmed because passive captures were silent.
- Public DTS export remains Ethernet-consistent: no board Ethernet enablement
  was found in the exported Cubie A7S DTS.
- `scripts/kernel-idle-review-sweep --next` now reports
  `idle_review_candidates=0` for the current queue.
- `scripts/kernel-cortex deploy-plan` prints a human-gated command sequence.
- The research endpoint is alive and advertises
  `qwen36-27b-7900xt-research`.
- Process check confirms llama.cpp was launched with `--device Vulkan2`.
- The first model call returned hidden/no visible content until
  `enable_thinking=false` was passed; the second call returned a clean
  Markdown blocker summary.
- `git diff --check` passed.
- `git status --short` still shows pre-existing dirty/untracked homelab work in
  addition to this integration.

## Known risks or blockers

- The vLLM ROCm image is large (`38.6GB`) and was pulled on AMD. Keep an eye on
  Docker storage before adding more ROCm service images.
- Qdrant is intentionally loopback-bound on ThinkCentre. Codex queries should
  use SSH or a later approved local API rather than exposing Qdrant broadly.
- The current BGE embedding model has a 512-token input limit. Larger chunks
  fail with HTTP 400, so keep the calibrated chunk defaults unless the model
  changes.
- A733 CCU/PRCM, pinctrl, and GMAC remain blocked for candidate submission
  until the workflow has coordination/rebase notes for in-flight Linux RFCs,
  reviewed clock/reset identifiers, pinctrl hardware evidence, and fresh proof
  IDs.
- One review-matrix smoke card came from a temporary git diff rather than a
  file artifact, so it is intentionally skipped by the idle-review ledger.
- Context-card compression ratios are useful only for large inputs. Tiny smoke
  diffs can produce cards larger than the source because the card includes
  metadata, model summaries, and lane usage.
- `kernel-idle-review-sweep` is intentionally manual and bounded, not a daemon.
  Use `--loop --max-runs N` for continuous work within a single explicit run.
- This integration is not committed yet because the homelab repo already has a
  broad dirty/untracked worktree; commit only a selected file list if/when
  backing this up.

## User approval needed

No further approval is needed for the deployed initial cortex proof.

## Recommended next action

When local model lanes are idle, use
`scripts/kernel-idle-review-sweep --next --run --allow-unavailable` or a
bounded loop such as
`scripts/kernel-idle-review-sweep --loop --max-runs 3 --run --allow-unavailable`.
The ledger prevents repeat reviews unless an artifact changes.

Use `scripts/kernel-idle-ledger status` to inspect long-term review coverage,
and `scripts/kernel-idle-ledger mark-consumed PATH` after Codex has used a card
or source artifact.

## Archived Status History

Older status entries remain below for continuity. They are not the active task.

## Previous status - Archive superseded top-level plan files

## Current status

The active slice is `Archive superseded top-level plan files`.

## Current task

Correct the plan-file procedure so old top-level plan files are archived before
fresh current entrypoint files are created at the same stable paths.

## What changed

- Archived old `PROJECT_PLAN.md`, `WORKFLOW.md`, `ROADMAP.md`, and
  `HOMELAB_LAYOUT.md` under `docs/archive/`.
- Created fresh current entrypoint files at those original top-level paths.
- Updated `PLAN_INDEX.md` with a `Current State Records` registry.
- Updated `PLAN_INDEX.md` rules to say old plan files are not edited in place to
  make them current.
- Updated `DECISIONS.md` with the archive-before-replacement decision.
- Updated `CURRENT_SLICE.md` for this slice.

## What did not change

- No files were deleted.
- No services were changed.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No Docker or systemd state was changed.
- No routing, deployment, provider, or model runtime state was changed.
- No files were staged or committed.

## Files changed

- `PLAN_INDEX.md`
- `PROJECT_PLAN.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `HOMELAB_LAYOUT.md`
- `DECISIONS.md`
- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `docs/archive/project-plan-superseded-2026-05-29.md`
- `docs/archive/workflow-two-surface-superseded-2026-05-29.md`
- `docs/archive/roadmap-two-surface-superseded-2026-05-29.md`
- `docs/archive/homelab-layout-two-surface-superseded-2026-05-29.md`

## Checks run

- `git status --short`
- `git diff --check`
- `git diff --stat`
- Reviewed fresh top-level entrypoint files.
- Verified archived superseded files exist under `docs/archive/`.
- Reviewed `PLAN_INDEX.md` current state records and archive registry.

## Results of checks

- `git diff --check` passed.
- Old top-level plan bodies were moved to `docs/archive/`.
- Fresh current entrypoint files exist at the stable top-level paths.
- `PLAN_INDEX.md` names the current state records and archive paths.

## Known risks or blockers

- This correction is not committed yet.

## User approval needed

Approval is needed before staging or committing this docs correction.

## Recommended next action

Run final checks, inspect the diff, then choose Commit / Revise / Revert /
Inspect more.

## Previous status - Clarify Aider preferred patch executor posture

## Current status

The active slice is `Clarify Aider preferred patch executor posture`.

## Current task

Correct workflow docs so they state that Aider is the preferred bounded patch
executor for planned strict slices, while OpenCode remains blocked for local
model patching. Also make the active workflow start order point to
`PLAN_INDEX.md` first.

## What changed

- Updated `docs/aider-workflow.md` to describe Aider as the preferred bounded
  patch executor after planning.
- Updated `docs/patch-review-workflow.md` so OpenCode is no longer described as
  the preferred next local-model coding-agent candidate.
- Updated `docs/provider-neutral-adhd-workflow.md` so the active workflow names
  Aider as the preferred bounded patch executor for planned strict slices.
- Added a `Start Here` order to `docs/provider-neutral-adhd-workflow.md` so
  future sessions begin with `PLAN_INDEX.md`.
- Updated `DECISIONS.md` with the clarified Aider patch-executor decision.
- Updated `CURRENT_SLICE.md` for this clarification slice.

## What did not change

- No services were changed.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No Docker or systemd state was changed.
- No routing, deployment, provider, or model runtime state was changed.
- No files were deleted.
- No files were staged or committed.

## Files changed

- `docs/aider-workflow.md`
- `docs/patch-review-workflow.md`
- `docs/provider-neutral-adhd-workflow.md`
- `DECISIONS.md`
- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`

## Checks run

- `git diff --check`
- Active-doc grep for stale OpenCode preferred-next wording in:
  - `docs/aider-workflow.md`
  - `docs/patch-review-workflow.md`
  - `docs/provider-neutral-adhd-workflow.md`
- Active-doc grep for Aider preferred bounded patch executor wording.
- Active workflow grep for `PLAN_INDEX.md` and `Start Here`.
- `git status --short`
- `git diff --stat`

## Results of checks

- `git diff --check` passed.
- Active workflow docs no longer say OpenCode is the preferred next local-model
  coding-agent candidate.
- Active workflow docs now state that Aider is the preferred bounded patch
  executor for planned strict slices.
- Active workflow now points future sessions to `PLAN_INDEX.md` first.
- Working tree contains docs-only changes.

## Known risks or blockers

- Older superseded docs and archived status history still contain historical
  Aider/OpenCode language, but `PLAN_INDEX.md` marks those docs as superseded
  or the sections as historical.

## User approval needed

User approved committing this docs clarification and pushing backups.

## Recommended next action

Commit this docs clarification and push it to the configured mirrors.

## Previous status - Provider-neutral workflow plan tracking checkpoint

## Current status

The active slice is `Provider-neutral workflow plan tracking checkpoint`.

## Current task

Preserve the provider-neutral workflow as the current plan while keeping older
plans and the long-context master history/evolution file available for review.

## What changed

- Added `PLAN_INDEX.md` as the canonical registry for current, superseded,
  archived, and quarantined plans.
- Marked `docs/provider-neutral-adhd-workflow.md` as the current active plan.
- Marked `docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md` as the
  protected long-context master history/evolution file.
- Preserved `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md` as
  an archived first draft.
- Updated `CODEX_CONTEXT.md` so future agents read `PLAN_INDEX.md` before
  choosing a workflow plan.
- Updated `PROJECT_PLAN.md`, `WORKFLOW.md`, `ROADMAP.md`, and
  `HOMELAB_LAYOUT.md` with current-plan pointers or historical/superseded
  notes.
- Updated `CURRENT_SLICE.md` and `DECISIONS.md` for this checkpoint.

## What did not change

- No files were deleted.
- The long-context master history/evolution file was not deleted.
- No live services were changed.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No Docker or systemd state was changed.
- No routing, deployment, provider, or model runtime state was changed.
- No files were staged or committed.

## Files changed

- `PLAN_INDEX.md`
- `CODEX_CONTEXT.md`
- `PROJECT_PLAN.md`
- `WORKFLOW.md`
- `ROADMAP.md`
- `HOMELAB_LAYOUT.md`
- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `DECISIONS.md`
- `docs/provider-neutral-adhd-workflow.md`
- `docs/provider-neutral-adhd-workflow-evolution-2026-05-29.md`
- `docs/archive/local-agent-workflow-runbook-draft-2026-05-29.md`

## Checks run

- Live homelab repo status.
- `git diff --check` on modified tracked docs.
- Trailing whitespace check across new and changed docs.
- Verified `PLAN_INDEX.md` contains exactly one `Current` plan.

## Results of checks

- Whitespace checks passed.
- `PLAN_INDEX.md` has exactly one current plan entry.
- The working tree contains docs-only changes.

## Known risks or blockers

- The new tracking system is not committed yet.
- Some older docs remain historical and can still be confusing if read without
  first reading `PLAN_INDEX.md`.
- The long-context master history/evolution file may grow over time and should
  be preserved deliberately rather than rewritten casually.

## User approval needed

Approval is needed before staging or committing these docs.

## Recommended next action

Inspect the diff, then choose Commit / Revise / Revert / Inspect more.

## Previous status - AMD Aider tiny code patch validation complete

## Current status

The active slice is `AMD Aider tiny code patch validation complete`.

## Current task

Preserve the first tiny code-file Aider validation through AMD
`local/amd-coder`.

## What changed

- Ran one bounded Aider code edit through model-dispatch `local/amd-coder`.
- Aider created only `/srv/projects/cubie-camera-node/scripts/cubie-node-summary`.
- The helper prints fixed project/source/deployment status lines.
- Committed the target repo change as
  `d6246ef add Cubie node summary helper`.
- Pushed `cubie-camera-node` to `thinkcentre:/srv/git/cubie-camera-node.git`.
- Added `inventory/aider-amd-coder-code-validation-2026-05-28.md`.
- Updated `DECISIONS.md` with the AMD Aider code-patch validation.
- Updated `CURRENT_SLICE.md` for the completed checkpoint.
- Preserved the prior OpenCode blocker checkpoint below as history.

## What did not change

- No live services were changed.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No model containers were changed.
- No Codex local-provider setup was attempted.
- No Cubie deployment was performed.
- No hidden daemon, watcher, auto-deploy job, or approval system was created.
- No OpenCode work was resumed.
- Aider was not promoted into the core workflow.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `DECISIONS.md`
- `inventory/aider-amd-coder-code-validation-2026-05-28.md`

## Checks run

- Live homelab repo status.
- Live `cubie-camera-node` status.
- Aider edit against `/srv/projects/cubie-camera-node`.
- `git status --short` in `cubie-camera-node`.
- `git diff --check` in `cubie-camera-node`.
- `git diff --stat` in `cubie-camera-node`.
- `bash -n scripts/cubie-node-summary`.
- `scripts/cubie-node-summary`.
- Push verification for `cubie-camera-node`.
- `git diff --check`
- `git diff --stat`
- `git status --short`

## Results of checks

- Aider exited `0`.
- The target repo diff was one new executable shell script.
- `bash -n` passed.
- The helper printed the expected output.
- `git diff --check` passed.
- Push to the ThinkCentre mirror succeeded.

## Known risks or blockers

- This validates only a tiny one-file shell-script edit.
- Aider remains unvalidated on AMD for multi-file code edits, tests, service
  edits, long context, and autonomous workflows.
- OpenCode remains blocked as a local patch tool.
- Codex with a local model on Strix is not proven.

## User approval needed

Approval is needed before changing OpenCode global config, changing
model-dispatch defaults, changing Open WebUI defaults, switching Strix to a
vLLM tool-call runtime for OpenCode testing, configuring Codex local-provider
profiles, or promoting any coding agent into normal workflow.

## Recommended next action

Stop here, or document/update the Cubie repo's own slice files to reflect the
new helper.

## Previous status - OpenCode local-model follow-up blocked

## Current task

Preserve the OpenCode local-model follow-up as a blocker checkpoint.

## Previous status - OpenCode local-model preflight complete

## Current task

Preserve the first OpenCode local-model preflight as a partial/negative
checkpoint.

## Previous status - AMD local coder bounded patch validation complete

## Current task

Preserve the first bounded Aider validation through AMD `local/amd-coder`.

## What changed

- Ran one bounded Aider edit through model-dispatch `local/amd-coder`.
- Aider edited only `/srv/projects/cubie-camera-node/README.md`.
- Aider history files were kept outside the repo.
- Committed the target repo change as
  `cd4b5a1 validate AMD coder bounded patch`.
- Pushed `cubie-camera-node` to `thinkcentre:/srv/git/cubie-camera-node.git`.
- Added `inventory/aider-amd-coder-validation-2026-05-28.md`.
- Updated `DECISIONS.md` with the AMD bounded patch-tool validation.
- Updated `CURRENT_SLICE.md` for the completed checkpoint.
- Preserved the prior provider-neutral workflow checkpoint below as history.

## What did not change

- No live services were changed.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No model containers were changed.
- No OpenCode install or trial was performed.
- No Codex local-provider setup was attempted.
- Aider was not promoted into the core workflow.
- No broad repo map, multi-file edit, service edit, or autonomous coding
  workflow was tested.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `DECISIONS.md`
- `inventory/aider-amd-coder-validation-2026-05-28.md`

## Checks run

- Live homelab repo status.
- Live Strix, ThinkCentre, and AMD container validation.
- model-dispatch chat check for `local/amd-coder`.
- Aider edit against `/srv/projects/cubie-camera-node`.
- `git status --short` in `cubie-camera-node`.
- `git diff --check` in `cubie-camera-node`.
- `git diff --stat` in `cubie-camera-node`.
- Push verification for `cubie-camera-node`.
- `git diff --check`
- `git diff --stat`
- `git status --short`

## Results of checks

- AMD `qwen3-coder-30b` was healthy on port `8083`.
- `local/amd-coder` returned clean `ok` through model-dispatch.
- Aider exited `0`.
- The target repo diff was one README sentence.
- `git diff --check` passed.
- Push to the ThinkCentre mirror succeeded.

## Known risks or blockers

- This validates only a tiny one-file documentation edit.
- Aider remains unvalidated on AMD for broad repo maps, multi-file edits,
  service edits, long context, and autonomous workflows.
- OpenCode still needs installation/evaluation before it can become a local
  coding-agent surface.
- Codex with a local model on Strix is not proven.

## User approval needed

Approval is needed before installing OpenCode, configuring Codex local-provider
profiles, changing model-dispatch defaults, changing Open WebUI defaults, or
promoting any coding agent into normal workflow.

## Recommended next action

Stop here, or plan an OpenCode local-model evaluation slice under the same
patch-review workflow.

## Previous status - Provider-neutral patch-review workflow checkpoint complete

## Current task

Preserve the provider-neutral workflow for planner, patch tool, reviewer, and
user approval.

## What changed

- Added `docs/patch-review-workflow.md`.
- Updated `WORKFLOW.md` with the provider-neutral patch-review loop.
- Updated `docs/aider-workflow.md` so Aider is only one patch tool and the
  reviewer role can be Codex desktop, ChatGPT, Open WebUI/local model,
  OpenCode, Claude Code, or another selected reviewer.
- Updated `DECISIONS.md` with the patch-review workflow decision.
- Clarified that local models can review diffs through Open WebUI without a
  coding agent.
- Clarified that local models need a coding harness only when expected to edit
  files.
- Documented OpenCode as the preferred next local-model coding-agent candidate
  to evaluate.
- Documented Codex-on-Strix-with-local-model as unproven and a separate
  investigation.
- Updated `CURRENT_SLICE.md` for the completed checkpoint.
- Preserved the prior Strix llama.cpp Aider validation below as history.

## What did not change

- No live services were changed.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No model containers were changed.
- No Aider run was performed.
- No OpenCode install or trial was performed.
- No Codex local-provider setup was attempted.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `DECISIONS.md`
- `WORKFLOW.md`
- `docs/aider-workflow.md`
- `docs/patch-review-workflow.md`

## Checks run

- Live homelab repo status.
- Read current workflow and Aider docs.
- Local check for Codex CLI on Mac mini.
- Local check for Codex/OpenCode on Strix.
- Official Codex documentation search for local-provider support context.
- `git diff --check`
- `git diff --stat`
- `git status --short`

## Results of checks

- Codex CLI exists on the Mac mini.
- Codex CLI was not found on Strix.
- OpenCode was not found on Strix.
- Official OpenAI Codex CLI documentation describes OpenAI-hosted Responses API
  model usage; local-provider Codex-on-Strix is not proven in this homelab.

## Known risks or blockers

- OpenCode still needs installation/evaluation before it can become a local
  coding-agent surface.
- Codex with a local model on Strix is not proven.
- Aider remains bounded-patch only, not a general autonomous coder.

## User approval needed

Approval is needed before installing OpenCode, configuring Codex local-provider
profiles, changing model-dispatch defaults, changing Open WebUI defaults, or
promoting any coding agent into normal workflow.

## Recommended next action

Stop here, or plan an OpenCode local-model evaluation slice using the same
patch-review workflow.

## Previous status - Strix llama.cpp Aider validation checkpoint complete

## Current task

Preserve the first bounded Aider validation through the restored Strix
llama.cpp/GGUF Coder-Next endpoint.

## What changed

- Ran one bounded Aider edit through Strix `qwen3-coder` on `8082`.
- Aider edited only `/srv/projects/cubie-camera-node/README.md`.
- Removed generated Aider history files before commit.
- Committed the target repo change as
  `8de720a clarify next hardware checklist step`.
- Pushed `cubie-camera-node` to `thinkcentre:/srv/git/cubie-camera-node.git`.
- Added `scripts/aider-strix-coder-llamacpp`.
- Added `inventory/aider-strix-llamacpp-validation-2026-05-28.md`.
- Updated `DECISIONS.md` and `docs/aider-workflow.md`.
- Updated `CURRENT_SLICE.md` for the completed checkpoint.
- Preserved the prior local model role reset below as history.

## What did not change

- model-dispatch config was not edited.
- Open WebUI config was not edited.
- No systemd units, daemons, watchdogs, timers, or hidden automation were
  added.
- Aider was not promoted into the core workflow.
- No broad repo map, multi-file edit, service edit, or autonomous coding
  workflow was tested.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `DECISIONS.md`
- `docs/aider-workflow.md`
- `scripts/aider-strix-coder-llamacpp`
- `inventory/aider-strix-llamacpp-validation-2026-05-28.md`

## Checks run

- Direct Strix `8082` `/v1/models`.
- Aider direct endpoint edit against `/srv/projects/cubie-camera-node`.
- `git status --short` in `cubie-camera-node`.
- `git diff --check` in `cubie-camera-node`.
- `git diff --stat` in `cubie-camera-node`.
- Push verification for `cubie-camera-node`.
- `bash -n scripts/aider-strix-coder-llamacpp`
- `git diff --check` in homelab.
- `git diff --stat` in homelab.
- `git status --short` in homelab.

## Results of checks

- Strix `qwen3-coder` served `Qwen3-Coder-Next-UD-Q4_K_XL.gguf`.
- Aider exited `0`.
- Aider edited only the requested README file.
- The target repo diff was one sentence.
- Generated Aider history files were removed before commit.
- Push to the ThinkCentre mirror succeeded.

## Known risks or blockers

- This validates only a tiny one-file documentation edit.
- Aider remains unvalidated for broad repo maps, multi-file edits, service
  edits, long context, and autonomous workflows.
- The Strix llama.cpp path has not been validated for OpenAI-style tool calls.

## User approval needed

Approval is needed before promoting Aider into normal workflow, changing
model-dispatch defaults, changing Open WebUI defaults, or using Aider for
service/deployment work.

## Recommended next action

Stop here, or validate AMD `local/amd-coder` as the RTX 3090 agentic workhorse
with a similarly bounded edit.

## Previous status - Local model role reset checkpoint complete

## Current task

Preserve the return to the former llama.cpp/GGUF multi-model arrangement and
the updated host roles for Strix and AMD.

## What changed

- Stopped the Strix vLLM Qwen3.6 AWQ runtime.
- Started Strix `qwen3-6` on `8081`.
- Started Strix `qwen3-coder` on `8082`.
- Started AMD `qwen3-coder-30b` on `8083`.
- Started AMD `gemma4-7900xt` on `8084`.
- Confirmed model-dispatch already routes:
  - `local/strix-reasoning` to Strix `8081`
  - `local/strix-coder` to Strix `8082`
  - `local/amd-coder` to AMD `8083`
  - `local/amd-small` to AMD `8084`
- Added `inventory/local-model-role-reset-2026-05-28.md`.
- Updated `DECISIONS.md` with the local model role reset.
- Updated `CURRENT_SLICE.md` for the completed checkpoint.
- Preserved the prior Strix variant comparison checkpoint below as history.

## What did not change

- model-dispatch config was not edited.
- Open WebUI config was not edited.
- No systemd units, daemons, watchdogs, timers, or hidden automation were
  added.
- Aider was not run.
- No Qwen 3.7 local model was installed or tested.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `DECISIONS.md`
- `inventory/local-model-role-reset-2026-05-28.md`

## Checks run

- Live Strix validation.
- Live ThinkCentre model-dispatch validation.
- Live AMD container inspection.
- Direct Strix `/v1/models` checks on `8081` and `8082`.
- Direct AMD `/v1/models` checks on `8083` and `8084`.
- model-dispatch chat checks for:
  - `local/strix-reasoning`
  - `local/strix-coder`
  - `local/amd-coder`
  - `local/amd-small`
- Web check for current Qwen 3.7 local/open-weight availability.
- `git diff --check`
- `git diff --stat`
- `git status --short`

## Results of checks

- `local/strix-reasoning` returned `ok`.
- `local/strix-coder` returned `ok`.
- `local/amd-coder` returned `ok`.
- `local/amd-small` reached the model, but returned reasoning content instead
  of clean final content for the tiny prompt.
- Qwen 3.7 appears to be proprietary/preview/API-only for now, not a local
  open-weight 7900 XT candidate.

## Known risks or blockers

- Strix llama.cpp/GGUF Coder-Next still needs Aider compatibility validation.
- AMD `local/amd-coder` still needs a focused agentic workload validation.
- `local/amd-small` is not a clean agent model until its thinking/output format
  is controlled.
- Qwen 3.7 cannot be tested locally until an official open-weight model or
  concrete compatible quant exists.

## User approval needed

Approval is needed before changing model-dispatch defaults, changing Open WebUI
defaults, promoting any model as the primary agentic backend, changing Aider
helpers, or installing/testing new 7900 XT models.

## Recommended next action

Stop here, revalidate Aider against `local/strix-coder`, or validate AMD
`local/amd-coder` with a focused agentic coding workload.

## Previous status - Strix concurrent model variant comparison checkpoint complete

## Current task

Preserve the comparison between the older concurrently runnable Strix model
pair and the current vLLM AWQ pair that failed concurrent startup.

## What changed

- Added `inventory/strix-concurrent-model-variant-comparison-2026-05-28.md`.
- Removed the temporary direct-test Coder-Next container after reboot.
- Removed the temporary `/tmp` direct-test Compose files.
- Proved the Qwen3.6 `tool` baseline again with `scripts/strix-vllm-mode tool`.
- Inspected the old `qwen3-6` and `qwen3-coder` containers.
- Confirmed the old concurrent pair used llama.cpp/Vulkan/GGUF variants.
- Compared that with the current vLLM/AWQ Hugging Face variants.
- Recorded the conclusion that the older concurrent success does not carry over
  to the current vLLM AWQ harness.
- Updated `CURRENT_SLICE.md` for the variant comparison checkpoint.
- Preserved the prior recovery checkpoint below as history.

## What did not change

- No model-dispatch config was changed.
- No Aider config or helper was changed.
- No Open WebUI config was changed.
- No persistent Compose files were changed.
- No service units, daemons, watchdogs, timers, or hidden automation were added.
- The old llama.cpp containers were inspected but not started.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `inventory/strix-concurrent-model-variant-comparison-2026-05-28.md`

## Checks run

- Post-reboot Strix validation.
- Remove temporary Coder-Next direct-test container.
- Remove temporary `/tmp` direct-test Compose files.
- `scripts/strix-vllm-mode tool`
- `scripts/model-tool-loop-smoke --model local/tool-test`
- `docker inspect qwen3-6 qwen3-coder`
- `docker logs --tail 40 qwen3-6`
- `docker logs --tail 40 qwen3-coder`
- Read current vLLM Compose files.
- `git diff --check`
- `git diff --stat`
- `git status --short`

## Results of checks

- Final Strix active mode: `tool`.
- Final served model: `qwen36-awq-agent-test`.
- `local/tool-test` passed through model-dispatch.
- Old concurrent pair:
  `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` and
  `Qwen3-Coder-Next-UD-Q4_K_XL.gguf` under llama.cpp/Vulkan.
- Current failing pair:
  `cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit` and
  `cyankiwi/Qwen3-Coder-Next-AWQ-4bit` under vLLM AWQ.

## Known risks or blockers

- Concurrent vLLM AWQ serving on Strix is not safe in the tested shape.
- The old llama.cpp/GGUF pair may not satisfy the current OpenAI-style tool-call
  and Aider requirements.
- Always-live `local/code-test` remains unproven.

## User approval needed

Approval is needed before starting the old llama.cpp containers, changing
model-dispatch, changing Aider helpers, changing Open WebUI, changing
persistent Compose files, or adding automation.

## Recommended next action

Stop here, or plan a separate evaluation of the old llama.cpp/GGUF code model
path for Aider compatibility before changing any live routes.

## Previous status - Strix two-model feasibility recovery checkpoint complete

## Current task

Preserve the failed two-model feasibility attempt and the successful recovery
to the known-good Strix `tool` baseline.

## What changed

- Added `inventory/strix-two-model-feasibility-attempt-2026-05-28.md`.
- Recorded the failed attempt to run Qwen3.6 on `8010` and Coder-Next on
  `8011`.
- Recorded the first failure: Coder-Next could not reserve enough GPU memory at
  `gpu-memory-utilization=0.70`.
- Recorded the second failure: lowering Coder-Next to `0.25` made Strix stop
  accepting SSH reliably and required a power cycle.
- Restored all temporary uncommitted Strix homelab edits from `HEAD`.
- Restored the temporary uncommitted ThinkCentre model-dispatch config edit
  from `HEAD`.
- Removed generated `scripts/__pycache__/`.
- Ran `scripts/strix-vllm-mode tool` to remove the failed Coder-Next container
  and prove the Qwen3.6 baseline.
- Updated `CURRENT_SLICE.md` for the recovery checkpoint.
- Preserved the prior runtime mode strategy checkpoint below as history.

## What did not change

- No failed-attempt runtime changes were committed.
- No model-dispatch route change was kept.
- No Aider helper change was kept.
- No `strix-vllm-mode both` helper change was kept.
- No Open WebUI config was changed.
- No systemd units, daemons, watchdogs, timers, or hidden automation were
  added.
- Aider was not run.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `inventory/strix-two-model-feasibility-attempt-2026-05-28.md`

## Checks run

- Post-reboot Strix validation.
- Post-reboot ThinkCentre model-dispatch validation.
- Restore homelab changed files from `HEAD`.
- Restore ThinkCentre `model-dispatch/config.json` from `HEAD`.
- Remove generated `scripts/__pycache__/`.
- `scripts/strix-vllm-mode tool`
- `scripts/model-tool-loop-smoke --model local/tool-test`
- `git status --short` in homelab.
- `git status --short` in model-dispatch.

## Results of checks

- Strix recovered after reboot.
- Qwen3.6 restarted and is live on `8010`.
- Coder-Next failed container was removed.
- `local/tool-test` passed through model-dispatch.
- Homelab returned to a clean working tree before this documentation update.
- model-dispatch returned to only the expected untracked backup files.
- Final active Strix mode: `tool`.

## Known risks or blockers

- Concurrent Strix serving is not proven.
- The simple two-port Coder-Next approach overloaded Strix during startup.
- The next concurrency attempt must test direct Strix runtime stability before
  touching model-dispatch or Aider.

## User approval needed

Approval is needed before any new two-model runtime test, model-dispatch route
change, Aider helper change, Open WebUI change, systemd change, or automation.

## Recommended next action

Stop here, or plan a safer direct-only two-model feasibility test with a
predefined rollback command and no model-dispatch or Aider changes.

## Previous status - Strix vLLM runtime mode strategy checkpoint complete

## Current task

Preserve a design-only Strix runtime mode strategy. Do not change services,
ports, Compose files, model-dispatch, Open WebUI, or default routes.

## What changed

- Added `inventory/strix-vllm-runtime-mode-strategy-2026-05-28.md`.
- Documented the current one-port Strix mode design.
- Compared manual switching, two-port concurrent serving, dispatch-aware
  single-backend behavior, and automatic mode switching.
- Recommended keeping manual one-port switching as the current approved
  operating strategy.
- Updated `CURRENT_SLICE.md` for the completed design checkpoint.
- Preserved the prior real bounded Aider trial checkpoint below as history.

## What did not change

- No Compose files were changed.
- No ports were changed.
- No containers were started, stopped, or restarted.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No systemd units, daemons, watchers, timers, or hidden automation were added.
- Aider was not run.
- Aider was not promoted into the core walking skeleton.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `inventory/strix-vllm-runtime-mode-strategy-2026-05-28.md`

## Checks run

- Live Strix checkpoint validation.
- Live ThinkCentre model-dispatch validation.
- Read `scripts/strix-vllm-mode`.
- Read both Strix vLLM Compose files.
- Read `runbooks/strix-vllm-qwen36-awq-agent.md`.
- `git diff --check`
- `git diff --stat`
- `git status --short`

## Results of checks

- Strix was on `333ac63 document real bounded aider trial` before this update.
- Strix active mode was `tool`.
- Strix served model was `qwen36-awq-agent-test`.
- ThinkCentre `model-dispatch.service` was active.
- ThinkCentre `model-dispatch.service` still used `Restart=on-failure`.
- The current design still uses one host port, `8010`, for both Strix vLLM
  runtimes.

## Known risks or blockers

- `local/tool-test` and `local/code-test` remain one-port Strix modes, not
  simultaneous services.
- Concurrent serving is not proven and may exceed Strix memory or stability
  limits.
- Any two-port strategy would require a separate implementation slice with live
  resource, routing, smoke, and rollback checks.

## User approval needed

Approval is needed before changing Compose files, ports, model-dispatch routes,
Open WebUI defaults, systemd units, Docker runtime behavior, default routes, or
adding automation.

## Recommended next action

Stop here, or write a separate approval brief for a future Strix two-port
concurrency feasibility test.

## Previous status - Real bounded Aider repo trial checkpoint complete

## Current task

Preserve the first real bounded Aider edit in a non-critical repo. Do not
promote Aider or change default routes without a new explicit slice.

## What changed

- Ran one real bounded Aider edit in `/srv/projects/cubie-camera-node`.
- Aider edited `README.md` only.
- Committed the result in `cubie-camera-node` as
  `3af1c05 document next hardware readiness step`.
- Pushed the commit to `thinkcentre:/srv/git/cubie-camera-node.git`.
- Restored Strix to `tool` mode after the trial.
- Documented the result in `DECISIONS.md` and `docs/aider-workflow.md`.
- Updated `CURRENT_SLICE.md` for the completed real bounded Aider checkpoint.
- Preserved the prior repo and mirror inventory checkpoint below as history.

## What did not change

- Aider was not promoted into the core walking skeleton.
- No homelab repo files were edited by Aider.
- No auto routes or default model routes were changed.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No Docker, systemd, service, storage, or repo remote changes were made.
- No deployment was performed in `cubie-camera-node`.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `DECISIONS.md`
- `docs/aider-workflow.md`

## Checks run

- Live Strix checkpoint validation.
- Live ThinkCentre model-dispatch validation.
- `scripts/strix-vllm-mode code`
- `scripts/model-tool-loop-smoke --model local/code-test`
- `scripts/aider-code-test README.md --yes-always --message ...`
- `git status --short` in `cubie-camera-node`
- `git diff --check` in `cubie-camera-node`
- `git diff --stat` in `cubie-camera-node`
- Push verification on `thinkcentre:/srv/git/cubie-camera-node.git`
- `scripts/strix-vllm-mode tool`
- `scripts/model-tool-loop-smoke --model local/tool-test`
- `git diff --check` in homelab
- `git diff --stat` in homelab
- `git status --short` in homelab

## Results of checks

- `local/code-test` passed before the Aider run.
- Aider edited only `README.md` in `cubie-camera-node`.
- Generated Aider history files were removed before commit.
- The `cubie-camera-node` diff was one file and four inserted lines.
- `cubie-camera-node` push to ThinkCentre succeeded.
- Strix was restored to `tool` mode.
- `local/tool-test` passed after restore.

## Known risks or blockers

- Aider is still only validated for tiny, explicit, one-file documentation
  edits.
- Aider is not validated for broad repo maps, long context, multi-file edits,
  auto-commits, service edits, deployment work, or autonomous follow-up work.
- `local/tool-test` and `local/code-test` remain one-port Strix modes, not
  simultaneous services.

## User approval needed

Approval is needed before promoting Aider into normal workflow, changing
default routes, making Coder-Next persistent, adding concurrent Strix serving,
editing Open WebUI defaults, changing `model-dispatch`, or adding automation.

## Recommended next action

Stop here, plan a second bounded Aider trial only for a specific low-risk
target, or design a clearer Strix runtime mode strategy without automating it.

## Previous status - Repo and mirror inventory checkpoint complete

## Current task

Preserve the current repo and mirror inventory before deciding any project
moves. Do not promote Aider or change default routes without a new explicit
slice.

## What changed

- Added `inventory/repo-and-mirror-inventory-2026-05-28.md`.
- Recorded current Strix working repositories, branches, remotes, and dirty
  working trees.
- Recorded current ThinkCentre working repositories, branches, remotes, and
  dirty working trees.
- Recorded current ThinkCentre bare mirrors and HEAD branches.
- Updated `CURRENT_SLICE.md` for the completed inventory checkpoint.
- Preserved the prior Strix local-agent checkpoint below as history.

## What did not change

- No Aider run was performed.
- No model runtime was switched.
- No model-dispatch config was changed.
- No Open WebUI config was changed.
- No Docker, systemd, service, route, storage, or repo remote changes were
  made.
- Dirty repositories found during inventory were not modified.

## Files changed

- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `inventory/repo-and-mirror-inventory-2026-05-28.md`

## Checks run

- Live Strix checkpoint validation.
- Live ThinkCentre model-dispatch validation.
- Strix working repo discovery under `/srv/projects`.
- ThinkCentre working repo and bare mirror discovery under `/srv`.
- Per-repo branch, remote, and `git status --short` checks for discovered
  working repositories.
- Bare mirror HEAD branch checks under `/srv/git`.
- `git diff --check`
- `git diff --stat`
- `git status --short`

## Results of checks

- Strix was still on `de7a33e` before this inventory update.
- Strix active mode was still `tool`.
- Strix served model was still `qwen36-awq-agent-test`.
- ThinkCentre `model-dispatch.service` was active.
- ThinkCentre `model-dispatch.service` still used `Restart=on-failure`.
- Strix dirty repo observed:
  `/srv/projects/cubie-a7s-armbian` with `M READ_ONLY_CUBIE_CAPTURE_BRIEF.md`.
- ThinkCentre dirty repos observed:
  `/srv/telegram-tasks-bot` with `M app.py`,
  `/srv/model-dispatch` with expected untracked backups, and
  `/srv/scandocs` with many untracked project files.

## Known risks or blockers

- ThinkCentre discovery hit `Permission denied` under `/srv/hermes-agent/data`
  because this inventory did not use `sudo`.
- The inventory records presence and Git state only. It does not classify repo
  ownership, archival status, migration priority, or cleanup order.

## User approval needed

Approval is needed before changing any repo remotes, moving projects, cleaning
dirty trees, changing service config, promoting Aider, changing default routes,
or adding automation.

## Recommended next action

Stop here, pick one non-critical repo for a bounded Aider trial, or plan a
separate repo/mirror cleanup slice using the inventory.

## Previous status - Strix vLLM local-agent validation checkpoint complete

## Current task

Preserve the current validated Strix vLLM and Aider compatibility state. Do not
promote Aider or change default routes without a new explicit slice.

## What changed

- Added and validated the Strix Qwen3.6 AWQ Compose runtime.
- Added and validated the Coder-Next AWQ manual test runtime.
- Added `scripts/model-tool-loop-smoke` and defaulted it to `local/tool-test`.
- Added `scripts/strix-vllm-mode` to switch the one-port Strix runtime between
  `tool` and `code` modes with readiness and smoke validation.
- Proved `local/tool-test` and `local/code-test` through model-dispatch.
- Proved Aider `0.86.2` can make one bounded throwaway edit through
  `local/code-test`.
- Added `scripts/aider-code-test` to preserve the validated Aider command shape
  while refusing to run unless Coder-Next is active.
- Documented the decisions and runbook updates for these validations.

## What did not change

- Aider was not promoted into the core walking skeleton.
- Aider was not run against the homelab repo for a real workflow edit.
- No auto routes or default model routes were changed.
- `local/tool-test` remains manual/test-only.
- `local/code-test` remains manual/test-only.
- Only one Strix vLLM runtime is active on port `8010` at a time.
- Strix was restored to `tool` mode after Coder-Next and Aider tests.
- No `/srv/model-dispatch` files were changed in this checkpoint.
- No Open WebUI config was changed.
- No OpenCode config was changed.
- No Continue.dev config was changed.
- No LiteLLM config was changed.
- No dashboard, monitoring, or observability config was changed.
- No systemd units, daemons, watchers, schedulers, hidden jobs, or approval
  automation were added.

## Files changed

Recently changed by this checkpoint:

- `DECISIONS.md`
- `docs/aider-workflow.md`
- `runbooks/strix-vllm-qwen36-awq-agent.md`
- `runtime/strix-qwen3-coder-next-awq-test/compose.yml`
- `scripts/aider-code-test`
- `scripts/strix-vllm-mode`
- `CURRENT_SLICE.md`
- `PROJECT_PLAN.md`
- `AGENT_STATUS.md`
- `ROADMAP.md`
- `WORKFLOW.md`

## Checks run

- `scripts/model-tool-loop-smoke`
- `scripts/model-tool-loop-smoke --model local/code-test`
- `scripts/strix-vllm-mode code`
- `scripts/strix-vllm-mode tool`
- `scripts/aider-code-test` failure path in `tool` mode.
- `scripts/aider-code-test` success path in a throwaway repo while in `code`
  mode.
- `bash -n scripts/aider-code-test`
- `git diff --check`
- `git status --short`

## Results of checks

- `local/tool-test` passes through model-dispatch when Qwen3.6 is active.
- `local/code-test` passes through model-dispatch when Coder-Next is active.
- Aider edited only the requested file in throwaway repos and exited `0`.
- `scripts/aider-code-test` refuses to run when the wrong Strix runtime is
  active.
- Final live Strix state after tests: `active_mode=tool`.
- Latest pushed checkpoint before this status alignment:
  `6ee8fc0 add local code-test aider helper`.

## Known risks or blockers

- `local/tool-test` and `local/code-test` share Strix port `8010`; they are
  mode-specific, not simultaneously live.
- Aider compatibility is still only proven for tiny, explicit, one-file edits.
- Aider is not validated for broad repo maps, long context, multi-file edits,
  auto-commits, or autonomous coding workflows.
- The existing `/home/enzo/.local/bin/aider-strix-coder` launcher still points
  at the older `8082` llama.cpp/GGUF path, not the validated vLLM Coder-Next
  path.

## User approval needed

Approval is needed before promoting Aider into normal workflow, changing
default routes, making Coder-Next persistent, adding concurrent Strix serving,
editing Open WebUI defaults, changing `model-dispatch`, or adding automation.

## Recommended next action

Stop here or choose one non-critical repo for a real bounded
`scripts/aider-code-test` edit, with manual diff review before commit.

## Previous status - Aider compatibility planning

The active slice was `Aider compatibility planning`.

This slice planned how to diagnose why Aider gets empty responses from local
`model-dispatch` aliases without running more Aider trials.

Completed changes:

- Updated `CURRENT_SLICE.md` so the active slice was
  `Aider compatibility planning`.
- Updated `PROJECT_PLAN.md` so the current build stage was
  `Slice 9: Aider compatibility planning`.
- Created `inventory/aider-compatibility-plan.md`.
- Documented observed Aider failures with `openai/coding` and
  `openai/local/amd-coder`.
- Documented likely hypotheses around Aider response format expectations,
  `model-dispatch` alias compatibility, generic aliases versus explicit model
  IDs, and possible Aider metadata, edit format, or provider configuration
  needs.
- Documented local `model-dispatch` checks, direct AMD endpoint checks,
  verified OpenRouter-free fallback rules, what not to do, and validation
  commands for a later slice.

## Previous status - Aider workflow integration

The active slice was `Aider workflow integration`.

This slice updated the homelab workflow docs to reflect the corrected agent
strategy: Codex remains primary for planning, sequencing, and risky
live-service work; Claude Code remains a frontier-code alternative; Aider is
added as the bounded patch assistant for small repo edits; OpenCode is demoted
to a later local-agent experiment; Continue.dev remains editor assist; and
Cline remains sandbox-only.

Completed changes:

- Updated `WORKFLOW.md` with agent division of labor.
- Added the Aider use rule to `WORKFLOW.md`.
- Created `docs/aider-workflow.md`.
- Updated `CURRENT_SLICE.md` so the active slice was
  `Aider workflow integration`.
- Updated `PROJECT_PLAN.md`, `DECISIONS.md`, `ROADMAP.md`,
  `HOMELAB_LAYOUT.md`, and `CODEX_CONTEXT.md` so the corrected strategy was
  reflected across workflow and planning docs.
- Preserved prior Aider elimination and OpenCode routing history as historical
  context instead of deleting it.

## Previous status - additive alias deployment planning

The active slice is `additive model-dispatch alias deployment planning`.

This slice produced a documentation-only deployment plan for adding
`model-dispatch` aliases later. No live routing behavior was changed.

## Current task

Plan an additive `model-dispatch` alias deployment from the reviewed source
repo. Do not change live routing yet.

## What changed

- Updated `CURRENT_SLICE.md` so the active slice is
  `additive model-dispatch alias deployment planning`.
- Created `inventory/model-dispatch-additive-alias-deployment-plan.md`.
- Documented current aliases and IDs to preserve:
  - `auto-local`
  - `auto-coding-local`
  - `auto-reasoning-local`
  - `auto-small-local`
  - explicit Strix and AMD model IDs
  - OpenRouter-free model forms
  - OpenCode direct AMD rollback IDs
  - Continue.dev and LiteLLM rollback posture
- Documented additive aliases to add:
  - `advisor`
  - `reasoning`
  - `coding`
  - `small`
  - `review`
  - `long-code`
  - `local/strix-reasoning`
  - `local/strix-coder`
  - `local/amd-coder`
  - `local/amd-small`
  - `free-cloud`
- Documented required Open WebUI display names.
- Documented exact future `config.json` additions for local aliases.
- Documented that `free-cloud` needs a reviewed source change because current
  `app.py` generates OpenRouter-free IDs outside `config.json`, and the current
  validator rejects route targets not present in `models`.
- Documented files eligible for a later alias deployment.
- Documented backup path as `/srv/model-dispatch/backups/<timestamp>/`.
- Documented future validation commands and rollback plan.
- Documented non-goals.
- Preserved prior slice history below in `CURRENT_SLICE.md`.

## What did not change

- No `/srv/model-dispatch` files were touched.
- No `/srv/projects/model-dispatch` files were touched.
- No service restart or reload was run.
- No Docker, systemd, sudo, deployment, or live endpoint-changing command was
  run.
- No dashboard, monitoring, or observability deployment was started.
- No OpenCode, Continue.dev, Open WebUI, LiteLLM, MCP, reverse proxy, or live
  service config was changed.
- No commit was made.

## Files changed

- `CURRENT_SLICE.md`
- `inventory/model-dispatch-additive-alias-deployment-plan.md`
- `AGENT_STATUS.md`

## Checks run

- Read required homelab docs:
  - `AGENTS.md` from the user-provided repo instructions
  - `CODEX_CONTEXT.md`
  - `CURRENT_SLICE.md`
  - `AGENT_STATUS.md`
  - `PROJECT_PLAN.md`
  - `DECISIONS.md`
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `ROADMAP.md`
- Read user-requested docs:
  - `inventory/model-dispatch-alias-registry-plan.md`
  - `inventory/model-dispatch-deployment-plan-2026-05-17.md`
  - `inventory/model-dispatch-deployment-approval-brief-2026-05-17.md`
  - `ROUTING_INVENTORY.md`
- Inspected reviewed source repo docs/config only:
  - `/srv/projects/model-dispatch/config.json`
  - `/srv/projects/model-dispatch/ROUTING.md`
  - `/srv/projects/model-dispatch/app.py`
  - `/srv/projects/model-dispatch/tests/check_config.py`
- Requested final checks:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Results of checks

- `git diff --check`: passed with no output.
- `git diff --stat`:
  - `AGENT_STATUS.md  | 137 +++++++++++++++++++++++++++++++++++--------------------`
  - `CURRENT_SLICE.md |  91 +++++++++++++++++++++++++++---------`
  - `2 files changed, 157 insertions(+), 71 deletions(-)`
  - Note: `git diff --stat` does not include the untracked additive alias
    deployment plan until it is staged or committed.
- `git status --short`:
  - `M AGENT_STATUS.md`
  - `M CURRENT_SLICE.md`
  - `?? inventory/model-dispatch-additive-alias-deployment-plan.md`

## Known risks or blockers

- Alias deployment would affect model routing and needs a separate explicit
  deployment slice.
- The `free-cloud` alias is not a pure `config.json` addition in the current
  reviewed source shape. It needs a small reviewed source change so it maps
  exactly to `openrouter-free/openrouter/auto-free-router` instead of falling
  through to `auto-local`.
- OpenCode and Continue.dev changes should remain separate explicit slices after
  aliases are validated.
- Existing model IDs should be preserved during any first alias deployment to
  avoid breaking Open WebUI or rollback paths.
- `long-code` points to `auto-coding-local` for now and needs large-context
  validation because the first target in that route is the AMD 32k coder.
- Direct AMD routing and LiteLLM rollback should remain documented until
  replacement paths are validated.
- Dashboards, monitoring, and observability remain deferred and require a
  separate explicit slice and operator approval.

## User approval needed

No approval is needed for this documentation-only planning slice because the
user explicitly requested it.

Approval will be needed before any live `model-dispatch` config change,
source repo implementation change, OpenCode config change, Continue.dev config
change, Open WebUI config change, MCP enablement, Docker/systemd change,
monitoring/dashboard deployment, push, or deployment.

## Recommended next action

Review `inventory/model-dispatch-additive-alias-deployment-plan.md`.

If accepted, the next safe slice is a reviewed source-repo implementation in
`/srv/projects/model-dispatch` that adds the local aliases to `config.json` and
implements an exact `free-cloud` alias without touching live
`/srv/model-dispatch`.

## Previous status - alias registry cleanup planning

The active slice was `model-dispatch alias registry cleanup planning`.

That slice made a documentation-only correction to the alias registry plan. No
live routing behavior was changed.

What changed:

- Updated `CURRENT_SLICE.md` so the active slice was
  `model-dispatch alias registry cleanup planning`.
- Created `inventory/model-dispatch-alias-registry-plan.md`.
- Documented current exposed model IDs, proposed stable aliases,
  compatibility aliases to preserve, validation requirements, rollback
  expectations, and display-name requirements.

What did not change:

No `/srv/model-dispatch` files, source repo files, service state, Docker,
systemd, sudo, OpenCode, Continue.dev, Open WebUI, LiteLLM, MCP, reverse proxy,
dashboards, monitoring, observability, benchmark code, `tools/` files, or
commits were changed.

## Previous status - deployment planning correction

The active slice was `model-dispatch deployment planning only`.

The deployment docs were updated after a failed `model-dispatch` deployment
attempt. The attempt started from `strix:/srv/projects/model-dispatch` and
stopped before copying files because backup directory creation failed with
`mkdir: Permission denied` at `/srv/model-dispatch-backups/<timestamp>`.

The live service remained healthy, and no deployment completed during that
attempt.

What changed:

- Updated `inventory/model-dispatch-deployment-plan-2026-05-17.md` to:
  - replace `/srv/model-dispatch-backups/<timestamp>` with
    `/srv/model-dispatch/backups/<timestamp>`
  - document that the earlier `/srv/model-dispatch-backups/<timestamp>` path
    failed because `/srv` is root-owned and backup directory creation returned
    `mkdir: Permission denied`
  - state that the failed attempt stopped before file copy and no live files
    were changed
- Updated `inventory/model-dispatch-deployment-approval-brief-2026-05-17.md`
  to use `/srv/model-dispatch/backups/<timestamp>` for the backup destination
  and rollback reference.

What did not change:

No deployment completed. The failed deployment attempt stopped before file copy.

No live services, production configs, OpenCode config, Open WebUI config, MCP
config, Docker state, systemd state, reverse proxy settings, SearXNG settings,
monitoring stack, observability stack, dashboard stack, or `model-dispatch`
runtime files were changed.

No files were copied to `/srv/model-dispatch`.

No service restart, reload, deploy command, push, Docker command, systemd
command, sudo command, or `/srv/litellm/.env` read occurred.

No homelab `tools/` files were touched.

No `/srv/model-dispatch` files were edited.

No homelab commit was made.

Dashboards, monitoring, and observability remained deferred.

## Previous status - local smoke-check scaffold

The Strix `model-dispatch` source repo candidate at
`/srv/projects/model-dispatch` now has a local-only smoke-check scaffold and a
first local commit.

Previous task:
Record the completed next local-only `model-dispatch` candidate repo step in
the homelab handoff, without touching `tools/`, committing, changing live
services, or editing the live `/srv/model-dispatch` path.

What changed:

- Added a local smoke-check scaffold in `/srv/projects/model-dispatch`.
- Added `/srv/projects/model-dispatch/tests/check_config.py`.
- Added `/srv/projects/model-dispatch/TESTING.md`.
- Updated `/srv/projects/model-dispatch/DECISIONS.md` to record that local
  tests avoid importing `app.py` because `app.py` has live-path side effects.
- Added `/srv/projects/model-dispatch/AGENT_STATUS.md`.
- Created the local `model-dispatch` commit:
  `add local config smoke check`.
- Updated the homelab handoff.

What did not change:

No live `/srv/model-dispatch` files were edited.

No live services, production configs, OpenCode config, Open WebUI config, MCP
config, Docker state, systemd state, reverse proxy settings, SearXNG settings,
or `model-dispatch` runtime files were changed.

No service restart, deploy, push, mirror creation, endpoint call, or
`/srv/litellm/.env` read occurred.

No homelab `tools/` files were touched.

No homelab commit was made.

`__pycache__` was created by `py_compile` in `/srv/projects/model-dispatch`,
but it is ignored by `.gitignore` and is not shown in Git status.

## Previous status - source repo candidate creation

The Strix `model-dispatch` source repo candidate was created for review at
`/srv/projects/model-dispatch`.

Previous task:
Create a source repo candidate at `/srv/projects/model-dispatch` using only the
reviewed include list from `thinkcentre:/srv/model-dispatch`, without deploying
anything or touching the live service.

What changed:

- Created `/srv/projects/model-dispatch`.
- Copied only the approved files from `thinkcentre:/srv/model-dispatch` using
  the LAN IP `192.168.50.225`:
  - `app.py`
  - `config.json`
  - `.gitignore`
  - `.cgcignore`
- Initialized Git in `/srv/projects/model-dispatch`.
- Added review-only repo docs in `/srv/projects/model-dispatch`:
  - `README.md`
  - `ROUTING.md`
  - `SERVICE.md`
  - `DEPLOYMENT.md`
  - `DECISIONS.md`
- Tightened `/srv/projects/model-dispatch/.gitignore` to explicitly exclude
  logs, request logs, backups, env files, secrets, tokens, keys, caches,
  virtualenvs, databases, generated runtime files, and dependency/vendor
  directories.
- Marked files in `/srv/projects/model-dispatch` with `git add -N .` so
  `git diff` and `git diff --check` can review the candidate without staging a
  commit.

What did not change:
No live services, production configs, OpenCode config, Open WebUI config, MCP
config, Docker state, systemd state, reverse proxy settings, SearXNG settings,
or `model-dispatch` runtime files were changed.

No `/srv/model-dispatch` files were edited. No service was restarted or
reloaded. No `sudo` was used.

No `thinkcentre:/srv/git/model-dispatch.git` mirror was created. Nothing was
pushed. No commit was made in `/srv/projects/model-dispatch` or
`/srv/projects/homelab`.

No homelab `tools/` files were touched.

The live `.git/` directory, `dispatch.log`, backup snapshots, env files,
secrets, tokens, keys, databases, sqlite files, caches, virtualenvs, generated
runtime files, and request logs were not copied from the live service.

Checks run:

- Read required homelab docs:
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENT_STATUS.md`
  - `inventory/model-dispatch-first-class-repo-plan.md`
  - `inventory/model-dispatch-live-inventory-2026-05-17.md`
- Ran candidate repo setup commands:
  - `mkdir -p /srv/projects/model-dispatch`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/app.py /srv/projects/model-dispatch/app.py`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/config.json /srv/projects/model-dispatch/config.json`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/.gitignore /srv/projects/model-dispatch/.gitignore`
  - `scp -F /dev/null 192.168.50.225:/srv/model-dispatch/.cgcignore /srv/projects/model-dispatch/.cgcignore`
  - `git init`
  - `git add -N .`
- Ran requested validation checks:
  - `cd /srv/projects/model-dispatch && git status --short`
  - `cd /srv/projects/model-dispatch && find . -maxdepth 2 -type f | sort`
  - `cd /srv/projects/model-dispatch && git diff --check`
  - `cd /srv/projects/homelab && git status --short`
  - `cd /srv/projects/homelab && git diff --check`
  - `cd /srv/projects/homelab && git diff --stat`

Results:

- Required docs were present and readable.
- `/srv/projects/model-dispatch` `git status --short` showed intent-to-add
  entries for the candidate files.
- `/srv/projects/model-dispatch` `git diff --check` passed with no output.
- `/srv/projects/homelab` `git status --short` initially showed:
  - `?? tools/`
- `/srv/projects/homelab` `git diff --check` passed with no output.

## Previous status — Slice 1 read-only live inventory

Slice 1 read-only live inventory of `thinkcentre:/srv/model-dispatch` was
completed and made ready for review.

Previous task:
Document the live `model-dispatch` file shape for include/exclude planning
without creating repos, copying files, restarting services, editing live config,
or reading secret contents.

What changed:

- `inventory/model-dispatch-live-inventory-2026-05-17.md` was added with:
  - purpose
  - boundaries
  - commands run
  - directory/file inventory summary
  - candidate source files to include later
  - candidate docs/config/tests to include later
  - candidate excludes
  - unknowns requiring user review
  - recommended include/exclude policy
  - next operator approval brief
- `AGENT_STATUS.md` was updated with that handoff while preserving older history
  below.

Live inventory highlights:

- `/srv/model-dispatch` already contains a `.git/` directory.
- Branch reported by read-only Git metadata: `main`.
- Recent commit reported: `ef65a5c initialize model dispatch service repo`.
- No Git remote was printed by `git remote -v`.
- Non-`.git` top-level files observed by name/metadata:
  - `.cgcignore`
  - `.gitignore`
  - `app.py`
  - `config.json`
  - timestamped `app.py.*.bak` files
  - timestamped `config.json.*.bak` files
  - `dispatch.log`

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No Docker state, systemd state, repo locations, scripts, daemons, watchers,
hidden automation, paid-provider fallback, model API calls, network calls, or
`tools/` files were changed.

No `/srv/projects/model-dispatch` repo was created. No
`thinkcentre:/srv/git/model-dispatch.git` mirror was created. No
`/srv/model-dispatch` files were copied. No file contents were printed.

Files changed:

- `inventory/model-dispatch-live-inventory-2026-05-17.md`
- `AGENT_STATUS.md`

Checks run:

- Read required context docs:
  - `CURRENT_SLICE.md`
  - `inventory/model-dispatch-first-class-repo-plan.md`
  - `inventory/baseline-2026-05-17.md`
  - `ROUTING_INVENTORY.md`
  - `AGENT_STATUS.md`
- Ran read-only remote inventory commands:
  - `ssh thinkcentre 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null thinkcentre 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -maxdepth 4 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -maxdepth 4 \( ... likely secret/log/cache name patterns ... \) -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -path /srv/model-dispatch/.git -prune -o -maxdepth 2 -printf "%y %s %TY-%Tm-%Td %TH:%TM %p\n" | sort'`
  - `ssh -F /dev/null 192.168.50.225 'git -C /srv/model-dispatch status --short && git -C /srv/model-dispatch branch --show-current && git -C /srv/model-dispatch log --oneline -5'`
  - `ssh -F /dev/null 192.168.50.225 'git -C /srv/model-dispatch remote -v'`
  - `ssh -F /dev/null 192.168.50.225 'find /srv/model-dispatch -path /srv/model-dispatch/.git -prune -o -type f -printf "%f\n" | awk ... | sort | uniq -c'`
- Ran requested post-edit checks:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

Results:

- Required docs were present and readable.
- Initial hostname SSH failed due local SSH config permissions, then DNS lookup
  with `-F /dev/null` failed for hostname `thinkcentre`.
- Read-only SSH using `192.168.50.225` succeeded.
- The likely secret/log/cache name scan reported `dispatch.log` only.
- No `.env`, obvious secret, token, key, database, sqlite, cache, virtualenv, or
  `__pycache__` path was reported by name in the max-depth-4 scan.
- `git -C /srv/model-dispatch status --short` printed no changes.
- `git -C /srv/model-dispatch branch --show-current` printed `main`.
- `git -C /srv/model-dispatch log --oneline -5` printed
  `ef65a5c initialize model dispatch service repo`.
- `git -C /srv/model-dispatch remote -v` printed no remotes.
- `git diff --check` passed with no output.
- `git diff --stat` reported tracked changes in `AGENT_STATUS.md`. The new
  untracked live inventory file is visible in `git status --short` but not
  included in tracked `git diff --stat` output until staged.
- `git status --short` showed:
  - `M AGENT_STATUS.md`
  - `?? inventory/model-dispatch-live-inventory-2026-05-17.md`
  - `?? tools/`

Known risks or blockers:

- `config.json` was identified by name only and still needed user review for
  secrets before any copy.
- `app.py` was identified by name only and may contain embedded operational
  details that need review before source promotion.
- The live `.git/` directory should not be copied into the Strix source repo
  candidate by default.
- `dispatch.log` and timestamped `.bak` files should be excluded by default.
- Open WebUI currently depends on `model-dispatch`; this inventory does not
  permit deployment changes.
- Direct AMD routing and LiteLLM rollback must remain available until later
  validated replacement slices.
- No known blocker for this documentation-only slice.

User approval needed:
No approval was needed for that docs-only update.

Recommended next action:
Review `inventory/model-dispatch-live-inventory-2026-05-17.md`, then decide
whether to approve the next narrow step: creating a Strix source repo candidate
from the reviewed include list only. If `config.json` has not been manually
reviewed safe, review it before copying it.

## Previous status — Slice 1 repo preparation plan

Slice 1 `model-dispatch` first-class repo preparation was completed and made
ready for review.

Previous task:
Prepare the plan and operator approval brief for making `model-dispatch` a
first-class source-controlled repo without changing the live service.

What changed:

- `CURRENT_SLICE.md` defined the active slice as
  "model-dispatch first-class repo preparation."
- `inventory/model-dispatch-first-class-repo-plan.md` was added with purpose,
  current documented live state, target repo layout, proposed future repo
  contents, exact non-goals, risks, rollback thinking, validation needed before
  touching the live service, operator approval brief template, and proposed
  future command blocks clearly marked `NOT RUN`.
- `AGENT_STATUS.md` was updated with that handoff while preserving older history
  below.

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No Docker state, systemd state, repo locations, scripts, daemons, watchers,
hidden automation, paid-provider fallback, model API calls, network calls, or
`tools/` files were changed.

No `/srv/projects/model-dispatch` repo was created. No `/srv/model-dispatch`
files were copied or inspected directly.

Files changed:

- `CURRENT_SLICE.md`
- `inventory/model-dispatch-first-class-repo-plan.md`
- `AGENT_STATUS.md`

Checks run:

- `git diff --check`
- `git diff --stat`
- `git status --short`

Results:

- `git diff --check` passed with no output.
- `git diff --stat` reported tracked changes in `AGENT_STATUS.md` and
  `CURRENT_SLICE.md`; the untracked Slice 1 plan was visible in
  `git status --short`.
- `git status --short` showed `M AGENT_STATUS.md`, `M CURRENT_SLICE.md`,
  `?? inventory/model-dispatch-first-class-repo-plan.md`, and `?? tools/`.

## Previous status — Slice 0 baseline inventory

Slice 0 baseline inventory and freeze point documentation update was completed
and made ready for review.

Previous task:
Create a documentation-only baseline inventory before any live service changes.

What changed:

- `CURRENT_SLICE.md` defined the active slice as "Baseline inventory and freeze
  point."
- `inventory/baseline-2026-05-17.md` was added as the Slice 0 baseline
  inventory and freeze point.
- `AGENT_STATUS.md` was updated with that handoff while preserving older history
  below.

The baseline recorded:

- Host roles and known LAN/Tailscale IPs.
- Open WebUI route.
- `model-dispatch` service path, port, endpoint, and current/target role.
- LiteLLM rollback/history status.
- OpenRouter-free artifact posture.
- Current known model endpoints.
- OpenCode current routing posture.
- Continue.dev current routing posture.
- CodeGraphContext/MCP posture.
- Git source and mirror posture.
- Backup/off-site roles.
- Known untracked repo path: `tools/`.

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No Docker state, systemd state, repo locations, scripts, daemons, watchers,
hidden automation, paid-provider fallback, model API calls, network calls, or
`tools/` files were changed.

Files changed:

- `CURRENT_SLICE.md`
- `inventory/baseline-2026-05-17.md`
- `AGENT_STATUS.md`

Checks run:

- `git diff --check`
- `git diff --stat`
- `git status --short`

Results:

- `git diff --check` passed with no output.
- `git diff --stat` reported tracked changes in `AGENT_STATUS.md` and
  `CURRENT_SLICE.md`; the untracked baseline file was visible in
  `git status --short`.
- `git status --short` showed `M AGENT_STATUS.md`, `M CURRENT_SLICE.md`,
  `?? inventory/baseline-2026-05-17.md`, and `?? tools/`.

## Previous status — Architecture transition planning

Documentation-only architecture transition slice was started and made ready for
review. The status file was repaired so prior useful history remained available
below that handoff.

Previous task:
Start a new active slice: "Architecture transition planning and model-dispatch
repo preparation."

What changed:

- `CURRENT_SLICE.md` defined the active transition-planning slice, including
  scope, non-scope, validation steps, and definition of done.
- `DECISIONS.md` recorded the 2026-05-17 decision to centralize model routing
  through `model-dispatch`, make Strix the canonical source/code-graph host, and
  make AMD a mode-switched GPU compute worker.
- `ROADMAP.md` included the ordered architecture transition plan from slice 0
  through slice 15.
- `HOMELAB_LAYOUT.md` included the target platform architecture and final
  desired host roles.
- `WORKFLOW.md` included the Codex-assisted deployment rule.
- `AGENT_STATUS.md` preserved useful prior status history under
  `Archived Status History` instead of replacing it.

What did not change:
No live services, production configs, OpenCode config, MCP config, or
`model-dispatch` runtime files were changed.

No scripts, daemons, watchers, hidden automation, paid-provider fallback, model
API calls, or network calls were added.

Files changed:

- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `ROADMAP.md`
- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `AGENT_STATUS.md`

Checks run:

- `git diff --check`
- `git diff --stat`
- `git diff -- AGENT_STATUS.md | sed -n '1,260p'`

Results:

- `git diff --check` passed with no output.
- `git diff --stat` reported 6 files changed, 403 insertions, and 69 deletions
  across the full uncommitted docs diff.
- The scoped `AGENT_STATUS.md` diff showed the current architecture transition
  handoff followed by restored archived history.

## Previous status — LLM runtime topology documentation

LLM runtime topology documentation update is complete and ready for review.

Previous task:
Edit `inventory/models/llm-runtime-topology.md` into a stable,
CodeGraphContext-friendly LLM model topology document.

What changed:
`inventory/models/llm-runtime-topology.md` now describes stable LLM topology
across:

- `strix`
- `thinkcentre`
- `AMD`

The document now includes:

- Purpose and scope.
- A clear statement that it is structural inventory, not runtime monitoring.
- Host sections for `strix`, `thinkcentre`, and `AMD`.
- Stable service/container names where known.
- Runtime/image families where known.
- Endpoint/port details where known.
- Role/purpose notes where known.
- Source/config path hints where known.
- A CGC exclusions section for logs, request logs, Docker stats, cache details,
  daily container churn, secrets, and unrelated containers.

What did not change:
No live services or live configs were changed.

No:

- Docker commands
- sudo commands
- network calls
- model API calls
- service restarts
- files outside this repo
- secrets, tokens, raw logs, request logs, daily activity logs, or cache details

Files changed:

- `inventory/models/llm-runtime-topology.md`
- `AGENT_STATUS.md`

Checks run:

- Read required context docs:
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENT_STATUS.md`
- Read related routing/workflow docs because the task touches service topology:
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `ROADMAP.md`
- Read the target file:
  - `inventory/models/llm-runtime-topology.md`
- Reviewed the edited target file with:
  - `sed -n '1,260p' inventory/models/llm-runtime-topology.md`
- Checked Git state with:
  - `git status --short`
- Attempted a tracked diff for the target file with:
  - `git diff -- inventory/models/llm-runtime-topology.md`

Results of checks:

- Required context files were present and readable.
- The target document is readable Markdown.
- The document separates stable topology from validation notes.
- The document explicitly says it is not runtime monitoring.
- The document excludes observer logs, request logs, Docker stats, cache
  directories, daily container churn, unrelated non-LLM containers, and secrets.
- `git status --short` showed `inventory/models/` as untracked, so the target
  file was not yet visible in normal tracked `git diff` output.

Known risks or blockers:

- No known technical blocker.
- Because `inventory/models/` was untracked, the user should review and add that
  path intentionally if this inventory document should become part of Git
  history.

User approval needed:
No approval was needed for the completed documentation-only edit.

Recommended next action:
Review `inventory/models/llm-runtime-topology.md`, then add and commit
`inventory/models/llm-runtime-topology.md` and `AGENT_STATUS.md` if the topology
wording matches the intended stable inventory.

## 2026-05-15 — Strix Halo vLLM Ubuntu Docker PR

Created upstream PR for the Ubuntu 26.04 Docker Engine adaptation of
`kyuz0/amd-strix-halo-vllm-toolboxes`.

PR:

- https://github.com/kyuz0/amd-strix-halo-vllm-toolboxes/pull/54

Validated before PR:

- Docker-only Ubuntu path.
- No Podman, Distrobox, Toolbx, Ubuntu toolbox, or LXC.
- ROCm/PyTorch/vLLM smoke test on Strix Halo.
- Conservative Qwen/Qwen2.5-7B-Instruct API validation.
- Hugging Face auth through `hf auth login`.
- Conservative google/gemma-4-26B-A4B-it API validation.
- Memory exposure notes with 48 GiB clean allocation while other model-serving
  containers were stopped.

## 2026-05-15 — Strix qwen3.6 visible-output fix

Restored Strix llama.cpp mode as the default after vLLM benchmarking.

Runtime state:
- `qwen3-6` runs on port 8081.
- `qwen3-coder` runs on port 8082.
- vLLM on port 8010 is stopped/manual testbed mode.

Fix:
- Recreated `qwen3-6` with llama-server `--reasoning off`.
- This fixed the issue where Qwen3.6 returned output only in
  `message.reasoning_content` while `message.content` was empty.

Validation:
- `/health` on 8081 returned OK.
- `/v1/models` on 8081 listed `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf`.
- `/v1/chat/completions` on 8081 returned visible content:
  `strix reasoning endpoint restored`.

Operational note:
- Keep `--reasoning off` for the normal visible-output Strix reasoning endpoint.
- vLLM remains validated as an optional Docker testbed, but current Strix
  default should remain llama.cpp Vulkan.

## 2026-05-17 — model-dispatch mirror documented in source repo

The `model-dispatch` source repo on Strix is now mirrored to ThinkCentre.

Source repo:
- `strix:/srv/projects/model-dispatch`

Mirror:
- `thinkcentre:/srv/git/model-dispatch.git`

Latest mirrored commit:
- `7cbb1d9 document thinkcentre mirror creation`

Previous source repo commits:
- `02679e7 add local config smoke check`
- `43b1f72 initialize model-dispatch source candidate`

What did not change:
- No deployment to live `/srv/model-dispatch`.
- No `model-dispatch.service` restart or reload.
- No Open WebUI, OpenCode, LiteLLM, Docker, systemd, MCP, reverse proxy, dashboard, monitoring, or observability change.

Current boundary:
- `model-dispatch` is now source-controlled on Strix and mirrored to ThinkCentre.
- It remains review-only.
- Deployment requires a later explicit deployment slice and rollback brief.

## 2026-05-17 — model-dispatch deployment documented in source repo

The live `model-dispatch` deployment was completed and documented in the `model-dispatch` source repo.

Source repo:
- `strix:/srv/projects/model-dispatch`

Latest source repo commit:
- `54e89c5 document live deployment`

Mirror:
- `thinkcentre:/srv/git/model-dispatch.git`

Live path:
- `thinkcentre:/srv/model-dispatch`

Backup:
- `/srv/model-dispatch/backups/20260517-212158`

Validation:
- `/health` returned `{"status": "ok"}`.
- `/v1/models` returned local routes and OpenRouter-free entries.
- `/v1/chat/completions` using `auto-local` returned a valid OpenAI-compatible response.
- `auto-local` selected `amd-coder-qwen3-coder-30b-32k`.
- Test response content was `OK`.

Cleanup:
- Removed accidental empty `main` file from `/srv/projects/model-dispatch` before commit.

What did not change:
- No Open WebUI config change.
- No OpenCode config change.
- No LiteLLM config change.
- No Docker, MCP, reverse proxy, dashboard, monitoring, or observability change.

Known follow-up:
- `model-dispatch.service` has a pre-existing invalid `Restart=unless-stopped` warning. Consider a separate tiny service-unit fix later.

## 2026-05-17 — model-dispatch systemd restart policy fixed

Fixed the pre-existing invalid restart policy in the live ThinkCentre systemd unit for `model-dispatch.service`.

Change:
- Replaced invalid `Restart=unless-stopped`
- With valid `Restart=on-failure`

Backup:
- `/etc/systemd/system/model-dispatch.service.backup.20260517-212830`

Validation:
- `systemctl daemon-reload` completed.
- `model-dispatch.service` restarted successfully.
- Service is active/running.
- `/health` returned `{"status": "ok"}`.
- `/v1/chat/completions` using `auto-local` returned a valid OpenAI-compatible response.
- `auto-local` selected `amd-coder-qwen3-coder-30b-32k`.
- Response content was `ok`.

What did not change:
- No Open WebUI config change.
- No OpenCode config change.
- No LiteLLM config change.
- No Docker, MCP, reverse proxy, dashboard, monitoring, or observability change.

## 2026-05-18 — additive model-dispatch aliases implemented in source repo

The additive alias implementation was completed in the `model-dispatch` source repo.

Source repo:
- `strix:/srv/projects/model-dispatch`

Latest source commit:
- `bf49923 add additive dispatch aliases`

What changed in source:
- Added additive aliases in `config.json`.
- Added descriptive Open WebUI display names.
- Added nested route expansion in `app.py`.
- Added explicit `free-cloud` handling so it resolves to `openrouter-free/openrouter/auto-free-router`.
- Updated `tests/check_config.py` to validate direct and expanded route targets.
- Updated `TESTING.md`, `DECISIONS.md`, and `AGENT_STATUS.md`.

Validation:
- `git diff --check` passed.
- `python3 -m py_compile app.py` passed.
- `python3 -m json.tool config.json` passed.
- `python3 tests/check_config.py` passed with `config check passed`.
- Source repo was pushed to `thinkcentre/main`.

What did not change:
- No live `/srv/model-dispatch` deployment.
- No `model-dispatch.service` restart or reload.
- No Open WebUI config change.
- No OpenCode config change.
- No Continue.dev config change.
- No Docker, systemd, MCP, dashboard, monitoring, or observability change.

Next:
- Prepare a deployment approval brief for the additive alias deployment before touching live `/srv/model-dispatch`.

## 2026-05-18 — additive alias deployment committed to homelab docs

The additive `model-dispatch` alias deployment record was committed and pushed.

Homelab commit:
- `24ce0dd document additive alias deployment`

Deployment state:
- Additive aliases are live.
- `/health` validated.
- `/v1/models` lists the new aliases.
- `advisor` and `local/amd-coder` validated through `/v1/chat/completions`.

Backup:
- `/srv/model-dispatch/backups/20260518-093534`

Next:
- Update `CURRENT_SLICE.md` to mark additive alias deployment complete.

## Aider bounded patch trial — local model response failure

Aider was tested on one harmless docs-only edit using the local `model-dispatch` alias `coding`.

Command shape:
- `aider docs/aider-workflow.md --model openai/coding --no-auto-commits`

Result:
- Aider started successfully.
- Aider was limited to `docs/aider-workflow.md`.
- Aider asked whether to add `AGENT_STATUS.md`; user answered no.
- Aider asked whether to add `CURRENT_SLICE.md`; user skipped additional files.
- The local model returned an empty response.
- No edit was made to `docs/aider-workflow.md`.

What changed:
- `CURRENT_SLICE.md` contains the manually added Aider bounded patch test slice.

What did not change:
- No live service was touched.
- No `/srv/model-dispatch` file was touched.
- No OpenCode, Continue.dev, Open WebUI, LiteLLM, Docker, systemd, dashboard, monitoring, or observability config changed.
- Aider did not commit.

Conclusion:
- Aider is installed and can be constrained to one file.
- The local `coding` alias is not yet proven usable with Aider.
- Next Aider trial should use a known-working frontier model or a separately validated Aider-compatible local model profile.

## Aider local-model compatibility trial

Aider was tested with local `model-dispatch` aliases.

Trials:
- `openai/coding`
- `openai/local/amd-coder`

Result:
- Aider started successfully.
- Aider could be constrained to `docs/aider-workflow.md`.
- Aider asked to add extra files; user declined/skipped them.
- Both local model attempts returned an empty response.
- No repository files were changed by Aider.

Conclusion:
- Aider is installed and can be constrained to one file.
- The current local `model-dispatch` aliases are not yet proven compatible with Aider's edit workflow.
- Non-Codex agentic work must use either a local LLM or a verified free OpenRouter model from the allowlist.
- Do not use paid frontier models for Aider/OpenCode/Cline-style agentic work.

Next:
- Create a dedicated Aider compatibility slice before further Aider trials.

## AMD and Strix vLLM readiness inspection

Read-only AMD, Strix, and ThinkCentre routing inspection was performed for the Codex/Aider/vLLM architecture plan.

AMD findings:
- Host `AMD` is reachable.
- RTX 3090 is visible through `nvidia-smi`.
- NVIDIA driver reports CUDA 13.2 support.
- RTX 3090 VRAM is mostly occupied by the current `qwen3-coder-30b` llama.cpp container.
- `rocm-smi` is present and reports AMD GPU devices, but emitted a low-power/device warning.
- Current model containers are healthy:
  - `qwen3-coder-30b` on port 8083.
  - `gemma4-7900xt` on port 8084.
- Existing AMD model endpoints return OpenAI-compatible `/v1/models`.
- `vllm` was not found in the current user path.
- Python is 3.14.4.

Strix findings:
- Host `strix` is reachable.
- Strix Halo Vulkan/RADV device is visible as `Radeon 8060S Graphics (RADV STRIX_HALO)`.
- `rocm-smi` and `rocminfo` are not available.
- `vllm` and `lemonade` were not found in the current user path.
- Current Strix llama.cpp Vulkan containers are healthy:
  - `qwen3-6` on port 8081.
  - `qwen3-coder` on port 8082.
- Existing Strix model endpoints return OpenAI-compatible `/v1/models`.
- Port 8000 is already used by `legacy-printer-app`.

ThinkCentre/model-dispatch findings:
- `model-dispatch` health returned `{"status": "ok"}`.
- `model-dispatch` exposes local AMD and Strix aliases plus OpenRouter-free entries.
- Open WebUI remains routed to `http://192.168.50.225:4010/v1`.
- Open WebUI has Ollama disabled and web search enabled.

Conclusion:
- AMD is the better first vLLM candidate because the NVIDIA/CUDA path is already visible and the coding model role lives there.
- Strix should remain a later vLLM/Lemonade/ROCm readiness slice because ROCm tools are not currently present and port 8000 is occupied.
- Do not run vLLM yet.
- Do not stop existing model containers yet.
- Do not change model-dispatch or Open WebUI routing yet.

Next:
- Plan an AMD-first vLLM validation slice.
- That slice must account for current RTX 3090 VRAM usage before starting any vLLM server.

## AMD vLLM validation planning

The active slice is `AMD vLLM validation planning`.

What changed:
- Updated `CURRENT_SLICE.md` for the AMD-first vLLM validation planning slice.
- Updated `PROJECT_PLAN.md` so the current build stage is `Slice 13: AMD vLLM validation planning`.
- Created `inventory/amd-vllm-validation-plan.md`.

Purpose:
- Plan AMD-first vLLM validation without starting vLLM, installing vLLM, stopping existing containers, changing `model-dispatch`, or changing Open WebUI.

Key planning constraints:
- AMD is the first vLLM candidate because the RTX 3090 and CUDA path are visible.
- The current `qwen3-coder-30b` llama.cpp container occupies most RTX 3090 VRAM.
- Do not stop or restart `qwen3-coder-30b` or `gemma4-7900xt` without a separate explicit approval slice.
- Do not run Aider until curl-only vLLM response-shape checks pass.
- Do not add a `model-dispatch` alias until Aider/vLLM compatibility is proven.

What did not change:
- vLLM was not run.
- vLLM was not installed.
- Aider was not run.
- `model-dispatch` was not edited.
- `/srv/model-dispatch` was not touched.
- Open WebUI, OpenCode, Continue.dev, LiteLLM, dashboards, monitoring, and observability were not changed.
- No `sudo`, Docker write command, or systemd write command was run.

Next:
- Review the diff.
- If accepted, commit the AMD vLLM validation plan.
- The next slice should be Phase 1: read-only AMD live-state recheck.

## AMD vLLM Phase 1 live-state recheck

Read-only AMD live-state recheck was performed for the AMD-first vLLM validation plan.

Findings:
- AMD host is reachable.
- RTX 3090 is visible through `nvidia-smi`.
- NVIDIA driver is `595.71.05`.
- `nvidia-smi` reports CUDA `13.2`.
- `nvcc` is present and reports CUDA toolkit `12.4`.
- RTX 3090 VRAM is mostly occupied: about `18299 MiB / 24576 MiB`.
- The active RTX 3090 compute process is `/app/llama-server`, using about `18276 MiB`.
- `qwen3-coder-30b` is running and healthy on port `8083`.
- `gemma4-7900xt` is running and healthy on port `8084`.
- Both existing endpoints return OpenAI-compatible `/v1/models`.
- Both existing endpoints returned simple chat completions.
- `vllm` was not found in the current user path.
- A local Docker image exists for `vllm/vllm-openai:latest`.
- Existing model artifacts found:
  - `/srv/llm/qwen3-coder-30b/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
  - `/srv/llm/gemma4-rocm/models/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`

Conclusion:
- AMD remains the correct first vLLM candidate.
- The next step should be read-only inspection of the existing `vllm/vllm-openai:latest` image.
- Do not start vLLM yet because RTX 3090 VRAM is currently occupied by the healthy `qwen3-coder-30b` endpoint.
- Do not stop or restart `qwen3-coder-30b` or `gemma4-7900xt` without a separate approval slice.

What did not change:
- vLLM was not started.
- vLLM was not installed.
- Aider was not run.
- No containers were stopped or restarted.
- No Docker write command was run.
- No systemd or sudo command was run.
- `model-dispatch` and Open WebUI routing were not changed.

Next:
- Phase 2: read-only inspect the local `vllm/vllm-openai:latest` image and candidate runtime method.

## AMD vLLM Phase 2 local image/runtime inspection

Read-only inspection of the local `vllm/vllm-openai:latest` image was performed.

Findings:
- Local image `vllm/vllm-openai:latest` exists on AMD.
- Initial dry-run with `python` failed because the image provides `python3`, not `python`.
- `python3` exists inside the image.
- `vllm` exists inside the image.
- Image Python version is `3.12.13`.
- Torch version is `2.10.0+cu129`.
- Torch CUDA version is `12.9`.
- vLLM version is `0.19.0`.
- The vLLM OpenAI API server help is available through `python3 -m vllm.entrypoints.openai.api_server --help`.
- With `--gpus all`, the image can see the RTX 3090.
- CUDA is available inside the image.
- The image reports one CUDA device:
  `NVIDIA GeForce RTX 3090`.
- Container-visible GPU memory was about:
  - free: `5836898304`
  - total: `25298141184`
- Existing containers remained running after dry checks:
  - `qwen3-coder-30b`
  - `gemma4-7900xt`

Conclusion:
- The local vLLM image is viable enough for a future approved runtime test.
- The next blocker is not image availability; it is RTX 3090 VRAM availability.
- Do not start vLLM yet because `qwen3-coder-30b` is still using most RTX 3090 VRAM.
- Do not stop or restart `qwen3-coder-30b` without a separate approval slice.

What did not change:
- vLLM was not started as a server.
- No vLLM package was installed.
- No image was pulled.
- No containers were stopped or restarted.
- No model-dispatch or Open WebUI routing was changed.
- No Aider trial was run.

Next:
- Plan the approved temporary runtime test, including port, model choice, VRAM freeing decision, exact start command, curl-only checks, and rollback command.

## AMD vLLM local model inventory

A read-only AMD model inventory was performed to determine whether a local HF/safetensors-style model candidate exists for vLLM.

Findings:
- Local HF/safetensors-style model directories were found under `/home/enzo/.cache/huggingface/hub/`.
- Candidate local HF-style models include:
  - `Qwen2.5-1.5B-Instruct`
  - `Qwen2.5-7B-Instruct`
  - `Qwen2.5-Coder-7B-Instruct`
  - `Qwen3-14B-AWQ`
  - `Qwen3.5-35B-A3B-GPTQ-Int4`
  - `cyankiwi/Qwen3-Coder-30B-A3B-Instruct-AWQ-4bit`
- Active llama.cpp GGUF artifacts remain:
  - `/srv/llm/qwen3-coder-30b/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
  - `/srv/llm/gemma4-rocm/models/google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- The HF-like directory summary found tokenizer files and safetensors weights for multiple Qwen candidates.
- `qwen3-coder-30b` remained healthy on port `8083`.
- `gemma4-7900xt` remained healthy on port `8084`.
- RTX 3090 VRAM remained mostly occupied by `/app/llama-server`.

Conclusion:
- Model acquisition is not the immediate next step.
- The next step should be read-only inspection of exact candidate model directories.
- The existing GGUF artifacts remain unsuitable as the first vLLM candidate unless separately proven otherwise.
- Do not stop `qwen3-coder-30b` yet.

Candidate priority:
- For a no-interruption vLLM smoke test, inspect `Qwen2.5-1.5B-Instruct`.
- For a coding-relevant vLLM test, inspect `Qwen2.5-Coder-7B-Instruct`.
- For a larger coding candidate, inspect `cyankiwi/Qwen3-Coder-30B-A3B-Instruct-AWQ-4bit`, but assume it may require freeing RTX 3090 VRAM.

What did not change:
- vLLM was not started.
- No model was downloaded.
- No containers were stopped or restarted.
- No Docker write command was run.
- No model-dispatch or Open WebUI routing was changed.

Next:
- Read-only inspect the exact local candidate directories and choose the first runtime candidate.

## AMD temporary vLLM runtime test succeeded and rolled back

A temporary AMD vLLM runtime test was performed using the downloaded
`Qwen2.5-Coder-7B-Instruct` HF/safetensors model.

Model acquisition:
- Hugging Face authentication was configured on AMD outside Git.
- HF username verification succeeded without exposing the token.
- `Qwen/Qwen2.5-Coder-7B-Instruct` was downloaded to:
  `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`
- The model directory is about `15G`.
- Safetensors shards are real multi-GB files, not placeholder cache entries.

Temporary vLLM runtime:
- `qwen3-coder-30b` was stopped to free RTX 3090 VRAM.
- `gemma4-7900xt` remained running on port `8084`.
- Temporary vLLM container was started:
  `amd-vllm-temp-test`
- Image:
  `vllm/vllm-openai:latest`
- Model path:
  `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`
- Served model:
  `amd-vllm-temp-qwen2.5-coder-7b`
- Host port:
  `18000`
- vLLM loaded the model as `Qwen2ForCausalLM`.
- vLLM loaded all four safetensors checkpoint shards successfully.
- vLLM started the OpenAI-compatible server successfully.

Curl validation:
- `GET /v1/models` returned HTTP 200 and listed:
  `amd-vllm-temp-qwen2.5-coder-7b`
- `POST /v1/chat/completions` returned HTTP 200.
- Completion content was:
  `vllm-ok`

Rollback:
- Temporary vLLM container `amd-vllm-temp-test` was stopped.
- `qwen3-coder-30b` was restarted.
- `qwen3-coder-30b` returned healthy on port `8083`.
- `gemma4-7900xt` remained healthy on port `8084`.
- `8083 /v1/models` again returned:
  `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- `8084 /v1/models` continued returning:
  `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- RTX 3090 VRAM returned to the expected llama.cpp state, with `/app/llama-server`
  using about `18212 MiB`.

What changed:
- A real HF/safetensors model now exists at:
  `/srv/llm/hf/Qwen2.5-Coder-7B-Instruct`
- Runtime state was temporarily changed during the approved test and then rolled
  back.

What did not change:
- `model-dispatch` was not edited.
- Open WebUI routing was not changed.
- Aider was not run.
- No vLLM endpoint was added to model-dispatch.
- No persistent vLLM container, Compose file, systemd unit, restart policy,
  wrapper, watcher, or daemon was created.

Conclusion:
- Direct temporary vLLM serving on AMD is proven with a real HF/safetensors
  coding model.
- The next decision is whether to test Aider directly against the temporary vLLM
  endpoint, or first create a dedicated model-dispatch alias plan.

## Direct Aider vLLM one-file docs trial succeeded

Aider was tested directly against the temporary AMD vLLM endpoint.

Endpoint:
- `http://192.168.50.252:18000/v1`

Model:
- `openai/amd-vllm-temp-qwen2.5-coder-7b`

Task:
- One small docs-only edit to `docs/aider-workflow.md`.
- Add section: `Direct vLLM Trial Note`.

Result:
- Aider connected to the direct vLLM endpoint.
- Aider returned a non-empty response.
- Aider edited only `docs/aider-workflow.md`.
- Aider asked to add extra files:
  - `AGENT_STATUS.md`
  - `CURRENT_SLICE.md`
  - `PROJECT_PLAN.md`
  - `AGENTS.md`
  - `CODEX_CONTEXT.md`
  - `DECISIONS.md`
- The user declined each extra file request.
- Aider did not commit.
- `git diff --check` passed.
- `git diff --stat` showed only:
  `docs/aider-workflow.md | 4 ++++`

Conclusion:
- Direct Aider against temporary AMD vLLM is now proven for a one-file docs edit.
- The previous empty-response failure appears tied to the earlier local alias/model-dispatch path, not Aider itself.
- Aider still tries to add context/control files when they are mentioned, so future trials must continue to decline extra files or avoid naming out-of-scope files in the prompt where practical.

What did not change:
- No model-dispatch alias was added.
- Open WebUI routing was not changed.
- No service config was changed.
- No Docker/systemd persistent unit, wrapper, restart policy, or daemon was created.

Next:
- Decide whether to run a second Aider trial with a slightly more realistic one-file patch, or plan a dedicated model-dispatch alias for the proven vLLM endpoint.

## Second direct Aider vLLM one-file docs trial succeeded

A second direct Aider trial was run against the temporary AMD vLLM endpoint.

Endpoint:
- `http://192.168.50.252:18000/v1`

Model:
- `openai/amd-vllm-temp-qwen2.5-coder-7b`

Task:
- Update only `docs/aider-workflow.md`.
- Replace the one-sentence `Direct vLLM Trial Note` with a structured bullet list.

Result:
- Aider connected to the direct AMD vLLM endpoint.
- Aider returned a non-empty response.
- Aider edited only `docs/aider-workflow.md`.
- Aider asked to add extra files:
  - `AGENTS.md`
  - `AGENT_STATUS.md`
  - `CODEX_CONTEXT.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `PROJECT_PLAN.md`
- The user declined each extra file request.
- Aider did not commit.
- `git diff --check` passed.
- `git diff --stat` showed only:
  `docs/aider-workflow.md | 6 +++++-`

Rollback:
- Temporary vLLM container `amd-vllm-temp-test` was stopped.
- `qwen3-coder-30b` was restarted and became healthy on port `8083`.
- `gemma4-7900xt` stayed healthy on port `8084`.
- `8083 /v1/models` returned:
  `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`
- `8084 /v1/models` returned:
  `google_gemma-4-26B-A4B-it-Q4_K_M.gguf`
- RTX 3090 returned to the expected llama.cpp state, with `/app/llama-server`
  using about `18212 MiB`.

Conclusion:
- Direct Aider against AMD vLLM is now proven twice for bounded one-file docs edits.
- Aider still asks to add context/control files, but it respected declined file additions.
- The next sensible step is to plan a dedicated model-dispatch alias for the proven vLLM endpoint, or decide that direct Aider-to-vLLM is sufficient for now.
