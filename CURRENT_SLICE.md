# Current Slice

## Slice 2: Build `advisor-packet`

Create a small local script named `advisor-packet`.

## Purpose

The script should create a compact markdown packet for the web UI advisor so the user does not have to manually copy raw terminal output, diffs, and status into chat.

## Requirements

The script should:

- Run from a project working tree.
- Write markdown to `/tmp/advisor-packet.md` by default.
- Accept an optional output path as the first argument.
- Include timestamp and current directory.
- Include these files if present:
  - `PROJECT_PLAN.md`
  - `CURRENT_SLICE.md`
  - `DECISIONS.md`
  - `AGENT_STATUS.md`
  - `AGENTS.md`
- Include Git information if available:
  - `git status --short`
  - `git diff --stat`
  - bounded `git diff` excerpt
- Include bounded recent coder log if `.agent/session.log` exists.
- Copy output to clipboard if `wl-copy` or `xclip` exists.
- Continue gracefully if optional files, Git, or clipboard tools are unavailable.

## Constraints

- No network calls.
- No model API calls.
- No Codex automation.
- No autonomous approval behavior.
- No watcher or daemon behavior.
- No MCP integration.
- Local shell script only.

## Acceptance Criteria

- Running `scripts/advisor-packet` from `/srv/projects/homelab` creates `/tmp/advisor-packet.md`.
- The output is readable markdown.
- The output is bounded by default.
- The script does not fail if optional files are missing.
- The script does not fail if not inside a Git repo.
- The script is committed to Git.
