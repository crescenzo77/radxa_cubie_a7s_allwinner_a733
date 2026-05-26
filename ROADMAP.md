# Roadmap: Two-Surface Homelab Workflow

This roadmap describes the path from the current setup to a practical
human-reviewed homelab workflow.

Last updated: 2026-05-23.

## Current Facts To Preserve

- Codex is the primary manual agent for planning, sequencing, approval briefs,
  and risky live-service work.
- Claude Code is a strong frontier-code alternative and second opinion.
- Aider is the preferred bounded repo patch assistant after a slice is planned.
  Direct Aider-to-temporary AMD vLLM is proven twice for bounded one-file docs
  edits, but Aider through `model-dispatch` is not yet proven.
- Non-Codex agentic work must use local LLMs or verified OpenRouter-free models
  only.
- vLLM is the preferred candidate serving layer for local coding/reasoning
  models on AMD and Strix, subject to validation.
- AMD vLLM with `Qwen2.5-Coder-7B-Instruct` is proven as a temporary direct
  endpoint at `http://192.168.50.252:18000/v1`, served as
  `amd-vllm-temp-qwen2.5-coder-7b`; it is not persistent and should not be
  treated as always available.
- AMD RTX 3090 is currently mode-switched between `qwen3-coder-30b` llama.cpp
  on `8083` and temporary vLLM on `18000`; both should not be assumed
  available at the same time.
- Qwen thinking-off or non-thinking mode is the baseline to test for Aider
  patch workflows.
- Reasoning-parser mode should be validated separately for complex
  review/architecture work.
- Hermes is observer, summarizer, reviewer, recorder, and
  approved-skill-assisted preservation checker only. It must not edit
  canonical repos, install live skills, restart services, or become an
  approval daemon.
- OpenCode is a later local-agent experiment, not the assumed next primary
  operating agent.
- Continue.dev remains editor assist and review.
- Cline remains sandbox-only.
- AMD has the current OpenCode local-agent setup if an explicit experiment
  needs it later.
- AMD OpenCode now defaults directly to `homelab-local` at `http://192.168.50.252:8083/v1`.
- AMD OpenCode uses `homelab-local-backup` at `http://192.168.50.252:8084/v1` as the direct RX 7900 XT backup provider for `small_model`.
- AMD OpenCode exposes `homelab-openrouter-free` as a manual-only provider with 25 verified free OpenRouter models.
- ThinkCentre hosts Open WebUI, model-dispatch, and related services. Open WebUI now points to `model-dispatch` at `http://192.168.50.225:4010/v1`.
- LiteLLM is retained for rollback/history, but it is no longer the active Open WebUI endpoint or the default OpenCode router.
- Strix is the target canonical project/source host.
- Framework laptop remains a thin client.
- OpenRouter must remain free-only and fail-closed; target is generated free-only config under `/srv/openrouter-free/`, not LiteLLM as active router.
- Codex/Claude-style tools must not be wired into API automation.
- The workflow should favor stable, practical, proven OSS with minimal bespoke glue.

## Target State

The normal loop is:

```text
Open WebUI advisor
  <- compact advisor-packet markdown
  -> user decision
  -> task-shaped manual agent selection
  -> git diff and shared markdown status
  -> advisor-packet again when needed
```

The user remains the final decision-maker. The system does not auto-approve coder actions.

## Slice 1: Create Canonical Homelab Repo and Add Operating Files

Create the canonical homelab repo on Strix:

```text
strix:/srv/projects/homelab/
```

Add the initial operating files:

- `PROJECT_PLAN.md`
- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`
- `AGENTS.md`
- `HOMELAB_LAYOUT.md`
- `WORKFLOW.md`
- `ROADMAP.md`

Seed the architecture docs from the two-surface versions.

Definition of done:

- The homelab docs have one canonical project location.
- The operating files exist and are committed.
- The Framework laptop remains only a client.
- Existing one-off docs can be archived or copied in without creating multiple sources of truth.

## Slice 2: Build `advisor-packet` Script

Build a small local script named:

```text
advisor-packet
```

It should run from a project working tree and print a compact markdown packet.

Initial packet contents:

- Header with repo path and timestamp.
- `CURRENT_SLICE.md`, if present.
- `DECISIONS.md`, bounded to recent entries.
- `AGENT_STATUS.md`, if present.
- `AGENTS.md`, bounded.
- `git status --short`.
- `git diff --stat`.
- Bounded `git diff` excerpt.
- Bounded recent coder log, if a known log file is present.

Definition of done:

- Running `advisor-packet` in the homelab repo produces markdown suitable for Open WebUI.
- Output is bounded by default.
- It does not call paid APIs.
- It does not supervise or approve anything.
- It works without network access.

## Slice 3: Add `AGENTS.md` Rules for Coder Status and Approval Briefs

Create clear project-local instructions for bounded coding agents.

`AGENTS.md` should require the coder to:

- Work only on the current slice unless explicitly redirected.
- Keep changes narrow and reviewable.
- Update `AGENT_STATUS.md` before handoff.
- List files changed.
- List tests or checks run.
- Identify risks or blockers.
- Ask for user approval before broadening scope.

Definition of done:

- A coder can read `AGENTS.md` and understand the project rules.
- `AGENT_STATUS.md` becomes the standard handoff surface.
- The advisor no longer needs raw terminal transcripts for normal interpretation.

## Slice 4: Test the Loop on One Small Real Task

Pick one small, real task in the homelab repo.

Run the complete loop:

1. Update `CURRENT_SLICE.md`.
2. Run `advisor-packet`.
3. Paste the packet into Open WebUI.
4. Generate a coder prompt.
5. Run the selected bounded coding agent on the project host.
6. Review the diff.
7. Update `DECISIONS.md` if needed.
8. Commit.

Definition of done:

- One real change lands through the two-surface loop.
- The user reviews and approves the final diff.
- Pain points are written down in `DECISIONS.md` or `PROJECT_PLAN.md`.
- No automation is added beyond the packet script.

## Slice 5: Aider Evaluation and Elimination

Aider was evaluated as a possible steady-state coder and eliminated after unsafe file-handling behavior during a simple documentation task.

This is preserved as historical context. Later decisions supersede the
OpenCode-recenter conclusion by allowing Aider back only as a bounded patch
assistant and keeping OpenCode as a later local-agent experiment.

Evaluation criteria:

- Works through local/self-hosted direct endpoints where possible.
- Produces reviewable diffs.
- Handles project instructions from `AGENTS.md`.
- Leaves useful `AGENT_STATUS.md` handoffs.
- Does not need paid API automation.
- Feels stable enough for repeated use.

Definition of done:

- `DECISIONS.md` records that Aider is eliminated from the homelab workflow.
- The workflow docs no longer present Aider as an active default or fallback path.
- The then-current OpenCode recentering conclusion is historical and no longer
  the active strategy.

## Slice 8: Aider Workflow Integration

The workflow is corrected to use Aider only as a bounded patch assistant after a
slice is planned.

Definition of done:
- `WORKFLOW.md` describes agent division of labor.
- `WORKFLOW.md` includes the Aider use rule.
- `docs/aider-workflow.md` documents the standard Aider workflow.
- `CURRENT_SLICE.md` and `AGENT_STATUS.md` reflect the handoff.
- No Aider installation, service change, model-dispatch edit, client config
  change, or commit happens in this slice.

## Slice 11: Codex Aider vLLM Hermes Strategy Consolidation

The workflow is consolidated around Codex for planning/risk, Aider for bounded
patch work after compatibility is validated, vLLM as the preferred serving
candidate for AMD and Strix tests, and Hermes as observer/reviewer/skill
proposer only.

Definition of done:
- `CURRENT_SLICE.md` identifies this active strategy consolidation slice.
- `inventory/codex-aider-vllm-hermes-strategy.md` records roles, target
  architecture, AMD/Strix vLLM roles, Aider compatibility path, Qwen mode
  decision tree, Hermes boundary, non-goals, validation order, and stop
  conditions.
- `WORKFLOW.md` no longer implies OpenCode is the next primary agent.
- Roadmap and status docs reflect the vLLM/Aider/Hermes direction.
- No Aider run, vLLM run, live-service edit, service restart, Docker/systemd,
  or commit happens in this slice.

## Slice 12: Codex Aider vLLM Architecture Planning

The architecture direction is documented around Codex as the high-trust manual
planner/reviewer, Aider as the bounded patch tool after compatibility is
proven, vLLM as the clean serving layer to evaluate for Aider-compatible local
models on AMD and Strix, `model-dispatch` as the policy/routing layer, and
Hermes as observer/reviewer/recorder/preservation checker only.

Definition of done:
- `CURRENT_SLICE.md` identifies this active architecture planning slice.
- `inventory/codex-aider-vllm-architecture-plan.md` records the operating
  decision, roles, Qwen thinking-mode treatment, Aider compatibility approach,
  non-changes, and phased path.
- OpenCode is not treated as the primary coder path.
- The phased path is preserved: document architecture, inspect AMD/Strix vLLM
  readiness, curl-only vLLM test, harmless one-file Aider docs edit, dedicated
  `model-dispatch` alias only after proof, then Hermes read-only preservation
  check.
- No Aider run, vLLM run, model-dispatch edit, live-service edit, service
  restart, Docker/systemd, or commit happens in this slice.

## Slice 7: Transition Away From LiteLLM Active Routing

LiteLLM is no longer the target long-term active routing layer for OpenCode or Open WebUI.

Completed for OpenCode:
- OpenCode uses `homelab-local` direct local-coder by default.
- OpenCode uses `homelab-local-backup` direct AMD RX 7900 XT endpoint for `small_model`.
- OpenCode exposes OpenRouter only through generated `homelab-openrouter-free` free-only manual provider entries.
- OpenRouter free-model discovery and filtering is preserved.
- Generated free-model artifacts exist under `/srv/openrouter-free/`.

Completed for Open WebUI:
- Open WebUI points to `model-dispatch` on ThinkCentre at `http://192.168.50.225:4010/v1`.
- `model-dispatch.service` runs from `/srv/model-dispatch`.
- Open WebUI exposes local auto routes, explicit local models, `openrouter-free/openrouter/auto-free-router`, and verified `openrouter-free/<verified-model>:free` entries.
- OpenRouter paid catalog remains hidden.

