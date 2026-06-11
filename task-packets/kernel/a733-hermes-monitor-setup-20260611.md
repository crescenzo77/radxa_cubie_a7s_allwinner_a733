# A733 Hermes Monitor Setup

Date: 2026-06-11

## Scope

This records the conservative Hermes setup for Radxa Cubie A7S / Allwinner A733
kernel work.

Hermes is acting as a read-only monitor/reporter. It must not edit kernel
repositories, run H149, boot or power-cycle Cubie boards, add trailers, promote
branches, send mail, or mutate model routing.

## Active Hermes Jobs

Live ThinkCentre Hermes jobs after setup:

| Job | ID | Cadence | Mode | Purpose |
|---|---|---:|---|---|
| A733 workflow status monitor | `069906e27192` | `17 * * * *` | `no-agent` | Reports queue head, maintainer blockers, dispatcher waiting actions, git status, and token-offload status. |
| A733 public-source monitor | `10dddfb0ab2b` | `23 * * * *` | `no-agent` | Searches local SearXNG for A733/Radxa/SDMMC0 public-source changes and records URLs/timestamps. |
| A733 model endpoint health | `cdab23637c7c` | `*/15 * * * *` | `no-agent` | Checks gateway and model endpoint availability through read-only `/health` and `/v1/models` requests. No inference is sent. |
| A733 public patch readiness | `b4a75d6a1c83` | `37 * * * *` | `no-agent` | Checks the public review repo, patch snapshot, and private final-send checklist without regenerating, validating, sending, or editing branches. |
| A733 patch blocker brief | `c4333a70d47c` | `39 * * * *` | `no-agent` | Converts readiness/model/queue findings into a human approval brief. It does not authorize or perform the action. |
| A733 repo drift monitor | `46c0255f59a9` | `41 * * * *` | `no-agent` | Compares the ThinkCentre public clone against the Mac-recorded expected public head. It reports drift only; it does not sync repos. |
| A733 repo sync approval brief | `9636aa1980e7` | `43 * * * *` | `no-agent` | Turns repo drift into explicit human choices. The default recommendation is monitor-only; sync/pull/push/reset still require approval. |
| A733 dashboard index | `c1ac3adc75dc` | `*/30 * * * *` | `no-agent` | Builds a read-only landing page with queue head, blockers, model failures, report freshness, and links to all current A733 Hermes reports. |
| A733 Hermes safety audit | `30edac32a8e5` | `*/30 * * * *` | `no-agent` | Checks active Hermes cron jobs against the approved monitor-only allowlist and reports unexpected hardware/runtime jobs. |

Paused after cleanup review:

| Job | ID | Former Cadence | Reason |
|---|---|---:|---|
| A733 source-diff heartbeat | `56633ee4233b` | `*/20 * * * *` | No active source-diff audit is running; this added scheduler noise without moving the kernel work forward. |

Quarantined deployed Hermes scripts:

```text
/home/enzo/.hermes/scripts.disabled/a733-cleanup-20260611/a733-breakthrough-watch.sh
/home/enzo/.hermes/scripts.disabled/a733-cleanup-20260611/a733-cubie3-discovery-keeper.sh
/home/enzo/.hermes/scripts.disabled/a733-cleanup-20260611/a733-heartbeat-cubie2.sh
/home/enzo/.hermes/scripts.disabled/a733-cleanup-20260611/a733-heartbeat-cubie3.sh
/home/enzo/.hermes/scripts.disabled/a733-cleanup-20260611/a733-hermes-cubie2-lead-supervisor.sh
/home/enzo/.hermes/scripts.disabled/a733-cleanup-20260611/a733-hermes-hourly-supervisor.sh
```

## Report URLs

```text
http://192.168.50.225:9181/hermes-hourly/a733-workflow-status-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-dashboard-index-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-hermes-safety-audit-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-public-source-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-model-health-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-h149-approval-brief-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-public-patch-readiness-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-patch-blocker-brief-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-repo-drift-latest.md
http://192.168.50.225:9181/hermes-hourly/a733-repo-sync-approval-brief-latest.md
http://192.168.50.225:9181/hermes-source-diff/a733-radxa-provenance-audit-latest.md
```

