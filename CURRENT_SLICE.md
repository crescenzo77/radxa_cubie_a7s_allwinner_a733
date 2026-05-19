# Current Slice

## Active: Aider compatibility planning

## Goal

Plan how to diagnose why Aider gets empty responses from local
`model-dispatch` aliases without running more Aider trials in this slice.

Known facts:

- Aider is installed at version `0.86.2`.
- Aider can start from `/srv/projects/homelab`.
- Aider can be constrained to one file.
- Aider asked to add extra files and the user rejected or skipped them.
- Aider trials with local `model-dispatch` aliases failed with empty responses:
  - `openai/coding`
  - `openai/local/amd-coder`
- The AMD containers were healthy:
  - `qwen3-coder-30b`
  - `gemma4-7900xt`
- Non-Codex agentic work must use either a local LLM or a verified free
  OpenRouter model from the allowlist.
- Paid frontier models must not be recommended for Aider, OpenCode, Cline, or
  other non-Codex agents.

## Files Expected to Change

- `inventory/aider-compatibility-plan.md`
- `CURRENT_SLICE.md`
- `AGENT_STATUS.md`
- `PROJECT_PLAN.md`

## Acceptance Criteria

- `CURRENT_SLICE.md` identifies the active slice as
  `Aider compatibility planning`.
- `inventory/aider-compatibility-plan.md` exists.
- The plan covers:
  - observed failures
  - hypotheses
  - what to inspect first
  - local `model-dispatch` compatibility checks
  - direct AMD endpoint compatibility checks
  - verified OpenRouter-free fallback test option
  - what not to do
  - validation commands for a later slice
- The plan includes these likely hypotheses:
  - Aider expects a response format or behavior not satisfied by
    `model-dispatch` or local llama.cpp response.
  - `model-dispatch` alias works for normal chat completion but may not satisfy
    Aider's edit format expectations.
  - Generic route aliases may be less compatible than direct explicit model
    IDs.
  - Aider may need model metadata, edit format override, or provider
    configuration.
- The plan does not recommend paid frontier models for Aider, OpenCode, Cline,
  or other non-Codex agents.
- Prior Aider and OpenCode history remains preserved.
- No `/srv/model-dispatch` files are touched.
- No `/srv/projects/model-dispatch` files are touched.
- No services are restarted.
- No Open WebUI config is changed.
- No OpenCode config is changed.
- No Continue.dev config is changed.
- No dashboard, monitoring, or observability deployment is started.
- Aider is not run.
- No new Aider trials are run.
- `model-dispatch` is not edited.
- `/srv/model-dispatch` is not touched.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

## Scope Expansion Risks

- Running Aider would turn this planning slice into a tool trial.
- Editing live `/srv/model-dispatch`, `/srv/projects/model-dispatch`, or
  restarting services would violate this docs-only slice.
- Changing OpenCode, Continue.dev, Open WebUI, LiteLLM, dashboard, monitoring,
  or observability configuration would broaden the slice.
- Replacing the historical decision record instead of adding the compatibility
  plan would lose useful audit history.
- Recommending paid frontier models for non-Codex agents would violate the
  current model-use constraint.
- Adding wrappers, background jobs, automation, paid fallback, or hidden
  supervision would violate the standing constraints.

## Prior Slice History

### Previous Active Slice: Aider workflow integration

Purpose:

Adapt the homelab workflow docs to reflect the corrected agent strategy:
Codex remains primary for planning, sequencing, and risky live-service work;
Claude Code remains a strong frontier-code alternative; Aider is added as the
preferred bounded patch assistant for small repo edits; OpenCode is demoted to a
later local-agent experiment; Continue.dev remains editor assist; and Cline
remains sandbox-only.

Definition of done from that slice:

- `WORKFLOW.md` includes an `Agent Division of Labor` section covering:
  - Codex for planning, migration choreography, and risky live-service steps.
  - Claude Code as a strong frontier-code alternative and second opinion.
  - Aider as the preferred bounded repo patch assistant.
  - OpenCode as a later local-agent experiment, not the default.
  - Continue.dev as editor assist and review.
  - Cline as sandbox-only.
- `WORKFLOW.md` includes an `Aider Use Rule` section.
- The Aider rule says Aider is used only after a slice is planned.
- The Aider rule limits Aider to one repo, one bounded edit, and one
  reviewable diff.
- The Aider rule forbids Aider for live deployment, service restarts,
  Docker/systemd, secrets, multi-host changes, and broad architecture
  decisions.
- The Aider rule requires validation before commit.
- `docs/aider-workflow.md` exists and covers purpose, when to use Aider, when
  not to use Aider, standard workflow, validation checklist, and commit
  guidance.
- The broader workflow docs no longer present OpenCode as the assumed next
  primary agent.
- Prior Aider/OpenCode history remains preserved in history sections and
  decision logs.
- No `/srv/model-dispatch` files were touched.
- No `/srv/projects/model-dispatch` files were touched.
- No services were restarted.
- No Open WebUI, OpenCode, Continue.dev, dashboard, monitoring, or
  observability configuration was changed.
- No commit was made.

### Previous Active State: next-slice choice pending

Purpose:

Choose the next bounded slice after completing the additive
`model-dispatch` alias deployment.

The additive aliases were already deployed live. This state was selection only:
do not edit live `/srv/model-dispatch`, restart services, edit the
`model-dispatch` source repo, or change Open WebUI, OpenCode, Continue.dev,
dashboard, monitoring, or observability configuration.

Next slice options listed at that time:

