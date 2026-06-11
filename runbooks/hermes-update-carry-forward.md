# Hermes Update Carry-Forward Inventory

Status: live ThinkCentre inventory captured
Updated: 2026-06-11

## Purpose

This is the checklist to use before and after updating Hermes Agent on
ThinkCentre. It records the normal Hermes settings we intentionally changed and
the bespoke homelab work that can disappear when the upstream agent tree is
updated.

The goal is not to freeze Hermes. The goal is to let Hermes update cleanly,
then carry forward the local integration layer that makes it useful in this
homelab.

## Current Live Baseline

ThinkCentre Hermes:

```text
Hermes Agent v0.16.0 (2026.6.5) upstream 8505e9d6
project: /home/enzo/.hermes/hermes-agent
config:  /home/enzo/.hermes/config.yaml
```

Active user services:

```text
hermes-dashboard.service
hermes-gateway.service
hermes-openrouter-free-sync.path
hermes-openrouter-free-sync.timer
hermes-watch-telegram-tasks-bot.service
a733-hermes-report-server.service
```

Open WebUI Hub and related containers currently active on ThinkCentre:

```text
open-webui                  0.0.0.0:3000->8080
open-webui-llm-gateway      0.0.0.0:4011->4010
open-webui-searxng          0.0.0.0:8080->8080
local-deep-research         0.0.0.0:5000->5000
telegram-tasks-bot          container-only Telegram polling bot
```

## Source Of Truth Files

Back these up before every Hermes update:

```text
/home/enzo/.hermes/config.yaml
/home/enzo/.hermes/.env
/home/enzo/.hermes/auth.json
/home/enzo/.hermes/channel_directory.json
/home/enzo/.hermes/gateway_state.json
/home/enzo/.hermes/cron/jobs.json
/home/enzo/.hermes/state.db
/home/enzo/.hermes/memory_store.db
/home/enzo/.hermes/kanban.db
/home/enzo/.hermes/scripts/
/home/enzo/.config/systemd/user/hermes-*.service
/home/enzo/.config/systemd/user/hermes-*.path
/home/enzo/.config/systemd/user/hermes-*.timer
/home/enzo/.local/bin/hermes-sync-openrouter-free-models
```

If the update touches Open WebUI Hub, also back up:

```text
/home/enzo/open-webui-hub/compose.yml
/home/enzo/open-webui-hub/gateway/app.py
/home/enzo/open-webui-hub/gateway/models.yml
/home/enzo/open-webui-hub/cache/openrouter-free-models.json
/home/enzo/open-webui-hub/scripts/
```

Do not paste secrets into notes or chat. Env files and API keys should be
checked only by path, key name, length, or presence.

## Model Routing To Preserve

Hermes should use ThinkCentre Open WebUI Hub as the single model gateway:

```text
provider: openwebui-hub
base_url: http://192.168.50.225:4011/v1
transport: chat_completions
default model: openrouter-free / Auto Free Router random available free model
```

Current intentional fallback:

```text
OpenRouter auto-free -> Strix Qwen3.6 ctx256k
```

Important constraints:

- Do not enable the RTX 3090 for Hermes while ComfyUI owns it.
- Keep the 3090 absent from Hermes and Open WebUI Hub LLM routing until Enzo
  explicitly releases it.
- Keep 7900XT out of the main Hermes Agent fallback chain because its 8K
  context is below Hermes Agent's 64K minimum.
- 7900XT is still useful for short auxiliary jobs.
- Strix is the long-context local fallback and delegation model.

Current local models in Hermes allowlist:

```text
Strix Qwen3.6 27B Dense ROCmFP4-MTP headQ6 GGUF rocmfp4-llama ROCm+Vulkan ctx256k self-spec reasoning-off coding
7900XT Qwen3.6 27B Dense Q4_K_M GGUF llama.cpp Vulkan ctx8k research
```

Current OpenRouter free allowlist is synced from:

```text
http://192.168.50.225:4011/v1/models
```

## Messaging Routing To Preserve

Hermes-originated notifications should use the dedicated Hermes Telegram bot:

```text
Bot: @messagero_divino_bot
Purpose: Hermes updates, notifications, summaries, approval prompts, and monitor output
Config: /home/enzo/.hermes/.env
Gateway: hermes-gateway.service
Preferred delivery: Hermes gateway, `hermes send --to telegram`, or cron `deliver=telegram`
```

Do not create project-local Telegram bots, bot tokens, polling containers,
sidecar scripts, or direct Telegram API workarounds for kernel patch work.
Do not route Hermes/kernel updates through the Todoist Telegram bot; that bot
is reserved for task intake, household, and Todoist flows.

If Telegram delivery fails, diagnose and repair the shared Hermes gateway/home
channel path first. Kernel-specific scripts should not read Telegram tokens or
send messages directly.

## Auxiliary Routing To Preserve

Hermes `auxiliary` routing should remain local through `openwebui-hub`.

Strix:

