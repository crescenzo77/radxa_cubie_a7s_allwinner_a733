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
| `framework` | Framework laptop, user seat/thin client; current LAN IP `192.168.50.140`, Tailscale `100.64.0.5`; do not assume always-on availability |
| `strix` | Framework Desktop / Strix Halo host; canonical homelab repo at `/srv/projects/homelab` |
| `thinkcentre` | Hub for model-dispatch, Open WebUI, AdGuard, dashboard, Hermes report browser, git mirrors, and kernel-cortex storage/services |
| `amd` | Desktop with RTX 3090 + RX 7900 XT; local model host, validation host, and kernel-cortex embedding worker |
| `mac-mini` | M4 Mac mini where Codex Desktop is running; no sustained container/model workloads |
| `mini-pc` | Media server |
| Oracle Cloud instance | Headscale host |

Current key repos:

| Repo | Location |
|---|---|
| Homelab repo | `strix:/srv/projects/homelab` |
| ThinkCentre model-dispatch repo | `thinkcentre:/srv/model-dispatch` |
| ThinkCentre homelab mirror | `thinkcentre:/srv/git/homelab.git` |
| Cubie camera test repo | `strix:/srv/projects/cubie-camera-node` |

Current kernel-cortex split:

- ThinkCentre `192.168.50.225`: Qdrant, ingestion worker, vector storage
- AMD `192.168.50.252`: RX 7900 XT ROCm embedding endpoint
- Mac mini: Codex Desktop dispatcher only

Current kernel-cortex endpoints:

- ThinkCentre Qdrant: `127.0.0.1:6333` on `192.168.50.225`
- AMD embeddings: `192.168.50.252:8091`
- AMD research synthesis: `127.0.0.1:8092` on `192.168.50.252`

The AMD-to-Mac 2.5GbE link is documented for future bulk staging, but it is not
the default reason to place services on the Mac.

The old two-surface layout document was archived instead of edited in place:

- `docs/archive/homelab-layout-two-surface-superseded-2026-05-29.md`
