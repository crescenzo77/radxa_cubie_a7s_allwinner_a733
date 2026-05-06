# Current Slice

## Slice 13: Prepare AMD OpenCode direct-local live-change approval brief

Prepare exact, reviewable commands to migrate AMD OpenCode from LiteLLM-only to a direct AMD local provider only.

## Purpose

Move OpenCode one step closer to the safer target architecture without changing live config yet.

This slice prepares the approval brief only. The first live migration must validate direct AMD local-coder access before adding any OpenRouter-free provider.

## Scope

Planning and approval-brief preparation only:

- Document backup command for AMD OpenCode config.
- Document candidate config path.
- Document direct-local candidate `opencode.json` shape.
- Document JSON validation command.
- Document local-only OpenCode validation command.
- Document rollback command.
- Do not edit `/home/enzo/.config/opencode/opencode.json`.
- Do not add `homelab-openrouter-free` yet.
- Do not call OpenRouter.
- Do not alter LiteLLM.
- Do not alter Open WebUI.
- Do not restart services.

## Constraints

- No live config edits in this slice.
- No remote mutation in this slice.
- No OpenRouter provider in the first live change.
- No OpenRouter model calls.
- No LiteLLM changes.
- No Open WebUI changes.
- Do not set `small_model` to the AMD 3090 model.
- Keep rollback simple: restore the previous OpenCode config.

## Approval Brief

### Target host

```text
amd
```

### Live config path

```text
/home/enzo/.config/opencode/opencode.json
```

### Candidate config path

```text
/home/enzo/.config/opencode/opencode.direct-local.candidate.json
```

### Backup command

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
cp opencode.json "opencode.json.bak.$(date +%Y%m%d-%H%M%S)"
ls -lh opencode.json opencode.json.bak.*
'
```

### Candidate config creation

This candidate intentionally configures only the direct AMD 3090 local-coder provider.

It does not add OpenRouter.

It omits `small_model` for the first direct-local validation because a direct backup provider is not part of this slice.

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

### Candidate JSON validation

```bash
ssh amd 'python3 -m json.tool /home/enzo/.config/opencode/opencode.direct-local.candidate.json >/tmp/opencode.direct-local.validated.json && echo "candidate-json-ok"'
```

### Live switch command

High-impact action: this replaces AMD OpenCode's live config.

Only run after reviewing the candidate and confirming rollback is available.

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
cp opencode.direct-local.candidate.json opencode.json
python3 -m json.tool opencode.json >/tmp/opencode.live.validated.json
echo "live-config-switched-to-direct-local"
'
```

### Local-only validation command

This test must use only the AMD local provider. It must not call OpenRouter.

```bash
ssh amd 'cd /srv/projects/homelab 2>/dev/null || cd ~
/home/enzo/.opencode/bin/opencode run "Reply with exactly: opencode-direct-local-ok"
'
```

Expected response:

```text
opencode-direct-local-ok
```

### Rollback command

Use this if OpenCode does not work after the live switch.

Replace `BACKUP_FILE` with the newest backup created by the backup command.

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
ls -1t opencode.json.bak.* | head -5
'
```

Then:

```bash
ssh amd 'set -e
cd /home/enzo/.config/opencode
cp BACKUP_FILE opencode.json
python3 -m json.tool opencode.json >/tmp/opencode.rollback.validated.json
echo "rollback-restored"
'
```

## Acceptance Criteria

- Approval brief is documented.
- Commands are copy-paste ready.
- Rollback is explicit.
- No live files are changed in this slice.
- No OpenRouter provider is added.
- No OpenRouter calls are made.
- Git diff is shown for review.
- Stop before commit.
