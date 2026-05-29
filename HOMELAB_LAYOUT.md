# Homelab Layout

This is the current layout entrypoint.

For workflow direction, do not use this file alone. Start with:

1. `PLAN_INDEX.md`
2. `docs/provider-neutral-adhd-workflow.md`
3. `CURRENT_SLICE.md`
4. `AGENT_STATUS.md`

Current host meanings:

| Host | Current meaning |
|---|---|
| `framework` | Framework laptop, user seat/thin client |
| `strix` | Framework Desktop / Strix Halo host; canonical homelab repo at `/srv/projects/homelab` |
| `thinkcentre` | Hub for model-dispatch, Open WebUI, AdGuard, dashboard, Hermes report browser, and git mirrors |
| `amd` | Desktop with RTX 3090 + RX 7900 XT; local model host |
| `mac-mini` | M4 Mac mini where Codex Desktop is running; git mirror target |
| `mini-pc` | Media server |
| Oracle Cloud instance | Headscale host |

Current key repos:

| Repo | Location |
|---|---|
| Homelab repo | `strix:/srv/projects/homelab` |
| ThinkCentre model-dispatch repo | `thinkcentre:/srv/model-dispatch` |
| ThinkCentre homelab mirror | `thinkcentre:/srv/git/homelab.git` |
| Cubie camera test repo | `strix:/srv/projects/cubie-camera-node` |

The old two-surface layout document was archived instead of edited in place:

- `docs/archive/homelab-layout-two-surface-superseded-2026-05-29.md`
