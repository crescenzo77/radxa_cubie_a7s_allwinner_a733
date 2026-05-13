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
