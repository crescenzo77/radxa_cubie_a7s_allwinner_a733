# Homelab Layout: Two-Surface Workflow

This is the architectural reference for the practical two-surface homelab workflow. It answers what runs where, which machines own which responsibilities, and what must not become infrastructure.

Last updated: 2026-05-18.

## Operating Model

The normal workflow has two human-operated surfaces plus one small bridge script:

1. **Web UI advisor/planner** in Open WebUI.
2. **Self-hosted coding agent** on the coding PC or project host.
3. **`advisor-packet`** local script that summarizes project state for the advisor.

The user remains the final decision-maker. The system helps prepare decisions, explain confusing coder output, and reduce context bloat. It does not auto-approve code, supervise agents autonomously, or turn Codex/Claude-style hosted tools into infrastructure.

Codex is the primary manual agent for planning, sequencing, approval briefs,
documentation slices, and risky live-service work. It must not become
background infrastructure or an autonomous approval system.

## Machine Roles

| Hostname | LAN | Tailscale | Role |
|---|---:|---:|---|
| `framework` | — | yes | Thin client: browser, SSH, VS Code Remote-SSH |
| `amd` | `192.168.50.252` | `100.107.201.16` | Current coding execution host; OpenCode installed; primary RTX 3090 coder model and RX 7900 XT backup |
| `strix` | `192.168.50.11` | `100.105.138.41` | Target canonical project/source host; reasoning/testbed inference |
| `thinkcentre` | `192.168.50.225` | `100.127.113.105` | Services hub: Open WebUI, model-dispatch, SearXNG, AdGuard, dashboard, proxies; LiteLLM retained for rollback/history |
| `mac mini` | `192.168.50.164` | yes | iMessage relay backend; future tier-2 git mirror |
| `minipc` | `192.168.50.76` | yes | LAN backup target |
| `oracle` | cloud | yes | Off-site backup, headscale host |

The Framework laptop remains a thin client. Important project state should live on the platform, not on the laptop.

## Target Platform Architecture

The desired end state separates control-plane services, source ownership, GPU
compute, backup, external anchoring, and edge devices.

| Host | Target role |
|---|---|
| `thinkcentre` | Control plane: Open WebUI, `model-dispatch`, SearXNG, reverse proxy, monitoring, service catalog, and tier-1 git mirrors |
| `strix` | Canonical source, development, code-graph, and reasoning host |
| `amd` | Mode-switched GPU compute worker for coding, LoRA/training, and creative workloads |
| `minipc` | LAN backup and artifact storage |
| `mac mini` | Apple/iMessage services and tier-2 git mirror |
| `oracle` | Headscale, off-site backup, and external anchor |
| `cubies` | Edge camera nodes only |
| `framework` | Thin client for browser, SSH, editor, and review |

`model-dispatch` is the target single model-facing API registry for Open WebUI,
OpenCode, Continue.dev, and scripts. Clients should eventually use stable model
aliases from `model-dispatch` rather than duplicating direct endpoint definitions.

Dashboards, monitoring, observability, service dashboards, Prometheus, Grafana,
Loki, and Vector are target control-plane capabilities only. They are not
current deployment tasks for the `model-dispatch` transition and require a
future explicit slice and operator approval before any deployment.

Direct AMD routing and LiteLLM remain rollback paths until each replacement path
is validated. The migration must stay sliced, reversible, and reviewable. Codex
may assist implementation, but it must not become background infrastructure or an
autonomous approval system.

## Surface 1: Web UI Advisor

Open WebUI on ThinkCentre is the browser-based advisor/planner:

```text
URL: http://192.168.50.225:3000
Current model access: Open WebUI -> model-dispatch -> local endpoints or explicit OpenRouter-free choices
```

Use the advisor for:

- Project planning before touching code.
- Interpreting confusing coder output.
- Deciding whether a proposed direction remains on path.
- Generating the next prompt for the coding agent.
- Reviewing a compact project-state packet instead of raw terminal dumps.