## Latest Observations

- Cleanup review on 2026-06-11: the source-diff heartbeat was paused and
  removed from the safety audit required-job allowlist. It was reasonable while
  an audit was active, but unreasonable as a permanent no-op heartbeat.
- Cleanup review on 2026-06-11: dashboard and safety audit cadence was reduced
  from every 10 minutes to every 30 minutes. Ten minutes was unnecessarily
  noisy for read-only status pages with a 75-minute stale threshold.
- The workflow status report sees queue head `A733-SDMMC-H149`, status
  `queued_unattended_runtime`; this is not approval to run it.
- The Radxa provenance audit did not prove an exact Radxa
  `5.15.147-21-a733` kernel source. Orange Pi remains a secondary BSP
  reference only.
- The model health baseline reports Strix, 7900XT, embeddings, ThinkCentre
  gateway, and SearXNG reachable. The AMD RTX 3090 endpoint on
  `192.168.50.252:8001` is currently refusing connections.
- The public patch-readiness baseline reports ThinkCentre public repo
  `/home/enzo/projects/radxa_cubie_a7s_allwinner_a733` clean against its
  origin, but the exported patches still contain `allwinner,pinmux` and the
  private final-send checklist is not `send_ready`. Hermes must report this,
  not fix it autonomously.
- The blocker brief baseline turns those findings into an approval-gated next
  action: do not run H149, regenerate patches, promote branches, or send mail
  without explicit operator approval.
- The repo drift baseline records that Mac public repo head
  `b54dade62c44` differs from ThinkCentre public clone head `57a1325c5a07`.
  ThinkCentre is monitoring a clean GitHub clone, but it is not the latest Mac
  patch-work state. Hermes must report the drift rather than pulling, pushing,
  resetting, or treating either side as silently authoritative.
- The repo sync approval brief records three explicit paths: keep monitoring
  only, refresh the ThinkCentre clone from GitHub, or perform a reviewed Mac to
  ThinkCentre sync. It recommends monitor-only by default because the Mac public
  repo is ahead of its public remote by 214 commits and no sync approval has
  been given.
- The patch blocker brief now consumes the repo drift report directly. If the
  ThinkCentre public clone differs from the Mac-recorded expected public head,
  that drift appears as a first-class blocker with a link to the sync approval
  brief.
- The dashboard index is the preferred human landing page for this Hermes lane.
  It summarizes current queue head, blockers, model failures, report freshness,
  next safe actions, scheduler safety state, and links while preserving the
  same read-only/no-approval boundary.
- The dashboard now emits `dashboard_status`, per-report freshness, and
  `report_findings`. Reports older than 75 minutes, missing reports, JSON load
  errors, or a non-`ok` safety audit turn the dashboard status to `attention`.
- The dashboard keeps a local state file and sends a Telegram notification only
  when `dashboard_status`, `report_findings`, or scheduler safety status
  changes after a prior state exists. Clean repeat runs do not spam Telegram.
- The dashboard records provenance for the ThinkCentre homelab checkout and the
  deployed dashboard script: repo path, repo HEAD, dirty-count summary, script
  path, and script SHA-256. Full repo status remains in the JSON report.
- The dashboard indexes both hourly reports and the source-diff Radxa
  provenance report, so the public/Radxa source evidence is visible from the
  same landing page.
- The dashboard surfaces the headline Radxa provenance result directly: exact
  Radxa `5.15.147-21-a733` kernel source remains unproven, so Orange Pi 6.6
  must stay labeled as a secondary BSP reference.
- The safety audit validates the Hermes cron surface against the current
  monitor-only allowlist. After cleanup, the intended active state is nine
  jobs, all no-agent and all read-only.
- The workflow status monitor now treats missing optional helper scripts on
  ThinkCentre as host capability gaps instead of reporting shell errors as if
  they were maintainer blockers.
