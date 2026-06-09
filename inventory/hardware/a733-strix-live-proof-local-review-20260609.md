# A733 Strix Live-Proof Local Review - 2026-06-09

Status: advisory review consumed
Scope: workflow guardrails only; no kernel patches rewritten or submitted

## Why This Exists

The active maintainer path is still blocked on exact v4 Cubie A7S runtime
proof. While waiting on the live operator/password step, Codex Desktop used the
configured local LLM lanes to review whether the Strix-dispatched proof flow
could mislead later patch preparation.

This preserves the useful result from the ignored generated context-card
directory in a tracked inventory note.

## Local Lanes Used

Command:

```sh
scripts/kernel-token-offload review-matrix \
  --file task-packets/kernel/reviews/a733-strix-live-proof-flow-review-20260609.md \
  --title a733-strix-live-proof-flow-review-20260609 \
  --prompt 'Find three ways this Strix-dispatched live-proof workflow could still mislead Codex into violating Linux kernel maintainer expectations. Keep the answer advisory and do not propose patch rewrites before runtime proof.' \
  --max-tokens 700 \
  --max-model-chars 12000
```

Generated advisory card:

```text
task-packets/kernel/context-cards/review-matrix-a733-strix-live-proof-flow-review-20260609-c67669ffba29.md
task-packets/kernel/context-cards/review-matrix-idle-review-a733-strix-live-proof-flow-review-20260609.md-5cfdfff5e061.md
```

Model lanes reported in the manifest:

- `amd-fast`: `qwen3.6-27b-q4km-amd-rtx3090-vulkan`
- `amd-research`: `qwen36-27b-7900xt-research`
- `strix-review`: `qwen3.6-27b-rocmfp4-mtp`

The manifest recorded no lane errors.

## Findings Consumed

Useful review signal:

- A successful boot with RAM-only `drm_debug=1` must not be confused with
  upstream DTS correctness.
- Bootability is not broad SoC correctness; the proof only supports the narrow
  v4 kernel/DTB boot path that the UART log actually demonstrates.
- Runtime proof must not promote local CCU/PRCM or pinctrl scaffolding while
  the external A733 RFCs remain the dependency path.

Action taken:

- Commit `77f93a8` made `scripts/cubie-corrected-root-proof-gate` report
  `drm_debug=1` under "Upstream Limitations" as a RAM-only vendor U-Boot
  workaround that is not upstream DTS evidence.
- The selftest now fails if the passing report does not mark that workaround as
  lab-only.
- The 2026-06-09 refresh also caught that pasteable Strix commands must include
  the SSH user. Operator-facing commands now use `enzo@192.168.50.11`, while
  `KERNEL_STRIX_HOST` remains the physical Strix host/IP for inventory and
  local-host detection.
- A follow-up search found no `drm_debug` occurrences in checked DTS, DTSI, or
  YAML files under the local A733/public kernel trees or the Strix copies; the
  token remains confined to lab bootargs and documentation.
- The Cubie `codex` automation user now passes Strix-to-Cubie2 and
  Strix-to-Cubie3 SSH plus `sudo -n true`; Cubie3's corrected-root extlinux
  entry is installed and checksum-verified.
- The Strix live UART proof for
  `a733-v4-abc8d07b0a63-partuuid-ro-proof` was captured at
  `tools/hardware-logs/cubie-uart/20260609T172722Z-a733-v4-abc8d07b0a63-partuuid-ro-proof-ttyUSB0.uart.log`
  and passes `scripts/cubie-latest-corrected-root-proof --strict`.

## Remaining Blocker

The actual maintainer-path blocker has advanced:

```text
A733 export shape is not maintainer-ready: too-many-patches, local CCU/pinctrl scaffolding, standalone MMC compatible, MAINTAINERS sun60i pattern, missing Depends-on headers
```

Do not reshape the public patch export, draft maintainer-facing mail, or claim
runtime proof beyond the captured evidence without preserving the strict gate
result and the upstream guardrails.
