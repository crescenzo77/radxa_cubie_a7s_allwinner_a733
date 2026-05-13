# Decisions

## 2026-05-05 — Two-surface workflow

Decision:
Use a two-surface workflow: web UI advisor/planner plus self-hosted coding agent.

Rationale:
This reduces copy/paste and context-window bloat without building a fragile autonomous approval system.

Consequences:
- The user remains the final approver.
- `advisor-packet` is only a local context packet generator.
- Markdown files and Git are the durable project state.
- Codex may be used manually during setup, but must not become infrastructure.

## 2026-05-06 — Slice 5 evaluation

Decision:
Aider is the preferred first candidate for the steady-state coder evaluation.
OpenCode remains available as a fallback.
Aider is not the final default until this bounded edit test is reviewed and accepted.
Aider must use Homelab LiteLLM, not direct paid-provider APIs.
No automation, daemon, watcher, or background job should be created around Aider.

Rationale:
Aider was tested as a candidate for the steady-state coder in the two-surface workflow.
It meets the requirements for Git-centered, terminal-based, bounded editing.
It does not pollute system Python and works inside a Git repo.
It produces reviewable diffs and respects workflow constraints.

Consequences:
- Aider is being evaluated as the first preferred coding agent.
- OpenCode remains available as a fallback.
- No automation or background processes are created around Aider.
- The final default will be determined after reviewing this bounded edit test.

## 2026-05-06 — Aider eliminated from homelab workflow

Decision:
Aider will not be used in the homelab steady-state workflow.

Rationale:
Aider installed cleanly and reached Homelab LiteLLM, but it failed a simple bounded documentation task in an unacceptable way. It created bogus files using prompt text as filenames and emptied `AGENT_STATUS.md`, one of the repo's control files. The repo had to be manually recovered.

This failure happened on a simple task, so simpler scope is not a sufficient safety control.

Consequences:
- Aider is not the default coder.
- Aider is not a fallback coder for the homelab workflow.
- Do not build wrappers, scripts, automation, or process steps around Aider.
- OpenCode through LiteLLM becomes the next coder path to evaluate and recenter around.
- The two-surface workflow remains valid: web UI advisor, OpenCode coder, `advisor-packet`, markdown state files, and Git review.

## 2026-05-06 — Transition away from LiteLLM active routing

Decision:
LiteLLM will be phased out of the active OpenCode and Open WebUI routing path.

Rationale:
The useful part of the current setup is the OpenRouter free-model discovery and free-only filtering, not LiteLLM itself. LiteLLM adds a large credential-bearing routing layer. The safer target is to preserve the free-model allowlist mechanism while generating OpenCode-safe provider config directly.

Target:
- OpenCode uses direct local-coder by default.
- OpenRouter is available only as a generated free-only manual fallback.
- Open WebUI moves back to direct local model endpoints.
- LiteLLM is kept temporarily for rollback, then removed from the active path after testing.

Consequences:
- Do not delete or stop LiteLLM yet.
- Do not remove OpenRouter fallback.
- Do not expose the broad OpenRouter paid catalog to OpenCode.
- Do not build a custom router or LiteLLM clone.
- Move free-model artifacts toward `/srv/openrouter-free/`.

## 2026-05-11 — Open WebUI model-dispatch compatibility layer

Decision:
Open WebUI uses `model-dispatch` on ThinkCentre as its active OpenAI-compatible model endpoint.

Live endpoint:

- `http://192.168.50.225:4010/v1`
- Service: `model-dispatch.service`
- Path: `/srv/model-dispatch`
- Host: `thinkcentre`

Rationale:
Open WebUI needs a stable OpenAI-compatible `/v1/models` and `/v1/chat/completions` surface that can present local-first routes, explicit local models, and verified OpenRouter-free choices without exposing the broad paid OpenRouter catalog or keeping LiteLLM in the active path.

Consequences:
- Open WebUI no longer actively routes through LiteLLM.
- LiteLLM remains rollback/history unless explicitly reactivated.
- The dispatcher exposes local auto routes: `auto-local`, `auto-coding-local`, `auto-reasoning-local`, and `auto-small-local`.
- The dispatcher exposes explicit local models for Strix reasoning, Strix coder, AMD coder, and AMD Gemma backup.
- The dispatcher exposes `openrouter-free/openrouter/auto-free-router` before specific verified free models.
- OpenRouter remains free-only, explicit/manual, and fail-closed.
- OpenCode remains direct-local on AMD and keeps its generated OpenRouter-free provider behavior separate from Open WebUI.
- Follow-up decisions remain: token-estimation improvements, LiteLLM rollback retention, whether `model-dispatch` should get its own repo, and the future Continue.dev path.

## 2026-05-12 — Defer live OpenCode CodeGraphContext MCP enablement

Decision:
Do not enable CodeGraphContext MCP in live OpenCode yet. Keep it documented as optional validated tooling.

