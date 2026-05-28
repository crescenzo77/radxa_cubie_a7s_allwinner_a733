# Repo and Mirror Inventory - 2026-05-28

Purpose: record current working repositories and known mirrors before deciding
any project moves.

This inventory is read-only. No services, routes, remotes, Docker runtimes,
systemd units, or repo contents outside this document were changed while
collecting it.

## Validation Context

Checked from the Mac mini Codex desktop session on 2026-05-28.

Live checkpoint before inventory:

- Strix homelab repo: `/srv/projects/homelab`
- Strix latest commit: `de7a33e align operating docs with strix local agent checkpoint`
- Strix active vLLM mode: `tool`
- Strix served model: `qwen36-awq-agent-test`
- ThinkCentre model-dispatch service: active
- ThinkCentre model-dispatch latest commit:
  `e8b945a add local code test role alias`

## Strix Working Repositories

| Path | Branch | Remotes | Working tree |
| --- | --- | --- | --- |
| `/srv/projects/amd-strix-halo-vllm-toolboxes` | `ubuntu-docker-only` | `origin` GitHub upstream, `fork` GitHub fork | clean |
| `/srv/projects/cubie-a7s-armbian` | `main` | `thinkcentre:/srv/git/cubie-a7s-armbian.git` | dirty: `M READ_ONLY_CUBIE_CAPTURE_BRIEF.md` |
| `/srv/projects/cubie-camera-node` | `main` | `thinkcentre:/srv/git/cubie-camera-node.git` | clean |
| `/srv/projects/model-dispatch` | `main` | `enzo@192.168.50.225:/srv/git/model-dispatch.git` | clean |
| `/srv/projects/hermes-homelab-runtime` | `main` | `thinkcentre:/srv/git/hermes-homelab-runtime.git` | clean |
| `/srv/projects/homelab` | `main` | ThinkCentre, AMD, and Mac mini mirrors | clean before this inventory edit |

## ThinkCentre Working Repositories

| Path | Branch | Remotes | Working tree |
| --- | --- | --- | --- |
| `/srv/projects/homelab` | `main` | `/srv/git/homelab.git` as `origin` | clean |
| `/srv/leantime` | `main` | none shown | clean |
| `/srv/imessage-decision-assistant` | `main` | none shown | clean |
| `/srv/telegram-tasks-bot` | `main` | none shown | dirty: `M app.py` |
| `/srv/model-dispatch` | `main` | none shown | expected untracked backups |
| `/srv/openwebui` | `main` | none shown | clean |
| `/srv/scandocs` | `main` | none shown | many untracked project files |

Expected untracked files in `/srv/model-dispatch`:

- `backups/`
- `config.json.backup-before-qwen36-awq-agent-20260526-204405`

## ThinkCentre Bare Mirrors

| Path | HEAD branch |
| --- | --- |
| `/srv/git/cubie-a7s-armbian.git` | `master` |
| `/srv/git/cubie-camera-node.git` | `main` |
| `/srv/git/hermes-homelab-runtime.git` | `main` |
| `/srv/git/homelab.git` | `main` |
| `/srv/git/lora-corpus-pipeline-journal.git` | `master` |
| `/srv/git/model-dispatch.git` | `master` |

## Notes

- `find` on ThinkCentre hit `Permission denied` under
  `/srv/hermes-agent/data`; this inventory did not use `sudo`.
- Strix does not currently have `rg` available, so repository discovery used
  `find`.
- Dirty repositories were only observed and documented. They were not inspected
  deeply or modified.
- This does not decide ownership, archival status, migration order, or mirror
  cleanup.

## Suggested Next Action

Use this inventory to select one non-critical repository for a bounded real
Aider trial, or to plan a separate repo/mirror cleanup slice. Do not combine
cleanup with model runtime, route, or service changes.
