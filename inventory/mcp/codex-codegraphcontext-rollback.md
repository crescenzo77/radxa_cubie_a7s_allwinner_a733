# Codex CodeGraphContext MCP Disable and Rollback

## Status

Documented rollback procedure.

Codex has been manually connected to CodeGraphContext on Strix and AMD for validation. Codex remains a manual setup/evaluation tool, not homelab infrastructure.

## Purpose

Provide a safe disable path if CodeGraphContext MCP causes instability, unwanted prompts, tool-surface confusion, or accidental mutation risk in Codex.

## Current Codex adapter block

Known manual block in `~/.codex/config.toml`:

    [mcp_servers.codegraphcontext]
    command = "/srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext"
    args = ["mcp", "start"]
    enabled = true
    startup_timeout_sec = 20
    tool_timeout_sec = 120

## Disable without deleting

Preferred first rollback is to disable the adapter without removing the block.

Edit:

    nano ~/.codex/config.toml

Change:

    enabled = true

to:

    enabled = false

Then restart Codex from the project directory.

Validate inside Codex:

    /mcp

Expected result:

- `codegraphcontext` should be absent or disabled.
- No CodeGraphContext tools should be available.

## Full removal

If disabling is not enough, remove the entire block:

    [mcp_servers.codegraphcontext]
    command = "/srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext"
    args = ["mcp", "start"]
    enabled = true
    startup_timeout_sec = 20
    tool_timeout_sec = 120

Then restart Codex.

## Repo safety validation after rollback

From the project working tree:

    git status --short

Expected result:

    no output

If output appears, inspect before doing anything else:

    git diff --stat
    git diff

## When to disable

Disable the Codex CodeGraphContext adapter if any of these happen:

- Codex repeatedly asks for broad MCP permissions.
- Codex attempts to use mutation-capable MCP tools without explicit need.
- Codex confuses CodeGraphContext with another MCP surface.
- Codex modifies project files during a read-only validation prompt.
- The MCP server becomes noisy, unstable, or distracting.
- OpenCode validation becomes the active priority and Codex should be removed from the path.

## Policy reminder

Codex must not become homelab infrastructure.

Allowed:

- Manual setup validation.
- Documentation-only experiments.
- Read-only MCP tests.

Not allowed:

- Codex API automation.
- Codex wrappers.
- Scheduled Codex tasks.
- Background Codex supervision.
- Codex-owned MCP architecture.
