# Codex Aider vLLM Architecture Plan

## Current Operating Decision

The homelab development architecture is recentered around manual, reviewable
agent use:

- Codex remains the high-trust manual planner, sequencer, approval-brief
  author, reviewer, and risky live-service agent.
- Aider becomes the small bounded patch tool only after local or verified-free
  model compatibility is proven.
- vLLM is the preferred model-serving direction to evaluate for coding and
  reasoning models on AMD and Strix.
- `model-dispatch` remains the policy and routing layer and should not be
  replaced casually.
- Hermes observes, reviews, records, and uses approved skills for preservation
  checks, but does not become the coding agent or an autonomous mutator.

OpenCode should no longer be treated as the primary coder path.

## Why OpenCode Is No Longer Primary

OpenCode fit an earlier routing direction, but the operating workflow has
shifted toward tools matched to task shape rather than tools matched to an
endpoint topology.

OpenCode remains useful as a later local-agent experiment, but it is not the
default path because:

- Codex has proven better suited for planning, sequencing, approval briefs,
  risky live-service reasoning, and docs-only architecture work.
- Aider better matches the desired small-patch workflow if compatibility can be
  solved.
- The current blocker is not lack of an agent slot; it is proving a clean local
  model-serving and response-format path for bounded patch work.
- Making OpenCode primary would over-weight the previous model-dispatch routing
  strategy instead of the current safety and workflow requirements.

Prior OpenCode and Aider history remains preserved as context. This plan does
not delete or rewrite that history.

## Codex Role

Codex is the primary manual agent for:

- Planning and sequencing.
- Risk assessment.
- Approval briefs.
- Documentation slices.
- Reviewing proposed changes.
- Drafting safe command blocks for live-service work.
- Handling tasks that could affect host roles, routing, billing exposure,
  persistent state, security posture, Docker, systemd, or deployment behavior.

Codex must remain manually invoked. It must not become a daemon, watcher,
approval system, background job, or infrastructure component.

## Aider Role

Aider is the preferred bounded patch assistant only after compatibility is
proven.

Aider is intended for:

- One repository.
- One already-planned edit.
- One reviewable diff.
- Local LLMs or verified OpenRouter-free models only.
- Changes that can be validated with normal git review and slice-specific
  checks.

Aider is not a planner, deployment tool, architecture decision-maker, service
operator, or approval agent. Do not recommend paid frontier models for Aider.

## vLLM Role On AMD

AMD is the preferred first host to evaluate vLLM for Aider-compatible local
coding-model serving.

AMD vLLM readiness should be inspected before anything is run:

- GPU/driver/runtime prerequisites.
- Available model storage and candidate model paths.
- Existing endpoint ports and conflicts.
- Whether Qwen coding models can be served with clean OpenAI-compatible
  responses.
- Whether thinking-off or non-thinking mode can produce clean patch-oriented
  output.

AMD vLLM evaluation must happen in a later explicit slice. This plan does not
run vLLM, start services, use Docker, use systemd, or change live routing.

## vLLM Role On Strix

Strix is the canonical source/development/code-graph host and a reasoning
testbed. Its vLLM role should focus on reasoning and review models near source
repos without giving model-serving any mutation authority.

Strix vLLM readiness should be inspected for:

- Hardware/runtime suitability.
- Candidate reasoning and review models.
- Long-context behavior.
- Qwen reasoning-parser or thinking-on behavior for review and architecture
  prompts.
- Separation between model-serving, repo mutation, and Hermes observation.

Strix vLLM evaluation also needs a later explicit slice and operator approval
before any live service or routing change.

## model-dispatch Role

`model-dispatch` remains the policy and routing layer.

Its role is to provide stable model-facing aliases and route policy for clients
after lower-level endpoints are proven. vLLM should be evaluated as a serving
layer underneath or beside current local endpoints first. `model-dispatch`
should not be replaced casually, edited during this slice, or given a new Aider
alias before Aider/vLLM compatibility is proven.

The correct order is:

1. Prove the vLLM endpoint directly.
2. Prove Aider can use the vLLM endpoint safely.
3. Add a dedicated `model-dispatch` alias only after compatibility is proven.

## Hermes Role

Hermes is an observer, reviewer, recorder, and approved-skill-assisted
preservation layer.