Current live Open WebUI model API target:

```text
OPENAI_API_BASE_URLS: http://192.168.50.225:4010/v1
```

ThinkCentre dispatcher details:

```text
Host: thinkcentre
Service: model-dispatch.service
Path: /srv/model-dispatch
Port: 4010
Endpoint: http://192.168.50.225:4010/v1
```

The dispatcher exposes OpenAI-compatible `/v1/models` and `/v1/chat/completions` for Open WebUI. It keeps Open WebUI local-first while allowing explicit, verified OpenRouter-free choices. LiteLLM is not the active Open WebUI model endpoint anymore; it remains rollback/history unless explicitly reactivated.

Open WebUI visible model categories:

- Auto local routes: `auto-local`, `auto-coding-local`, `auto-reasoning-local`, `auto-small-local`.
- Explicit local models: `strix-reasoning-qwen3.6-65k`, `strix-coder-qwen3-coder-next-65k`, `amd-coder-qwen3-coder-30b-32k`, `amd-backup-gemma4-26b-8k`.
- OpenRouter-free choices: `openrouter-free/openrouter/auto-free-router` and `openrouter-free/<verified-model>:free` entries.

## Surface 2: Manual Agent Execution

The execution surface runs on the project host or coding PC, not on the thin
client. Choose the manual agent by task shape:

- Codex: planning, migration choreography, approval briefs, documentation
  slices, and risky live-service work.
- Claude Code: strong frontier-code alternative and second opinion.
- Aider: preferred bounded repo patch assistant for one planned edit in one
  repo.
- OpenCode: later local-agent experiment, not the default operating agent.
- Continue.dev: editor assist and review.
- Cline: sandbox-only.

Existing OpenCode setup for later experiments:

```text
Host: amd
Tool: OpenCode
Binary: /home/enzo/.opencode/bin/opencode
Version: 1.14.39
Default provider: homelab-local
Default base URL: http://192.168.50.252:8083/v1
Default model: homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf
Backup provider: homelab-local-backup
Backup base URL: http://192.168.50.252:8084/v1
Small model: homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf
Default path: OpenCode on AMD -> direct AMD local-coder
Manual provider: homelab-openrouter-free
Manual provider model count: 25 verified free OpenRouter models
Rollback endpoint: http://192.168.50.225:4000/v1
```

OpenCode remains installed and usable for later explicit local-agent
experiments. It is not the assumed next primary agent just because it fits the
local model-dispatch architecture.

Aider may be used only as a bounded patch assistant after a slice is planned:
one repo, one bounded edit, one reviewable diff, validated before commit.
LiteLLM is no longer in the default OpenCode path and no longer active for Open
WebUI, but remains available as rollback/history. OpenRouter is available only
through generated free-only entries when selected manually, not as an automatic
hidden route.

Codex/Claude-style hosted tools must not be wired into API automation, wrappers, scheduled tasks, or background jobs. If used at all during setup or emergency manual work, they remain manually invoked tools.

## MCP and CodeGraphContext Boundary

CodeGraphContext is optional tooling and must not become a broad mutation path into canonical repositories.

Architecture boundary:

```text
canonical project repo = source of truth / read-only input by default
CodeGraphContext sandbox = writable disposable task workspace
promotion path = reviewed diff, patch, manual copy, or branch review
```

CodeGraphContext may read from approved canonical project repositories. By default, it must not write directly to canonical working trees.

Any write-capable CodeGraphContext use belongs in a disposable sandbox. Git worktrees are the preferred sandbox shape because they preserve normal Git review while separating experiments from the source-of-truth working tree. Temporary branch checkouts, dedicated patch-proposal directories, and `/tmp` patch artifacts are also valid when they better fit the task. Exact paths are intentionally not required.

This boundary is path-agnostic. It applies to operational source repos, project journal repos, documentation/control repos, and future project repos. No persistent broad mutation approval is allowed, and no automatic MCP setup wizard should be run against primary repositories.

