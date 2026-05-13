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

