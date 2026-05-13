# OpenCode CodeGraphContext MCP Adapter Template

## Status

Template-only. Not live.

This file documents the intended OpenCode MCP adapter direction for CodeGraphContext. It must not be treated as an enabled configuration until OpenCode MCP schema and behavior are verified on the target host.

## Purpose

Make the OpenCode transition path real without changing the live OpenCode configuration.

CodeGraphContext has already been installed and indexed on canonical project hosts. Codex has been manually connected and validated. OpenCode still needs a careful manual adapter validation path because OpenCode is the intended OSS/local coding client.

## Policy

- Run CodeGraphContext on the canonical active project host.
- Do not run MCP servers on Cubies.
- Do not use `codegraphcontext mcp setup`.
- Do not let Codex-specific config define the architecture.
- Do not grant persistent approval to mutation-capable tools.
- Do not allow MCP tooling to mutate core control files without explicit user review.

Core control files:

    AGENTS.md
    CURRENT_SLICE.md
    DECISIONS.md
    AGENT_STATUS.md

## Known CodeGraphContext command

Current validated command path on Strix and AMD:

    /srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext

Current validated MCP start args:

    mcp start

Equivalent command:

    /srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext mcp start

## Candidate OpenCode adapter shape

This is a documentation template, not a live config.

Before using this, verify the current OpenCode MCP schema with the installed OpenCode version. Current OpenCode documentation shows local MCP `command` as an array and supports `enabled: false` for temporary disablement.

    {
      "$schema": "https://opencode.ai/config.json",
      "mcp": {
        "codegraphcontext": {
          "type": "local",
          "command": [
            "/srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext",
            "mcp",
            "start"
          ],
          "enabled": false,
          "timeout": 20000
        }
      },
      "permission": {
        "codegraphcontext_*": "ask"
      }
    }

If OpenCode expects a different MCP schema, adapt this template rather than forcing this shape.

## Validation procedure before enabling

Run from the canonical project host and project working tree.

For homelab on Strix:

    cd /srv/projects/homelab
    git status --short
    /srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext list

For LoRA journal on AMD:

    cd /home/enzo/crucial/lora-corpus-pipeline-journal
    git status --short
    /srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext list

Then inspect OpenCode's current config and help output without changing anything:

    opencode --help
    find "$HOME" -maxdepth 4 \
      \( -path "$HOME/.config/opencode/*" -o -path "$HOME/.opencode/*" \) \
      -type f \
      -print

Do not edit live OpenCode config until the exact MCP schema is confirmed. Keep the template disabled first, and require approval for CodeGraphContext tools with the `codegraphcontext_*` permission guard.

## First OpenCode MCP validation prompt

Use only after the adapter is enabled manually and intentionally.

    Use the codegraphcontext MCP server only for read-only inspection. Do not use any other MCP server. Do not edit files. In this repo, list the indexed repository, summarize repository stats, and stop. Do not modify anything.

After exiting OpenCode:

    git status --short

Expected result:

    no output

## Read-only tools allowed for first validation

Allow only for the current session:

    get_repository_stats
    list_indexed_repositories
    find_code
    find_most_complex_functions
    find_dead_code

## Tools not approved for persistent allow

Do not grant persistent approval to:

    add_code_to_graph
    add_package_to_graph
    delete_repository
    watch_directory
    unwatch_directory
    switch_context
    execute_cypher_query

These may mutate graph state, repository tracking state, or execute broad graph queries. They require explicit case-by-case review.

## Definition of done for future live validation

OpenCode MCP validation is complete only when:

- OpenCode starts with the adapter on the canonical host.
- OpenCode sees the CodeGraphContext MCP server.
- Read-only tools work.
- The repo remains clean after the session.
- The result is documented in `inventory/mcp/codegraphcontext.md`.
- No live config is changed outside the intended host.
- No Cubie receives MCP tooling.