Large videos, extracted frames, datasets, generated evidence, model outputs, and bulky review artifacts should not be duplicated into sandboxes or tracked by Git unless that storage is explicitly intended.

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

## Routing State: OpenCode Direct, Open WebUI Dispatch

AMD OpenCode is configured directly to the local AMD RTX 3090 coder endpoint and has a direct AMD RX 7900 XT backup provider for `small_model`. This remains available for later explicit local-agent experiments. Open WebUI now points to `model-dispatch` on ThinkCentre at `http://192.168.50.225:4010/v1`. LiteLLM on ThinkCentre is retained as rollback/history only.

Continue.dev on framework intentionally routes through LiteLLM using the verbose exposed model IDs returned by `/v1/models`. Continue is treated as an editor-side shared routing client. OpenCode remains configured direct-local on AMD for later local-agent experiments.

```text
OpenCode on AMD
  -> homelab-local
  -> http://192.168.50.252:8083/v1
  -> homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf

OpenCode small_model backup on AMD
  -> homelab-local-backup
  -> http://192.168.50.252:8084/v1
  -> homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf

OpenCode manual free cloud provider
  -> homelab-openrouter-free
  -> 25 verified free OpenRouter models only

Open WebUI
  -> model-dispatch on ThinkCentre
  -> http://192.168.50.225:4010/v1
  -> local-first dispatch plus explicit OpenRouter-free choices

OpenCode rollback
  -> LiteLLM on ThinkCentre
  -> http://192.168.50.225:4000/v1
```

Active Open WebUI dispatcher details:

```text
Host: thinkcentre
Path: /srv/model-dispatch
Service: model-dispatch.service
Port: 4010
Endpoint: http://192.168.50.225:4010/v1
```

LiteLLM rollback/history details:

```text
Host: thinkcentre
Path: /srv/litellm
Port: 4000
Endpoint: http://192.168.50.225:4000/v1
Container: litellm
```

OpenRouter remains allowed only as free-model access. The existing free-model discovery/filtering mechanism now generates neutral artifacts under `/srv/openrouter-free/` and model-dispatch consumes the verified allowlist for Open WebUI:

- `openrouter/openrouter/free`
- `openrouter-free/openrouter/auto-free-router`
- Generated model entries ending in `:free`

No paid OpenRouter fallback is allowed. If free models cannot be verified, they must not be exposed.

## Model Role Assignments

| Role | Model label / target | Endpoint | Use |
|---|---|---|---|
| OpenCode local-agent experiment | `homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` | `amd:8083` | Direct AMD coder path |
| OpenCode small model backup | `homelab-local-backup/google_gemma-4-26B-A4B-it-Q4_K_M.gguf` | `amd:8084` | Direct AMD RX 7900 XT backup provider |
| Planning/reasoning | `local-reasoning | Strix | Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` | `strix:8081` | Advisor/planning |
| Strix coder testbed | `local-coder-testbed | Strix | Qwen3-Coder-Next-UD-Q4_K_XL.gguf` | `strix:8082` | Manual coder testbed |
| Manual free cloud provider | generated `homelab-openrouter-free` entries | OpenRouter API | Free-only manual use, generated from verified allowlist |
| Open WebUI auto local | `auto-local`, `auto-coding-local`, `auto-reasoning-local`, `auto-small-local` | `thinkcentre:4010` | Local-first model-dispatch routes |
| Open WebUI manual free cloud | `openrouter-free/openrouter/auto-free-router`, `openrouter-free/<verified-model>:free` | `thinkcentre:4010` | Explicit free-only OpenRouter choices |

## Project Source Convention

Target canonical source host:

```text
strix:/srv/projects/<project-name>/
```

AMD remains an intentional exception for projects that need the RTX 3090 directly, such as the LoRA pipeline. AMD also hosts the existing OpenCode setup for later local-agent experiments.

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
