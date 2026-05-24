# Codex Aider vLLM Hermes Strategy

## Purpose

Consolidate the current development workflow direction before any new tool or
serving trials. The strategy is to use Codex for planning and high-risk
sequencing, Aider for bounded patch work once compatibility is validated, vLLM
as the preferred serving candidate for local coding and reasoning models, and
Hermes only as an observer/reviewer/skill proposer.

This is a documentation strategy record. It does not authorize tool execution,
service changes, or repository mutation outside the homelab docs.

## Current State

- Codex is the primary manual agent for planning, sequencing, approval briefs,
  documentation slices, and risky live-service work.
- Aider is the preferred bounded patch assistant, but local compatibility is
  not solved yet.
- Aider trials against local `model-dispatch` aliases returned empty responses.
- Non-Codex agentic work must use local LLMs or verified OpenRouter-free models
  only.
- OpenCode is no longer the assumed next primary coder. It remains a later
  local-agent experiment.
- Existing OpenCode and Open WebUI routing history is preserved for rollback
  and context, but it should not drive the development-agent choice.
- vLLM is the preferred candidate serving layer for future AMD and Strix local
  coding/reasoning tests, subject to validation.
- Hermes must stay outside canonical-repo mutation and live-service operation.

## Development Roles

| Tool | Role |
|---|---|
| Codex | Primary planner, sequencer, documentation editor, approval-brief author, and risky live-service choreographer. |
| Aider | Preferred bounded patch assistant for one planned edit in one repo after compatibility is validated. |
| vLLM | Preferred candidate model-serving layer for local coding/reasoning models on AMD and Strix. |
| Hermes | Observer, summarizer, reviewer, and skill proposer only. |
| OpenCode | Deferred local-agent experiment, not the default operating coder. |
| Continue.dev | Editor assist and selected code review. |
| Claude Code | Frontier-code alternative or second opinion when explicitly chosen. |

Codex and Aider remain manually invoked development tools. Do not wrap them in
daemons, approval loops, scheduled jobs, or hidden background workflows.

## Target Architecture

The target operating shape is:

```text
Open WebUI advisor
  -> user decision
  -> Codex for planning/risk/approval briefs
  -> Aider for validated bounded patch edits
  -> local model serving through validated vLLM candidates where possible
  -> git diff and markdown handoff
```

`model-dispatch` remains the model-facing registry direction for clients, but
this strategy does not change it. vLLM validation should happen as a serving
candidate underneath or beside existing local endpoints before any client
migration is proposed.

## AMD vLLM Role

AMD is the preferred validation host for local coding-model serving because it
has the stronger discrete GPU capacity for coder workloads.

AMD vLLM validation should answer:

- Whether the target coding model serves reliably through an OpenAI-compatible
  API.
- Whether non-thinking Qwen output is stable enough for Aider patch workflows.
- Whether response shape, streaming behavior, stop handling, and long-context
  behavior satisfy Aider and manual coding clients.
- Whether AMD can remain a mode-switched compute worker without adding hidden
  schedulers or autonomous service switching.

AMD vLLM validation must not be folded into this docs slice. It requires a
future explicit slice with commands, rollback, and operator approval before any
live service change.

## Strix vLLM Role

Strix is the canonical source/development/code-graph host and a reasoning
testbed. Its vLLM role is to test reasoning and review models close to source
repos without turning Strix into an autonomous mutator.

Strix vLLM validation should answer:

- Whether reasoning/review models can serve reliably for architecture review
  and long planning prompts.
- Whether reasoning-parser mode improves complex review quality enough to
  justify separate configuration.
- Whether Strix can host validation without moving canonical repo mutation into
  model-serving or Hermes workflows.

Strix vLLM should remain validation-first. Live client routing changes need a
separate approval brief.

## Aider Compatibility Path

Aider is not rejected as a workflow role, but compatibility is unresolved.

Validation path:

1. Preserve the prior Aider failure history and compatibility inspection docs.
2. Validate response shape from the candidate serving layer without running
   Aider.
3. Prefer local vLLM-backed OpenAI-compatible endpoints for the next Aider
   compatibility target.
4. Test a Qwen non-thinking mode first for bounded patch output.
5. Only after response shape is validated, run a separate explicit Aider trial
   against one file in one repo with one reviewable diff.
6. Keep verified OpenRouter-free models as a manual fallback test option, not a
   paid or automatic route.

Aider must not plan, deploy, restart services, change secrets, edit multiple
repos, mutate live infrastructure, or make approval decisions.

## Qwen Thinking-Off Vs Reasoning-Parser Decision Tree

Use Qwen thinking-off or non-thinking mode as the baseline when the task is:

- A bounded patch.
- One repo and one planned edit.
- Expected to produce direct code or markdown changes.
- Intended for Aider.
- Easy to validate with normal diff and tests.

Use reasoning-parser mode separately when the task is:

- Architecture review.
- Complex failure analysis.
- Migration planning.
- Multi-step risk analysis.
- Approval-brief preparation.
- A read-only review where chain-of-thought-like internal reasoning artifacts
  must not leak into patch output.

Do not mix these modes in one Aider patch trial. If reasoning-parser mode is
useful, validate it as a review/planning model first, then decide whether any
coding client should ever use it.

## Hermes Observer/Reviewer Role

Hermes may:

- Observe project state.
- Summarize diffs, status files, and review notes.
- Propose skills or checklists.
- Suggest review questions.
- Flag scope drift or missing handoff details.

Hermes must not:

- Edit canonical repositories.
- Install live skills.
- Restart or reload services.
- Change model routing.
- Mutate `/srv/model-dispatch`, `/srv/projects/model-dispatch`, or
  `/srv/projects/hermes-homelab-runtime` as part of this strategy.
- Become an approval daemon.
- Supervise failures autonomously.
- Run hidden background jobs.

Hermes outputs should be proposals for the user or Codex/Aider to review, not
direct mutations.

## Explicit Non-Goals

- No Aider execution in this slice.
- No vLLM execution in this slice.
- No service restart or deployment.
- No `sudo`, Docker, or systemd commands.
- No OpenCode migration.
- No Open WebUI, Continue.dev, LiteLLM, dashboard, monitoring, or observability
  configuration changes.
- No edits to `/srv/model-dispatch`.
- No edits to `/srv/projects/model-dispatch`.
- No edits to `/srv/projects/hermes-homelab-runtime`.
- No paid-provider automation.
- No Codex, Aider, Hermes, or OpenCode wrappers.
- No hidden background jobs, watchers, daemons, or autonomous approval
  behavior.
- No commit.

## Validation Order

1. Finish this documentation consolidation and review the diff.
2. Preserve the Aider compatibility read-only inspection as prior context.
3. Plan a vLLM validation slice for AMD coding-model serving.
4. Validate OpenAI-compatible response shape from the AMD vLLM candidate.
5. Test Qwen thinking-off/non-thinking mode for direct patch-style output.
6. Plan a separate Aider compatibility trial against one file and one repo.
7. Plan a Strix vLLM validation slice for reasoning/review models.
8. Test reasoning-parser mode for complex review and architecture prompts.
9. Keep Hermes limited to observation and review proposals throughout.

## Rollback And Stop Conditions

Stop and write an approval brief before continuing if any proposed next step
would:

- Change host roles.
- Change model routing.
- Expose paid model access.
- Add automation, watchers, daemons, wrappers, or approval behavior.
- Change persistent state locations.
- Change security posture.
- Restart services or alter live service config.
- Edit canonical repositories through Hermes.
- Require modifying `/srv/model-dispatch`, `/srv/projects/model-dispatch`, or
  `/srv/projects/hermes-homelab-runtime`.

Rollback for this slice is a normal git diff rejection. Since this slice is
docs-only and makes no live changes, no service rollback is required.