Still pending:
- Improve model-dispatch token estimation.
- Decide how long to retain LiteLLM rollback/history.
- Decide whether `model-dispatch` should get its own repo.
- Decide the future Continue.dev path.

Definition of done:
- Docs describe LiteLLM as transitional/rollback, not the long-term router.
- OpenCode direct local-coder path is tested.
- OpenRouter free-only generated provider is tested manually.
- Open WebUI model-dispatch migration is documented as complete.
- LiteLLM rollback path is documented.

## Future Routing Work

- Improve model-dispatch token estimation, especially for long pasted logs and advisor packets.
- After a stability period, decide whether to keep or retire LiteLLM rollback/history.
- Decide whether `/srv/model-dispatch` should become its own repo.
- Decide whether Continue.dev should remain LiteLLM-routed, move to model-dispatch, or use another explicit local path.

## Architecture Transition Plan

This plan transitions the homelab toward a clearer platform split:
ThinkCentre control plane, Strix canonical source/development/code-graph host,
AMD mode-switched GPU compute worker, MiniPC LAN backup/artifact storage, Mac
Mini Apple services and tier-2 git mirror, Oracle Headscale/off-site
backup/external anchor, and Cubies as edge camera nodes only.

Each slice must be reversible, validated, and reviewable. No slice should add
hidden automation, autonomous approval behavior, paid fallback, or broad
orchestration. Codex may assist with patches and docs, but it must not become
background infrastructure.

### Slice 0: Baseline Inventory and Freeze Point

Capture the current live state before moving anything.

Definition of done:
- Current model endpoints, OpenCode config posture, Open WebUI routing,
  Continue.dev routing, git mirror state, and service locations are documented.
- Rollback references are recorded.
- No live services are changed.

