# Roadmap: Two-Surface Homelab Workflow

This roadmap describes the path from the current setup to a practical two-surface workflow.

Last updated: 2026-05-06.

## Current Facts To Preserve

- AMD is the current OpenCode and coding execution host.
- AMD OpenCode now defaults directly to `homelab-local` at `http://192.168.50.252:8083/v1`.
- AMD OpenCode exposes `homelab-openrouter-free` as a manual-only provider with 25 verified free OpenRouter models.
- ThinkCentre hosts Open WebUI and related services. LiteLLM is still active for Open WebUI and retained for OpenCode rollback, but it is no longer the default OpenCode router.
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
  -> OpenCode on the project host through direct local-coder path
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

Create clear project-local instructions for OpenCode.

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
5. Run OpenCode on the project host.
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
- OpenCode remains the coder path to recenter around.

## Slice 7: Transition Away From LiteLLM Active Routing

LiteLLM is no longer the target long-term active routing layer for OpenCode or Open WebUI.

Completed for OpenCode:
- OpenCode uses `homelab-local` direct local-coder by default.
- OpenCode exposes OpenRouter only through generated `homelab-openrouter-free` free-only manual provider entries.
- OpenRouter free-model discovery and filtering is preserved.
- Generated free-model artifacts exist under `/srv/openrouter-free/`.

Still pending:
- Open WebUI still routes through LiteLLM.
- LiteLLM remains active for Open WebUI and retained for OpenCode rollback.
- Later stability review can decide whether LiteLLM should be removed from OpenCode entirely.

Definition of done:
- Docs describe LiteLLM as transitional/rollback, not the long-term router.
- OpenCode direct local-coder path is tested.
- OpenRouter free-only generated provider is tested manually.
- Open WebUI direct endpoints are tested in a later slice.
- LiteLLM rollback path is documented.

## Future Routing Work

- Add an optional direct AMD backup provider for the RX 7900 XT endpoint.
- After a stability period, decide whether to remove LiteLLM from OpenCode entirely while preserving rollback notes.
- Reevaluate Open WebUI routing later; do not claim it has migrated until the live Open WebUI config changes.

## Optional Later Improvements

Only consider these after the basic loop works:

- tmux logging for coder sessions.
- Better known-location coder log capture for `advisor-packet`.
- Continue.dev review through direct/local model configuration after router transition.
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

- Continue.dev should eventually remove stale endpoints and align with the post-LiteLLM direct/local model configuration.
- MCP Ledger should eventually become a Pattern A service on Strix if it remains part of the stack.
- Git mirror topology should converge on Strix canonical, ThinkCentre tier-1, Mac Mini tier-2.
- iMessage relay and family dashboard documentation should be captured in the homelab repo.
- Aider was evaluated and eliminated from the homelab workflow; do not migrate or integrate it.
