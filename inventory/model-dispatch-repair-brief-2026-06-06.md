# model-dispatch Repair Brief - 2026-06-06

## Purpose

Record the current ThinkCentre `model-dispatch` failure mode and the safe
operator-gated repair path. This is documentation only. No live service file,
systemd unit, Open WebUI setting, or route was changed while writing this
brief.

## Current State

| Area | Evidence |
|---|---|
| ThinkCentre host | `192.168.50.225` |
| Live port | `4010` |
| `/v1/models` | Responds |
| `/v1/chat/completions` | Drops the connection with `RemoteDisconnected` |
| Process | PID `1812`, command `/usr/bin/python3 /srv/model-dispatch/app.py` |
| Process cwd | `/srv/model-dispatch (deleted)` |
| Live directory | `/srv/model-dispatch` is absent |
| Source worktree | `192.168.50.11:/srv/projects/model-dispatch` |
| Source commit | `524a201c293ebeb669201d221f227c16e463b482` |
| ThinkCentre mirror | `/srv/git/model-dispatch.git`, `main` at `524a201c293ebeb669201d221f227c16e463b482` |
| Source checks | `python3 -m py_compile app.py`, `python3 -m json.tool config.json`, and `python3 tests/check_config.py` passed |

`systemctl show model-dispatch.service` reports an active process, but
`LoadState=not-found` and no service unit file was found under the checked
systemd unit directories. Treat the current process as an orphaned stale live
runtime.

## Kernel Workflow Impact

The direct kernel offload workflow does not depend on ThinkCentre
`model-dispatch` right now:

- AMD RTX 3090 direct endpoint: `192.168.50.252:8001`
- AMD RX 7900 XT research endpoint: `192.168.50.252:8092`
- Strix review endpoint: `192.168.50.11:8082`
- ThinkCentre Qdrant endpoint: `192.168.50.225:6333`

Until `model-dispatch` is repaired, Codex Desktop should continue using the
direct kernel offload helpers and treat `model-dispatch` as warning-only.

## Repair Preconditions

Do not perform a live repair until an operator explicitly approves a
`model-dispatch` repair/deploy slice.

Before approval, confirm:

- The target is still `192.168.50.225`.
- The current process is still stale or intentionally stopped.
- `/srv/model-dispatch` is still absent or ready to be recreated.
- The source commit to deploy is exactly recorded.
- The source config is reconciled with the current live model endpoints.
- OpenRouter-free behavior remains explicit/manual and fail-closed.
- Open WebUI validation is ready after restart.

## Required Route Reconciliation

The Strix source config is syntactically valid, but it still contains historical
model-dispatch routes such as AMD ports `8083`/`8084` and Strix port `8081`.
The current kernel offload lanes use AMD `8001`, AMD research `8092`, and Strix
`8082`.

Treat source commit `524a201c293ebeb669201d221f227c16e463b482` as diagnostic
evidence, not as an approved deployment commit for the kernel workflow. Do not
deploy its `config.json` as-is without first deciding whether
`model-dispatch` should:

- remain an Open WebUI compatibility surface using its historical aliases, or
- be updated to reflect the current direct kernel offload endpoints.

A live repair for the kernel workflow requires a later source commit whose
`config.json` has been reconciled and reviewed.

The route audit in `inventory/model-dispatch-route-audit-2026-06-06.md`
currently shows that the direct kernel lanes are not reachable from
ThinkCentre as ordinary LAN URLs. If those services remain bound to
host-local `127.0.0.1`, repair must choose one explicit access pattern before
`model-dispatch` can participate in the kernel workflow:

- expose the selected model services on reviewed LAN bindings,
- create reviewed tunnels from ThinkCentre to each host-local endpoint, or
- keep `model-dispatch` out of the kernel workflow and continue using the
  direct SSH-assisted offload helpers.

## Proposed Repair Block - Not Run

The following block is a future operator-approved repair outline. It was not
run. It intentionally requires explicit approval and route reconciliation
environment variables so it cannot be pasted accidentally while the source
config is known to be stale for the current kernel workflow.