- One false Telegram stall alert was sent during smoke testing because the
  heartbeat matched the Hermes gateway process as an active audit. The matcher
  was narrowed and the state file was cleared; a subsequent Hermes-triggered
  heartbeat run recorded `ok`.

## Files Added

```text
scripts/a733-hermes-source-diff-heartbeat-wrapper
scripts/a733-hermes-workflow-status-monitor
scripts/a733-hermes-public-source-monitor
scripts/a733-hermes-model-health-monitor
scripts/a733-hermes-radxa-provenance-audit
scripts/a733-hermes-h149-approval-brief
scripts/a733-hermes-public-patch-readiness-monitor
scripts/a733-hermes-patch-blocker-brief
scripts/a733-hermes-repo-drift-monitor
scripts/a733-hermes-repo-sync-approval-brief
scripts/a733-hermes-dashboard-index
scripts/a733-hermes-safety-audit
```

## Validation

Commands run:

```text
bash -n scripts/a733-hermes-source-diff-heartbeat-wrapper scripts/a733-hermes-workflow-status-monitor scripts/a733-hermes-public-source-monitor
python3 -m py_compile scripts/a733-source-diff-heartbeat
bash -n scripts/a733-hermes-model-health-monitor
bash -n scripts/a733-hermes-radxa-provenance-audit
bash -n scripts/a733-hermes-workflow-status-monitor
bash -n scripts/a733-hermes-patch-blocker-brief
bash -n scripts/a733-hermes-dashboard-index
bash -n scripts/a733-hermes-safety-audit
git diff --check -- <new/changed monitor scripts>
```

Live smoke checks:

```text
/home/enzo/.hermes/scripts/a733-source-diff-heartbeat.sh
/home/enzo/.hermes/scripts/a733-workflow-status-monitor.sh
/home/enzo/.hermes/scripts/a733-public-source-monitor.sh
/home/enzo/.hermes/scripts/a733-model-health-monitor.sh
/home/enzo/.hermes/scripts/a733-radxa-provenance-audit.sh
/home/enzo/.hermes/scripts/a733-dashboard-index.sh
```

## Next Safe Increment

The next safe operator decision is whether to keep monitoring only or approve a
repo authority/sync path. The dashboard and blocker brief currently show three
open blockers:

- the ThinkCentre public clone differs from the Mac-recorded public head
- the ThinkCentre public patch snapshot still contains rejected
  `allwinner,pinmux` text
- the private final-send checklist is not `send_ready`

Hermes must continue reporting these as blockers. It must not resolve them by
syncing repos, regenerating patches, promoting branches, sending mail, or
running H149 unless the operator gives explicit approval for that specific
action.

## Enhancement Review

Keep:

- Dashboard index: worth keeping as the single landing page.
- Patch blocker brief and public patch readiness: worth keeping because they
  protect against accidental send/regenerate work.
- Repo drift and repo sync approval brief: worth keeping because Mac and
  ThinkCentre public states differ.
- Safety audit: worth keeping because it catches accidental live hardware jobs.
- Dashboard freshness/status alerts: worth keeping, but only on state changes.

Questionable but acceptable:

- Public-source monitor: low-cost, but only useful if it finds new public
  A733/Radxa/SDMMC information. Keep for now; retire if it stays uninformative.
- Model endpoint health: useful because local-model routing was part of the
  workflow, but it should remain read-only and non-inference.

Removed from active schedule:

- Source-diff heartbeat: useful only during an active source-diff audit. It is
  paused now.

Deleted from the tracked helper set and quarantined from active Hermes scripts:

- `a733-breakthrough-watch`
- `a733-cubie3-discovery-keeper`
- `a733-heartbeat-watch`
- `a733-hermes-cubie2-lead-supervisor`
- `a733-hermes-hourly-supervisor`

These were too close to unattended hardware orchestration for the current
monitor-only phase. They remain recoverable from git history and the disabled
ThinkCentre script directory if explicitly needed later.

Do not add more:

- No more Hermes process enhancements unless a live report is wrong, stale,
  unsafe, or missing a specific operator decision.
