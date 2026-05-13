# Current Slice

## Slice 21: Decide whether to enable CodeGraphContext MCP live in OpenCode

Decide whether the validated CodeGraphContext MCP adapter should be enabled in live OpenCode on AMD.

## Current State

Slice 20 completed the OpenCode MCP transition path without changing live OpenCode config.

Completed:

- OpenCode CodeGraphContext adapter template documented.
- Codex CodeGraphContext rollback procedure documented.
- OpenCode schema corrected to command-array format.
- AMD disabled candidate config created and validated.
- AMD isolated enabled config connected successfully.
- AMD isolated read-only OpenCode session succeeded.
- Live OpenCode config remained unchanged.
- Live enable and rollback procedure documented.
- ThinkCentre mirror received all documentation commits.

Latest relevant homelab commit:

- `b21bbf6 document opencode mcp live enable procedure`

## Decision To Make

Choose one:

1. Do not enable live MCP yet.
2. Enable CodeGraphContext MCP live on AMD only.
3. Test CodeGraphContext on a source-code-heavy repo before enabling live.
4. Leave CodeGraphContext as documented optional tooling and move to another roadmap item.

## Recommendation

Do not enable live MCP yet unless there is an immediate use case.

Reason:

- The validated repos are mostly Markdown/documentation.
- CodeGraphContext indexing reports 0 functions, 0 classes, and 0 modules for these repos.
- The isolated validation proved compatibility, but not enough practical value to justify adding a live MCP surface by default.
- Keeping it documented and ready preserves portability without adding daily tool noise.

## Scope For This Slice

Decision/documentation only unless explicitly redirected.

## Constraints

- Do not change live OpenCode config unless the user explicitly chooses option 2.
- Do not install MCP tooling on Cubies.
- Do not grant persistent approval to mutation-capable MCP tools.
- Do not make Codex part of infrastructure.
- Do not broaden into GitNexus evaluation unless explicitly selected.

## Acceptance Criteria

- The next action is chosen deliberately.
- If live enable is deferred, record that decision.
- If live enable is chosen, follow `inventory/mcp/opencode-codegraphcontext-live-enable.md`.
- Git diff is reviewed before commit.
