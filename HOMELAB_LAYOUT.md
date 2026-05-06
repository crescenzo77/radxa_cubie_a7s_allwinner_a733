# Homelab Layout: Two-Surface Workflow

This is the architectural reference for the practical two-surface homelab workflow. It answers what runs where, which machines own which responsibilities, and what must not become infrastructure.

Last updated: 2026-05-05.

## Operating Model

The normal workflow has two human-operated surfaces plus one small bridge script:

1. **Web UI advisor/planner** in Open WebUI.
2. **Self-hosted coding agent** on the coding PC or project host.
3. **`advisor-packet`** local script that summarizes project state for the advisor.

The user remains the final decision-maker. The system helps prepare decisions, explain confusing coder output, and reduce context bloat. It does not auto-approve code, supervise agents autonomously, or turn Codex/Claude-style hosted tools into infrastructure.

Codex may be used manually during setup documentation work, but it is not part of the steady-state operating workflow.

## Machine Roles

| Hostname | LAN | Tailscale | Role |
|---|---:|---:|---|
| `framework` | — | yes | Thin client: browser, SSH, VS Code Remote-SSH |
| `amd` | `192.168.50.252` | `100.107.201.16` | Current coding execution host; OpenCode installed; primary RTX 3090 coder model and RX 7900 XT backup |
| `strix` | `192.168.50.11` | `100.105.138.41` | Target canonical project/source host; reasoning/testbed inference |
| `thinkcentre` | `192.168.50.225` | `100.127.113.105` | Services hub: Open WebUI, SearXNG, AdGuard, dashboard, proxies; LiteLLM retained temporarily for rollback during router transition |
| `mac mini` | `192.168.50.164` | yes | iMessage relay backend; future tier-2 git mirror |
| `minipc` | `192.168.50.76` | yes | LAN backup target |
| `oracle` | cloud | yes | Off-site backup, headscale host |

The Framework laptop remains a thin client. Important project state should live on the platform, not on the laptop.

## Surface 1: Web UI Advisor

Open WebUI on ThinkCentre is the browser-based advisor/planner:

```text
URL: http://192.168.50.225:3000
Target model access: Open WebUI -> direct local model endpoints; optional OpenRouter access remains free-only and explicit
```

Use the advisor for:

- Project planning before touching code.
- Interpreting confusing coder output.
- Deciding whether a proposed direction remains on path.
- Generating the next prompt for the coding agent.
- Reviewing a compact project-state packet instead of raw terminal dumps.

Current live Open WebUI still uses LiteLLM during the transition window:

```yaml
OPENAI_API_BASE_URLS: "http://192.168.50.225:4000/v1"
```

Target state: Open WebUI should move back to direct local model endpoints for AMD and Strix. LiteLLM should remain available temporarily only as a rollback path until the direct endpoint configuration is tested.

## Surface 2: Self-Hosted Coding Agent

The coding surface runs on the coding PC or project host, not on the thin client.

Current practical default:

```text
Host: amd
Tool: OpenCode
Binary: /home/enzo/.opencode/bin/opencode
Version: 1.14.38
Current provider: Homelab LiteLLM during transition
Transition target: direct local-coder provider on AMD
Rollback endpoint: http://192.168.50.225:4000/v1
```

Preferred steady-state coder:

- **OpenCode** using the direct local-coder path.

Aider was evaluated and eliminated from the homelab workflow. LiteLLM is being phased out of the active OpenCode path. OpenRouter should remain available only as a generated free-only manual fallback, not as an automatic hidden route.

Codex/Claude-style hosted tools must not be wired into API automation, wrappers, scheduled tasks, or background jobs. If used at all during setup or emergency manual work, they remain manually invoked tools.

## Bridge: `advisor-packet`

`advisor-packet` is a small local script run from a project working tree. It creates a compact markdown packet for the web UI advisor.

Purpose:

- Reduce copy/paste between terminal, editor, and web chat.
- Avoid pasting raw terminal output into the advisor.
- Keep context bounded so the advisor sees the current state without swallowing the whole repo.
- Make the user’s decision point clearer.

It is not:

- An approval daemon.
- An autonomous supervisor.
- A hidden watcher agent.
- An MCP failure-supervision layer.
- A paid API automation bridge.

The first version of `advisor-packet` should collect:

- `CURRENT_SLICE.md`
- `DECISIONS.md`
- `AGENT_STATUS.md`
- `AGENTS.md`
- `git status`
- `git diff --stat`
- Bounded `git diff` excerpt
- Bounded recent coder log, if present

The output should be markdown suitable for pasting into Open WebUI.

## Shared Project State

Each active project should keep human-readable operating files in the repository:

| File | Purpose |
|---|---|
| `PROJECT_PLAN.md` | Durable project goals, constraints, and broad plan |
| `CURRENT_SLICE.md` | The current narrow unit of work |
| `DECISIONS.md` | Decision log with dates and rationale |
| `AGENT_STATUS.md` | Latest coder status, blockers, proposed next action |
| `AGENTS.md` | Instructions and boundaries for local coding agents |
| Git history/diffs | Actual source-of-truth change record |

These files are the shared state between the user, advisor, and coder. They are deliberately simple markdown plus git.

## Router transition: LiteLLM to direct local endpoints

LiteLLM on ThinkCentre is the current live router but is no longer the target long-term active path.

```text
OpenCode
  -> direct local-coder on AMD

OpenCode manual fallback
  -> generated homelab-openrouter-free provider
  -> verified free OpenRouter models only

Open WebUI
  -> direct local model endpoints on AMD and Strix
```

Host details:

```text
Host: thinkcentre
Path: /srv/litellm
Port: 4000
Endpoint: http://192.168.50.225:4000/v1
Container: litellm
```

OpenRouter remains allowed only as free-model access. The target is to preserve the existing free-model discovery/filtering mechanism while moving generated artifacts to neutral config under `/srv/openrouter-free/`:

- `openrouter/openrouter/free`
- Generated model entries ending in `:free`

No paid OpenRouter fallback is allowed. If free models cannot be verified, they must not be exposed.

## Model Role Assignments During Transition

| Role | Model label / target | Endpoint | Use |
|---|---|---|---|
| Primary local coding | `local-coder | AMD RTX 3090 | Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` | `amd:8083` | OpenCode coding work |
| 3090-off backup | `local-coder-backup | AMD RX 7900 XT | Gemma 4 26B A4B Q4_K_M.gguf` | `amd:8084` | Direct/manual backup target after transition |
| Planning/reasoning | `local-reasoning | Strix | Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` | `strix:8081` | Advisor/planning |
| Strix coder testbed | `local-coder-testbed | Strix | Qwen3-Coder-Next-UD-Q4_K_XL.gguf` | `strix:8082` | Manual coder testbed |
| Cloud fallback | generated `homelab-openrouter-free` entries | OpenRouter API | Free-only manual fallback, generated from verified allowlist |

## Project Source Convention

Target canonical source host:

```text
strix:/srv/projects/<project-name>/
```

AMD remains an intentional exception for projects that need the RTX 3090 directly, such as the LoRA pipeline. AMD is also the current OpenCode execution host.

Target git mirror convention:

```text
Canonical source: strix:/srv/projects/<project-name>/
Tier-1 mirror: thinkcentre:/srv/git/<project>.git
Tier-2 mirror: mac mini:~/git-mirrors/<project>.git
```

## Explicit Non-Goals

Do not build:

- Custom approval daemons.
- Hidden watcher agents.
- Automated coder supervisors.
- MCP failure-supervision systems.
- Codex API automation.
- Claude/Codex wrapper infrastructure.
- Paid-provider automation.
- Fragile bespoke orchestration when stable local OSS and simple markdown files are enough.

The target is stable, practical, proven OSS with minimal glue.
