# Current Slice

## Paused: MCP validation complete, no active implementation slice

## Current State

The recent MCP validation work is complete and documented.

Completed:

- CodeGraphContext installed and validated on Strix and AMD.
- Codex MCP adapter manually validated on Strix and AMD.
- OpenCode MCP schema validated on AMD.
- OpenCode disabled candidate config validated.
- OpenCode isolated enabled config validated.
- OpenCode isolated read-only session validated.
- Live OpenCode MCP enablement deferred by decision.
- Live OpenCode config remains unchanged.
- CodeGraphContext remains documented optional tooling.

Cubie camera-node setup is also documented but not active:

- `cubie-camera-node` source repo exists on Strix.
- ThinkCentre mirror exists and tracks `main`.
- Hardware readiness checklist exists.
- No Cubie runtime state has been changed.

## Active Posture

No active implementation slice.

Do not proceed into Wyze/Cubie camera work until explicitly selected.

## Recommended Next Choices

1. Stop here and treat MCP setup as complete.
2. Enable CodeGraphContext live in OpenCode only if there is a concrete need.
3. Test CodeGraphContext on a source-code-heavy repo before enabling it live.
4. Resume Cubie/Wyze hardware readiness later.

## Constraints

- Do not change live OpenCode config unless explicitly requested.
- Do not install MCP tooling on Cubies.
- Do not deploy camera services.
- Do not use ThinkCentre for camera processing.
- Keep Codex manual-only and out of infrastructure.

## 2026-05-13 — Force non-streaming upstream calls in model-dispatch

Decision:
`model-dispatch` now forces `stream: false` when forwarding chat completion requests to local and OpenRouter-free upstreams.

Rationale:
Open WebUI sends streaming chat requests. The local OpenAI-compatible backends return `text/event-stream` chunks for streaming responses. `model-dispatch` is not a streaming proxy and expects one JSON response object, so it failed with `no capable model available` after trying to parse SSE output as JSON.

Consequence:
Open WebUI can continue using streaming behavior at its own API boundary, while `model-dispatch` normalizes upstream calls to non-streaming JSON. Local model routing through `auto-local` is working again.

## 2026-05-13 — Open WebUI web search validated

Current state:
Open WebUI web search is validated for `auto-local` and `openrouter-free/openrouter/auto-free-router` using SearXNG JSON snippet retrieval with `BYPASS_WEB_SEARCH_WEB_LOADER=true` and the task model pinned to `amd-coder-qwen3-coder-30b-32k`.
