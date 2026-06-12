# Hermes ThinkCentre Integration

Status: live baseline configured on ThinkCentre
Updated: 2026-06-11

## Purpose

This document defines the useful Hermes Agent setup for the ThinkCentre
instance, based on the current homelab workflow and pinned Codex threads.

The intent is to make Hermes a persistent observer, monitor, reviewer, and
status reporter for local work. Hermes must not become an autonomous patch
author, approval daemon, mail sender, service restarter, or power-control
operator.

## SearXNG Decision

Open WebUI's SearXNG integration is useful, but it is not enough by itself.

Open WebUI should remain a human-facing chat and research UI. It can use the
same SearXNG service for manual web search, saved web sources, and chat
research. That does not automatically make search available to Hermes cron
jobs, Codex task packets, Antigravity MCP tools, kernel monitors, or proof
audit scripts.

The better hookup is one shared ThinkCentre SearXNG service with JSON enabled,
then multiple bounded consumers:

- Open WebUI uses SearXNG through its web-search settings.
- Hermes uses SearXNG through a read-only web/search tool or MCP wrapper.
- Kernel monitors use a narrow search wrapper that records query, URL, title,
  timestamp, and search backend.
- Codex and Antigravity may use the same search wrapper through MCP when a
  future approved slice enables that path.

This avoids three bad outcomes:

- search that only works inside Open WebUI
- search implementations that drift across tools
- model-written claims without source URLs or timestamps

Official behavior to preserve:

- Open WebUI supports SearXNG as a web-search provider.
- SearXNG JSON consumers require `format=json` support enabled in
  `settings.yml`.

Current local SearXNG service:

```text
http://192.168.50.225:8080/search?q=<query>&format=json
```

Read-only discovery on 2026-06-11 confirmed that local SearXNG JSON search
returns results for `A733 SDMMC IDMAC`.

The same discovery found a live Hermes cron issue: the active
`A733 source-diff heartbeat` job points at `a733-source-diff-heartbeat.sh`, but
Hermes runs `.sh` scripts through bash while that file contained Python code.
The first live setup pass should fix that wrapper before enabling more jobs.

Approval brief:

```text
inventory/hermes-thinkcentre-live-setup-approval-brief-20260611.md
```

## Scope Approved For Setup

The user approved setting up the useful Hermes items except media/ComfyUI MCP
integration and except project-specific cron jobs. Those cron jobs should be
enabled from the corresponding topic conversation.

In scope:

1. kernel proof and verification harness integration
2. cron-based monitors, only from the matching project thread
3. safe command allowlist
4. SearXNG shared search backend
5. auxiliary model routing
6. memory or repo-backed knowledge integration
7. hooks and audit logs
8. messaging and web UI notifications
9. MCP tool servers for local hardware and status, gated as read-only or
   approval-required

Out of scope for this setup:

- ComfyUI/media-generation MCP integration
- autonomous patch edits
- autonomous branch promotion
- autonomous `b4 send` or email submission
- autonomous power cycling
- unattended destructive shell commands

## Kernel Patch Integration

Hermes should treat the A733/Cubie A7S work as the highest-value integration.

Authority chain:

1. git state
2. task packet
3. proof log
4. UART or hardware evidence
5. public source URL, commit, message ID, or archived query result
6. local model review card
7. Hermes summary

Hermes summaries are never authoritative above proof logs or human approval.

Existing kernel surfaces to use:

```text
scripts/kernel-workflow-env
scripts/kernel-workflow-status
scripts/kernel-patch-export-status
scripts/kernel-proof
scripts/kernel-token-offload
scripts/kernel-research-query
scripts/kernel-review-matrix
scripts/kernel-idle-ledger
scripts/kernel-idle-review-sweep
scripts/a733-source-diff-heartbeat
scripts/a733-heartbeat-watch
scripts/a733-breakthrough-watch
scripts/a733-rfc-recheck-packet
scripts/cubie-runtime-proof-approval-packet
scripts/hermes-kernel-work-cycle
scripts/a733-hermes-hourly-supervisor
scripts/a733-hermes-source-diff-audit-prompt
task-packets/kernel/a733-hypothesis-queue.json
task-packets/kernel/results/
task-packets/kernel/hermes-source-diff/
```