### Slice 1: `model-dispatch` First-Class Repo

Move `model-dispatch` source/config into a reviewable repo boundary without
changing the live service behavior.

Definition of done:
- Repo ownership, service source path, config files, and deploy path are
  documented.
- Existing live behavior is reproducible from reviewed files.
- No service restart or config change happens without a later approval brief.

### Slice 2: Model Registry and Stable Aliases

Define the model registry and stable aliases that clients should use.

Definition of done:
- Aliases for advisor, coding, reasoning, small, training, and creative roles
  are documented.
- Open WebUI, OpenCode, Continue.dev, and scripts have intended alias mappings.
- Rollback aliases or direct endpoints remain documented.

### Slice 3: Strix Dual-Coder/Reasoning Layout

Document and validate Strix as the source/development/code-graph/reasoning host.

Definition of done:
- Strix project layout, coder/reasoning endpoints, and CodeGraphContext
  boundaries are documented.
- No direct CodeGraphContext mutation of canonical repos is allowed.
- AMD remains available for current coding until migration is validated.

### Future Slice: OpenCode Through `model-dispatch`

Evaluate OpenCode through stable `model-dispatch` aliases only after an
explicit local-agent experiment slice.

Definition of done:
- Candidate OpenCode config is tested in isolation.
- Direct AMD routing remains documented rollback.
- Live OpenCode config is changed only after operator approval.

### Future Slice: AMD vLLM Coding Validation

Validate vLLM as the preferred candidate serving layer for local coding models
on AMD before any Aider patch trial depends on it.

Definition of done:
- Candidate model, vLLM launch shape, endpoint, rollback path, and validation
  commands are documented before execution.
- OpenAI-compatible response shape is validated without running Aider first.
- Qwen thinking-off or non-thinking mode is tested as the baseline patch-output
  mode.
- No client routing changes happen without a later approval brief.

### Future Slice: Aider vLLM Compatibility Trial

After AMD vLLM response shape is validated, test Aider against one file in one
repo with one planned edit and one reviewable diff.

Definition of done:
- The trial uses a local LLM or verified OpenRouter-free model only.
- Aider is constrained to one repo and one bounded edit.
- The diff is reviewed and validated before commit.
- Any empty-response, edit-format, or model-metadata issue is recorded instead
  of worked around with broad automation.

### Future Slice: Strix vLLM Reasoning Validation

Validate vLLM on Strix for reasoning/review workloads near canonical source and
code-graph context.

Definition of done:
- Reasoning-parser mode is tested separately from Aider patch workflows.
- Review/architecture quality and response-shape behavior are documented.
- Strix remains source/development/code-graph host, not an autonomous mutator.
- Client routing changes require a separate approval brief.

### Future Slice: Hermes Read-Only Review Workflow

Define how Hermes may observe, summarize, review, and propose skills without
mutating canonical repositories or live services.

Definition of done:
- Read-only inputs, output artifacts, and review boundaries are documented.
- Hermes does not install live skills, restart services, edit canonical repos,
  or become an approval daemon.
- Any proposed skill is reviewed manually before installation.

### Slice 5: Canonical Repos to Strix

Move canonical project repositories to Strix where appropriate.

Definition of done:
- Repo inventory and ownership are documented.
- ThinkCentre tier-1 mirrors are validated.
- Mac Mini tier-2 mirror expectations are documented.
- Projects that must remain AMD-local are explicitly listed.

### Slice 6: Worktree Parallelism

Define safe parallel worktree patterns for reviewable agent/coder work.

Definition of done:
- Worktree naming, cleanup, review, and promotion rules are documented.
- Disposable worktrees are preferred for risky or tool-assisted edits.
- Canonical working trees remain protected.

### Slice 7: Scoped CodeGraphContext Live Use

Enable CodeGraphContext only for scoped, validated use cases if there is a
source-heavy project need.

Definition of done:
- Read-only indexing boundaries are documented.
- Any write-capable use is confined to disposable worktrees or sandboxes.
- Live MCP enablement requires its own approval brief.

### Slice 8: AMD Mode Switching