```text
compression
curator
kanban_decomposer
triage_specifier
web_extract
```

7900XT:

```text
approval
mcp
profile_describer
skills_hub
title_generation
tts_audio_tags
```

Vision:

```text
provider: auto
```

## Hermes Settings To Preserve

Agent behavior:

```text
max_turns: 90
reasoning_effort: xhigh
gateway_timeout: 1800
clarify_timeout: 600
environment_probe: true
task_completion_guidance: true
tool_use_enforcement: auto
```

Security:

```text
allow_private_urls: true
redact_secrets: true
tirith_enabled: true
tirith_fail_open: true
allow_lazy_installs: true
```

Memory:

```text
memory_enabled: true
user_profile_enabled: true
provider: holographic
write_approval: false
memory_char_limit: 2200
user_char_limit: 1375
```

Delegation:

```text
provider: openwebui-hub
model: Strix Qwen3.6 ctx256k
orchestrator_enabled: true
inherit_mcp_toolsets: true
max_iterations: 50
max_spawn_depth: 1
child_timeout_seconds: 900
max_concurrent_children: 2
```

Approvals:

```text
mode: manual
cron_mode: deny
destructive_slash_confirm: true
mcp_reload_confirm: true
```

Hooks:

```text
/home/enzo/.hermes/scripts/hermes-audit-hook
```

Hook events currently configured:

```text
api_request_error
on_session_end
subagent_stop
post_tool_call
```

Post-tool matcher:

```text
(web_search|web_extract|browser|computer_use|execute_code|terminal|shell|send_message|fact_store|memory|delegate_task)
```

## Bespoke Work To Preserve

### OpenRouter Free Sync

Script:

```text
/home/enzo/.local/bin/hermes-sync-openrouter-free-models
```

Systemd:

```text
hermes-openrouter-free-sync.service
hermes-openrouter-free-sync.path
hermes-openrouter-free-sync.timer
```

What it does:

- Reads `http://192.168.50.225:4011/v1/models`.
- Allows `openrouter-free / ...` entries.
- Allows local `owned_by=homelab-local` chat models.
- Excludes embedding-only models.
- Keeps context lengths in Hermes config.
- Marks OpenRouter entries with `free_only: true`.
- Removes stale local hardware-prefixed and OpenRouter-free entries.

Hardware prefixes the sync script knows about:

```text
3090
7900XT
Strix
amd-3090 /
amd-7900xt /
strix /
```

### Hardware-First Model Names

Local models should remain hardware-prefixed in picker surfaces:

```text
Strix ...
7900XT ...
3090 ... only when released from ComfyUI
```

This makes the accelerator visible before the model family.

### LAN Dashboard Engine

Service:

```text
hermes-dashboard.service
```

Preserve:

```text
hermes dashboard --host 0.0.0.0 --port 9120 --no-open --insecure --skip-build
```

This intentionally exposes Hermes Dashboard to local LAN devices without a
tunnel. Treat it as LAN-only and do not expose it to the public internet.

### Hermes Gateway

Service:

```text
hermes-gateway.service
```

Current use:

- Keep the Hermes messaging gateway running.
- Telegram is not currently enabled in Hermes gateway.
- The separate `telegram-tasks-bot` container is the actual Telegram bot.

### Telegram Tasks Bot Watcher

Service:

```text
hermes-watch-telegram-tasks-bot.service
```

What it does:

```text
/usr/local/bin/hermes-project-watch thinkcentre telegram-tasks-bot /srv/telegram-tasks-bot true
```

This is not the Telegram bot. It is Hermes watching the Telegram bot project.
The bot itself is:

```text
/srv/telegram-tasks-bot
container: telegram-tasks-bot
```

### A733 Monitoring Layer

Hermes scripts live at:

```text
/home/enzo/.hermes/scripts/a733-*.sh
```

Active A733 monitor scripts include:

```text
a733-dashboard-index.sh
a733-h149-approval-brief.sh
a733-hermes-safety-audit.sh
a733-hermes-source-diff-audit-prompt.sh
a733-model-health-monitor.sh
a733-patch-blocker-brief.sh
a733-public-patch-readiness-monitor.sh
a733-public-source-monitor.sh
a733-radxa-provenance-audit.sh
a733-repo-drift-monitor.sh
a733-repo-sync-approval-brief.sh
a733-source-diff-heartbeat.sh
a733-workflow-status-monitor.sh
```

Current enabled cron jobs:

```text
A733 workflow status monitor       17 * * * *
A733 public-source monitor         23 * * * *
A733 model endpoint health         */15 * * * *
A733 public patch readiness        37 * * * *
A733 patch blocker brief           39 * * * *
A733 repo drift monitor            41 * * * *
A733 repo sync approval brief      43 * * * *
A733 dashboard index               */30 * * * *
A733 Hermes safety audit           */30 * * * *
```

Current disabled cron jobs:

```text
A733 Cubie3 discovery keeper       1,21,41 * * * *
A733 breakthrough notifier         */5 * * * *
A733 Cubie3 heartbeat              0,20,40 * * * *
A733 Cubie2 heartbeat              10,30,50 * * * *
A733 source-diff heartbeat         */20 * * * *
```

Do not enable project-specific cron jobs from a generic Hermes update pass.
Those should be enabled from the specific pinned conversation for that project.

### Homelab-Only Model Picker Filter

This is the main update-sensitive source patch.

After the latest update, the live Hermes source tree is clean upstream, and the
homelab model-picker filter exists only in backups:

```text
/home/enzo/.hermes/hermes-agent/hermes_cli/inventory.py.bak.hardware-labels.20260610181647
/home/enzo/.hermes/hermes-agent/hermes_cli/inventory.py.bak.homelab-filter.20260610115206
/home/enzo/.hermes/hermes-agent/hermes_cli/web_server.py.bak.homelab-filter.20260610115206
/home/enzo/.hermes/hermes-agent/tui_gateway/server.py.bak.homelab-filter.20260610115206
```

The missing function is:

```text
filter_homelab_model_options(...)
```

Intended behavior:

- Hermes Dashboard and TUI model switchers should only show the
  `openwebui-hub` provider.
- The model list should come from the synced Open WebUI Hub allowlist.
- The picker should include local chat models and OpenRouter-free models.
- It should exclude embedding-only models.
- It should not append unrelated canonical providers or paid model catalogs.

Current live upstream behavior to check after every update:

```text
hermes_cli/inventory.py
tui_gateway/server.py model.options
hermes_cli/web_server.py /api/model/options
```

If the dashboard again shows models that are not in ThinkCentre's model server,
reapply this filter against the current upstream files instead of blindly
copying the old backups.

## Update Procedure

1. Snapshot state:

```sh
ssh thinkcentre 'bash -s' <<'REMOTE'
set -euo pipefail
stamp=$(date -u +%Y%m%dT%H%M%SZ)
dst="$HOME/.hermes/state-snapshots/$stamp-pre-update"
mkdir -p "$dst"
cp -a "$HOME/.hermes/config.yaml" "$dst/config.yaml"
cp -a "$HOME/.hermes/.env" "$dst/.env" 2>/dev/null || true
cp -a "$HOME/.hermes/auth.json" "$dst/auth.json" 2>/dev/null || true
cp -a "$HOME/.hermes/channel_directory.json" "$dst/channel_directory.json" 2>/dev/null || true
cp -a "$HOME/.hermes/gateway_state.json" "$dst/gateway_state.json" 2>/dev/null || true
cp -a "$HOME/.hermes/cron/jobs.json" "$dst/jobs.json"
cp -a "$HOME/.hermes/scripts" "$dst/scripts"
cp -a "$HOME/.config/systemd/user" "$dst/systemd-user"
printf 'snapshot=%s\n' "$dst"
REMOTE
```

2. Update Hermes using the normal upstream update path.

3. Re-run the OpenRouter free sync:

```sh
ssh thinkcentre 'systemctl --user start hermes-openrouter-free-sync.service && systemctl --user status hermes-openrouter-free-sync.service --no-pager'
```

4. Check whether the homelab-only model picker patch survived:

```sh
ssh thinkcentre "cd ~/.hermes/hermes-agent && rg -n 'filter_homelab_model_options|_homelab_selectable_model' hermes_cli/inventory.py hermes_cli/web_server.py tui_gateway/server.py"
```

5. If the filter is missing, port it from the backup files into the current
   upstream implementation and restart the dashboard.

6. Restart and verify user services:

```sh
ssh thinkcentre 'systemctl --user daemon-reload && systemctl --user restart hermes-dashboard.service hermes-gateway.service && systemctl --user status hermes-dashboard.service hermes-gateway.service --no-pager'
```

## Post-Update Verification

Run these checks after every update:

```sh
ssh thinkcentre '~/.local/bin/hermes --version'
ssh thinkcentre 'systemctl --user list-units --all "hermes*" "a733*" --no-pager'
ssh thinkcentre 'curl -fsS http://127.0.0.1:4011/v1/models | python3 -m json.tool >/dev/null'
ssh thinkcentre 'curl -fsS http://127.0.0.1:9120 >/dev/null && echo dashboard-ok'
ssh thinkcentre '~/.local/bin/hermes cron list'
```

Model picker manual check:

- Open Hermes Dashboard.
- Open the switch-model UI.
- Confirm local models are hardware-prefixed.
- Confirm the list contains only local chat models and `openrouter-free / ...`
  entries.
- Confirm embedding models are not offered as chat targets.
- Confirm the 3090 is absent while ComfyUI owns it.

## Known Drift To Fix Next

These are known follow-up items, not blockers for this inventory:

- Restore the homelab-only model picker filter against the current Hermes
  source tree.
- Update stale Open WebUI Hub docs that still mention the 3090 as the default
  chat model.
- Consider adding an automated post-update check that reports whether
  `filter_homelab_model_options` is missing.