Hermes should initially run only read-only checks and report:

- current queue head
- current maintainer blockers
- latest proof ID or missing proof
- latest lore/public-search result
- whether a monitor found new source-backed input
- whether any local model lane is down
- whether a human-only gate is waiting

Hermes should read `inventory/kernel-workflow-paths.json` before assuming any
kernel tree, patch export, or report path. Do not use a Mac-only path on
ThinkCentre just because it appears in older thread context.

Hermes must not run the queued H149 unattended runtime sweep unless the human
operator explicitly approves that live hardware action. It may summarize H149
status and produce an approval brief.

Longer Hermes kernel-work cycles should use `scripts/hermes-kernel-work-cycle`
so timeout state, logs, and final output are captured under
`task-packets/kernel/hermes-work/`.

Normal completion notifications for that wrapper are opt-in. Set
`HERMES_KERNEL_NOTIFY=1` to send one concise completion, timeout, or failure
message through the existing Hermes messaging route. The target defaults to
`telegram` and can be overridden with `HERMES_KERNEL_NOTIFY_TARGET`. Do not add
project-local Telegram bot code or direct Telegram API calls for this path.

## Cron Jobs

Useful cron jobs for ThinkCentre Hermes:

| Job | Cadence | Action |
|---|---:|---|
| A733 source-diff heartbeat | 20 minutes | Confirm source-diff report state and notify only on movement |
| A733 lore/public monitor | 60 minutes | Search SearXNG/lore mirrors for new A733 SDMMC0 evidence |
| A733 workflow status | 60 minutes | Run read-only workflow status commands |
| Model endpoint health | 15 minutes | Check Open WebUI gateway, Strix, 7900XT, and embeddings while ComfyUI owns the 3090 |
| OpenRouter free cache health | 4 hours after refresh | Verify allowlist count and sync state |
| Hermes config drift check | daily | Report changed model IDs, fallback chain, or tool allowlist |

Cron outputs should land under repo-owned task packets or a Hermes report
directory, not as untracked private chatter.

Suggested output roots:

```text
task-packets/kernel/hermes-hourly/
task-packets/kernel/hermes-source-diff/
task-packets/kernel/results/
```

## Safe Command Allowlist

Hermes `command_allowlist` is a permanent allowlist for dangerous command
patterns, not a normal list of safe commands. The live ThinkCentre baseline
therefore leaves `command_allowlist: []` and relies on manual approval for
dangerous operations.

Start with read-only commands and existing scripts:

```text
git status --short --branch
git log --oneline --decorate -n
git diff --stat
git diff --check
rg
find
cat
sed -n
jq
curl -fsS http://192.168.50.225:4011/health
curl -fsS http://192.168.50.225:4011/v1/models
systemctl --user status hermes-dashboard.service
scripts/kernel-workflow-status
scripts/kernel-token-offload status
scripts/kernel-idle-ledger status
scripts/routing-health
scripts/a733-source-diff-heartbeat
scripts/a733-heartbeat-watch
scripts/a733-breakthrough-watch
```

Do not allow initially:

```text
git commit
git push
git send-email
b4 send
docker compose up
docker compose down
systemctl restart
rm
mv
scp to production paths
power-cycle scripts
scripts/a733-idmac-bruteforce-lab full-auto
```

Those commands require an approval brief and a separate operator action.

## Auxiliary Model Routing

Hermes should not use a random free cloud model for deterministic internal
tasks. As of 2026-06-11, the 3090 is reserved for ComfyUI and must not be used
by Hermes, Open WebUI Hub, or Antigravity until the operator releases it.

Live routing:

| Purpose | Preferred model |
|---|---|
| primary chat | OpenRouter auto-free through Open WebUI gateway |
| main fallback | Strix Qwen3.6 ctx256k |
| fast triage, short summaries | 7900XT Qwen3.6 ctx8k |
| long context compression/review | Strix Qwen3.6 ctx256k |
| secondary research review | 7900XT Qwen3.6 ctx8k |
| title generation | 7900XT |
| web extraction | Strix |
| triage specifier | Strix |
| kanban decomposition | Strix |
| curator/profile summaries | Strix |

The live fallback chain is:

```text
OpenRouter auto-free -> Strix
```

7900XT is intentionally not a main Hermes Agent fallback because its 8K context
window is below Hermes Agent's 64K minimum. It is suitable only for smaller
auxiliary calls.

## Memory And Knowledge

Use repo-backed memory first:

```text
CODEX_CONTEXT.md
CURRENT_SLICE.md
AGENT_STATUS.md
DECISIONS.md
PLAN_INDEX.md
inventory/pinned-threads/
runbooks/
task-packets/kernel/
```

External memory providers or OpenBrain can be added later, but Hermes should
write durable facts back to reviewed repo docs or task packets, not only into a
private opaque memory store.

## Hooks And Audit Logs

Live baseline:

- `~/.hermes/scripts/hermes-audit-hook`
- append-only JSONL output at `~/.hermes/logs/audit-hooks.jsonl`
- enabled for `on_session_end`, `api_request_error`, `subagent_stop`, and
  selected `post_tool_call` events
- hook registrations verified with `hermes hooks doctor`

Useful hooks:

- session end: append summary to a Hermes report file
- cron failure: create a JSON result with command, exit code, and stderr tail
- model change: record old model ID, new model ID, and source gateway count
- search result: record query, backend, URL, title, timestamp, and result hash
- proof result: record proof ID and status, never model interpretation alone

Hooks should be append-only unless the target file is a generated latest report.

## Messaging And Web UI

Telegram is useful for short interrupts:

- model endpoint down
- new public A733 evidence found
- proof gate changed
- cron monitor failed repeatedly
- human-only approval is waiting

Hermes now has a dedicated Telegram bot for those notices:

```text
@messagero_divino_bot
```

Kernel patch notifications must use Hermes' shared messaging path, not
project-local Telegram code:

```text
hermes send --to telegram
hermes cron edit <job-id> --deliver telegram
hermes cron create ... --deliver telegram
```

The Todoist Telegram bot is separate and should stay dedicated to task
intake/household/Todoist flows. Do not add Telegram tokens, polling scripts,
containers, or kernel-specific sidecars for A733 work. If delivery through
`@messagero_divino_bot` fails, fix the shared Hermes gateway/home-channel
configuration rather than bypassing it.

The Hermes Web UI is better for detailed review:

- latest A733 queue state
- latest source-diff report
- endpoint health
- model fallback chain
- recent cron results
- command allowlist status

## MCP Tool Server Direction

Preferred MCP shape:

- `kernel-status`: read-only workflow status, queue status, proof status
- `kernel-search`: SearXNG and local Qdrant search, source URLs required
- `kernel-proof`: proof-log listing and retrieval; validation runs require
  human approval
- `model-health`: read-only endpoint health
- `cubie-lab`: read-only UART/log inventory first; power and boot actions
  approval-required

## Live-Service Change Approval Brief

Before live setup, produce an exact command block for each host.

Required fields:

- intended change
- files or services affected
- rollback path
- validation command
- exact command block

Do not restart Hermes, edit live Hermes config, alter cron jobs, or deploy MCP
servers until the operator approves the command block.

## Acceptance Criteria

The approved non-cron setup pass is complete when:

- Hermes can run read-only A733 status checks from ThinkCentre.
- Hermes can query SearXNG JSON and record source URLs.
- Project-specific Hermes cron jobs are left to their matching topic
  conversations.
- Hermes targeted auxiliary models are local and deterministic.
- Command allowlist remains empty unless a future approval intentionally adds a
  dangerous-command pattern.
- Notifications are partially configured; the Hermes gateway still needs a
  Telegram platform token before it can send/receive gateway messages.
- All changes are documented in this repo.
- No media/ComfyUI MCP integration has been added.
