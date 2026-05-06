# Current Slice

## Slice 15: Add OpenRouter-free provider to OpenCode as manual-only

Add the generated `homelab-openrouter-free` provider to AMD OpenCode without changing the direct local default provider.

## Purpose

Allow OpenCode to manually select verified free OpenRouter models while keeping AMD direct local-coder as the default.

This slice must not create automatic cloud fallback.

## Scope

Live OpenCode config change on AMD only:

- Back up current direct-local OpenCode config.
- Copy generated `homelab-openrouter-free` provider from ThinkCentre.
- Create a candidate OpenCode config that includes:
  - `homelab-local`
  - `homelab-openrouter-free`
- Keep `model` set to AMD direct local-coder.
- Do not set OpenRouter as `model`.
- Do not set OpenRouter as `small_model`.
- Validate JSON.
- Switch live config only after validation.
- Confirm OpenCode still defaults to direct local provider.
- Do not call any OpenRouter model in this slice.

## Constraints

- Do not alter LiteLLM.
- Do not alter Open WebUI.
- Do not delete rollback config.
- Do not call OpenRouter.
- Do not add automatic OpenRouter fallback.
- Do not set `small_model` to the AMD 3090 model.
- Do not expose broad built-in OpenRouter provider access.
- Use only generated verified-free model entries.
- Stop after local default validation.

## Live Change Commands

### 1. Confirm current direct-local config works

```bash
ssh amd 'cd /tmp
timeout 180 /home/enzo/.opencode/bin/opencode run "Reply with exactly: opencode-direct-local-ok"
'
```

Expected response:

```text
opencode-direct-local-ok
```

### 2. Back up current direct-local config

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
backup="opencode.json.bak.$(date +%Y%m%d-%H%M%S).direct-local"
cp opencode.json "$backup"
echo "$backup"
python3 -m json.tool "$backup" >/tmp/opencode.direct-local.backup.validated.json
echo "backup-json-ok"
'
```

### 3. Copy generated provider from ThinkCentre to AMD

```bash
ssh thinkcentre 'cat /srv/openrouter-free/opencode.generated.json' > /tmp/opencode.generated.json
scp /tmp/opencode.generated.json amd:/tmp/opencode.generated.json
```

### 4. Build candidate config on AMD

This keeps local as default and adds OpenRouter-free only as a selectable/manual provider.

```bash
ssh amd 'python3 - <<'"'"'PY'"'"'
import json
from pathlib import Path

live = Path("/home/enzo/.config/opencode/opencode.json")
generated = Path("/tmp/opencode.generated.json")
candidate = Path("/home/enzo/.config/opencode/opencode.with-openrouter-free.candidate.json")

cfg = json.loads(live.read_text())
gen = json.loads(generated.read_text())

or_provider = gen["provider"]["homelab-openrouter-free"]

cfg["enabled_providers"] = [
    "homelab-local",
    "homelab-openrouter-free"
]

cfg["provider"]["homelab-openrouter-free"] = or_provider

# Preserve local default.
cfg["model"] = "homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"

# Do not set OpenRouter as small_model. Keep small_model absent unless a direct backup provider is added later.
cfg.pop("small_model", None)

candidate.write_text(json.dumps(cfg, indent=2) + "\n")
print(candidate)
print("openrouter_free_model_count =", len(or_provider["models"]))
PY'
```

### 5. Validate candidate JSON

```bash
ssh amd 'python3 -m json.tool /home/enzo/.config/opencode/opencode.with-openrouter-free.candidate.json >/tmp/opencode.with-openrouter-free.validated.json && echo "candidate-json-ok"'
```

### 6. Inspect candidate without secrets

```bash
ssh amd 'python3 - <<'"'"'PY'"'"'
import json
from pathlib import Path

p = Path("/home/enzo/.config/opencode/opencode.with-openrouter-free.candidate.json")
data = json.loads(p.read_text())

def redact(x):
    if isinstance(x, dict):
        return {
            k: ("<redacted>" if any(s in k.lower() for s in ["key", "token", "secret", "password"]) else redact(v))
            for k, v in x.items()
        }
    if isinstance(x, list):
        return [redact(v) for v in x]
    return x

print(json.dumps(redact(data), indent=2)[:8000])
print()
print("enabled_providers =", data.get("enabled_providers"))
print("default_model =", data.get("model"))
print("has_small_model =", "small_model" in data)
print("openrouter_free_model_count =", len(data["provider"]["homelab-openrouter-free"]["models"]))
PY'
```

### 7. Switch live config

This is the live config change.

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
cp opencode.with-openrouter-free.candidate.json opencode.json
python3 -m json.tool opencode.json >/tmp/opencode.live.with-openrouter-free.validated.json
echo "live-config-switched-with-openrouter-free-manual-provider"
'
```

### 8. Validate default still uses direct local provider

This must still use AMD direct local model, not OpenRouter.

```bash
ssh amd 'cd /tmp
timeout 180 /home/enzo/.opencode/bin/opencode run "Reply with exactly: opencode-direct-local-ok"
'
```

Expected response:

```text
opencode-direct-local-ok
```

## Rollback Commands

### 1. List backups

```bash
ssh amd 'cd /home/enzo/.config/opencode && ls -1t opencode.json.bak.* | head -10'
```

### 2. Restore selected backup

Replace `BACKUP_FILE` with the selected direct-local backup.

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
cp BACKUP_FILE opencode.json
python3 -m json.tool opencode.json >/tmp/opencode.rollback.validated.json
echo "rollback-restored"
'
```

## Acceptance Criteria

- Current direct-local config is backed up.
- Generated OpenRouter-free provider is copied from ThinkCentre.
- Candidate config validates as JSON.
- Live config validates as JSON.
- `enabled_providers` includes `homelab-local` and `homelab-openrouter-free`.
- Default `model` remains AMD direct local-coder.
- No `small_model` points to OpenRouter or the AMD 3090.
- No OpenRouter model call is made.
- Default OpenCode validation still returns `opencode-direct-local-ok`.
- LiteLLM remains unchanged.
- Open WebUI remains unchanged.
- Result is documented in `AGENT_STATUS.md`.