```sh
# NOT RUN - requires explicit operator approval
set -euo pipefail

: "${MODEL_DISPATCH_REPAIR_APPROVED:?set to yes only after explicit operator approval}"
: "${MODEL_DISPATCH_CONFIG_RECONCILED:?set to yes only after config routes are reviewed}"
: "${APPROVED_SOURCE_COMMIT:?set to the reviewed reconciled source commit}"
test "$MODEL_DISPATCH_REPAIR_APPROVED" = yes
test "$MODEL_DISPATCH_CONFIG_RECONCILED" = yes

SRC_HOST=192.168.50.11
DST_HOST=192.168.50.225
SRC_DIR=/srv/projects/model-dispatch
DST_DIR=/srv/model-dispatch
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

ssh "$SRC_HOST" "cd '$SRC_DIR' && test -z \"\$(git status --short)\""
ACTUAL_SOURCE_COMMIT="$(ssh "$SRC_HOST" "cd '$SRC_DIR' && git rev-parse HEAD")"
test "$ACTUAL_SOURCE_COMMIT" = "$APPROVED_SOURCE_COMMIT"
ssh "$SRC_HOST" "cd '$SRC_DIR' && python3 -m py_compile app.py"
ssh "$SRC_HOST" "cd '$SRC_DIR' && python3 -m json.tool config.json >/tmp/model-dispatch-config-json-check.txt"
ssh "$SRC_HOST" "cd '$SRC_DIR' && python3 tests/check_config.py"

ssh "$DST_HOST" "pgrep -af '/srv/model-dispatch/app.py' || true"

# Stop the stale process only after approval. If systemd cannot stop it because
# the unit is missing, kill only a python process with the exact command and a
# deleted /srv/model-dispatch cwd.
ssh "$DST_HOST" "sudo systemctl stop model-dispatch.service || true"
STALE_PIDS="$(ssh "$DST_HOST" '
for pid in $(pgrep -x python3 || true); do
  cmd=$(tr "\000" " " </proc/$pid/cmdline 2>/dev/null || true)
  cwd=$(readlink /proc/$pid/cwd 2>/dev/null || true)
  if [ "$cmd" = "/usr/bin/python3 /srv/model-dispatch/app.py " ] &&
     [ "$cwd" = "/srv/model-dispatch (deleted)" ]; then
    echo "$pid"
  fi
done
')"
if [ -n "$STALE_PIDS" ]; then
  ssh "$DST_HOST" "sudo kill $STALE_PIDS"
fi
ssh "$DST_HOST" "! ss -ltnp 2>/dev/null | grep -q ':4010 '"

ssh "$DST_HOST" "mkdir -p '$DST_DIR'"
ssh "$SRC_HOST" "cd '$SRC_DIR' && tar -cf - app.py config.json .gitignore .cgcignore" |
  ssh "$DST_HOST" "tar -C '$DST_DIR' -xf -"

ssh "$DST_HOST" "python3 -m py_compile '$DST_DIR/app.py'"
ssh "$DST_HOST" "python3 -m json.tool '$DST_DIR/config.json' >/tmp/model-dispatch-config-json-check.txt"

# Restore an existing reviewed unit if one is found. If none exists, create the
# minimal reviewed unit below as part of the approved repair.
ssh "$DST_HOST" "sudo tee /etc/systemd/system/model-dispatch.service >/dev/null" <<'UNIT'
[Unit]
Description=Homelab model-dispatch OpenAI-compatible router
After=network-online.target
Wants=network-online.target

[Service]
User=enzo
Group=enzo
WorkingDirectory=/srv/model-dispatch
ExecStart=/usr/bin/python3 /srv/model-dispatch/app.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
UNIT

ssh "$DST_HOST" "sudo systemctl daemon-reload"
ssh "$DST_HOST" "sudo systemctl enable --now model-dispatch.service"
```

## Proposed Validation Block - Not Run

```sh
# NOT RUN - future validation after approved repair
curl -fsS http://192.168.50.225:4010/health
curl -fsS http://192.168.50.225:4010/v1/models

curl -fsS http://192.168.50.225:4010/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "auto-local",
    "messages": [{"role": "user", "content": "Reply with ok."}],
    "stream": false,
    "max_tokens": 16
  }'
```

## Rollback Notes

Because `/srv/model-dispatch` is currently absent, there may be no live files to
back up before recreating the directory. The main rollback path is therefore:

- stop the repaired service,
- remove or move the recreated `/srv/model-dispatch`,
- restore a known prior backup if one exists,
- restore the prior unit file if one exists,
- or leave `model-dispatch` stopped while direct kernel offload remains active.

Do not expose secrets, copy logs, or commit runtime data during repair.