- OpenCode through `model-dispatch`.
- Continue.dev through `model-dispatch`.
- Observe current deployment.


### Completed Slice: additive model-dispatch alias deployment

Purpose:

Deploy additive `model-dispatch` aliases live after the deployment plan and
approval checkpoint.

Completed facts:

- Homelab latest commit before this status update:
  `5ce3374 document additive alias deployment checkpoint`.
- Additive aliases were deployed live.
- Deployment record exists:
  `inventory/model-dispatch-additive-alias-deployment-approval-brief-2026-05-18.md`.
- Backup path:
  `/srv/model-dispatch/backups/20260518-093534`.
- No Open WebUI config change.
- No OpenCode config change.
- No Continue.dev config change.
- No dashboard, monitoring, or observability deployment.

Validation completed:

- `/health` returned OK.
- `/v1/models` listed:
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
- `advisor` worked through `/v1/chat/completions`.
- `local/amd-coder` worked through `/v1/chat/completions`.

Definition of done from that slice:

- Additive aliases were deployed live.
- Existing client configuration was left unchanged.
- Backup path was recorded as
  `/srv/model-dispatch/backups/20260518-093534`.
- Validation confirmed health, model listing, and chat completions for
  `advisor` and `local/amd-coder`.
- No Open WebUI, OpenCode, Continue.dev, dashboard, monitoring, or
  observability configuration was changed.

### Previous Active Slice: additive model-dispatch alias deployment planning

Purpose:

Plan an additive `model-dispatch` alias deployment from the reviewed source
repo without changing live routing yet.

This slice was planning only. It did not edit live `/srv/model-dispatch`,
restart services, deploy aliases, or change Open WebUI, OpenCode, or
Continue.dev configuration.

Definition of done from that slice:

- `CURRENT_SLICE.md` identifies the active slice as
  `additive model-dispatch alias deployment planning`.
- `inventory/model-dispatch-additive-alias-deployment-plan.md` exists and
  covers the required deployment planning sections.
- The first alias deployment is planned as additive only.
- Existing IDs remain available.
- Open WebUI display names are descriptive enough to infer model family,
  parameter size, quantization, context window, and host or role where known.
- Exact future `config.json` model and route additions are documented.
- Files eligible for deployment are documented.
- The backup path is documented as
  `/srv/model-dispatch/backups/<timestamp>/`.
- Validation commands and rollback steps are documented as future
  operator-approved commands, not run in this slice.
- OpenCode direct AMD routing remains unchanged.
- Continue.dev's current documented route remains unchanged.
- Open WebUI live config remains unchanged.
- `/srv/model-dispatch` is not edited.
- `/srv/projects/model-dispatch` may be inspected only; it is not edited.
- No services are restarted.
- No Docker, systemd, sudo, deployment, or live endpoint-changing command is
  run.
- No dashboards, monitoring, or observability are deployed.
- No commit is made.
- `AGENT_STATUS.md` is updated with the handoff.
- The requested checks are run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

### Previous Active Slice: model-dispatch alias registry cleanup planning

Purpose:

Plan and document stable `model-dispatch` model aliases before changing
OpenCode or Continue.dev.

This slice was planning only. No live routing behavior changed in that slice.

Definition of done from that slice:

- `CURRENT_SLICE.md` identified the active slice as
  `model-dispatch alias registry cleanup planning`.
- `inventory/model-dispatch-alias-registry-plan.md` existed and covered the
  required alias planning sections.
- The plan preserved current behavior and explicitly said no live
  `model-dispatch` config changes happened in that slice.
- OpenCode direct AMD routing remained unchanged.
- Continue.dev's current documented route remained unchanged.
- `/srv/model-dispatch` was not edited.
- No services were restarted.
- No dashboards, monitoring, or observability were deployed.
- `AGENT_STATUS.md` was updated with the handoff.
- Requested checks were run:
  - `git diff --check`
  - `git diff --stat`
  - `git status --short`

### Previous Active Slice: model-dispatch deployment planning only

Purpose:

Write the deployment, rollback, and validation plan for eventually deploying
the Strix `model-dispatch` source repo to the live ThinkCentre
`/srv/model-dispatch` service path.

This slice was planning only. No deployment happened in that slice.

Definition of done from that slice:

- `CURRENT_SLICE.md` identified the active slice as
  `model-dispatch deployment planning only`.
- `inventory/model-dispatch-deployment-plan-2026-05-17.md` covered the
  required deployment, rollback, validation, and approval plan.
- The deployment plan explicitly said:
  - no deployment happens in this slice
  - live `/srv/model-dispatch` remains untouched
  - `model-dispatch.service` remains untouched
  - dashboards, monitoring, and observability remain deferred
- `AGENT_STATUS.md` described what changed, what did not change, checks run,
  risks, and next recommended action.
- No live services, configs, OpenCode settings, Open WebUI settings, LiteLLM
  settings, MCP settings, Docker state, systemd state, reverse proxy settings,
  dashboard, monitoring, observability, source mirror, live runtime files,
  `tools/` files, or commits were changed.

## Trial Slice: Aider bounded patch test

Purpose:
Test Aider on one harmless docs-only edit.

Scope:
- Edit only `docs/aider-workflow.md`.
- Add a short "Trial rule" note.
- Do not edit live services.
- Do not edit `/srv/model-dispatch`.
- Do not install tools.
- Do not change OpenCode, Continue.dev, Open WebUI, LiteLLM, Docker, systemd, dashboards, monitoring, or observability.
- Do not commit from Aider.

Validation:
- `git diff --check`
- `git diff --stat`
- `git status --short`
