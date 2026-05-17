# Current Slice

## Active: Baseline inventory and freeze point

## Purpose

Capture the current documented homelab architecture, routing, source, mirror,
backup, and tooling posture before any transition implementation changes.

This slice is documentation-only. It creates a freeze point for later reversible
migration slices.

## Scope

- Record host roles and known LAN/Tailscale IPs from existing docs.
- Record current Open WebUI, `model-dispatch`, LiteLLM rollback, OpenRouter-free,
  local model endpoint, OpenCode, MCP/CodeGraphContext, git source/mirror,
  backup/off-site, and known untracked-path posture.
- Use existing repo docs as the primary source of truth.
- Use only safe read-only repo/Git checks where needed.
- Leave a clear handoff in `AGENT_STATUS.md`.

## Non-Scope

- Do not edit live service files outside this repo.
- Do not change OpenCode settings.
- Do not change `model-dispatch` runtime files.
- Do not change Open WebUI, LiteLLM, Docker, systemd, reverse proxy, SearXNG,
  monitoring, backup, or MCP settings.
- Do not restart services.
- Do not run `sudo`.
- Do not move repo locations.
- Do not add scripts.
- Do not touch `tools/`.
- Do not commit.

## Validation Steps

- Read the required control docs:
  - `CURRENT_SLICE.md`
  - `ROADMAP.md`
  - `HOMELAB_LAYOUT.md`
  - `WORKFLOW.md`
  - `DECISIONS.md`
  - `ROUTING_INVENTORY.md` if present
  - `AGENT_STATUS.md`
- Confirm the baseline inventory is documentation-only.
- Run `git diff --check`.
- Run `git diff --stat`.
- Run `git status --short`.

## Definition of Done

- `CURRENT_SLICE.md` identifies Slice 0 as the active slice.
- `inventory/baseline-2026-05-17.md` records the baseline inventory and freeze
  point.
- `AGENT_STATUS.md` describes what changed, what did not change, checks run,
  risks, and next recommended action.
- No live services, configs, OpenCode settings, `model-dispatch` runtime files,
  MCP settings, Docker state, systemd state, repo locations, scripts, or
  `tools/` files were changed.
