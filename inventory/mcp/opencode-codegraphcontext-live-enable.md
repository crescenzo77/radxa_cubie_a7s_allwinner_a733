# OpenCode CodeGraphContext Live Enable Procedure

## Status

Procedure only. Not yet executed.

## Purpose

Define the controlled process for enabling CodeGraphContext MCP in live OpenCode after isolated validation succeeded.

## Current validation state

Validated on AMD:

- OpenCode accepted the local MCP schema.
- Disabled candidate config was recognized as disabled.
- Isolated enabled config connected to CodeGraphContext.
- Isolated read-only session succeeded.
- Live OpenCode config remained unchanged.
- LoRA journal repo stayed clean after validation.

## Live enable policy

Do not enable CodeGraphContext live unless all of these are true:

- The target host is the canonical project host.
- CodeGraphContext is already installed on that host.
- The target repo has already been indexed.
- A rollback backup of the live OpenCode config exists.
- `opencode mcp list` is checked before and after the change.
- First live session is read-only only.
- MCP tool permissions remain ask-gated.
- Mutation-capable tools are not granted persistent approval.

## Target host for first live enable

AMD only.

Reason:

- AMD already hosts OpenCode.
- AMD already has CodeGraphContext installed.
- AMD LoRA journal repo has already been indexed.
- Isolated validation already succeeded there.

## Files involved

Live OpenCode config:

    /home/enzo/.config/opencode/opencode.json

Validated candidate config:

    /home/enzo/.config/opencode/opencode.with-codegraphcontext-disabled.candidate.json

Recommended backup naming:

    /home/enzo/.config/opencode/opencode.json.bak.YYYYMMDD-HHMMSS.before-codegraphcontext-mcp

## Live config addition

Add this shape to the live OpenCode config:

    "mcp": {
      "codegraphcontext": {
        "type": "local",
        "command": [
          "/srv/mcp/servers/codegraphcontext-venv/bin/codegraphcontext",
          "mcp",
          "start"
        ],
        "enabled": true,
        "timeout": 20000
      }
    },
    "permission": {
      "codegraphcontext_*": "ask"
    }

If the live config already contains `mcp` or `permission`, merge carefully instead of overwriting.

## First live validation prompt

Use this exact prompt:

    Use only the codegraphcontext MCP server for read-only inspection. Do not edit files. Do not read repository files directly. Use only these tools if needed: list_indexed_repositories, get_repository_stats, list_watched_paths. In 5 bullet points or fewer, report the indexed repository name/path and repository stats. Then stop.

Allow once only for:

- `codegraphcontext_list_indexed_repositories`
- `codegraphcontext_get_repository_stats`
- `codegraphcontext_list_watched_paths`

Reject mutation-capable tools, including:

- `codegraphcontext_add_code_to_graph`
- `codegraphcontext_add_package_to_graph`
- `codegraphcontext_delete_repository`
- `codegraphcontext_watch_directory`
- `codegraphcontext_unwatch_directory`
- `codegraphcontext_switch_context`
- `codegraphcontext_execute_cypher_query`

## Rollback

Restore the backup:

    cp /home/enzo/.config/opencode/opencode.json.bak.YYYYMMDD-HHMMSS.before-codegraphcontext-mcp \
       /home/enzo/.config/opencode/opencode.json

Then validate:

    opencode mcp list

Expected rollback result:

    No MCP servers configured

Also check the repo:

    cd /home/enzo/crucial/lora-corpus-pipeline-journal
    git status --short

Expected result:

    no output

## Definition of done

Live enable is complete only if:

- `opencode mcp list` shows CodeGraphContext connected.
- First live read-only prompt succeeds.
- `git status --short` remains clean.
- The exact OpenCode version is recorded.
- The result is documented in `inventory/mcp/codegraphcontext.md`.
- ThinkCentre mirror receives the documentation commit.