Hermes may:

- Observe project state.
- Summarize diffs and status files.
- Review handoffs.
- Record preservation findings.
- Use approved skills for read-only preservation checks.
- Flag scope drift or missing status information.

Hermes must not:

- Become the primary coding agent.
- Edit canonical repositories.
- Mutate live services.
- Install live skills in this slice.
- Restart services.
- Change routing.
- Supervise failures autonomously.
- Run hidden background jobs.
- Become an approval daemon.

The completed Hermes skill installation slice in `hermes-homelab-runtime`
remains separate. Return to Hermes after this architecture direction is
documented.

## Qwen Thinking-On Vs Thinking-Off

Treat Qwen modes as separate validation paths.

Thinking-off or non-thinking mode is the baseline for Aider patch work because
Aider needs clean, direct patch output with minimal reasoning noise.

Thinking-on or reasoning-parser mode may help hard reasoning, architecture
review, and failure analysis, but it can create output noise that is risky for
patch generation. Validate it separately for read-only review and planning
before considering it for any coding workflow.

Do not mix thinking-on and thinking-off in the same Aider compatibility trial.

## Aider Compatibility Test Approach

Aider compatibility should be tested in increasing order of risk:

1. Preserve the existing failure record: Aider returned empty responses against
   local `model-dispatch` aliases.
2. Preserve the manual curl finding: `model-dispatch` and direct AMD endpoints
   returned valid non-empty OpenAI-compatible responses.
3. Treat the likely issue as Aider configuration, edit format, model metadata,
   or reasoning-output handling until proven otherwise.
4. Inspect vLLM readiness on AMD and Strix without running vLLM.
5. In a later slice, start or target a vLLM endpoint only with explicit
   approval.
6. Test the vLLM endpoint with curl only before running Aider.
7. Test Aider against vLLM only with a harmless one-file docs edit.
8. Review the diff and `AGENT_STATUS.md` before considering any broader Aider
   use.

Do not use paid models for Aider compatibility testing. Non-Codex agentic work
must use local LLMs or verified OpenRouter-free models from the allowlist.

## What Not To Change Yet

Do not change:

- Aider runtime behavior.
- vLLM runtime behavior.
- `model-dispatch`.
- `/srv/model-dispatch`.
- `/srv/projects/model-dispatch`.
- `/srv/projects/hermes-homelab-runtime`.
- Open WebUI.
- OpenCode.
- Continue.dev.
- LiteLLM.
- Dashboards, monitoring, or observability.
- Service units, containers, ports, reverse proxies, or live endpoint config.
- Host roles, persistent state locations, or security posture.

Do not run Aider, vLLM, `sudo`, Docker, systemd, service restarts, or commits in
this slice.

## Phased Path

### Phase 1: Document Architecture

Complete this docs-only plan and update the handoff. No runtime changes.

### Phase 2: Inspect AMD And Strix vLLM Readiness

Read-only inspection of prerequisites, candidate models, ports, existing
service posture, and risks. No vLLM run.

### Phase 3: Test vLLM Endpoint With curl Only

After explicit approval, validate a vLLM OpenAI-compatible endpoint using curl
only. Confirm non-empty responses, response shape, model IDs, stop handling,
streaming/non-streaming behavior, and Qwen thinking-off behavior.

### Phase 4: Test Aider Against vLLM

Run Aider only in a later explicit slice, against the validated vLLM endpoint,
with a harmless one-file docs edit and one reviewable diff.

### Phase 5: Add Dedicated model-dispatch Alias

Only after Aider/vLLM compatibility is proven, add a dedicated
`model-dispatch` alias for the validated Aider model path. Keep the alias
explicit and reversible.

### Phase 6: Return To Hermes Preservation

Return to Hermes and use the approved runtime preservation skill for a
read-only preservation check. Hermes remains reviewer/observer only.

## Next Recommended Slices

1. AMD and Strix vLLM readiness inspection.
2. AMD vLLM curl-only endpoint validation.
3. Strix vLLM curl-only reasoning/review validation.
4. Aider against vLLM harmless one-file docs edit.
5. Dedicated `model-dispatch` Aider alias planning.
6. Hermes read-only preservation check using the approved runtime preservation
   skill.
