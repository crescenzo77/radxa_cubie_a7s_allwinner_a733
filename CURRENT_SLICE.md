# Current Slice

## Slice 14: Execute AMD OpenCode direct-local migration

Execute the approved narrow live change for AMD OpenCode: migrate from LiteLLM-only to a direct AMD local-coder provider only.

## Purpose

Validate that OpenCode can use the AMD 3090 local-coder endpoint directly without LiteLLM in the OpenCode path.

This slice intentionally does not add OpenRouter. OpenRouter-free provider integration remains a later slice after direct-local operation is proven.

## Scope

Live change on AMD only:

- Back up current AMD OpenCode config.
- Write candidate direct-local config beside the live config.
- Validate candidate JSON.
- Replace live OpenCode config with candidate.
- Validate live JSON.
- Run one local-only OpenCode test.
- Roll back immediately if validation fails.

## Constraints

- Do not add `homelab-openrouter-free`.
- Do not call OpenRouter.
- Do not alter LiteLLM.
- Do not alter Open WebUI.
- Do not restart Docker services.
- Do not delete old config.
- Do not set `small_model` to the AMD 3090 model.
- Keep rollback available before switching live config.
- Stop after the local-only OpenCode test and record the result.

## Live Change Commands

### 1. Backup current live config

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
backup="opencode.json.bak.$(date +%Y%m%d-%H%M%S)"
cp opencode.json "$backup"
echo "$backup"
python3 -m json.tool "$backup" >/tmp/opencode.backup.validated.json
echo "backup-json-ok"
'
```

### 2. Create candidate direct-local config

```bash
ssh amd 'cat > /home/enzo/.config/opencode/opencode.direct-local.candidate.json <<'"'"'EOF'"'"'
{
  "$schema": "https://opencode.ai/config.json",
  "enabled_providers": [
    "homelab-local"
  ],
  "model": "homelab-local/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
  "provider": {
    "homelab-local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Homelab Local",
      "options": {
        "baseURL": "http://192.168.50.252:8083/v1",
        "apiKey": "dummy",
        "timeout": 600000,
        "chunkTimeout": 60000
      },
      "models": {
        "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf": {
          "name": "local-coder | AMD RTX 3090 | Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
        }
      }
    }
  }
}
EOF'
```

### 3. Validate candidate JSON

```bash
ssh amd 'python3 -m json.tool /home/enzo/.config/opencode/opencode.direct-local.candidate.json >/tmp/opencode.direct-local.validated.json && echo "candidate-json-ok"'
```

### 4. Switch live config to direct-local

This is the live config change.

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
cp opencode.direct-local.candidate.json opencode.json
python3 -m json.tool opencode.json >/tmp/opencode.live.validated.json
echo "live-config-switched-to-direct-local"
'
```

### 5. Inspect live config without secrets

```bash
ssh amd 'python3 - <<'"'"'PY'"'"'
import json
from pathlib import Path

p = Path("/home/enzo/.config/opencode/opencode.json")
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

print(json.dumps(redact(data), indent=2))
PY'
```

### 6. Run local-only OpenCode validation

```bash
ssh amd 'cd /tmp
/home/enzo/.opencode/bin/opencode run "Reply with exactly: opencode-direct-local-ok"
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

### 2. Restore newest backup

Review the listed backup name first. Then replace `BACKUP_FILE` with the selected backup.

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
cp BACKUP_FILE opencode.json
python3 -m json.tool opencode.json >/tmp/opencode.rollback.validated.json
echo "rollback-restored"
'
```

### 3. Validate rollback path

```bash
ssh amd 'cd /tmp
/home/enzo/.opencode/bin/opencode run "Reply with exactly: opencode-router-ok"
'
```

Expected response after rollback:

```text
opencode-router-ok
```

## Acceptance Criteria

- Current OpenCode config is backed up.
- Candidate config validates as JSON.
- Live config validates as JSON after switch.
- OpenCode responds exactly `opencode-direct-local-ok`.
- No OpenRouter call is made.
- LiteLLM remains running and unchanged.
- Open WebUI remains unchanged.
- Result is documented in `AGENT_STATUS.md`.
- Commit records the outcome.
