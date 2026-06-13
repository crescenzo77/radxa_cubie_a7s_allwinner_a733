# Hermes Model Priority UI

Small LAN-only control panel for ThinkCentre-hosted Hermes Agent model priority.

It reads available models from the Open WebUI/model-dispatch hub at
`http://192.168.50.225:4011/v1/models`, filters to Hermes-eligible models, and
updates `~/.hermes/config.yaml`.

Eligibility rules:

- OpenRouter models must be marked `free_only`.
- Local models must be online chat models.
- Models must have at least `64000` context tokens.
- Embedding models are excluded.
- RTX 3090 models are excluded unless `HERMES_ALLOW_3090=true`.

Applying a new order:

- creates a timestamped backup beside `~/.hermes/config.yaml`
- sets the first model as Hermes primary
- writes the rest into `fallback_providers`
- restarts `hermes-gateway.service` by default

Automatic reconcile:

- `hermes-sync-openrouter-free-models` runs after the OpenRouter free cache is
  refreshed.
- The sync script calls `reconcile_priority.py` after a successful allowlist
  sync.
- Reconcile keeps the user's chosen order, prunes models that are no longer
  eligible, and restores the baseline auto-free router plus Strix fallback when
  they are eligible.
- Reconcile does not promote newly discovered free models above the existing
  order.
- Reconcile refuses to write if live model discovery reports an error.
- Reconcile probes the first OpenRouter model in the active order. If the probe
  fails, it enters degraded mode and moves eligible local models to the front of
  the order. When the probe later succeeds, it restores the previous preferred
  order after pruning anything no longer eligible.
- Automatic reconcile runs with `HERMES_RESTART_GATEWAY=0` so routine cache
  refreshes do not send Telegram shutdown/interruption warnings.

ThinkCentre deployment path:

```sh
~/.hermes/model-priority-ui/app.py
~/.hermes/model-priority-ui/reconcile_priority.py
~/.local/bin/hermes-sync-openrouter-free-models
~/.config/systemd/user/hermes-model-priority-ui.service
```

Default URL:

```text
http://192.168.50.225:9130/
```
