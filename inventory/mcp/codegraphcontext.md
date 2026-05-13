# CodeGraphContext Inventory

## Purpose

CodeGraphContext is the first evaluated local code graph / MCP candidate for the homelab.

## Policy

- Install only on canonical active project hosts.
- Do not install on Cubies.
- Do not run automatic MCP setup wizards against primary repos.
- Do not allow MCP tooling to mutate `AGENTS.md`, `CURRENT_SLICE.md`, `DECISIONS.md`, or `AGENT_STATUS.md`.
- Use manual Codex/OpenCode adapter config.

## Strix install

Install path:

- `/srv/mcp/servers/codegraphcontext-venv`

Validated behavior:

- Installed successfully in a Python virtual environment.
- Indexed `/srv/projects/homelab`.
- Listed `homelab` as an indexed project.
- Created `.cgcignore` in the repo root.
- `.cgcignore` was reviewed and committed.

## Current status

- CLI indexing works on Strix.
- Codex MCP adapter was manually connected and validated on Strix.
- OpenCode MCP adapter is not connected yet.
- AMD CLI indexing works for `lora-corpus-pipeline-journal`.
- AMD `.cgcignore` was reviewed and committed.
- Codex MCP adapter was manually connected and validated on AMD.

## OpenCode adapter template status

A documentation-only OpenCode adapter template now exists at:

    inventory/mcp/opencode-codegraphcontext-template.md

This does not enable CodeGraphContext in OpenCode. It records the intended manual adapter direction, safety rules, validation prompt, and first read-only tool allowlist.

OpenCode MCP remains not yet connected and not yet validated.

## Codex rollback status

A Codex disable and rollback note now exists at:

    inventory/mcp/codex-codegraphcontext-rollback.md

Codex remains manual-only and must not become homelab infrastructure.

## AMD OpenCode disabled-candidate validation

Validated on AMD with OpenCode `1.14.39`.

A disabled candidate config was created at:

    /home/enzo/.config/opencode/opencode.with-codegraphcontext-disabled.candidate.json

The candidate added:

- `mcp.codegraphcontext`
- `enabled: false`
- local command array:
  - `/srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext`
  - `mcp`
  - `start`
- `permission.codegraphcontext_* = ask`

Validation result:

- Candidate JSON was valid.
- Running OpenCode with an isolated temporary `XDG_CONFIG_HOME` recognized the MCP server as configured but disabled.
- Temporary output showed `codegraphcontext disabled`.
- Live OpenCode config remained unchanged.
- Live `opencode mcp list` still showed no MCP servers configured.

Conclusion:

The documented OpenCode MCP schema is accepted by OpenCode `1.14.39` when tested in an isolated temporary config. CodeGraphContext is still not enabled in live OpenCode.

## AMD OpenCode isolated-enabled validation

Validated on AMD with OpenCode `1.14.39`.

An isolated temporary config directory was created with `XDG_CONFIG_HOME` pointing to a copied candidate config. Only the temporary copy was changed from:

    enabled: false

to:

    enabled: true

Validation result:

- Temporary config JSON was valid.
- `XDG_CONFIG_HOME=<temp>` `opencode mcp list` showed `codegraphcontext connected`.
- The command path shown was:
  - `/srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext`
  - `mcp`
  - `start`
- Live OpenCode config remained unchanged.
- Live `opencode mcp list` still showed no MCP servers configured.

Conclusion:

OpenCode `1.14.39` can connect to CodeGraphContext through the documented local MCP schema. CodeGraphContext is still not enabled in live OpenCode.