Rationale:
OpenCode MCP compatibility has been validated through disabled-candidate, isolated-enabled, and isolated read-only sessions on AMD. However, the currently validated repos are mostly Markdown/documentation, and CodeGraphContext reports 0 functions, 0 classes, and 0 modules for them. Enabling the MCP server live would add daily tool-surface noise without a strong immediate benefit.

Consequences:
- Live OpenCode config remains unchanged.
- CodeGraphContext remains available through the documented candidate and live-enable procedure.
- Future live enablement should happen only when there is a source-code-heavy repo or a concrete workflow need.
- GitNexus remains eval-only.
- No MCP tooling is installed on Cubies.

## 2026-05-13 — CodeGraphContext write use requires sandboxing

Decision:
CodeGraphContext may evolve beyond read-only use, but write-capable use must happen only inside a disposable sandbox. CodeGraphContext may read from approved canonical project repositories, but it must not write directly to canonical working trees by default.

Valid sandboxes include Git worktrees, temporary branch checkouts, dedicated patch-proposal directories, or `/tmp` patch artifacts. Changes created in a sandbox must be promoted only through reviewed diffs, patches, manual copy, or branch review.

Rationale:
CodeGraphContext can be useful for code understanding and may become useful for patch proposal workflows, but canonical project repositories are the source of truth. Direct mutation of primary working trees by an MCP tool would blur review boundaries and could accidentally alter operational source repos, project journal repos, documentation/control repos, or future project repos.

Consequences:
- Approved canonical repositories may be indexed or read as CodeGraphContext input.
- Canonical working trees remain read-only inputs by default.
- No persistent broad mutation approval is allowed.
- No automatic MCP setup wizard may be run against primary repositories.
- The policy is path-agnostic and applies to operational source repos, project journal repos, documentation/control repos, and future project repos.
- Large videos, extracted frames, datasets, generated evidence, model outputs, and bulky review artifacts should not be duplicated into sandboxes or tracked by Git unless explicitly intended.

## 2026-05-12 — Initialize Cubie camera-node source repository

Decision:
Create the canonical `cubie-camera-node` source repository on Strix and push the initial skeleton to the ThinkCentre bare mirror.

Rationale:
Cubies should remain runtime-only appliance nodes. Source development belongs on Strix, with ThinkCentre storing the bare mirror.

Consequences:
- Canonical source repo exists at `strix:/srv/projects/cubie-camera-node`.
- ThinkCentre mirror exists at `/srv/git/cubie-camera-node.git`.
- Mirror default branch is `main`.
- Initial skeleton commit is `8fcd154 initialize cubie camera node skeleton`.
- No Cubie runtime state was changed.

## 2026-05-12 — Add Cubie camera hardware readiness checklist

Decision:
Add a hardware-first readiness checklist to the `cubie-camera-node` repository before any software deployment.

Rationale:
The cameras are old and the Cubies use microSD-backed Debian installs. Hardware, power, network, storage, and camera stream basics should be verified before building or deploying runtime services.

Consequences:
- Checklist exists at `cubie-camera-node:docs/hardware-readiness-checklist.md`.
- Cubie repo commit is `3449eba add hardware readiness checklist`.
- No Cubie runtime state was changed.
- Software deployment remains blocked until hardware readiness is reviewed.

## 2026-05-13 — Force non-streaming upstream calls in model-dispatch

Decision:
`model-dispatch` now forces `stream: false` when forwarding chat completion requests to local and OpenRouter-free upstreams.

Rationale:
Open WebUI sends streaming chat requests. The local OpenAI-compatible backends return `text/event-stream` chunks for streaming responses. `model-dispatch` is not a streaming proxy and expects one JSON response object, so it failed with `no capable model available` after trying to parse SSE output as JSON.

Consequence:
Open WebUI can continue using streaming behavior at its own API boundary, while `model-dispatch` normalizes upstream calls to non-streaming JSON. Local model routing through `auto-local` is working again.

## 2026-05-13 — Use snippet-based SearXNG web search in Open WebUI

Decision:
Open WebUI web search should use SearXNG JSON results with snippet-based retrieval by keeping `BYPASS_WEB_SEARCH_WEB_LOADER=true`. The task model should be pinned to the explicit local AMD model `amd-coder-qwen3-coder-30b-32k`, not the `auto-local` route alias.

Rationale:
SearXNG JSON search worked from inside the Open WebUI container, and Open WebUI successfully generated web-search embeddings, stored snippet results in a `web-search-*` collection, and queried those results during chat. The fragile part was Open WebUI's downstream full-page fetch path, which repeatedly failed on page loads. Snippet-based retrieval avoids that loader path while preserving working web search for both local models and OpenRouter-free models.

Consequences:
- Web search works for `auto-local` and `openrouter-free/openrouter/auto-free-router`.
- Search/query preparation is handled locally by `amd-coder-qwen3-coder-30b-32k`.
- Full-page web loading remains deferred unless a later slice shows a concrete need for it.