Define AMD modes for coding, LoRA/training, and creative GPU workloads.

Definition of done:
- Modes, required services, stop/start boundaries, and rollback steps are
  documented.
- No hidden scheduler or autonomous mode switcher is added.
- Manual validation exists for each mode before regular use.

### Slice 9: Continue.dev Through `model-dispatch`

Move Continue.dev from LiteLLM routing to stable `model-dispatch` aliases.

Definition of done:
- Candidate Continue.dev config is documented and tested.
- LiteLLM remains rollback until the new path is stable.
- Paid-provider exposure remains blocked.

### Slice 10: Observability Foundation

Place basic monitoring under the ThinkCentre control-plane role.

Observability remains deferred. No dashboard deployment is part of the current
`model-dispatch` transition. Any monitoring or dashboard work requires a future
explicit slice and operator approval before implementation.

Definition of done:
- Monitoring scope, endpoints, and retained metrics are documented.
- No hidden remediation or approval automation is added.
- Alerts remain informational unless explicitly approved later.

### Slice 11: Service Catalog and Inventory

Create a durable service catalog for hosts, ports, repos, data paths, and
ownership.

Definition of done:
- Services have documented host, port, source/config path, data path, and
  rollback notes where known.
- Secrets and raw logs are excluded.
- Inventory is reviewable markdown or another simple local format.

### Slice 12: Backup/Restore Hardening

Validate MiniPC, Mac Mini, and Oracle backup/restore roles.

Definition of done:
- Backup sources, destinations, retention expectations, and restore tests are
  documented.
- At least one restore path is tested for critical repos or artifacts before
  relying on it.
- No paid backup automation is introduced.

### Slice 13: LiteLLM Retirement Decision

Decide whether LiteLLM remains rollback/history or is retired.

Definition of done:
- Remaining clients and rollback needs are reviewed.
- Retirement, retention, or cold-standby options are documented.
- Any live stop/remove action requires explicit operator approval.

### Slice 14: Mac Mini Cleanup

Limit Mac Mini to Apple/iMessage services and tier-2 git mirror duties.

Definition of done:
- Active Mac Mini services are inventoried.
- Non-target responsibilities are either retired, moved, or explicitly retained
  with rationale.
- Tier-2 mirror behavior is documented and validated.

### Slice 15: Cubie/Camera Edge Nodes

Keep Cubies as edge camera nodes only.

Definition of done:
- Camera-node responsibilities are documented separately from control-plane
  services.
- No model routing, source ownership, or control-plane duties are assigned to
  Cubies.
- Runtime changes wait for hardware readiness and explicit approval.

## Optional Later Improvements

Only consider these after the basic loop works:

- tmux logging for coder sessions.
- Better known-location coder log capture for `advisor-packet`.
- Continue.dev validated against LiteLLM routing using current verbose LiteLLM model IDs.
- Small shell completions or local install convenience for `advisor-packet`.

These remain optional. Do not build them before the simple markdown-plus-git loop proves useful.

Definition of done:

- Any optional improvement removes observed friction.
- No hidden watcher, daemon, autonomous supervisor, or paid API automation is introduced.

## Explicitly Out of Scope

- Codex API usage.
- Codex wrappers.
- Claude/Codex scheduled tasks.
- Background approval jobs.
- Custom approval daemons.
- Hidden watcher agents.
- MCP failure-supervision.
- Paid API automation.
- Fragile bespoke orchestration.
- Moving project state onto the Framework laptop.

## Existing Roadmap Items To Reconcile Later

These remain valid but are not the immediate two-surface build:

- Continue.dev remains intentionally LiteLLM-routed for shared editor-side model access and stable review semantics.
- MCP Ledger should eventually become a Pattern A service on Strix if it remains part of the stack.
- Git mirror topology should converge on Strix canonical, ThinkCentre tier-1, Mac Mini tier-2.
- iMessage relay and family dashboard documentation should be captured in the homelab repo.
- Aider is allowed only as a bounded patch assistant after a slice is planned;
  do not migrate it into automation or live-service workflows.
