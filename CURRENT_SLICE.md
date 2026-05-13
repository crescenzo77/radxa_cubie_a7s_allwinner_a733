# Current Slice

## Slice 20: Document OpenCode MCP adapter template and Codex rollback

Create documentation-only MCP adapter material for CodeGraphContext so the OpenCode transition path is real without changing live OpenCode configuration.

## Purpose

Codex has already been manually validated with CodeGraphContext on Strix and AMD. OpenCode remains the intended OSS/local steady-state coding client, but its MCP adapter has not been connected or validated yet.

This slice prepares the OpenCode side carefully by documenting:

- the intended OpenCode MCP adapter shape
- what must be verified before enabling it
- safety rules for CodeGraphContext MCP tools
- a Codex MCP disable/rollback procedure

## Scope

Documentation-only changes:

- create `inventory/mcp/opencode-codegraphcontext-template.md`
- create `inventory/mcp/codex-codegraphcontext-rollback.md`
- update `inventory/mcp/codegraphcontext.md` with links/status notes if appropriate

## Constraints

- Do not change live OpenCode config.
- Do not change live Codex config.
- Do not run `codegraphcontext mcp setup`.
- Do not install MCP tooling on Cubies.
- Do not grant persistent MCP tool permissions.
- Do not enable mutation-capable tools by default.
- Do not commit until the diff is reviewed.

## Acceptance Criteria

- OpenCode MCP adapter path is documented as template-only.
- The template clearly says it is not yet live.
- The template preserves canonical-host execution.
- Codex rollback/disable procedure is documented.
- The diff is reviewed before commit.
