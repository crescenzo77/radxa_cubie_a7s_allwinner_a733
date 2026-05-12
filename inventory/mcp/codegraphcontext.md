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
